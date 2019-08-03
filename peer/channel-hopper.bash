#!/bin/bash
# Channel Hopper
declare -a      MIXERS=("10.42.0.10" "10.42.0.40" "10.42.0.60" "10.42.0.50")
declare -a MIXER_NAMES=("Cockle_Bay" "c3.3"       "c3.4/5"     "c3.6")

MIXER_COUNT=${#MIXERS[@]}

# Needs gstreamer1.0-alsa package
AUDIO_SINK="alsasink"
# Reduces crackling audio problem
AUDIO_BUFFER="50000" # microseconds

# Best performance
#VIDEO_SINK="autovideosink"

# Needed for the nVidia Jetson
VIDEO_SINK="nveglglessink"

# Needed on virtualbox, comment out on other platforms
#VIDEO_SINK="ximagesink"


while [ true ]
do
  i="0"
  while [ $i -lt $MIXER_COUNT ] 
  do
    # Playback from that mixer.
    echo -e "\e[1;96mPlaying from \e[93m${MIXERS[$i]}\e[94m"
    gst-launch-1.0 \
      tcpclientsrc "host=${MIXERS[$i]}" port=15000 \
      ! matroskademux name=demux \
        ! queue \
        ! videoconvert \
        ! textoverlay text="${MIXER_NAMES[$i]}" valignment=top halignment=right font-desc="Sans, 32" \
        ! $VIDEO_SINK \
      demux. \
        ! queue \
        ! audioconvert \
        ! audioresample \
        ! $AUDIO_SINK "buffer-time=${AUDIO_BUFFER}" &

    # Hop channels after a few seconds
    GSTREAMER_PID=$!
    sleep 10s
    kill $GSTREAMER_PID
    echo -e "\e[1;96mKilled \e[93m${MIXER_NAMES[$i]}\e[94m"
    i=$[$i+1]
  done
done
