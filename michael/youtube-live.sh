#!/bin/sh

YT_SERVER="rtmp://a.rtmp.youtube.com/live2"
# Needs AUTH, which is the "Stream Name" from Ingestion Settings > Main Camera
# Needs MIXER, which is the voctomix mixer IP address

# apt-get install --assume-yes gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly gstreamer1.0-libav gstreamer1.0-tools



# https://bugzilla.gnome.org/show_bug.cgi?id=731352#c6
gst-launch-1.0 \
	tcpclientsrc "host=${MIXER}" port=15000 \
	! matroskademux name=demux \
	! queue \
        ! x264enc bitrate=2000 byte-stream=false key-int-max=60 bframes=0 aud=true tune=zerolatency ! "video/x-h264,profile=main" \
	! flvmux streamable=true name=mux \
	! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/x/${AUTH} app=live2" demux. \
	! queue \
	! audioconvert ! voaacenc bitrate=128000 ! mux.

