from __future__ import annotations

import json

from app.config import AI_CACHE_THRESHOLD
from app.services.db import get_conn


def find_cached_recommendation(query_embedding: list[float]) -> list[dict] | None:
    """Look for a previous AI recommendation whose query_embedding is very
    similar to the current one.  Returns the parsed distro list or None."""
    conn = get_conn()
    cur = conn.cursor()

    vec_literal = "[" + ",".join(str(v) for v in query_embedding) + "]"
    sql = """
        SELECT response_json, query_embedding <=> %s::vector AS distance
        FROM ai_recommendations
        WHERE query_embedding IS NOT NULL
        ORDER BY query_embedding <=> %s::vector
        LIMIT 1
    """
    cur.execute(sql, [vec_literal, vec_literal])
    row = cur.fetchone()
    cur.close()
    conn.close()

    if row is None:
        return None

    distance: float = row[1]
    similarity = 1 - distance
    if similarity < AI_CACHE_THRESHOLD:
        return None

    raw = row[0]
    if isinstance(raw, str):
        return json.loads(raw)
    return raw  # already a Python object (list/dict) from JSONB


def save_ai_recommendation(
    query_text: str,
    query_embedding: list[float],
    distro_list: list[dict],
) -> None:
    """Persist an AI-generated recommendation so future similar queries can
    reuse it without calling the LLM again."""
    conn = get_conn()
    cur = conn.cursor()

    vec_literal = "[" + ",".join(str(v) for v in query_embedding) + "]"
    sql = """
        INSERT INTO ai_recommendations (query_text, query_embedding, response_json)
        VALUES (%s, %s::vector, %s)
    """
    cur.execute(sql, [query_text, vec_literal, json.dumps(distro_list)])
    conn.commit()
    cur.close()
    conn.close()
