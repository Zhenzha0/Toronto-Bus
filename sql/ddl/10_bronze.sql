-- Bronze infrastructure. For now just the ingestion watermark table;
-- the bronze DATA tables are added in Phase 3, once we know the file columns.

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
