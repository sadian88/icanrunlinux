"""Test FastAPI endpoints with mocked DB and embeddings."""

from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


MOCK_DISTRO = {
    "id": 1,
    "slug": "ubuntu",
    "url": "https://distrowatch.com/table.php?distribution=ubuntu",
    "name": "Ubuntu",
    "based_on": ["Debian"],
    "origin": "Isle of Man",
    "architecture": ["x86_64"],
    "desktop": ["GNOME"],
    "category": ["Beginners", "Desktop"],
    "status": "Active",
    "latest_version": "",
    "description": "Ubuntu is a complete desktop Linux OS.",
    "popularity_rank": 10,
    "hits_per_day": 1066,
    "use_cases": ["desktop", "general_use", "modern_ui"],
    "difficulty": 1,
    "min_ram_gb": 4,
    "min_storage_gb": 25,
    "recommended_for": ["desktop", "general_use"],
    "architectures": ["x86_64"],
    "created_at": "2026-01-01T00:00:00",
    "updated_at": "2026-01-01T00:00:00",
}


class FakeCursor:
    def __init__(self, rows, columns=None):
        self._rows = rows
        self.description = columns or [
            ("id",), ("slug",), ("url",), ("name",), ("based_on",),
            ("origin",), ("architecture",), ("desktop",), ("category",),
            ("status",), ("latest_version",), ("description",),
            ("popularity_rank",), ("hits_per_day",), ("use_cases",),
            ("difficulty",), ("min_ram_gb",), ("min_storage_gb",),
            ("recommended_for",), ("architectures",),
            ("created_at",), ("updated_at",),
        ]

    def execute(self, query, params=None):
        pass

    def fetchall(self):
        return self._rows

    def close(self):
        pass


class FakeConn:
    def cursor(self):
        return self._cursor

    def close(self):
        pass


def fake_conn_factory(rows):
    cur = FakeCursor(rows)
    conn = FakeConn()
    conn._cursor = cur
    return conn


@patch("app.routers.distros.get_conn")
def test_get_distros(mock_conn):
    mock_conn.return_value = fake_conn_factory([tuple(MOCK_DISTRO.values())])
    resp = client.get("/distros?limit=5")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["slug"] == "ubuntu"


@patch("app.routers.distros.get_conn")
def test_get_distros_filter_slug(mock_conn):
    mock_conn.return_value = fake_conn_factory([tuple(MOCK_DISTRO.values())])
    resp = client.get("/distros?slug=ubuntu")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["slug"] == "ubuntu"


@patch("app.routers.recommend.find_compatible")
def test_recommend_with_filters(mock_find):
    mock_find.return_value = [{"distro": MOCK_DISTRO, "similarity": 0.95}]
    resp = client.post(
        "/recommend",
        json={"ram_gb": 4, "use_cases": ["desktop"], "limit": 5},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["similarity"] == 0.95
    assert data[0]["distro"]["slug"] == "ubuntu"
    call_args = mock_find.call_args
    assert call_args.kwargs["ram_gb"] == 4
    assert call_args.kwargs["use_cases"] == ["desktop"]


@patch("app.routers.recommend.find_compatible")
def test_recommend_with_free_text(mock_find):
    mock_find.return_value = [{"distro": MOCK_DISTRO, "similarity": 0.98}]
    resp = client.post(
        "/recommend",
        json={"free_text": "beginner friendly ubuntu based"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["similarity"] == 0.98
    call_args = mock_find.call_args
    assert call_args.kwargs["free_text"] == "beginner friendly ubuntu based"
