
sudo -u postgres pg_dump -U postgres drinks --schema-only > sql/01-schema.sql
sudo -u postgres pg_dump -U postgres drinks -t drink -t drink_id_seq > sql/02-drinks.sql

