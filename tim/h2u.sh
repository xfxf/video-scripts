#!/bin/bash

function find_hdmi2usb() {
    for V in /dev/video*; do
	if v4l-info $V | grep 'HDMI2USB' > /dev/null 2>&1; then
		echo $V
		break
	fi
    done
}

    echo "HDMI2USB is $(find_hdmi2usb)"

    gst-launch-1.0 \
        v4l2src device=$(find_hdmi2usb) !\
            image/jpeg,width=1280,height=720 !\
            jpegdec !\
            videoconvert !\
            videorate !\
            video/x-raw,format=I420,width=1280,height=720,framerate=30/1,pixel-aspect-ratio=1/1 !\
            queue !\
            mux. \
        \
        audiotestsrc  wave=silence !\
            queue !\
            mux. \
        \
        matroskamux name=mux !\
            tcpclientsink port=10001 host=192.168.227.136

