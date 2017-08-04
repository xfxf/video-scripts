#!/bin/sh
# Channel Hopper
MIXERS="10.20.0.10 10.20.0.20 10.20.0.30 10.20.0.40"

# Needs gstreamer1.0-alsa package
AUDIO_SINK="alsasink"
# Reduces crackling audio problem
AUDIO_BUFFER="50000" # microseconds

# Best performance
VIDEO_SINK="autovideosink"

# Needed on virtualbox, comment out on other platforms
#VIDEO_SINK="ximagesink"

while [ true ]
do
  for MIXER in $MIXERS
  do
    # Playback from that mixer.
    gst-launch-1.0 \
      tcpclientsrc "host=${MIXER}" port=15000 \
      ! matroskademux name=demux \
        ! queue \
        ! videoconvert \
        ! textoverlay text="${MIXER}" valignment=top halignment=left font-desc="Sans, 48" \
        ! $VIDEO_SINK \
      demux. \
        ! queue \
        ! audioconvert \
        ! audioresample \
        ! $AUDIO_SINK "buffer-size=${AUDIO_BUFFER}" &

    # Hop channels after a few seconds
    GSTREAMER_PID=$!
    sleep 10s
    kill $GSTREAMER_PID
  done
done
