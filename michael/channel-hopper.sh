#!/bin/sh
# Channel Hopper
MIXERS="10.20.0.10 10.20.0.20 10.20.0.30 10.20.0.40"

AUDIO_SINK="autoaudiosink"

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
        ! $AUDIO_SINK &

    # Hop channels after a few seconds
    GSTREAMER_PID=$!
    sleep 10s
    kill $GSTREAMER_PID
  done
done
