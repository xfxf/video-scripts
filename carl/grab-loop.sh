#!/bin/bash -ei

# loops the grabber

cd ~/lca/video-scripts/carl/

while true; do

    ./grabber.sh 1

    sleep 1

done
