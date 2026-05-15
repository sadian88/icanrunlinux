"""Test scraper parsing with mocked HTML."""

import sys
from pathlib import Path
from unittest.mock import patch

from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from scraper import enrich_distro_basic, extract_distro_details, extract_popular_distros

POPULARITY_HTML = (
    '<html><body><table>'
    '<tr><th colspan="3">Last 12 months</th></tr>'
    '<tr><th class="phr1">1</th>'
    '<td class="phr2"><a href="?distribution=mint">Linux Mint</a></td>'
    '<td class="phr3">2,451</td></tr>'
    '<tr><th class="phr1">2</th>'
    '<td class="phr2"><a href="?distribution=ubuntu">Ubuntu</a></td>'
    '<td class="phr3">1,066</td></tr>'
    '<tr><th class="phr1">3</th>'
    '<td class="phr2"><a href="?distribution=debian">Debian</a></td>'
    '<td class="phr3">1,555</td></tr>'
    '</table></body></html>'
)

DETAIL_HTML = (
    '<html><body>'
    '<h1>Linux Mint</h1>'
    '<table>'
    '<tr><td>Based on:</td><td>Debian (Stable), Ubuntu (LTS)</td></tr>'
    '<tr><td>Origin:</td><td>Ireland</td></tr>'
    '<tr><td>Architecture:</td><td>x86_64</td></tr>'
    '<tr><td>Desktop:</td><td>Cinnamon, MATE, Xfce</td></tr>'
    '<tr><td>Category:</td><td>Beginners, Desktop, Live Medium</td></tr>'
    '<tr><td>Status:</td><td>Active</td></tr>'
    '</table>'
    '<div class="pkgtab">Linux Mint is a great distribution for beginners.</div>'
    '</body></html>'
)


def test_extract_popular_distros():
    soup = BeautifulSoup(POPULARITY_HTML, "html.parser")
    result = extract_popular_distros(soup)
    assert len(result) == 3
    assert result[0]["name"] == "Linux Mint"
    assert result[0]["rank"] == 1
    assert result[0]["slug"] == "mint"
    assert result[1]["slug"] == "ubuntu"
    assert result[2]["slug"] == "debian"


@patch("scraper.get_page")
def test_extract_distro_details(mock_get_page):
    mock_get_page.return_value = BeautifulSoup(DETAIL_HTML, "html.parser")
    details = extract_distro_details("mint")
    assert details is not None
    assert details["name"] == "Linux Mint"
    assert "Debian (Stable)" in details["based_on"]
    assert details["origin"] == "Ireland"
    assert "x86_64" in details["architecture"]
    assert "Cinnamon" in details["desktop"]
    assert "Beginners" in details["category"]
    assert details["status"] == "Active"


@patch("scraper.get_page")
def test_full_pipeline(mock_get_page):
    mock_get_page.return_value = BeautifulSoup(DETAIL_HTML, "html.parser")
    details = extract_distro_details("mint")
    assert details is not None
    enriched = enrich_distro_basic(details)
    assert enriched["difficulty"] == 1
    assert "desktop" in enriched["use_cases"]
    assert "general_use" in enriched["use_cases"]
    assert enriched["min_ram_gb"] == 4
