"""Central configuration: read .env and expose settings the rest of the code uses."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Absolute path to the folder this file lives in = the project root.
# Using __file__ means paths work no matter what directory you run from.
PROJECT_ROOT = Path(__file__).resolve().parent
SQL_DIR = PROJECT_ROOT / "sql"

# Read key=value lines from .env into the process environment (os.environ).
# If .env is missing (e.g. inside Docker, where Compose injects the vars
# directly), this silently does nothing and we fall back to os.environ.
load_dotenv(PROJECT_ROOT / ".env")

# Required settings: os.environ[...] raises immediately if one is missing,
# so we fail fast with a clear error instead of a confusing one later.
DB_NAME = os.environ["POSTGRES_DB"]
DB_USER = os.environ["POSTGRES_USER"]
DB_PASSWORD = os.environ["POSTGRES_PASSWORD"]

# Optional settings: sensible defaults if not set.
DB_HOST = os.environ.get("POSTGRES_HOST", "localhost")
DB_PORT = os.environ.get("POSTGRES_PORT", "5432")

# Connection string in libpq keyword format, which psycopg2.connect() accepts.
DATABASE_URL = (
    f"host={DB_HOST} port={DB_PORT} dbname={DB_NAME} "
    f"user={DB_USER} password={DB_PASSWORD}"
)
