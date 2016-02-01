#!/bin/bash -xi

# loops the grabber

cd ~/lca/video-scripts/carl/

while true; do

    # python hu-conf.py /dev/ttyVIZ0 hdmi2usb.cmd

    # ./grabber.sh 1
    ./lca-voctomix-ingest.py blackmagichdmi 0

    sleep 1

done
