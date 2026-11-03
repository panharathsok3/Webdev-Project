
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(
  DATABASE_URL,
  pool_pre_ping=True
)

def get_hospitals():
  with engine.connect() as connection:
    result = connection.execute(
      text("SELECT * FROM hospitals")
    )

    return [
      dict(row)
      for row in result.mappings()
    ]
