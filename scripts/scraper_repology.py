#!/usr/bin/env python3
"""Fetch package statistics from Repology for all known distros.

Scrapes the global statistics table at https://repology.org/repositories/statistics
which lists all repos with their package counts.

Usage:
    source .venv/bin/activate
    python scripts/scraper_repology.py
"""

import os
import re

import httpx
import psycopg2
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.environ["DATABASE_URL"]
REPOLOGY_STATS = "https://repology.org/repositories/statistics"

REPOLOGY_DISPLAY_TO_SLUG: dict[str, str] = {
    "Arch Linux": "arch",
    "Ubuntu 24.04": "ubuntu",
    "Debian 12": "debian",
    "Fedora 44": "fedora",
    "Manjaro Stable": "manjaro",
    "openSUSE Tumbleweed": "opensuse",
    "nixpkgs unstable": "nixos",
    "Gentoo": "gentoo",
    "Void Linux x86_64": "void",
    "Slackware64 current": "slackware",
    "Kali Linux Rolling": "kali",
    "Alpine Linux Edge": "alpine",
    "MX Linux MX-25": "mx",
    "Devuan Unstable": "devuan",
    "Artix": "artix",
    "FreeBSD Ports": "freebsd",
    "Solus": "solus",
    "PCLinuxOS": "pclinuxos",
    "Tails stable": "tails",
    "CentOS Stream 9": "centos",
    "AlmaLinux 9": "alma",
    "Parrot": "parrot",
}


def get_db():
    conn = psycopg2.connect(DB_URL)
    return conn, conn.cursor()


def fetch_distro_slugs(cur) -> dict[str, int]:
    cur.execute("SELECT id, slug FROM distros")
    return {row[1]: row[0] for row in cur.fetchall()}


def parse_k(text: str) -> int:
    n = 0
    m = re.search(r"([\d.]+)(k?)", text)
    if m:
        n = float(m.group(1))
        if m.group(2) == "k":
            n *= 1000
    return int(n)


def scrape_statistics_table() -> dict[str, dict[str, int]]:
    headers = {"User-Agent": "ICanRunLinux/1.0 (research)"}
    resp = httpx.get(REPOLOGY_STATS, headers=headers, timeout=30)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    table = soup.find("table")
    if not table:
        return {}

    results: dict[str, dict[str, int]] = {}

    for tr in table.find_all("tr"):
        name_th = tr.find("th")
        if not name_th:
            continue
        name = name_th.get_text(strip=True)
        if not name or name in ("", "Total"):
            continue

        cells = tr.find_all("td")
        if len(cells) < 5:
            continue

        stats = {
            "total": parse_k(cells[0].get_text(strip=True)),
            "newest": parse_k(cells[2].get_text(strip=True)),
            "outdated": parse_k(cells[3].get_text(strip=True)),
            "problematic": parse_k(cells[5].get_text(strip=True)) if len(cells) > 5 else 0,
            "vulnerable": parse_k(cells[6].get_text(strip=True)) if len(cells) > 6 else 0,
        }
        results[name] = stats

    return results


def upsert_stats(cur, distro_id: int, stats: dict):
    cur.execute(
        """
        INSERT INTO distro_package_stats
            (distro_id, total_packages, outdated_packages, vulnerable_packages,
             newest_packages, problematic_packages, source_url)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        [
            distro_id,
            stats.get("total", 0),
            stats.get("outdated", 0),
            stats.get("vulnerable", 0),
            stats.get("newest", 0),
            stats.get("problematic", 0),
            "https://repology.org/repositories/statistics",
        ],
    )


def main():
    conn, cur = get_db()
    slug_map = fetch_distro_slugs(cur)
    print(f"📦 {len(slug_map)} distros in DB")

    table_data = scrape_statistics_table()
    print(f"📊 Parsed {len(table_data)} repos from statistics table")

    processed = 0
    for display_name, stats in table_data.items():
        slug = REPOLOGY_DISPLAY_TO_SLUG.get(display_name)
        if not slug:
            # fuzzy match: repo display name → slug
            for s, sid in slug_map.items():
                pat = s.replace("-", " ").lower()
                if pat in display_name.lower():
                    slug = s
                    break

        if slug and slug in slug_map:
            upsert_stats(cur, slug_map[slug], stats)
            conn.commit()
            processed += 1
            print(f"  ✓ {slug}: {stats['total']} pkgs  ({display_name})")

    cur.close()
    conn.close()
    print(f"\n✅ Done. Stats fetched for {processed} distros.")


if __name__ == "__main__":
    main()
