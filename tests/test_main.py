import os
import subprocess
import sys

import pytest
from fastapi.testclient import TestClient

import main
from main import app

client = TestClient(app)


@pytest.fixture
def fake_get_hospitals(monkeypatch):
    calls = []

    def fake(state=None, rating=None):
        calls.append({"state": state, "rating": rating})
        return [{"name": "TEST HOSPITAL", "overall_rating": rating}]

    monkeypatch.setattr(main, "get_hospitals", fake)
    return calls


def test_hospitals_passes_filters_to_database(fake_get_hospitals):
    response = client.get("/hospitals", params={"state": "me", "rating": 5})
    assert response.status_code == 200
    assert fake_get_hospitals == [{"state": "ME", "rating": 5}]


def test_hospitals_without_filters(fake_get_hospitals):
    response = client.get("/hospitals")
    assert response.status_code == 200
    assert fake_get_hospitals == [{"state": None, "rating": None}]


@pytest.mark.parametrize("params", [{"rating": 6}, {"rating": 0}, {"state": "Maine"}])
def test_hospitals_rejects_bad_filters(fake_get_hospitals, params):
    response = client.get("/hospitals", params=params)
    assert response.status_code == 422
    assert fake_get_hospitals == []


def test_hospitals_allows_frontend_origin(fake_get_hospitals):
    response = client.get("/hospitals", headers={"Origin": "http://localhost:5173"})
    assert response.headers["access-control-allow-origin"] == "*"


def test_home_returns_running_message():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hospital API is running"}


def test_missing_database_url_gives_clear_error():
    env = {key: value for key, value in os.environ.items() if key != "DATABASE_URL"}
    script = "import dotenv; dotenv.load_dotenv = lambda *a, **k: False; import database"
    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        env=env,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "DATABASE_URL is not set" in result.stderr
