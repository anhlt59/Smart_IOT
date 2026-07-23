-- Runs once on first cluster init (docker-entrypoint-initdb.d).
-- The timescale/timescaledb image preloads the library and runs
-- timescaledb-tune; this makes the extension explicit for the app DB.
CREATE EXTENSION IF NOT EXISTS timescaledb;
