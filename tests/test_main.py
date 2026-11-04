import os
import subprocess
import sys

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


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
