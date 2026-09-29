#!/bin/bash
set -e

MASTER_HOST="db-master"
MASTER_PORT="5432"
MASTER_USER="admin"
MASTER_PASS="Django@123#"
MASTER_DB="master_db"
REPL_USER="replicator"
REPL_PASS="Django@123#"

echo "Waiting for master to be ready..."
for i in {1..60}; do
  if pg_isready -h "$MASTER_HOST" -p "$MASTER_PORT" -U "$MASTER_USER" 2>/dev/null; then
    echo "Master is ready!"
    break
  fi
  echo "Attempt $i/60..."
  sleep 2
done

echo "Creating replicator role on master..."
PGPASSWORD="$MASTER_PASS" psql -h "$MASTER_HOST" -p "$MASTER_PORT" -U "$MASTER_USER" -d "$MASTER_DB" <<-EOF
  CREATE ROLE $REPL_USER WITH REPLICATION LOGIN PASSWORD '$REPL_PASS';
EOF

echo "Replicator role created successfully!"

