#!/usr/bin/env bash

parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path"

docker exec dsd_postgres pg_dump drinks -U postgres --schema-only > 01-schema.sql
docker exec dsd_postgres pg_dump drinks -U postgres -t drink -t drink_id_seq > 02-drinks.sql
