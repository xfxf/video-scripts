#!/bin/bash -ex

gst-launch-1.0 \
    v4l2src device=$HDMI2USB !\
        image/jpeg,width=1280,height=720 !\
        jpegdec !\
        fpsdisplaysink 

