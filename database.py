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

EMERGENCY_HOSPITAL_SQL = text("""
        SELECT
            name,
            city,
            state,
            hospital_type,
            emergency_services,
            birthing_friendly,
            overall_rating
        FROM hospitals
        WHERE state = :state
          AND emergency_services = TRUE
        ORDER BY overall_rating DESC NULLS LAST, name
    """)

HOSPITAL_READMISSION_SQL = text("""
        SELECT
            h.name,
            h.city,
            h.state,
            u.measure_name,
            u.score,
            u.compared_to_national,
            u.number_of_patients,
            u.start_date,
            u.end_date
        FROM hospitals h
        JOIN unplanned_visits u
            ON h.facility_id = u.facility_id
        WHERE h.state = :state
          AND u.measure_id LIKE 'READM%'
        ORDER BY h.name, u.measure_name
    """)


def get_hospitals(state=None, rating=None):
    with engine.connect() as connection:
        result = connection.execute(HOSPITALS_SQL, {"state": state, "rating": rating})
        return [dict(row) for row in result.mappings()]


def get_emergency_hospitals(state):
    with engine.connect() as connection:
        result = connection.execute(EMERGENCY_HOSPITAL_SQL, {"state": state})

        return [dict(row) for row in result.mappings()]


def get_hospital_readmissions(state):
    with engine.connect() as connection:
        result = connection.execute(HOSPITAL_READMISSION_SQL, {"state": state})

        return [dict(row) for row in result.mappings()]
