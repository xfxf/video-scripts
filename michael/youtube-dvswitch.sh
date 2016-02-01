#!/bin/sh

YT_SERVER="rtmp://a.rtmp.youtube.com/live2"
# Needs AUTH, which is the "Stream Name" from Ingestion Settings > Main Camera
# Needs MIXER, which is the dvswitch mixer IP address
PORT=2000

# apt-get install --assume-yes gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly gstreamer1.0-libav gstreamer1.0-tools gstreamer1.0-dvswitch



# https://bugzilla.gnome.org/show_bug.cgi?id=731352#c6
gst-launch-1.0 \
	dvswitchsrc host=$MIXER port=$PORT \
	! dvdemux name=demux \
	! queue \
	! dvdec \
	! videoconvert \
	! videoscale ! video/x-raw,width=1280,height=720,pixel-aspect-ratio=\(fraction\)1/1 \
	! x264enc bitrate=2000 byte-stream=false key-int-max=60 bframes=0 aud=true tune=zerolatency ! "video/x-h264,profile=main" \
	! flvmux streamable=true name=mux \
	! rtmpsink location="${YT_SERVER}/x/${AUTH} app=live2" demux. \
	! queue \
	! audioconvert ! voaacenc bitrate=128000 ! mux.

