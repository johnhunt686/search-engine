#!/bin/bash
sudo apt update
sudo apt install git apt curl cmake build-essential nodejs libpqxx-dev libpq-dev

cmake -S . -B build
cmake --build build