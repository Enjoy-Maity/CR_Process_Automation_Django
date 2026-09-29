#!/usr/bin/env bash
set -e

PGDATA="${PGDATA:-/var/lib/postgresql/data}"

if [ -z "$(ls -A "$PGDATA" 2>/dev/null)" ]; then
    echo "Replica data dir empty — cloning from db-master..."
    until pg_isready -h db-master -p 5432 -U replicator; do
        echo "Waiting for db-master to be ready..."
        sleep 2
    done

    PGPASSWORD="Django@123#" gosu postgres pg_basebackup \
        -h db-master -p 5432 \
        -U replicator \
        -D "$PGDATA" \
        -Fp -Xs -P -R

    echo "primary_conninfo = 'host=db-master port=5432 user=replicator password=Django@123# application_name=db-replica'" >> "$PGDATA/postgresql.auto.conf"
    chown -R postgres:postgres "$PGDATA"
    chmod 0700 "$PGDATA"
    echo "Clone complete and standby configured."
else
    echo "Replica data dir not empty — starting existing standby."
fi

exec gosu postgres postgres
