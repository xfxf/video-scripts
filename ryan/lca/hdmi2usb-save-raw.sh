#!/bin/bash

mkdir raw

gst-launch-1.0 v4l2src device=/dev/video0 ! jpegparse ! avimux ! filesink location=raw/hdmi2usb-test-`date --iso-8601=seconds`.avi



