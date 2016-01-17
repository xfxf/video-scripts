#!/bin/bash

    gst-launch-1.0 \
        dv1394src \
            decodebin !\
            deinterlace !\
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

