-- Cross-dataset route reconciliation.
-- The delay data identifies a route by a number (e.g. '89'); GTFS identifies it
-- by route_short_name. This maps each distinct delay route to its GTFS route_id
-- (NULL where no match), which lets us join delays to schedule data and report a
-- match rate as a data-quality signal.

DROP TABLE IF EXISTS silver.route_xref CASCADE;
CREATE TABLE silver.route_xref AS
SELECT
    d.route            AS delay_route,
    r.route_id         AS gtfs_route_id,
    r.route_long_name  AS gtfs_route_name,
    (r.route_id IS NOT NULL) AS matched
FROM (SELECT DISTINCT route FROM silver.delay WHERE route IS NOT NULL) d
LEFT JOIN silver.routes r
    ON r.route_short_name = d.route;
