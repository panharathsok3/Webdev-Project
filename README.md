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
