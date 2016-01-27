#!/bin/bash -ex

# VOC_ALSA_DEV='hw:1,0'

    gst-launch-1.0 -v \
        videotestsrc pattern=ball !\
            video/x-raw,format=I420,width=1280,height=720,framerate=30/1,pixel-aspect-ratio=1/1 !\
            queue !\
            mux. \
        \
        alsasrc device=$VOC_ALSA_DEV !\
            audio/x-raw,format=S16LE,channels=2,layout=interleaved,rate=48000 !\
            queue !\
            mux. \
        \
        matroskamux name=mux !\
            tcpclientsink port=1000$1 host=$VOC_CORE

