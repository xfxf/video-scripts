#!/bin/bash

    gst-launch-1.0 \
        \
        alsasrc device='hw:1,0' provide-clock=false !\
            audio/x-raw,format=S16LE,channels=2,layout=interleaved,rate=48000 !\
            queue !\
            tee name=t ! \
            queue !\
            mux. \
        \
        t. !\
            queue !\
            audioconvert !\
            monoscope !\
            videoconvert !\
            videoscale method=0 add-borders=1 !\
            video/x-raw,format=I420,width=1280,height=720,framerate=30/1,pixel-aspect-ratio=1/1 !\
            queue !\
            mux. \
        \
        matroskamux name=mux !\
            tcpclientsink port=10000 host=localhost

