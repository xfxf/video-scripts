#!/bin/bash -xi

# loops the grabber

cd ~/lca/voctomix-outcasts/

while true; do

    # python hu-conf.py /dev/ttyVIZ0 hdmi2usb.cmd

    ./ingest.py --video-source hdmi2usb --video-attribs device=$HDMI2USB --host $VOC_CORE --port 10001 --video-delay 1000

    sleep 1

done
