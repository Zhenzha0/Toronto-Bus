-- Create the three medallion-architecture layers as schemas.
-- IF NOT EXISTS makes this safe to run on every pipeline run (idempotent):
-- the first run creates them, later runs do nothing instead of erroring.

CREATE SCHEMA IF NOT EXISTS bronze;   -- raw landed data (all TEXT)
CREATE SCHEMA IF NOT EXISTS silver;   -- cleaned, typed, conformed data
CREATE SCHEMA IF NOT EXISTS gold;     -- final analysis results
