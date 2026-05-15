from __future__ import annotations

import uuid
from typing import Optional

from app.services.db import dict_row, get_conn


def generate_session_token() -> str:
    return uuid.uuid4().hex


def save_search_history(
    session_token: str,
    ip_address: str,
    request_data: dict,
) -> None:
    conn = get_conn()
    cur = conn.cursor()
    import json

    cur.execute(
        """
        INSERT INTO search_history (ip_address, session_token, request_data)
        VALUES (%s, %s, %s)
        ON CONFLICT (session_token) DO NOTHING
        """,
        [ip_address, session_token, json.dumps(request_data)],
    )
    conn.commit()
    cur.close()
    conn.close()


def submit_feedback(
    session_token: str,
    ip_address: str,
    rating: Optional[int],
    comment: Optional[str],
    search_query: Optional[str] = None,
) -> bool:
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        "SELECT id FROM search_history WHERE session_token = %s",
        [session_token],
    )
    if cur.fetchone() is None:
        cur.close()
        conn.close()
        return False

    if rating is not None and not (1 <= rating <= 5):
        rating = None
    if comment is not None and isinstance(comment, str):
        comment = comment.strip()[:2000]

    cur.execute(
        """
        INSERT INTO search_feedback (session_token, ip_address, search_query, rating, comment)
        VALUES (%s, %s, %s, %s, %s)
        """,
        [session_token, ip_address, search_query, rating, comment],
    )
    conn.commit()
    cur.close()
    conn.close()
    return True


def get_history_by_ip(ip_address: str, limit: int = 20) -> list[dict]:
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            sh.id,
            sh.session_token,
            sh.request_data,
            sh.created_at,
            sf.id AS feedback_id,
            sf.rating,
            sf.comment,
            sf.search_query AS feedback_query,
            sf.created_at AS feedback_created_at
        FROM search_history sh
        LEFT JOIN search_feedback sf ON sf.session_token = sh.session_token
        WHERE sh.ip_address = %s
        ORDER BY sh.created_at DESC
        LIMIT %s
        """,
        [ip_address, limit],
    )

    rows = [dict_row(cur, row) for row in cur.fetchall()]
    cur.close()
    conn.close()

    sessions: dict[str, dict] = {}
    for row in rows:
        token = row["session_token"]
        if token not in sessions:
            sessions[token] = {
                "session_token": token,
                "request_data": row.get("request_data"),
                "created_at": row.get("created_at").isoformat() if row.get("created_at") else None,
                "feedback": None,
            }
        if row.get("feedback_id"):
            sessions[token]["feedback"] = {
                "rating": row.get("rating"),
                "comment": row.get("comment"),
                "created_at": row.get("feedback_created_at").isoformat() if row.get("feedback_created_at") else None,
            }

    return list(sessions.values())


def get_feedback_for_session(session_token: str) -> Optional[dict]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT rating, comment, created_at, search_query
        FROM search_feedback
        WHERE session_token = %s
        ORDER BY created_at DESC
        LIMIT 1
        """,
        [session_token],
    )
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row is None:
        return None
    return {
        "rating": row[0],
        "comment": row[1],
        "created_at": row[2].isoformat() if row[2] else None,
        "search_query": row[3],
    }


def get_public_feedback(limit: int = 50) -> list[dict]:
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            sf.id AS feedback_id,
            sf.rating,
            sf.comment,
            sf.search_query,
            sf.created_at AS feedback_created_at,
            sh.request_data,
            sh.created_at AS search_created_at,
            sh.session_token
        FROM search_feedback sf
        JOIN search_history sh ON sh.session_token = sf.session_token
        ORDER BY sf.created_at DESC
        LIMIT %s
        """,
        [limit],
    )

    rows = [dict_row(cur, row) for row in cur.fetchall()]
    cur.close()
    conn.close()

    results = []
    for row in rows:
        results.append({
            "rating": row.get("rating"),
            "comment": row.get("comment"),
            "search_query": row.get("search_query"),
            "request_data": row.get("request_data"),
            "created_at": row.get("feedback_created_at").isoformat() if row.get("feedback_created_at") else None,
        })

    return results
