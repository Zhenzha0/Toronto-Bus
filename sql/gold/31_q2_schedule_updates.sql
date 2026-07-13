-- Q2: route with the most frequent schedule updates.
-- Interpretation: a single GTFS snapshot has no update history, so we read this
-- as the most actively scheduled route = the route with the most trips.
-- The full ranking is stored; the top row is the answer.

DROP TABLE IF EXISTS gold.route_trip_counts CASCADE;
CREATE TABLE gold.route_trip_counts AS
SELECT
    r.route_id,
    r.route_short_name,
    r.route_long_name,
    count(*) AS trip_count
FROM silver.routes r
JOIN silver.trips t ON t.route_id = r.route_id
GROUP BY r.route_id, r.route_short_name, r.route_long_name
ORDER BY trip_count DESC;
