#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Define volume paths relative to the script directory
MASTER_VOL_DIR="$SCRIPT_DIR/volumes/db_master_volume"
REPLICA_VOL_DIR="$SCRIPT_DIR/volumes/db_replica_volume"

echo "Creating volume directories..."
mkdir -p "$MASTER_VOL_DIR"
mkdir -p "$REPLICA_VOL_DIR"

echo "Starting Docker Compose..."
docker-compose up