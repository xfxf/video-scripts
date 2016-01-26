#!/bin/bash -xi

# loops the grabber

cd ~/lca/video-scripts/carl/

while true; do

    ./hu-conf.sh
    ./grabber.sh 1

    sleep 1

done
