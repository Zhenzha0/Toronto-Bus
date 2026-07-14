"""Central configuration: read .env and expose settings the rest of the code uses."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Project root (this file's folder), so paths work no matter where you run from.
PROJECT_ROOT = Path(__file__).resolve().parent
SQL_DIR = PROJECT_ROOT / "sql"

# Load .env into os.environ. In Docker there's no .env file (Compose injects
# the vars instead), so this just no-ops there.
load_dotenv(PROJECT_ROOT / ".env")

# Required - fail loudly if any of these are missing.
DB_NAME = os.environ["POSTGRES_DB"]
DB_USER = os.environ["POSTGRES_USER"]
DB_PASSWORD = os.environ["POSTGRES_PASSWORD"]

# Optional - default to a local Postgres.
DB_HOST = os.environ.get("POSTGRES_HOST", "localhost")
DB_PORT = os.environ.get("POSTGRES_PORT", "5432")

# libpq keyword string; psycopg2.connect() takes it directly.
DATABASE_URL = (
    f"host={DB_HOST} port={DB_PORT} dbname={DB_NAME} "
    f"user={DB_USER} password={DB_PASSWORD}"
)

# --- Data source (CKAN open-data API) ---
CKAN_HOST = "https://ckan0.cf.opendata.inter.prod-toronto.ca"
DATASET_GTFS = "ttc-routes-and-schedules"
DATASET_DELAY = "ttc-bus-delay-data"

# --- Local landing paths ---
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"

# --- Load scope ---
# FULL_LOAD=true -> all years; otherwise just SAMPLE_YEARS (fast to iterate on).
FULL_LOAD = os.environ.get("FULL_LOAD", "false").lower() == "true"
SAMPLE_YEARS = [2024]
DELAY_YEARS_FULL = list(range(2014, 2026))  # 2014..2025 (2025 = rolling file)
