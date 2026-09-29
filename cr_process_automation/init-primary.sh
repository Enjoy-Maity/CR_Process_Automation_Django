#!/usr/bin/env bash
set -e

echo "Configuring PostgreSQL for replication..."

# Append replication settings to pg_hba.conf
echo "" >> "$PGDATA/pg_hba.conf"
echo "# Replication connections" >> "$PGDATA/pg_hba.conf"
echo "host replication replicator 0.0.0.0/0 md5" >> "$PGDATA/pg_hba.conf"
echo "" >> "$PGDATA/pg_hba.conf"
echo "# Application connections" >> "$PGDATA/pg_hba.conf"
echo "host all all 0.0.0.0/0 md5" >> "$PGDATA/pg_hba.conf"

echo "Setup complete - waiting for PostgreSQL to start..."
