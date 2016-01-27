#!/bin/bash -xi

# loops the grabber

cd ~/lca/video-scripts/carl/

while true; do

    python hu-conf.py /dev/ttyVIZ0 hdmi2usb.cmd

    ./grabber.sh 2

    sleep 1

done
