#!/bin/bash -xi

# loops the grabber

cd ~/lca/video-scripts/carl/

while true; do

    python hu-conf.py /dev/ttyVIZ0 hdmi2usb.cmd
    # flterm --port /dev/ttyVIZ0 --speed 115200 < hdmi2usb.cmd
    # flterm --port /dev/ttyACM0 --speed 115200 < hdmi2usb.cmd

    ./grabber.sh 1

    sleep 1

done
