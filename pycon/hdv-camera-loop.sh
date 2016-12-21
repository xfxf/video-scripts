#!/bin/bash -xi

# loops the grabber

cd ~/lca/voctomix-outcasts/

while true; do

    # python hu-conf.py /dev/ttyVIZ0 hdmi2usb.cmd

    ./ingest.py --video-source hdv --audio-source alsa --audio-attribs device=$DVS_ALSA_DEV --host $VOC_CORE --port 10000 --audio-delay 4600

    sleep 1

done
