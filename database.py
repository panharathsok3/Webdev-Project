import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    # Fail at startup with a fix, instead of a bare KeyError.
    raise RuntimeError(
        "DATABASE_URL is not set. Add it to a .env file in the repo root (see README)."
    )

engine = create_engine(DATABASE_URL, pool_pre_ping=True)


def get_hospitals():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT * FROM hospitals"))
        return [dict(row) for row in result.mappings()]
