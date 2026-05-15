import httpx

from app.config import (
    EMBEDDINGS_API_KEY,
    EMBEDDINGS_API_URL,
    EMBEDDINGS_DIMENSIONS,
    EMBEDDINGS_MODEL,
)


def build_embedding_url() -> str:
    url = EMBEDDINGS_API_URL.rstrip("/")
    if not url.endswith("/embeddings"):
        url += "/embeddings"
    return url


def get_embedding(text: str) -> list[float]:
    url = build_embedding_url()
    headers = {"Authorization": f"Bearer {EMBEDDINGS_API_KEY}", "Content-Type": "application/json"}
    payload: dict = {"input": text, "model": EMBEDDINGS_MODEL}
    if EMBEDDINGS_DIMENSIONS:
        payload["dimensions"] = int(EMBEDDINGS_DIMENSIONS)

    resp = httpx.post(url, json=payload, headers=headers, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return data["data"][0]["embedding"]
