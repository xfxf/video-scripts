#!/bin/bash -xi

# loops the dv-firewire cam + alsa

cd ~/lca/video-scripts/carl/

while true; do

    #./dv-camera-alsa.sh 0
    # ./3c-dv-camera-audio.sh 0
    #./lca-voctomix-ingest.py dvpulse 0
    ./lca-voctomix-ingest.py hdvpulse 0

    sleep 1

done
