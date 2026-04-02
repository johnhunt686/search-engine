#!/bin/bash

set -e

# Install PostgreSQL + ODBC
sudo apt update
sudo apt install -y postgresql postgresql-contrib odbc-postgresql

# Set port to 41204
PG_CONF=$(sudo find /etc/postgresql -name postgresql.conf)
sudo sed -i "s/^#port = 5432/port = 41204/" "$PG_CONF"

# Ensure peer auth for postgres user
PG_HBA=$(sudo find /etc/postgresql -name pg_hba.conf)
sudo sed -i "s/^local\s\+all\s\+postgres\s\+.*/local all postgres peer/" "$PG_HBA"

# Restart PostgreSQL
sudo systemctl restart postgresql

# Set password (run from accessible dir)
sudo -u postgres bash -c "cd /tmp && psql -U postgres -c \"ALTER USER postgres WITH PASSWORD '1234';\""
