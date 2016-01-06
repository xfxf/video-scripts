#!/bin/bash
    gst-launch-1.0 \
        multifilesrc location="$1" loop=true !\
            jpegparse !\
            jpegdec !\
            videoconvert !\
            videorate !\
            video/x-raw,format=I420,width=1280,height=720,framerate=25/1,pixel-aspect-ratio=1/1 !\
            queue !\
            mux. \
        \
        alsasrc device='hw:0,0' !\
            audio/x-raw,format=S16LE,channels=2,layout=interleaved,rate=48000 !\
            queue !\
            mux. \
        \
        matroskamux name=mux !\
            tcpclientsink port=10001 host=localhost

