"""Gold layer: rebuild the analysis result tables from silver by running SQL files."""

import config
from pipeline import db

GOLD_FILES = [
    config.SQL_DIR / "gold" / "30_q1_avg_stops.sql",
    config.SQL_DIR / "gold" / "31_q2_schedule_updates.sql",
    config.SQL_DIR / "gold" / "32_q3_avg_delay.sql",
]


def run():
    for path in GOLD_FILES:
        db.run_sql_file(path)
