# search engine

## the instalation will be consoloidated to scripts to update build and run; however, should it fail verbose instructions are provided [Here](#Build-Instructions)
this project is designed to run on debian or a similar fork, windows will not be supported.
install.sh
run.sh

## Using the system
blah blah blah



## Build Instructions
clone the repo
'git clone https://github.com/johnhunt686/search-engine'

required packages before install
git
apt
curl
cmake
build-essential
nodejs
libpqxx-dev
libpq-dev

cmake execution
cmake -C . -B build
cmake --build build

## Run Instructions
starting the web-server
the server is started by executing
'node server.js'

## Access
This system is utilizing a cloudflared tunnel to provide external access, defaulting to a local connection.