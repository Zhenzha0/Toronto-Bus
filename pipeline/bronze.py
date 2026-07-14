"""Bronze layer: COPY the landed raw files into all-TEXT Postgres tables."""

import csv
import io
import json

import openpyxl

import config
from pipeline import db

# Each GTFS file -> (bronze table, the columns in the file's header order).
GTFS_TABLES = {
    "routes.txt": (
        "bronze.routes",
        ["route_id", "agency_id", "route_short_name", "route_long_name",
         "route_desc", "route_type", "route_url", "route_color", "route_text_color"],
    ),
    "trips.txt": (
        "bronze.trips",
        ["route_id", "service_id", "trip_id", "trip_headsign", "trip_short_name",
         "direction_id", "block_id", "shape_id", "wheelchair_accessible", "bikes_allowed"],
    ),
    "stops.txt": (
        "bronze.stops",
        ["stop_id", "stop_code", "stop_name", "stop_desc", "stop_lat", "stop_lon",
         "zone_id", "stop_url", "location_type", "parent_station", "stop_timezone",
         "wheelchair_boarding"],
    ),
    "stop_times.txt": (
        "bronze.stop_times",
        ["trip_id", "arrival_time", "departure_time", "stop_id", "stop_sequence",
         "stop_headsign", "pickup_type", "drop_off_type", "shape_dist_traveled"],
    ),
}


def _copy_file(cur, table, columns, file_path):
    """Stream one CSV file into a table using COPY (skipping its header row)."""
    col_list = ", ".join(columns)
    sql = f"COPY {table} ({col_list}) FROM STDIN WITH (FORMAT csv, HEADER true)"
    with open(file_path, "rb") as f:      # binary = faster, skips decoding
        cur.copy_expert(sql, f)


def load_gtfs():
    """Truncate + reload the GTFS bronze tables from data/raw/gtfs (idempotent)."""
    conn = db.connect()
    try:
        with conn.cursor() as cur:
            for filename, (table, columns) in GTFS_TABLES.items():
                path = config.RAW_DIR / "gtfs" / filename
                cur.execute(f"TRUNCATE {table};")
                _copy_file(cur, table, columns, path)
                cur.execute(f"SELECT count(*) FROM {table};")
                print(f"  loaded {table}: {cur.fetchone()[0]} rows")
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# --- Delay files (XLSX/CSV with drifting headers) ---

# The canonical column order for bronze.delay.
DELAY_COLUMNS = [
    "report_date", "route", "time", "day", "location",
    "incident", "min_delay", "min_gap", "direction", "vehicle",
]

# Maps a normalized header (stripped + lowercased) to our canonical column,
# handling the drift across years: "Delay"/"Min Delay", "Date"/"Report Date".
HEADER_MAP = {
    "date": "report_date", "report date": "report_date",
    "route": "route", "line": "route",              # 2025 feed renamed Route -> Line
    "time": "time",
    "day": "day",
    "location": "location", "station": "location",  # 2025: Location -> Station
    "incident": "incident", "code": "incident",      # 2025: Incident -> Code (a code, not text)
    "delay": "min_delay", "min delay": "min_delay",
    "gap": "min_gap", "min gap": "min_gap",
    "direction": "direction", "bound": "direction",
    "vehicle": "vehicle",
}


def _normalize(name):
    """Lowercase + strip a header cell so drifting variants line up."""
    return str(name).strip().lower() if name is not None else ""


def _column_order(header):
    """For each canonical column, find its position in this file's header."""
    found = {}
    for index, name in enumerate(header):
        canonical = HEADER_MAP.get(_normalize(name))
        if canonical:
            found[canonical] = index
    return [found.get(col) for col in DELAY_COLUMNS]


def _to_text(value):
    """Everything becomes raw text; missing stays None (loaded as NULL)."""
    return None if value is None else str(value)


def _delay_rows(path, fmt):
    """Yield each data row as canonical-ordered text values (XLSX or CSV)."""
    if fmt == "XLSX":
        workbook = openpyxl.load_workbook(path, read_only=True)
        try:
            rows = workbook.active.iter_rows(values_only=True)
            order = _column_order(list(next(rows)))          # first row = header
            for row in rows:
                yield [_to_text(row[i]) if i is not None and i < len(row) else None
                       for i in order]
        finally:
            workbook.close()
    else:  # CSV
        with open(path, newline="", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            order = _column_order(next(reader))              # first row = header
            for row in reader:
                yield [_to_text(row[i]) if i is not None and i < len(row) else None
                       for i in order]


def _read_manifest():
    path = config.RAW_DIR / "manifest.json"
    if not path.exists():
        raise RuntimeError("No manifest.json - run the ingest stage first")
    return json.loads(path.read_text(encoding="utf-8"))


def _copy_delay(cur, entry):
    """Build an in-memory CSV of one delay file (+ lineage) and COPY it in."""
    year, source_file = entry["year"], entry["name"]
    last_modified = entry.get("last_modified")
    path = config.PROJECT_ROOT / entry["path"]

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    count = 0
    for values in _delay_rows(path, entry["format"]):
        writer.writerow(values + [year, source_file, last_modified])
        count += 1
    buffer.seek(0)

    cols = DELAY_COLUMNS + ["_year", "_source_file", "_resource_last_modified"]
    sql = f"COPY bronze.delay ({', '.join(cols)}) FROM STDIN WITH (FORMAT csv, NULL '')"
    cur.copy_expert(sql, buffer)
    return count


def load_delay():
    """Delete-then-reload each delay year listed in the manifest (idempotent)."""
    entries = [e for e in _read_manifest() if e["dataset"] == "delay"]
    conn = db.connect()
    try:
        with conn.cursor() as cur:
            for entry in entries:
                cur.execute("DELETE FROM bronze.delay WHERE _year = %s;", (entry["year"],))
                count = _copy_delay(cur, entry)
                print(f"  loaded bronze.delay year={entry['year']}: {count} rows")
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
