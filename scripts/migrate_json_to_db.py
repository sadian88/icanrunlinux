#!/usr/bin/env python3
"""Load distros_raw.json into PostgreSQL + generate embeddings via external API."""

import asyncio
import json
import os
import sys
import time
from pathlib import Path

import httpx
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATA_FILE = Path("data/distros_raw.json")
BATCH_SIZE = 20


def build_embedding_text(distro: dict) -> str:
    parts = [
        f"Distribution: {distro.get('name', '')}",
        f"Description: {distro.get('description', '')}",
        f"Use cases: {', '.join(distro.get('use_cases', []))}",
        f"Categories: {', '.join(distro.get('category', []))}",
        f"Desktop environments: {', '.join(distro.get('desktop', []))}",
        f"Difficulty: {distro.get('difficulty', 3)}",
    ]
    return "\n".join(p for p in parts if p and not p.endswith(": "))


def get_embedding_client() -> tuple[httpx.AsyncClient, str]:
    raw = os.getenv("EMBEDDINGS_API_URL", "https://api.openai.com/v1/embeddings")
    api_url = raw.rstrip("/")
    if not api_url.endswith("/embeddings"):
        api_url += "/embeddings"
    api_key = os.getenv("EMBEDDINGS_API_KEY", "")
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    return httpx.AsyncClient(headers=headers, timeout=60), api_url


async def fetch_embeddings(
    client: httpx.AsyncClient, url: str, texts: list[str]
) -> list[list[float]]:
    model = os.getenv("EMBEDDINGS_MODEL", "text-embedding-3-small")
    dims = os.getenv("EMBEDDINGS_DIMENSIONS")
    payload = {"input": texts, "model": model}
    if dims:
        payload["dimensions"] = int(dims)
    resp = await client.post(url, json=payload)
    try:
        resp.raise_for_status()
        data = resp.json()
    except Exception:
        print(f"  ❌ API error: {resp.status_code} {resp.text[:300]}")
        raise
    return [item["embedding"] for item in sorted(data["data"], key=lambda x: x["index"])]


def get_db() -> tuple:
    db_url = os.environ["DATABASE_URL"]
    conn = psycopg2.connect(db_url)
    return conn, conn.cursor()


def upsert_distro(cur, distro: dict, embedding: list[float]):
    cur.execute(
        """
        INSERT INTO distros (
            slug, url, name, based_on, origin, architecture, desktop,
            category, status, latest_version, description,
            popularity_rank, hits_per_day, use_cases, difficulty,
            min_ram_gb, min_storage_gb, recommended_for, architectures,
            package_manager, init_system, release_model, technical_notes,
            embedding, updated_at
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s,
            %s::vector, NOW()
        ) ON CONFLICT (slug) DO UPDATE SET
            url = EXCLUDED.url,
            name = EXCLUDED.name,
            based_on = EXCLUDED.based_on,
            origin = EXCLUDED.origin,
            architecture = EXCLUDED.architecture,
            desktop = EXCLUDED.desktop,
            category = EXCLUDED.category,
            status = EXCLUDED.status,
            latest_version = EXCLUDED.latest_version,
            description = EXCLUDED.description,
            popularity_rank = EXCLUDED.popularity_rank,
            hits_per_day = EXCLUDED.hits_per_day,
            use_cases = EXCLUDED.use_cases,
            difficulty = EXCLUDED.difficulty,
            min_ram_gb = EXCLUDED.min_ram_gb,
            min_storage_gb = EXCLUDED.min_storage_gb,
            recommended_for = EXCLUDED.recommended_for,
            architectures = EXCLUDED.architectures,
            package_manager = EXCLUDED.package_manager,
            init_system = EXCLUDED.init_system,
            release_model = EXCLUDED.release_model,
            technical_notes = EXCLUDED.technical_notes,
            embedding = EXCLUDED.embedding,
            updated_at = NOW()
        """,
        (
            distro["slug"],
            distro.get("url", ""),
            distro.get("name", ""),
            distro.get("based_on", []),
            distro.get("origin"),
            distro.get("architecture", []),
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
            distro.get("architectures", []),
            distro.get("package_manager", ""),
            distro.get("init_system", ""),
            distro.get("release_model", ""),
            distro.get("technical_notes", ""),
            embedding,
        ),
    )


async def main():
    if not DATA_FILE.exists():
        print(f"❌ {DATA_FILE} not found. Run scripts/scraper.py first.")
        sys.exit(1)

    with open(DATA_FILE, encoding="utf-8") as f:
        distros = json.load(f)

    print(f"📦 Loaded {len(distros)} distros from JSON")

    conn, cur = get_db()
    print("✅ Connected to database")

    client, api_url = get_embedding_client()
    print(f"🤖 Embeddings API: {api_url}")

    inserted = 0
    for i in range(0, len(distros), BATCH_SIZE):
        batch = distros[i : i + BATCH_SIZE]
        texts = [build_embedding_text(d) for d in batch]

        try:
            embeddings = await fetch_embeddings(client, api_url, texts)
        except httpx.HTTPStatusError as e:
            print(f"❌ Embedding API error at batch {i}: {e}")
            print(f"   Response: {e.response.text[:200]}")
            cur.close()
            conn.close()
            sys.exit(1)

        for distro, embedding in zip(batch, embeddings):
            upsert_distro(cur, distro, embedding)
            inserted += 1

        conn.commit()
        print(f"  ✓ [{i + len(batch)}/{len(distros)}] inserted batch")

        if i + BATCH_SIZE < len(distros):
            time.sleep(0.5)

    await client.aclose()
    cur.close()
    conn.close()
    print(f"\n✅ Done. {inserted} distros inserted/updated.")


if __name__ == "__main__":
    asyncio.run(main())
