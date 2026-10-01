#!/usr/bin/env bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE ROLE replicator WITH REPLICATION LOGIN PASSWORD 'Django@123#';
EOSQL

# Allow the replica to stream replication
echo "host replication replicator 0.0.0.0/0 md5" >> "$PGDATA/pg_hba.conf"

# Allow application (admin) connections to all databases from any host
echo "host all all 0.0.0.0/0 md5" >> "$PGDATA/pg_hba.conf"



# #!/usr/bin/env bash
# set -e

# echo "Configuring PostgreSQL db-master for replication..."

# # Append replication permissions to pg_hba.conf
# echo "" >> "$PGDATA/pg_hba.conf"
# echo "# Replication connections" >> "$PGDATA/pg_hba.conf"
# echo "host replication replicator 0.0.0.0/0 md5" >> "$PGDATA/pg_hba.conf"

# # Create replication user
# psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
#     CREATE ROLE replicator WITH REPLICATION LOGIN PASSWORD 'Django@123#';
# EOSQL

# echo "Replication setup on db-master complete."