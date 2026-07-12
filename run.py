"""Command-line entry point for the TTC pipeline.

Usage:
    python run.py --stage ddl   # create schemas + bronze infrastructure
    python run.py --reset       # drop everything and recreate from scratch
"""

import argparse

import config
from pipeline import db

# The DDL files that build the schema structure, in the order they must run.
DDL_FILES = [
    config.SQL_DIR / "ddl" / "00_schemas.sql",
    config.SQL_DIR / "ddl" / "10_bronze.sql",
]


def run_ddl():
    """Create the schemas and bronze infrastructure (idempotent)."""
    print("Stage: ddl")
    for path in DDL_FILES:
        db.run_sql_file(path)


def reset():
    """Drop the medallion schemas (and everything in them), then recreate."""
    print("Reset: dropping schemas bronze/silver/gold")
    conn = db.connect()
    try:
        with conn.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS bronze, silver, gold CASCADE;")
        conn.commit()
    finally:
        conn.close()
    run_ddl()


def main():
    parser = argparse.ArgumentParser(description="TTC data pipeline")
    parser.add_argument(
        "--stage",
        choices=["ddl"],   # later phases add: ingest, bronze, silver, gold
        help="run a single stage",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="drop and recreate all schemas from scratch",
    )
    args = parser.parse_args()

    if args.reset:
        reset()
    elif args.stage == "ddl":
        run_ddl()
    else:
        # No flags: for now just run the DDL. Later this becomes the full pipeline.
        run_ddl()

    print("Done.")


if __name__ == "__main__":
    main()
