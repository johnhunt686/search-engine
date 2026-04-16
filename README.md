# search engine

## The installation will be consolidated to scripts to update, build, and run; however, should it fail, verbose instructions are provided [Here](#Build-Instructions)

This project is designed to run on Debian or a similar fork; Windows will not be supported.

In the root of the project, first run install.sh and then run.sh. 

## Using the system

When the service has been started, it broadcasts on localhost:8080 with the API available on localhost:3000.

To populate data, the scrapper must be run and will collect site information until the specified limit.

## Build Instructions (manual)

Clone the repo.

'git clone https://github.com/johnhunt686/search-engine'

sudo apt update

npm install cors

required packages before install

git

apt

curl

cmake

build-essential

nodejs

libpqxx-dev

libpq-dev

libstemmer-dev

cmake execution

cmake -C . -B build

cmake --build build

Within the database directory there are two scripts, install.sh and install_postgresql.sh

These will setup the database and python environment.

## Run Instructions

starting the web-server

The API server is started by executing

'node server.js' in the root folder

The node server for the user interface is located in the website directory and is started by executing

'node server.js'

Within the 'database' directory there is a run.sh script that initializes the web scraper with default settings.

## Access

This system is designed to use a tunneled web host such as cloudflared.

