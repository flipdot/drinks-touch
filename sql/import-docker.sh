#!/usr/bin/env bash

parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path"

cat 01-schema.sql | docker exec -i dsd_postgres psql -U postgres -d drinks
cat 02-drinks.sql | docker exec -i dsd_postgres psql -U postgres -d drinks
