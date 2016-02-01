#!/bin/sh

YT_SERVER="rtmp://a.rtmp.youtube.com/live2"
# Also needs AUTH, which is the "Stream Name" from Ingestion Settings > Main Camera

# apt-get install --assume-yes gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly gstreamer1.0-libav gstreamer1.0-tools


# https://bugzilla.gnome.org/show_bug.cgi?id=731352#c6
gst-launch-1.0 \
    videotestsrc is-live=1 \
        ! "video/x-raw, width=1280, height=720, framerate=25/1" \
        ! timeoverlay \
        ! x264enc bitrate=2000 ! "video/x-h264,profile=main" \
      ! queue ! mux. \
    audiotestsrc is-live=1 wave=12 ! avenc_aac compliance=experimental ! queue ! mux. \
    flvmux streamable=1 name=mux  \
      ! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/x/$AUTH app=live2"

