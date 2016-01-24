#!/bin/bash

# edit A-variables.sh for each computer

SRC="$(dirname $(realpath ${BASH_SOURCE[@]}))"
source $SRC/A-variables.sh
echo "Running from $SRC..."

killall -9 voctocore.py
killall -9 ssh
killall -9 ffmpeg
killall -9 gst-launch-1.0
sleep 2

$SRC/1-vcore.sh &
sleep 5
$SRC/2-vgui.sh &
$SRC/$SCRIPT &
$SRC/4-remote.sh &

while [ -x /dev ];
 do $SRC/5-record-timestamp.sh
 echo "ERROR: Recording stopped!  Attempting to restart..."
 echo -en "\007"
 sleep 1
 echo -en "\007"
 sleep 3
done
 

