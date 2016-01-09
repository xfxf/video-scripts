#!/bin/bash -ex

dir=$(date +%Y-%m-%d/atlys)
# mkdir -p $dir

dir=~/Videos

# HDMI2USB=/dev/video0

while [ 1 ]; do

gst-launch-1.0 -v \
    --eos-on-shutdown \
    v4l2src device=$HTMI2USB \
    ! image/jpeg,width=1280,height=720 \
      ! queue max-size-bytes=100000000 max-size-time=0 \
    ! matroskamux name=mux \
    alsasrc device=hw:CARD=CODEC latency-time=100 \
      ! queue max-size-bytes=100000000 max-size-time=0 \
    ! audioconvert \
      ! queue max-size-bytes=100000000 max-size-time=0 \
    ! vorbisenc \
      ! queue max-size-bytes=100000000 max-size-time=0 \
    ! mux. mux. \
      ! queue max-size-bytes=100000000 max-size-time=0 \
    ! filesink location=$dir/$(date +%H_%M_%S).mkv

exit 
sleep 1

done
