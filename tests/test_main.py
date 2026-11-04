import os
import subprocess
import sys

# A dummy URL is enough here. SQLAlchemy does not connect until a query runs.
os.environ.setdefault("DATABASE_URL", "postgresql://user:pass@localhost:5432/test")

from fastapi.testclient import TestClient  # noqa: E402

from main import app  # noqa: E402

client = TestClient(app)


def test_home_returns_running_message():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hospital API is running"}


def test_missing_database_url_gives_clear_error():
    # Fresh process with DATABASE_URL removed. load_dotenv is stubbed out
    # because a developer's real .env would otherwise put the URL back.
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
