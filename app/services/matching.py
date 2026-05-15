from __future__ import annotations

from typing import Optional

from app.config import MATCH_THRESHOLD
from app.services.ai_cache import find_cached_recommendation, save_ai_recommendation
from app.services.db import dict_row, get_conn
from app.services.embedding import get_embedding
from app.services.llm import call_llm


def _build_query_text(
    free_text: Optional[str] = None,
    use_cases: Optional[list[str]] = None,
    ram_gb: Optional[int] = None,
    storage_gb: Optional[int] = None,
    architecture: Optional[str] = None,
) -> str:
    parts: list[str] = []
    if free_text:
        parts.append(free_text)
    if use_cases:
        parts.append("Use cases: " + ", ".join(use_cases))
    if ram_gb:
        parts.append(f"RAM: {ram_gb}GB")
    if storage_gb:
        parts.append(f"Storage: {storage_gb}GB")
    if architecture:
        parts.append(f"Architecture: {architecture}")
    return " | ".join(parts) if parts else "Linux distribution recommendation"


def _vector_literal(vector: list[float]) -> str:
    return "[" + ",".join(str(v) for v in vector) + "]"


def _enrich_with_external_data(rows: list[dict]) -> list[dict]:
    """Attach benchmarks and package stats to distro rows."""
    if not rows:
        return rows

    ids = [str(r["id"]) for r in rows]
    id_list = ",".join(ids)

    conn = get_conn()
    cur = conn.cursor()

    # Fetch benchmarks
    cur.execute(
        f"""
        SELECT distro_id, test_name, score, unit, source_url
        FROM distro_benchmarks
        WHERE distro_id IN ({id_list})
        ORDER BY distro_id, test_name
        """
    )
    benchmarks: dict[int, list[dict]] = {}
    for row in cur.fetchall():
        bid = row[0]
        benchmarks.setdefault(bid, []).append(
            {
                "test_name": row[1],
                "score": row[2],
                "unit": row[3] or "",
                "source_url": row[4] or "",
            }
        )

    # Fetch package stats (max total_packages per distro - pick the main repo)
    cur.execute(
        f"""
        SELECT DISTINCT ON (distro_id)
            distro_id, total_packages, outdated_packages,
            vulnerable_packages, newest_packages, problematic_packages,
            source_url
        FROM distro_package_stats
        WHERE distro_id IN ({id_list})
        ORDER BY distro_id, total_packages DESC
        """
    )
    pkg_stats: dict[int, dict] = {}
    for row in cur.fetchall():
        pkg_stats[row[0]] = {
            "total_packages": row[1] or 0,
            "outdated_packages": row[2] or 0,
            "vulnerable_packages": row[3] or 0,
            "newest_packages": row[4] or 0,
            "problematic_packages": row[5] or 0,
            "source_url": row[6] or "",
        }

    cur.close()
    conn.close()

    for row in rows:
        rid = row["id"]
        row["benchmarks"] = benchmarks.get(rid, [])
        row["package_stats"] = pkg_stats.get(rid)

    return rows


def _fetch_distro_by_slug(slug: str) -> dict | None:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM distros WHERE slug = %s", [slug])
    row = cur.fetchone()
    if row:
        result = dict_row(cur, row)
    else:
        result = None
    cur.close()
    conn.close()
    return result


