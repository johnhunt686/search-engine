# search engine

## the instalation will be consoloidated to scripts to update build and run; however, should it fail verbose instructions are provided [Here](#Build-Instructions)
this project is designed to run on debian or a similar fork, windows will not be supported.
in the root of the project first run instal.sh and then run.sh 

## Using the system
When the service has been started it broadcasts on localhost:8080 with the api avaliable on localhost:3000.
To populate data, the scrapper must be run and will collect site information until the specified limit.


## Build Instructions (manual)
clone the repo
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

within the databse directory there are two scripts, install.sh and install_postgresql.sh
these will setup the database and python environment

## Run Instructions
starting the web-server
the api server is started by executing
'node server.js' in the root folder

the node server for the user interface is located in the website directory annd is started by executing
'node server.js'

with in the 'database' directory there is a run.sh script that initializes the web scrapper with default settings

## Access
This system is designed to use a tunneled web host such as cloudflared.
