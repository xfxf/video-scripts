#!/bin/bash -xi

# loops the grabber

cd ~/lca/voctomix-outcasts/

while true; do

    # python hu-conf.py /dev/ttyVIZ0 hdmi2usb.cmd

    ./ingest.py --video-source hdmi2usb --video-attribs device=$HDMI2USB --audio-source pulse --audio-dev $VOC_PULSE_DEV --host $VOC_CORE --port 10000

    sleep 1

done
