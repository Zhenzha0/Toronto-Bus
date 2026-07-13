-- Bronze infrastructure and raw data tables.
-- Data tables mirror the source file headers exactly, ALL COLUMNS TEXT (no
-- casting happens here) plus an _ingested_at lineage timestamp.

-- One row is written every time we consider loading a source resource.
-- It records what we loaded and when, so a re-run can SKIP a download whose
-- source data has not changed since last time. This is the heart of idempotent
-- ingestion.
CREATE TABLE IF NOT EXISTS bronze.ingestion_log (
    id             BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,  -- surrogate key
    dataset        TEXT        NOT NULL,          -- CKAN dataset slug
    resource_id    TEXT        NOT NULL,          -- CKAN resource UUID
    resource_name  TEXT,                          -- human-readable name / filename
    source_url     TEXT,                          -- download URL actually used
    last_modified  TIMESTAMPTZ,                   -- resource's last_modified (the watermark)
    checksum       TEXT,                          -- hash of the downloaded file (secondary guard)
    rows_loaded    BIGINT,                        -- number of rows landed into bronze
    status         TEXT        NOT NULL,          -- 'loaded' or 'skipped'
    loaded_at      TIMESTAMPTZ NOT NULL DEFAULT now()  -- when this run happened
);


-- --- GTFS raw tables (columns mirror the .txt headers exactly) ---

CREATE TABLE IF NOT EXISTS bronze.routes (
    route_id          TEXT,
    agency_id         TEXT,
    route_short_name  TEXT,
    route_long_name   TEXT,
    route_desc        TEXT,
    route_type        TEXT,
    route_url         TEXT,
    route_color       TEXT,
    route_text_color  TEXT,
    _ingested_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS bronze.trips (
    route_id               TEXT,
    service_id             TEXT,
    trip_id                TEXT,
    trip_headsign          TEXT,
    trip_short_name        TEXT,
    direction_id           TEXT,
    block_id               TEXT,
    shape_id               TEXT,
    wheelchair_accessible  TEXT,
    bikes_allowed          TEXT,
    _ingested_at           TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS bronze.stops (
    stop_id              TEXT,
    stop_code            TEXT,
    stop_name            TEXT,
    stop_desc            TEXT,
    stop_lat             TEXT,
    stop_lon             TEXT,
    zone_id              TEXT,
    stop_url             TEXT,
    location_type        TEXT,
    parent_station       TEXT,
    stop_timezone        TEXT,
    wheelchair_boarding  TEXT,
    _ingested_at         TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS bronze.stop_times (
    trip_id              TEXT,
    arrival_time         TEXT,
    departure_time       TEXT,
    stop_id              TEXT,
    stop_sequence        TEXT,
    stop_headsign        TEXT,
    pickup_type          TEXT,
    drop_off_type        TEXT,
    shape_dist_traveled  TEXT,
    _ingested_at         TIMESTAMPTZ NOT NULL DEFAULT now()
);


-- --- Delay raw table (canonical columns; drifting source headers are mapped
-- onto these in the loader). _year is the partition key for reloads. ---

CREATE TABLE IF NOT EXISTS bronze.delay (
    report_date              TEXT,
    route                    TEXT,
    time                     TEXT,
    day                      TEXT,
    location                 TEXT,
    incident                 TEXT,
    min_delay                TEXT,
    min_gap                  TEXT,
    direction                TEXT,
    vehicle                  TEXT,
    _year                    INT,          -- partition key (delete-year-reload)
    _source_file             TEXT,         -- which file this row came from
    _resource_last_modified  TEXT,         -- source last_modified (from manifest)
    _ingested_at             TIMESTAMPTZ NOT NULL DEFAULT now()
);
