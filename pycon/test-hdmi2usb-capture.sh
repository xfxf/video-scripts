#!/bin/sh
gst-launch-1.0]
        v4l2src device=/dev/hdmi2usb/by-num/opsis0/video name=videosrc !\
                queue!\
                image/jpeg,width=1280,height=720 !\
                jpegdec !\
                videoconvert !\
                videoscale !\
                videorate !\
                video/x-raw,format=I420,width=1280,height=720,framerate=25/1,pixel-aspect-ratio=1/1!\
                videoconvert !\
                avenc_mpeg2video bitrate=5000000 max-key-interval=0 !\
mux.\
        alsasrc device=hw:1,0 provide-clock=false slave-method=re-timestamp name=audiosrc !\
                queue!\
		audiorate!\
                audio/x-raw,format=S16LE,channels=2,layout=interleaved,rate=48000!\
                audioconvert !\
                avenc_mp2 bitrate=192000 !\
mux.\
        matroskamux name=mux ! filesink location=hdmi2usb_recording_`date +%s`.mkv

