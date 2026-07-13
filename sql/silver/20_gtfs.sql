-- Silver GTFS: typed, cleaned tables rebuilt deterministically from bronze.
-- Only the columns the analyses need are carried forward.

DROP TABLE IF EXISTS silver.routes CASCADE;
CREATE TABLE silver.routes AS
SELECT
    route_id,
    NULLIF(TRIM(route_short_name), '') AS route_short_name,   -- the cross-dataset join key
    NULLIF(TRIM(route_long_name), '')  AS route_long_name,
    route_type::int                    AS route_type
FROM bronze.routes;

DROP TABLE IF EXISTS silver.trips CASCADE;
CREATE TABLE silver.trips AS
SELECT
    route_id,
    trip_id,
    service_id,
    NULLIF(direction_id, '')::int AS direction_id
FROM bronze.trips;

-- Times (arrival/departure) are intentionally omitted: GTFS allows values like
-- '25:30:00' for after-midnight trips, which are not valid SQL time values.
DROP TABLE IF EXISTS silver.stop_times CASCADE;
CREATE TABLE silver.stop_times AS
SELECT
    trip_id,
    stop_id,
    stop_sequence::int AS stop_sequence
FROM bronze.stop_times;
