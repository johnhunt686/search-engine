#!/bin/bash
echo "starting api..."
node server.js&
echo "done!"

cd website

echo "starting webserver"
node server.js&
echo "done!"

read -p "Would you like to begin scrapping? This will remove existing data. (y/n): " answer
if[["$answer" == [Yy]]]; then
    echo "starting scrapper"
    cd database
    ./run.sh
else
    echo "starting with existing data..."
fi

echo "startup complete!"