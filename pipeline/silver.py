"""Silver layer: rebuild typed/cleaned tables from bronze by running SQL files."""

import config
from pipeline import db

SILVER_FILES = [
    config.SQL_DIR / "silver" / "20_gtfs.sql",
    config.SQL_DIR / "silver" / "21_delay.sql",
    config.SQL_DIR / "silver" / "22_route_xref.sql",
]


def run():
    for path in SILVER_FILES:
        db.run_sql_file(path)
