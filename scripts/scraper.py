#!/usr/bin/env python3
"""
DistroWatch Scraper para Linux Compatibility Checker
Extrae información de las distribuciones más populares
"""

import json
import re
import time
from typing import Optional

import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}

BASE_URL = "https://distrowatch.com"
POPULARITY_URL = f"{BASE_URL}/dwres.php?resource=popularity"


def get_page(url: str, retries: int = 3) -> Optional[BeautifulSoup]:
    """Obtiene una página con reintentos"""
    for i in range(retries):
        try:
            response = requests.get(url, headers=HEADERS, timeout=15)
            if response.status_code == 200:
                return BeautifulSoup(response.text, "html.parser")
            time.sleep(2)
        except requests.RequestException as e:
            print(f"Error en intento {i + 1}: {e}")
            time.sleep(3)
    return None


def extract_popular_distros(soup: BeautifulSoup) -> list[dict]:
    """Extrae la lista de distribuciones populares de tablas de ranking"""
    distros = []
    tables = soup.find_all("table")

    seen_names = set()

    for table in tables:
        text = table.get_text()
        if "Last 12 months" in text:
            ranks = table.find_all("th", class_="phr1")
            name_cells = table.find_all("td", class_="phr2")
            hit_cells = table.find_all("td", class_="phr3")

            for i, rank_th in enumerate(ranks[:50]):
                try:
                    rank = int(rank_th.get_text(strip=True))
                    name_td = name_cells[i] if i < len(name_cells) else None
                    hit_td = hit_cells[i] if i < len(hit_cells) else None

                    if name_td:
                        name = name_td.get_text(strip=True)
                        link = name_td.find("a")
                        slug = (
                            link.get("href", name.lower().replace(" ", "-")) if link else name.lower().replace(" ", "-")
                        )  # noqa: E501
                        if isinstance(slug, str) and "=" in slug:
                            slug = slug.split("=")[-1]
                        hits_text = hit_td.get_text(strip=True).replace(",", "") if hit_td else "0"
                        hits = int(hits_text) if hits_text.isdigit() else 0

                        if name and name not in seen_names and rank <= 100:
                            seen_names.add(name)
                            distros.append({"rank": rank, "name": name, "slug": slug, "hits_per_day": hits})
                except (ValueError, IndexError):
                    continue
            break

    distros.sort(key=lambda x: x["rank"])
    return distros


def extract_distro_details(slug: str) -> Optional[dict]:
    """Extrae detalles de una distribución específica"""
    url = f"{BASE_URL}/table.php?distribution={slug}"
    soup = get_page(url)

    if not soup:
        return None

    details = {
        "slug": slug,
        "url": url,
        "name": "",
        "based_on": [],
        "origin": "",
        "architecture": [],
        "desktop": [],
        "category": [],
        "status": "",
        "latest_version": "",
        "description": "",
        "popularity_rank": 0,
    }

    tables = soup.find_all("table")
    info_text = ""

    for table in tables:
        text = table.get_text()
        if "Based on:" in text:
            info_text = text
            break

    if info_text:
        based_match = re.search(r"Based on:\s*(.+?)(?=Origin:|Architecture:)", info_text, re.DOTALL)
        if based_match:
            based_val = based_match.group(1).strip()
            details["based_on"] = [b.strip() for b in re.split(r",\s*(?![^(]*\))", based_val) if b.strip()]

        origin_match = re.search(r"Origin:\s*([A-Za-z\s,]+?)(?=Architecture:|Desktop:)", info_text, re.DOTALL)
        if origin_match:
            details["origin"] = origin_match.group(1).strip()

        arch_match = re.search(r"Architecture:\s*([A-Za-z0-9_\-,\s]+?)(?=Desktop:)", info_text, re.DOTALL)
        if arch_match:
            arch_val = arch_match.group(1).strip()
            details["architecture"] = [a.strip() for a in arch_val.split(",") if a.strip()]

        desktop_match = re.search(r"Desktop:\s*([A-Za-z0-9\s,]+?)(?=Category:)", info_text, re.DOTALL)
        if desktop_match:
            desktop_val = desktop_match.group(1).strip()
            details["desktop"] = [d.strip() for d in desktop_val.split(",") if d.strip()]

        cat_match = re.search(r"Category:\s*([A-Za-z0-9\s,]+?)(?=Status:)", info_text, re.DOTALL)
        if cat_match:
            cat_val = cat_match.group(1).strip()
            details["category"] = [c.strip() for c in cat_val.split(",") if c.strip()]

        status_match = re.search(r"Status:\s*([A-Za-z]+)(?:\s*Popularity:)?", info_text, re.DOTALL)
        if status_match:
            details["status"] = status_match.group(1).strip()

        pop_match = re.search(r"Popularity:\s*(\d+)", info_text, re.DOTALL)
        if pop_match:
            details["popularity_rank"] = int(pop_match.group(1))

    h1 = soup.find("h1")
    if h1:
        details["name"] = (
            h1.get_text(strip=True).replace("Table of Distribution ", "").replace("Table of Distribution ", "")
        )  # noqa: E501

    divs = soup.find_all("div", class_="pkgtab")
    if divs:
        desc = divs[0].get_text(strip=True)
        details["description"] = desc[:1000]
    else:
        for table in tables:
            text = table.get_text()
            if details["name"] in text and " is a " in text:
                start_idx = text.find(" is a ")
                if start_idx > 0:
                    details["description"] = text[start_idx : start_idx + 600].strip()
                break

    return details


