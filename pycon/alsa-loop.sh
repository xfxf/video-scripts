#!/bin/bash -xi

# loops the grabber

cd ~/lca/voctomix-outcasts/

while true; do

    ./ingest.py --video-source test device=$HDMI2USB --audio-source alsa --audio-attribs device=$DVS_ALSA_DEV --host $VOC_CORE --port 10000

    sleep 1

done
