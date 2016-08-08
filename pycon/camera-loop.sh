#!/bin/bash -xi

# loops the grabber

cd ~/lca/voctomix-outcasts/

while true; do

    # python hu-conf.py /dev/ttyVIZ0 hdmi2usb.cmd

    ./ingest.py --video-source hdmi2usb --video-attribs device=$HDMI2USB --audio-source alsa --audio-attribs device=$DVS_ALSA_DEV --host $VOC_CORE --port 10000 --video-delay 200

    sleep 1

done
