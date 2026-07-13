-- Q1: average number of stops per route.
-- Interpretation: for each route, count the DISTINCT stops it serves (across all
-- its trips/directions), then average that count across all routes.

DROP TABLE IF EXISTS gold.avg_stops_per_route CASCADE;
CREATE TABLE gold.avg_stops_per_route AS
WITH stops_per_route AS (
    SELECT r.route_id, count(DISTINCT st.stop_id) AS stop_count
    FROM silver.routes r
    JOIN silver.trips t       ON t.route_id = r.route_id
    JOIN silver.stop_times st ON st.trip_id = t.trip_id
    GROUP BY r.route_id
)
SELECT
    round(avg(stop_count), 2) AS avg_stops_per_route,
    count(*)                  AS routes_counted
FROM stops_per_route;
