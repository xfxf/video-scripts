#!/bin/bash

gst-launch-1.0 v4l2src device=/dev/video1 !\
            image/jpeg,width=1280,height=720 !\
            fdsink |\
            pv >/dev/null

