# Webdev-Project

HQE, the Hospital Quality Explorer. This is the backend. It serves CMS hospital quality data through a FastAPI app backed by Postgres.

## Setup

1. Install PostgreSQL and create a database called `hqe`.
2. Activate the conda env: `conda activate fastapi-server`
3. Install the packages: `pip install -r requirements.txt`
4. Create a `.env` file in the repo root with your own database password. Do not commit `.env`.
   ```
   DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/hqe
   ```
5. Load the env vars into the shell: `set -a; source .env; set +a`

## Load the data

```bash
python load_data.py
```

This downloads the CMS hospital files into `data/`, cleans them, and loads them into Postgres. It drops and recreates the tables in `schema.sql` each time, all in one transaction, so a failed run keeps the old data. It takes about a minute.

The CSVs are only downloaded once. To get a newer CMS release, delete the `data/` folder and run it again.

The tables:

- `hospitals`: one row per hospital, with the overall star rating
- `infections`: infection measures per hospital
- `unplanned_visits`: readmissions and return visits per hospital
- `patient_survey`: patient experience survey results per hospital
- `footnotes`: what each CMS footnote code means

"Not Available" and "Not Applicable" are stored as NULL. When a value is missing, the footnote columns say why.

## Run

Start the API from the repo root:

```bash
uvicorn main:app --reload
```

It runs at http://127.0.0.1:8000. The docs are at http://127.0.0.1:8000/docs.

## Tests

```bash
pytest
```
