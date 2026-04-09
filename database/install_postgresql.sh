#!/bin/bash

set -e  # stop on error

echo "=== System update ==="
sudo apt update && sudo apt upgrade -y

echo "=== Install PostgreSQL ==="
sudo apt install -y postgresql postgresql-contrib

echo "=== Start PostgreSQL ==="
sudo systemctl enable postgresql
sudo systemctl start postgresql

echo "=== Configure PostgreSQL ==="

sudo -u postgres psql <<EOF
ALTER USER postgres WITH PASSWORD '1234';
CREATE DATABASE "SearchEngine";
EOF

echo "=== PostgreSQL ready (default port 5432) ==="

echo "=== Create Python virtual environment (if needed) ==="
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

echo "=== Activate venv ==="
source venv/bin/activate

echo "=== Install dependencies ==="
pip install --upgrade pip
pip install -r requirements.txt

echo "=== Download NLTK data ==="
python3 -m nltk.downloader popular
