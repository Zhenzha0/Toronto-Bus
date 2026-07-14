-- Silver delay: typed + cleaned, rebuilt deterministically from bronze.delay.
-- Bronze already stored blanks as NULL; here we cast to real dates/integers.

DROP TABLE IF EXISTS silver.delay CASCADE;
CREATE TABLE silver.delay AS
SELECT
    report_date::date            AS report_date,
    -- Leading route number only: the 2025 feed stores "102 MARKHAM ROAD", older
    -- years store "89". Extracting the number lets all years join to GTFS.
    NULLIF(substring(TRIM(route) from '^[0-9]+'), '') AS route,
    time,
    day,
    NULLIF(TRIM(location), '')   AS location,
    NULLIF(TRIM(incident), '')   AS incident,
    min_delay::int               AS min_delay,
    min_gap::int                 AS min_gap,
    NULLIF(TRIM(direction), '')  AS direction,
    vehicle::int                 AS vehicle,
    _year                        AS year
FROM bronze.delay;
