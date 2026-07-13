-- Q3: average time delay across all routes.
-- Note: the source is historical delay logs, not true real-time updates.
-- Interpretation: the mean Min Delay (minutes) over all logged delay records
-- that have a numeric delay value. Zero-minute records are included (they are
-- logged events with no measured delay); a per-route breakdown is also stored.

DROP TABLE IF EXISTS gold.avg_delay CASCADE;
CREATE TABLE gold.avg_delay AS
SELECT
    round(avg(min_delay), 2) AS avg_delay_minutes,
    count(*)                 AS delay_records
FROM silver.delay
WHERE min_delay IS NOT NULL;

DROP TABLE IF EXISTS gold.avg_delay_by_route CASCADE;
CREATE TABLE gold.avg_delay_by_route AS
SELECT
    route,
    round(avg(min_delay), 2) AS avg_delay_minutes,
    count(*)                 AS delay_records
FROM silver.delay
WHERE min_delay IS NOT NULL AND route IS NOT NULL
GROUP BY route
ORDER BY avg_delay_minutes DESC;
