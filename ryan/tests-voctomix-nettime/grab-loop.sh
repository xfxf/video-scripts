#!/bin/bash -xi

# loops the grabber

cd ~/lca/video-scripts/ryan/tests/

while true; do

    python hu-conf.py /dev/ttyVIZ0 hdmi2usb.cmd

    python3 grabber.py

    sleep 1

done
