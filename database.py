import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not set. Add it to a .env file in the repo root (see README)."
    )

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

HOSPITALS_SQL = text("""
    SELECT
        h.facility_id,
        h.name,
        h.address,
        h.city,
        h.state,
        h.zip_code,
        h.county,
        h.phone,
        h.hospital_type,
        h.ownership,
        h.emergency_services,
        h.birthing_friendly,
        h.overall_rating,
        (
            SELECT array_agg(f.description ORDER BY f.code)
            FROM footnotes f
            WHERE f.code = ANY (h.overall_rating_footnotes)
        ) AS rating_notes
    FROM hospitals h
    WHERE (CAST(:state AS TEXT) IS NULL OR h.state = :state)
      AND (CAST(:rating AS SMALLINT) IS NULL OR h.overall_rating = :rating)
    ORDER BY h.overall_rating DESC NULLS LAST, h.name
""")


def get_hospitals(state=None, rating=None):
    with engine.connect() as connection:
        result = connection.execute(HOSPITALS_SQL, {"state": state, "rating": rating})
        return [dict(row) for row in result.mappings()]