def _insert_distro_from_llm(distro: dict) -> dict:
    """Insert a new AI-suggested distro and return the inserted row."""
    conn = get_conn()
    cur = conn.cursor()

    # Generate embedding (include technical_notes for richer semantic search)
    tech_notes = distro.get("technical_notes", "") or ""
    text_for_embedding = (
        f"{distro.get('name', '')} {distro.get('description', '')} "
        f"{' '.join(distro.get('use_cases', []))} "
        f"{' '.join(distro.get('category', []))} "
        f"{' '.join(distro.get('desktop', []))} "
        f"Package manager: {distro.get('package_manager', '')} "
        f"Init system: {distro.get('init_system', '')} "
        f"Release model: {distro.get('release_model', '')} "
        f"Technical notes: {tech_notes}"
    ).strip()
    embedding = get_embedding(text_for_embedding)
    vec_literal = _vector_literal(embedding)

    cur.execute(
        """
        INSERT INTO distros (
            slug, url, name, based_on, origin, architecture, desktop,
            category, status, latest_version, description, popularity_rank,
            hits_per_day, use_cases, difficulty, min_ram_gb, min_storage_gb,
            recommended_for, architectures, package_manager, init_system,
            release_model, technical_notes, embedding, created_at, updated_at
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s,
            %s::vector, NOW(), NOW()
        ) RETURNING id
        """,
        [
            distro["slug"],
            distro.get("url", f"https://distrowatch.com/{distro['slug']}"),
            distro["name"],
            distro.get("based_on", []),
            distro.get("origin"),
            distro.get("architectures", ["x86_64"]),
            distro.get("desktop", []),
            distro.get("category", []),
            distro.get("status"),
            distro.get("latest_version"),
            distro.get("description"),
            distro.get("popularity_rank"),
            distro.get("hits_per_day"),
            distro.get("use_cases", []),
            distro.get("difficulty", 3),
            distro.get("min_ram_gb"),
            distro.get("min_storage_gb"),
            distro.get("recommended_for", []),
            distro.get("architectures", ["x86_64"]),
            distro.get("package_manager", ""),
            distro.get("init_system", ""),
            distro.get("release_model", ""),
            tech_notes,
            vec_literal,
        ],
    )
    new_id = cur.fetchone()[0]
    conn.commit()

    cur.execute("SELECT * FROM distros WHERE id = %s", [new_id])
    row = cur.fetchone()
    new_distro = dict_row(cur, row)
    cur.close()
    conn.close()
    return new_distro


def find_compatible(
    ram_gb: Optional[int] = None,
    storage_gb: Optional[int] = None,
    use_cases: Optional[list[str]] = None,
    architecture: Optional[str] = None,
    difficulty: Optional[list[int]] = None,
    free_text: Optional[str] = None,
    limit: int = 10,
) -> list[dict]:
    """Vector search against the distros table returning real cosine similarity."""
    conn = get_conn()
    cur = conn.cursor()

    conditions: list[str] = []
    params: list = []

    if ram_gb is not None:
        conditions.append("(min_ram_gb IS NULL OR min_ram_gb <= %s)")
        params.append(ram_gb)

    if storage_gb is not None:
        conditions.append("(min_storage_gb IS NULL OR min_storage_gb <= %s)")
        params.append(storage_gb)

    if architecture:
        conditions.append("%s = ANY(architectures)")
        params.append(architecture)

    if difficulty:
        placeholders = ", ".join(["%s" for _ in difficulty])
        conditions.append(f"difficulty IN ({placeholders})")
        params.extend(difficulty)

    where_clause = ""
    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    if free_text:
        vector = get_embedding(free_text)
        vec_literal = _vector_literal(vector)
        # Real cosine similarity = 1 - cosine distance
        query_sql = f"""
            SELECT *, 1 - (embedding <=> %s::vector) AS similarity
            FROM distros
            {where_clause}
            ORDER BY embedding <=> %s::vector
            LIMIT %s
        """
        params.append(vec_literal)
        params.append(vec_literal)
        params.append(limit)
    else:
        query_sql = f"""
            SELECT *, NULL::float AS similarity
            FROM distros
            {where_clause}
            ORDER BY popularity_rank ASC NULLS LAST
            LIMIT %s
        """
        params.append(limit)

    cur.execute(query_sql, params)
    rows = [dict_row(cur, row) for row in cur.fetchall()]
    cur.close()
    conn.close()

    # Enrich with benchmarks and package stats from external sources
    rows = _enrich_with_external_data(rows)

    results = []
    if free_text:
        for row in rows:
            sim = row.pop("similarity", 0.0) or 0.0
            sim = max(0.0, min(1.0, float(sim)))
            results.append({"distro": row, "similarity": round(sim, 4), "source": "database"})
    else:
        max_rank = max((r["popularity_rank"] or 999) for r in rows) if rows else 999
        for row in rows:
            rank = row["popularity_rank"] or max_rank
            sim = round(1.0 - (rank - 1) / max_rank, 4) if max_rank > 0 else 1.0
            results.append({"distro": row, "similarity": sim, "source": "database"})

    return results[:limit]


