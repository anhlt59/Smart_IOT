#!/bin/sh
# Read-only role for the Grafana datasource — dashboards must never be able
# to mutate app data. Runs once on first cluster init; GRAFANA_RO_PASSWORD
# comes from the container environment (.env).
set -eu

psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" <<SQL
CREATE ROLE grafana_ro WITH LOGIN PASSWORD '${GRAFANA_RO_PASSWORD}';
GRANT CONNECT ON DATABASE ${POSTGRES_DB} TO grafana_ro;
GRANT USAGE ON SCHEMA public TO grafana_ro;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO grafana_ro;
-- future tables created by migrations (run as ${POSTGRES_USER}) stay readable
ALTER DEFAULT PRIVILEGES FOR ROLE ${POSTGRES_USER} IN SCHEMA public GRANT SELECT ON TABLES TO grafana_ro;
SQL
