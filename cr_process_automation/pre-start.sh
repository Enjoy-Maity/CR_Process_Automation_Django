#!/bin/bash

# Check and create the volumes directory
if [ ! -d "./volumes" ]; then
  mkdir -p ./volumes
fi

# Create the volumes
if [ ! -d "./volumes/db_master_volume" ]; then
  mkdir -p ./volumes/db_master_volume
fi

if [ ! -d "./volumes/db_replica_volume" ]; then
  mkdir -p ./volumes/db_replica_volume
fi