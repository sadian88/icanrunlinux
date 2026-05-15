"""Test the enrich_distro_basic function."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from scraper import enrich_distro_basic


def test_basic_desktop_distro():
    d = enrich_distro_basic({
        "name": "Ubuntu",
        "category": ["Beginners", "Desktop"],
        "desktop": ["GNOME"],
        "architecture": ["x86_64"],
        "based_on": ["Debian"],
    })
    assert "desktop" in d["use_cases"]
    assert "general_use" in d["use_cases"]
    assert d["min_ram_gb"] == 4


def test_old_hardware_distro():
    d = enrich_distro_basic({
        "name": "Lubuntu",
        "category": ["Desktop"],
        "desktop": ["LXQt"],
        "architecture": ["x86_64"],
        "based_on": ["Ubuntu"],
    })
    assert "low_resources" in d["use_cases"]
    assert "old_hardware" in d["use_cases"]
    assert d["difficulty"] == 1
    assert d["min_ram_gb"] == 2


def test_server_distro():
    d = enrich_distro_basic({
        "name": "Debian",
        "category": ["Server"],
        "desktop": [],
        "architecture": ["x86_64"],
        "based_on": ["Independent"],
    })
    assert "servers" in d["use_cases"]


def test_advanced_distro():
    d = enrich_distro_basic({
        "name": "Arch",
        "category": ["Advanced"],
        "desktop": [],
        "architecture": ["x86_64"],
        "based_on": ["Independent"],
    })
    assert "advanced" in d["use_cases"]
    assert "customization" in d["use_cases"]
    assert d["difficulty"] >= 4


def test_kde_adds_customization():
    d = enrich_distro_basic({
        "name": "KDE neon",
        "category": ["Desktop"],
        "desktop": ["KDE Plasma"],
        "architecture": ["x86_64"],
        "based_on": ["Ubuntu"],
    })
    assert "customization" in d["use_cases"]


def test_gnome_adds_modern_ui():
    d = enrich_distro_basic({
        "name": "Fedora",
        "category": ["Desktop"],
        "desktop": ["GNOME"],
        "architecture": ["x86_64"],
        "based_on": ["Independent"],
    })
    assert "modern_ui" in d["use_cases"]


def test_empty_categories_fallsback():
    d = enrich_distro_basic({
        "name": "Some Distro",
        "category": [],
        "desktop": [],
        "architecture": ["x86_64"],
        "based_on": [],
    })
    assert d["difficulty"] == 3
    assert d["recommended_for"] == ["general_use"]
