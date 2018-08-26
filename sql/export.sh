#!/usr/bin/env bash

parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path"

sudo -u postgres pg_dump -U postgres drinks --schema-only > 01-schema.sql
sudo -u postgres pg_dump -U postgres drinks -t drink -t drink_id_seq > 02-drinks.sql
