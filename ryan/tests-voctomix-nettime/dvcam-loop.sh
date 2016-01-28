#!/bin/bash -xi

# loops the dv-firewire cam + alsa

cd ~/lca/video-scripts/ryan/tests-voctomix-nettime/

while true; do

    ./dv-camera-alsa.py 0
    # ./3c-dv-camera-audio.sh 0

    sleep 1

done
