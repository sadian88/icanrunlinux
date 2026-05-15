#!/usr/bin/env python3
"""Scrape Phoronix benchmark articles comparing multiple Linux distributions.

This scraper extracts benchmark test results from Phoronix review articles
that compare distros (e.g. "Linux Distribution Benchmarks for 2026").

Usage:
    source .venv/bin/activate
    python scripts/scraper_phoronix.py
"""

import os
import re
import sys
import time

import httpx
import psycopg2
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.environ["DATABASE_URL"]
DELAY = 2.0  # be polite to Phoronix

# Known Phoronix review articles comparing multiple distros
PHORONIX_ARTICLES = [
    "https://www.phoronix.com/review/cachyos-ubuntu-2604-fedora-44",
    "https://www.phoronix.com/review/popos-2404-ubuntu-2604",
    "https://www.phoronix.com/review/ubuntu-2510-2604-zen5",
    "https://www.phoronix.com/review/fedora-44-beta",
    "https://www.phoronix.com/review/ubuntu-2604-windows-11",
    "https://www.phoronix.com/review/ubuntu-2604-ryzen-ai-max",
]

# Distro name patterns Phoronix uses → our slug

# Distro name patterns Phoronix uses → our slug
PHORONIX_NAME_PATTERNS: dict[str, list[str]] = {
    "ubuntu": [r"\bUbuntu\b"],
    "linux-mint": [r"Linux Mint\b"],
    "debian": [r"\bDebian\b"],
    "fedora": [r"\bFedora\b"],
    "arch": [r"Arch Linux\b"],
    "manjaro": [r"\bManjaro\b"],
    "pop": [r"Pop!_OS\b"],
    "opensuse": [r"openSUSE\b"],
    "nixos": [r"\bNixOS\b"],
    "gentoo": [r"\bGentoo\b"],
    "void": [r"Void Linux\b"],
    "zorin": [r"Zorin OS\b"],
    "kali": [r"Kali Linux\b"],
    "endeavouros": [r"EndeavourOS\b"],
    "solus": [r"\bSolus\b"],
    "alpine": [r"Alpine Linux\b"],
    "mx": [r"MX Linux\b"],
    "garuda": [r"Garuda Linux\b"],
    "cachyos": [r"\bCachyOS\b"],
}


def get_db():
    conn = psycopg2.connect(DB_URL)
    return conn, conn.cursor()


def fetch_distro_slugs(cur) -> dict[str, int]:
    """Return {slug: id} for all distros."""
    cur.execute("SELECT id, slug FROM distros")
    return {row[1]: row[0] for row in cur.fetchall()}


def fetch_article(url: str) -> str | None:
    try:
        resp = httpx.get(url, headers={"User-Agent": "ICanRunLinux/1.0"}, timeout=30, follow_redirects=True)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        print(f"    ✗ HTTP error: {e}")
        return None


def find_distro_in_text(text: str) -> dict[str, int]:
    """Find which of our distros appear in the text. Returns {slug: count}."""
    matches: dict[str, int] = {}
    for slug, patterns in PHORONIX_NAME_PATTERNS.items():
        count = 0
        for pat in patterns:
            count += len(re.findall(pat, text))
        if count > 0:
            matches[slug] = count
    return matches


def extract_benchmark_data(html: str) -> list[dict]:
    """
    Try to extract benchmark scores from Phoronix article HTML.

    Phoronix articles often have benchmark tables with structure:
      <table class="benchmark"> ... <tr><td>Test Name</td><td>Score</td>...</tr>

    We look for any table that contains distro names in headers or rows.
    Returns list of {test_name, distro_scores: {slug: score}}.
    """
    soup = BeautifulSoup(html, "html.parser")
    results: list[dict] = []

    # Find all tables in the article
    tables = soup.find_all("table")
    for table in tables:
        rows = table.find_all("tr")
        if len(rows) < 2:
            continue

        # Check header row for distro names
        header_cells = rows[0].find_all(["th", "td"])
        header_texts = [cell.get_text(strip=True) for cell in header_cells]

        detected_slugs: dict[int, str] = {}  # col_index → slug
        for col_idx, htext in enumerate(header_texts):
            for slug, patterns in PHORONIX_NAME_PATTERNS.items():
                if any(re.search(p, htext) for p in patterns):
                    detected_slugs[col_idx] = slug

        if not detected_slugs:
            continue  # no distros in this table

        # Parse data rows
        for row in rows[1:]:
            cells = row.find_all(["th", "td"])
            if len(cells) < 2:
                continue

            test_name = cells[0].get_text(strip=True)
            if not test_name or len(test_name) > 80:
                continue

            scores: dict[str, float] = {}
            for col_idx, slug in detected_slugs.items():
                if col_idx < len(cells):
                    try:
                        val = cells[col_idx].get_text(strip=True)
                        # Try to parse as number
                        match = re.search(r"[\d.]+", val)
                        if match:
                            scores[slug] = float(match.group())
                    except (ValueError, TypeError):
                        pass

            if scores:
                results.append({"test_name": test_name, "distro_scores": scores})

    return results


def upsert_benchmark(cur, distro_id: int, test_name: str, score: float, source_url: str):
    cur.execute(
        """
        INSERT INTO distro_benchmarks (distro_id, test_name, score, source_url)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (distro_id, test_name, source_url) DO NOTHING
        """,
        [distro_id, test_name, round(score, 4), source_url],
    )


def main():
    conn, cur = get_db()
    distro_map = fetch_distro_slugs(cur)
    print(f"📦 {len(distro_map)} distros in DB")

    total_benchmarks = 0
    urls_scraped = 0

    for url in PHORONIX_ARTICLES:
        print(f"\n🔍 Scraping: {url}")
        html = fetch_article(url)
        if not html:
            continue

        urls_scraped += 1
        benchmark_data = extract_benchmark_data(html)
        print(f"  Found {len(benchmark_data)} benchmark tables/data points")

        for item in benchmark_data:
            test_name = item["test_name"]
            for slug, score in item["distro_scores"].items():
                distro_id = distro_map.get(slug)
                if distro_id:
                    upsert_benchmark(cur, distro_id, test_name, score, url)
                    total_benchmarks += 1

        if benchmark_data:
            conn.commit()
            print(f"  → Committed {len(benchmark_data)} records")

        time.sleep(DELAY)

    cur.close()
    conn.close()

    if urls_scraped == 0:
        print("\n⚠️  Could not access Phoronix articles. Run manually with a proxy or use cached data.")
    else:
        print(f"\n✅ Done. {total_benchmarks} benchmark scores stored.")


if __name__ == "__main__":
    main()
