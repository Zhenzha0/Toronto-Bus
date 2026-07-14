-- ============================================================================
-- Sample route-analysis queries (read-only) against the pipeline's output.
--
-- Run after the pipeline has populated the gold tables, e.g.:
--   docker exec -i ttc_db psql -U ttc -d ttc < analysis/sample_queries.sql
-- Each query just SELECTs and prints its result; nothing is written back.
-- ============================================================================


-- Average number of stops per route.
SELECT * FROM gold.avg_stops_per_route;


-- Most frequently scheduled routes (top 10 by trip count).
SELECT route_short_name, route_long_name, trip_count
FROM gold.route_trip_counts
LIMIT 10;


-- Least reliable routes: highest average delay, minimum 100 delay records.
SELECT route, avg_delay_minutes, delay_records
FROM gold.avg_delay_by_route
WHERE delay_records >= 100
ORDER BY avg_delay_minutes DESC
LIMIT 10;
