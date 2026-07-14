-- ============================================================================
-- Sample route-analysis queries (read-only) against the pipeline's output.
-- Answers the three required questions, plus one extra ranking.
--
-- Run after the pipeline has populated the gold tables, e.g.:
--   docker exec -i ttc_db psql -U ttc -d ttc < analysis/sample_queries.sql
-- Each query just SELECTs and prints its result; nothing is written back.
-- ============================================================================


-- Q1: average number of stops per route.
SELECT * FROM gold.avg_stops_per_route;


-- Q2: most frequently scheduled routes (top 10 by trip count).
SELECT route_short_name, route_long_name, trip_count
FROM gold.route_trip_counts
LIMIT 10;


-- Q3: average delay across all routes.
SELECT * FROM gold.avg_delay;


-- Extra: least reliable routes (highest average delay, min 100 delay records).
SELECT route, avg_delay_minutes, delay_records
FROM gold.avg_delay_by_route
WHERE delay_records >= 100
ORDER BY avg_delay_minutes DESC
LIMIT 10;
