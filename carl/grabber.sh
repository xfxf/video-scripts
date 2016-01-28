#!/bin/bash -ex

# hdmi2usb, generated audio, local display (including fps)
# used for screen grabber, loops and sends to core

    gst-launch-1.0 \
        v4l2src device=$HDMI2USB !\
            image/jpeg,width=1280,height=720 !\
            jpegdec !\
            videoconvert !\
            videorate !\
         tee name=t ! queue ! \
            videoconvert ! fpsdisplaysink sync=false t. ! \
            video/x-raw,format=I420,width=1280,height=720,framerate=30/1,pixel-aspect-ratio=1/1 !\
            queue !\
            mux. \
        \
        audiotestsrc !\
            audio/x-raw,format=S16LE,channels=2,layout=interleaved,rate=48000 !\
            queue !\
            mux. \
        \
        matroskamux name=mux !\
            tcpclientsink port=1000$1 host=$VOC_CORE

