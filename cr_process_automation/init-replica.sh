#!/usr/bin/env bash
set -e

if [ -z "$(ls -A "$PGDATA" 2>/dev/null)" ]; then
    echo "Replica data dir empty — cloning from db-master..."
    until pg_isready -h db-master -p 5432 -U replicator; do
        echo "Waiting for db-master..."
        sleep 2
    done

    gosu postgres pg_basebackup \
        -h db-master -p 5432 \
        -U replicator \
        -D "$PGDATA" \
        -Fp -Xs -P -R

    chmod 0700 "$PGDATA"
    echo "Clone complete."
else
    echo "Replica data dir not empty — starting existing standby."
fi

exec gosu postgres postgres