def find_compatible_hybrid(
    ram_gb: Optional[int] = None,
    storage_gb: Optional[int] = None,
    use_cases: Optional[list[str]] = None,
    architecture: Optional[str] = None,
    difficulty: Optional[list[int]] = None,
    free_text: Optional[str] = None,
    limit: int = 10,
) -> list[dict]:
    """Three-tier recommendation engine:

    1. AI cache – reuse a previous LLM answer if the query is very similar.
    2. pgvector search – real cosine similarity against DistroWatch data.
    3. LLM fallback – ask DeepSeek when the best DB match is below threshold.

    New distros suggested by the LLM are inserted into the DB so future
    queries benefit from them (self-enrichment).
    """
    query_text = _build_query_text(free_text, use_cases, ram_gb, storage_gb, architecture)

    # ------------------------------------------------------------------
    # 1. Generate embedding for the query
    # ------------------------------------------------------------------
    query_embedding = get_embedding(query_text)

    # ------------------------------------------------------------------
    # 2. Check AI cache
    # ------------------------------------------------------------------
    cached = find_cached_recommendation(query_embedding)
    if cached:
        results = []
        for item in cached[:limit]:
            # Build a Distro-like dict from the cached JSON
            cached_distro = {
                "id": item.get("id", 0),
                "slug": item.get("slug", ""),
                "url": item.get("url", ""),
                "name": item.get("name", ""),
                "based_on": item.get("based_on", []),
                "origin": item.get("origin"),
                "architecture": item.get("architectures", []),
                "desktop": item.get("desktop", []),
                "category": item.get("category", []),
                "status": item.get("status"),
                "latest_version": item.get("latest_version"),
                "description": item.get("description", ""),
                "popularity_rank": item.get("popularity_rank"),
                "hits_per_day": item.get("hits_per_day"),
                "use_cases": item.get("use_cases", []),
                "difficulty": item.get("difficulty", 3),
                "min_ram_gb": item.get("min_ram_gb"),
                "min_storage_gb": item.get("min_storage_gb"),
                "recommended_for": item.get("recommended_for", []),
                "architectures": item.get("architectures", []),
                "created_at": item.get("created_at"),
                "updated_at": item.get("updated_at"),
            }
            results.append(
                {
                    "distro": cached_distro,
                    "similarity": 1.0,
                    "source": "ai_cache",
                    "ai_reason": item.get("why", ""),
                }
            )
        return results

    # ------------------------------------------------------------------
    # 3. Search distros via pgvector (with real similarity)
    # ------------------------------------------------------------------
    db_results = find_compatible(
        ram_gb=ram_gb,
        storage_gb=storage_gb,
        use_cases=None,  # soft boost below
        architecture=architecture,
        difficulty=difficulty,
        free_text=free_text,
        limit=limit * 2,
    )

    # Soft boost for use-case overlap
    if use_cases:
        for r in db_results:
            distro_uc = set(r["distro"].get("use_cases", []))
            if distro_uc & set(use_cases):
                r["similarity"] = min(1.0, r["similarity"] + 0.15)

    db_results.sort(key=lambda x: x["similarity"], reverse=True)
    db_results = db_results[:limit]

    best_similarity = db_results[0]["similarity"] if db_results else 0.0

    # ------------------------------------------------------------------
    # 4. If best match is strong enough, return DB results
    # ------------------------------------------------------------------
    if best_similarity >= MATCH_THRESHOLD:
        return db_results

    # ------------------------------------------------------------------
    # 5. Fallback to LLM (DeepSeek via OpenRouter)
    # ------------------------------------------------------------------
    try:
        llm_distros = call_llm(query_text, limit=limit)
    except Exception as exc:
        # LLM call failed – log and fall back to weak DB results
        import logging

        logging.getLogger(__name__).warning("LLM fallback failed: %s", exc)
        return db_results

    if not llm_distros:
        # LLM returned empty – return whatever DB gave us, even if weak
        return db_results

    # Persist raw LLM response for future cache hits
    try:
        save_ai_recommendation(query_text, query_embedding, llm_distros)
    except Exception:
        pass  # don't block the response if cache insert fails

    # Build results, merging with existing DB rows or inserting new ones
    llm_results = []
    for d in llm_distros:
        existing = _fetch_distro_by_slug(d["slug"])
        if existing:
            llm_results.append(
                {
                    "distro": existing,
                    "similarity": 0.95,
                    "source": "llm",
                    "ai_reason": d.get("why", ""),
                }
            )
        else:
            try:
                new_distro = _insert_distro_from_llm(d)
                llm_results.append(
                    {
                        "distro": new_distro,
                        "similarity": 0.95,
                        "source": "llm",
                        "ai_reason": d.get("why", ""),
                    }
                )
            except Exception as exc:
                import logging

                logging.getLogger(__name__).warning("Failed to insert AI distro %s: %s", d.get("slug"), exc)
                # Still return the distro data even if DB insert failed
                llm_results.append(
                    {
                        "distro": d,
                        "similarity": 0.95,
                        "source": "llm",
                        "ai_reason": d.get("why", ""),
                    }
                )

    return llm_results
