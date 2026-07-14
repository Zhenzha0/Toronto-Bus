-- ============================================================================
-- Sample route-analysis queries (read-only) against the pipeline's output.
--
-- Run after the pipeline has populated the gold/silver tables, e.g.:
--   docker exec -i ttc_db psql -U ttc -d ttc < analysis/sample_queries.sql
-- Each query just SELECTs and prints its result; nothing is written back.
-- ============================================================================


-- Q1 -- Average number of stops per route ---------------------------------
SELECT * FROM gold.avg_stops_per_route;


-- Q2 -- Most frequently scheduled routes (top 10 by trip count) -----------
SELECT route_short_name, route_long_name, trip_count
FROM gold.route_trip_counts
LIMIT 10;


-- Q3 -- Average delay across all routes (minutes) -------------------------
SELECT * FROM gold.avg_delay;


-- Least reliable routes: highest average delay (min 100 records) ----------
SELECT route, avg_delay_minutes, delay_records
FROM gold.avg_delay_by_route
WHERE delay_records >= 100
ORDER BY avg_delay_minutes DESC
LIMIT 10;


-- Cross-dataset analysis: total delay minutes per SCHEDULED trip -----------
-- Normalises each route's delay burden by how much it is actually scheduled,
-- combining the delay data (delay minutes) with the GTFS schedule (trip count).
-- Only routes that reconcile across both datasets appear (INNER JOIN on the
-- route number = GTFS route_short_name).
WITH route_delays AS (
    SELECT route, sum(min_delay) AS total_delay_min, count(*) AS delay_events
    FROM silver.delay
    WHERE min_delay IS NOT NULL AND route IS NOT NULL
    GROUP BY route
),
route_trips AS (
    SELECT r.route_short_name, count(*) AS trip_count
    FROM silver.routes r
    JOIN silver.trips t ON t.route_id = r.route_id
    GROUP BY r.route_short_name
)
SELECT
    d.route,
    t.trip_count,
    d.total_delay_min,
    round(d.total_delay_min::numeric / t.trip_count, 2) AS delay_min_per_trip
FROM route_delays d
JOIN route_trips t ON t.route_short_name = d.route
ORDER BY delay_min_per_trip DESC
LIMIT 10;


-- Data-quality: how well do delay route numbers reconcile to GTFS? ---------
SELECT
    count(*)                              AS distinct_delay_routes,
    count(*) FILTER (WHERE matched)       AS matched,
    round(100.0 * count(*) FILTER (WHERE matched) / count(*), 1) AS match_pct
FROM silver.route_xref;
