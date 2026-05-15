#!/usr/bin/env python3
"""Enrich existing distros with technical metadata using DeepSeek via OpenRouter.

Usage:
    source .venv/bin/activate
    python scripts/enrich_technical.py

Processes all distros that have empty technical_notes, batch-wise.
"""

import json
import os
import sys
import time

import httpx
import psycopg2
from dotenv import load_dotenv

load_dotenv()

BATCH_SIZE = 5
API_URL = os.getenv("LLM_API_URL", "https://openrouter.ai/api/v1/chat/completions")
API_KEY = os.getenv("LLM_API_KEY", os.getenv("EMBEDDINGS_API_KEY", ""))
MODEL = os.getenv("LLM_MODEL", "deepseek/deepseek-chat")
DB_URL = os.environ["DATABASE_URL"]

ENRICH_PROMPT = """You are a Linux distribution analyst. Given a distribution name and its description, provide technical metadata.

Return ONLY a valid JSON object with this exact structure (no markdown, no explanations):

{
  "package_manager": "apt",
  "init_system": "systemd",
  "release_model": "LTS / 6-month cycle",
  "technical_notes": "Uses apt/deb packages. Systemd init. LTS versions supported for 5 years. Strong community support and extensive documentation. Ubuntu has a large package repository and supports Snaps natively. Default desktop is GNOME but official flavors provide KDE, Xfce, MATE, Budgie, and more."
}

Rules:
- "package_manager": the primary package management tool (apt, pacman, dnf, zypper, emerge, xbps, etc).
- "init_system": the init system (systemd, openrc, runit, s6, busybox-init, etc).
- "release_model": describe the release type and cadence (rolling, LTS every 2 years, fixed release, semi-rolling, point release, stable with backports).
- "technical_notes": a short paragraph (2-4 sentences) describing technical characteristics: package manager details, driver compatibility (NVIDIA, AMD, WiFi), default filesystem, kernel version policy, security features, desktop compositor info.
- If you are not certain about a specific value, use your best knowledge from the distribution's reputation and history.
"""


def get_db():
    conn = psycopg2.connect(DB_URL)
    return conn, conn.cursor()


def fetch_distros_to_enrich(cur) -> list[tuple[int, str, str]]:
    cur.execute(
        """
        SELECT id, name, COALESCE(description, '') || ' ' || COALESCE(array_to_string(use_cases, ' '), '') AS info
        FROM distros
        WHERE (technical_notes IS NULL OR technical_notes = '')
        ORDER BY id
        """
    )
    return cur.fetchall()


def call_llm_for_enrichment(name: str, info: str) -> dict | None:
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://icanrunlinux.local",
        "X-Title": "I Can Run Linux",
    }
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": ENRICH_PROMPT},
            {
                "role": "user",
                "content": f"Distribution: {name}\nExisting info: {info}",
            },
        ],
        "temperature": 0.3,
        "max_tokens": 512,
        "response_format": {"type": "json_object"},
    }

    resp = httpx.post(API_URL, json=payload, headers=headers, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    content = data["choices"][0]["message"]["content"]
    return json.loads(content)


def update_distro(cur, distro_id: int, metadata: dict):
    cur.execute(
        """
        UPDATE distros
        SET package_manager = %s,
            init_system = %s,
            release_model = %s,
            technical_notes = %s
        WHERE id = %s
        """,
        [
            metadata.get("package_manager", ""),
            metadata.get("init_system", ""),
            metadata.get("release_model", ""),
            metadata.get("technical_notes", ""),
            distro_id,
        ],
    )


def main():
    conn, cur = get_db()
    distros = fetch_distros_to_enrich(cur)
    total = len(distros)
    print(f"📦 Found {total} distros to enrich")

    if total == 0:
        print("✅ All distros already have technical data.")
        cur.close()
        conn.close()
        return

    for i in range(0, total, BATCH_SIZE):
        batch = distros[i : i + BATCH_SIZE]
        print(f"\n  Batch {i // BATCH_SIZE + 1}/{(total + BATCH_SIZE - 1) // BATCH_SIZE}")

        for d_id, name, info in batch:
            try:
                print(f"    → {name}...", end=" ", flush=True)
                metadata = call_llm_for_enrichment(name, info)
                if metadata:
                    update_distro(cur, d_id, metadata)
                    conn.commit()
                    print("✓")
                else:
                    print("✗ (empty response)")
            except Exception as e:
                conn.rollback()
                print(f"✗ ({e})")

            time.sleep(0.3)

    cur.close()
    conn.close()
    print(f"\n✅ Done. {total} distros enriched.")


if __name__ == "__main__":
    main()
