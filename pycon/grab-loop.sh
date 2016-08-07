#!/bin/bash -xi

# loops the grabber

cd ~/lca/voctomix-outcasts/

while true; do

    # python hu-conf.py /dev/ttyVIZ0 hdmi2usb.cmd

    ./ingest.py --video-source hdmi2usb --video-dev $HDMI2USB --host $VOC_CORE --port 10001

    sleep 1

done