def enrich_distro_basic(distro: dict) -> dict:
    """Enriquece los datos brutos con información útil para matching"""

    use_cases = []
    difficulty = 3

    categories_raw = distro.get("category", [])
    desktops = distro.get("desktop", [])
    name = distro.get("name", "").lower()
    based_on = distro.get("based_on", [])

    if not isinstance(categories_raw, list):
        categories_raw = [categories_raw] if categories_raw else []
    categories = [c.lower() for c in categories_raw]
    if not isinstance(desktops, list):
        desktops = [desktops] if desktops else []
    if not isinstance(based_on, list):
        based_on = [based_on] if based_on else []
    based_on_lower = [b.lower() for b in based_on]

    if "beginners" in categories or "desktop" in categories:
        use_cases.append("desktop")
        use_cases.append("general_use")
        if "ubuntu" in name or "mint" in name or "zorin" in name:
            difficulty = 1
        else:
            difficulty = 2

    if "professional" in categories or "science" in categories:
        use_cases.append("development")
        use_cases.append("programming")
        difficulty = max(difficulty, 3)

    if "server" in categories or "debian" in based_on_lower:
        use_cases.append("servers")
        if "debian" in based_on_lower:
            use_cases.append("stability")
        difficulty = max(difficulty, 3)

    if "custom" in categories or "advanced" in categories:
        use_cases.append("advanced")
        use_cases.append("customization")
        difficulty = max(difficulty, 4)

    if "old computers" in categories or "old hardware" in categories or "lubuntu" in name or "xubuntu" in name:
        use_cases.append("low_resources")
        use_cases.append("old_hardware")
        difficulty = 1

    if any("kde" in d.lower() for d in desktops):
        use_cases.append("customization")
    if any("gnome" in d.lower() for d in desktops):
        use_cases.append("modern_ui")

    archs = distro.get("architecture", [])
    if isinstance(archs, str):
        archs = [archs]

    details = {
        **distro,
        "use_cases": use_cases,
        "difficulty": difficulty,
        "min_ram_gb": 2 if "old_hardware" in use_cases else 4,
        "min_storage_gb": 15 if "old_hardware" in use_cases else 25,
        "recommended_for": use_cases[:4] if use_cases else ["general_use"],
        "architectures": archs,
    }

    return details


def scrape_distrowatch(top_n: int = 50) -> list[dict]:
    """Ejecuta el scraping completo"""
    print(f"🔍 Obteniendo ranking de popularidad (Top {top_n})...")

    soup = get_page(POPULARITY_URL)
    if not soup:
        print("❌ Error al obtener la página de popularidad")
        return []

    distros = extract_popular_distros(soup)[:top_n]
    print(f"✅ Encontradas {len(distros)} distribuciones")

    enriched = []
    for i, distro in enumerate(distros, 1):
        print(f"📦 [{i}/{len(distros)}] Extrayendo: {distro['name']}...", end=" ")

        details = extract_distro_details(distro["slug"])
        if details:
            details["popularity_rank"] = distro["rank"]
            details["hits_per_day"] = distro["hits_per_day"]

            enriched_distro = enrich_distro_basic(details)
            enriched.append(enriched_distro)
            print(f"✓ {len(enriched)}/{i}")
        else:
            print("❌ (saltado)")

        time.sleep(1.5)

    return enriched


def main():
    print("=" * 60)
    print("🐧 Linux Compatibility Checker - DistroWatch Scraper")
    print("=" * 60)

    distros = scrape_distrowatch(top_n=50)

    if distros:
        output_file = "data/distros_raw.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(distros, f, indent=2, ensure_ascii=False)

        print(f"\n✅ Guardados {len(distros)} distros en {output_file}")

        print("\n📊 Resumen:")
        print(f"   - Distribuciones extraídas: {len(distros)}")
        ranks = [d.get("popularity_rank", 999) for d in distros if d.get("popularity_rank")]
        min_r = min(ranks) if ranks else 0
        max_r = max(ranks) if ranks else 0
        print(f"   - Rankings disponibles: {min_r} - {max_r}")
        bases = set()
        for d in distros:
            for b in d.get("based_on", []):
                bases.add(b)
        print(f"   - Bases detectadas: {bases}")
    else:
        print("\n❌ No se encontraron distribuciones")


if __name__ == "__main__":
    main()
