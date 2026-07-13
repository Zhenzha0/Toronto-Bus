"""Command-line entry point for the TTC pipeline.

Usage:
    python run.py --stage ddl   # create schemas + bronze infrastructure
    python run.py --reset       # drop everything and recreate from scratch
"""

import argparse

import config
from pipeline import bronze, db, ingest

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


def run_ingest(local=False):
    """Download source files into data/raw (or reuse existing ones with --local)."""
    if local:
        print("Stage: ingest (local mode - reusing files already in data/raw)")
        return
    print("Stage: ingest")
    ingest.run()


def run_bronze():
    """Load the landed raw files into the all-TEXT bronze tables."""
    print("Stage: bronze")
    bronze.load_gtfs()
    bronze.load_delay()


def main():
    parser = argparse.ArgumentParser(description="TTC data pipeline")
    parser.add_argument(
        "--stage",
        choices=["ddl", "ingest", "bronze"],   # later phases add: silver, gold
        help="run a single stage",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="drop and recreate all schemas from scratch",
    )
    parser.add_argument(
        "--local",
        action="store_true",
        help="skip network; reuse files already in data/raw",
    )
    args = parser.parse_args()

    if args.reset:
        reset()

    if args.stage == "ddl":
        run_ddl()
    elif args.stage == "ingest":
        run_ddl()                       # ensure schemas/ingestion_log exist first
        run_ingest(local=args.local)
    elif args.stage == "bronze":
        run_ddl()                       # ensure bronze tables exist first
        run_bronze()
    elif args.stage is None and not args.reset:
        # No stage given: run the full pipeline (so far: ddl + ingest + bronze).
        run_ddl()
        run_ingest(local=args.local)
        run_bronze()

    print("Done.")


if __name__ == "__main__":
    main()
