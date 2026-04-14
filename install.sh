#!/bin/bash
sudo apt update
sudo apt install git apt curl cmake build-essential nodejs libpqxx-dev libpq-dev

npm install cors

cmake -S . -B build
cmake --build build

cd database
echo installing python dependencies
./install.sh

echo installing postgresql
./install_postgresql.sh

echo "installation complete"
