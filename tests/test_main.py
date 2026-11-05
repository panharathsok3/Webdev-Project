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


# User Story 2: Emergency Services test
@pytest.fixture
def fake_get_emergency_hospitals(monkeypatch):
    calls = []

    def fake(state):
        calls.append({"state": state})
        return [
            {
                "name": "TEST EMERGENCY HOSPITAL",
                "state": state,
                "emergency_services": True,
                "overall_rating": 5
            }
        ]

    monkeypatch.setattr(
        main,
        "get_emergency_hospitals",
        fake
    )

    return calls


def test_emergency_hospitals_by_state(
    fake_get_emergency_hospitals
):
    response = client.get(
        "/hospitals/emergency",
        params={"state": "CA"}
    )

    assert response.status_code == 200

    assert fake_get_emergency_hospitals == [
        {"state": "CA"}
    ]

    assert response.json()[0]["emergency_services"] is True


def test_emergency_hospitals_default_state(
    fake_get_emergency_hospitals
):
    response = client.get("/hospitals/emergency")

    assert response.status_code == 200

    assert fake_get_emergency_hospitals == [
        {"state": "CA"}
    ]


@pytest.mark.parametrize(
    "state",
    ["California", "123", "C"]
)
def test_emergency_hospitals_rejects_bad_state(
    fake_get_emergency_hospitals, state
):
    response = client.get(
        "/hospitals/emergency",
        params={"state": state}
    )

    assert response.status_code == 422
    assert fake_get_emergency_hospitals == []


# User Story 3: Readmissions test
@pytest.fixture
def fake_get_hospital_readmissions(monkeypatch):
    calls = []

    def fake(state):
        calls.append({"state": state})
        return [
            {
                "name": "TEST HOSPITAL",
                "state": state,
                "measure_name": "Readmission Rate",
                "score": 12.5,
                "compared_to_national": "Same as the National Rate"
            }
        ]

    monkeypatch.setattr(
        main,
        "get_hospital_readmissions",
        fake
    )

    return calls


def test_readmissions_by_state(
    fake_get_hospital_readmissions
):
    response = client.get(
        "/hospitals/readmissions",
        params={"state": "CA"}
    )

    assert response.status_code == 200

    assert fake_get_hospital_readmissions == [
        {"state": "CA"}
    ]

    assert response.json()[0]["measure_name"] == "Readmission Rate"


def test_readmissions_default_state(
    fake_get_hospital_readmissions
):
    response = client.get("/hospitals/readmissions")

    assert response.status_code == 200

    assert fake_get_hospital_readmissions == [
        {"state": "CA"}
    ]


@pytest.mark.parametrize(
    "state",
    ["California", "123", "C"]
)
def test_readmissions_rejects_bad_state(
    fake_get_hospital_readmissions, state
):
    response = client.get(
        "/hospitals/readmissions",
        params={"state": state}
    )

    assert response.status_code == 422
    assert fake_get_hospital_readmissions == []
