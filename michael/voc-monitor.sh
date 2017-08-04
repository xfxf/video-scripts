#!/bin/sh

# Video layout:
#
# +--------------------------------------------+-+
# |                                            | |
# |                                            | |
# |                                            | |
# |                                            | |
# |                      A                     | |
# |                                            |C|
# |                                            | |
# |                                            | |
# |                                            | |
# +--------------------------------------------+ |
# |                      B                     | |
# +--------------------------------------------+-+
#
# A = Main video
# B = O-scope
# C = VU-meter
#
# The video is composited as follows:
#  1. Extra padding is added around A
#  2. Extra padding is added around B, composited onto A
#  3. Extra padding is added around C, composited onto A

SRC_WIDTH="1280"
SRC_HEIGHT="720"

OSCOPE_HEIGHT="48"
VU_WIDTH="20"

TOTAL_WIDTH="$(echo ${SRC_WIDTH}+${VU_WIDTH} | bc)"
TOTAL_HEIGHT="$(echo ${SRC_HEIGHT}+${OSCOPE_HEIGHT} | bc)"

MIXER="10.20.0.10"


#GST_DEBUG="*:4"
gst-launch-1.0 \
	tcpclientsrc "host=${MIXER}" port=15000 \
	! matroskademux name=demux \
	! queue \
	  ! videobox border-alpha=0 bottom=-${OSCOPE_HEIGHT} right=-${VU_WIDTH} \
	  ! videomixer name=mix \
	  ! videoconvert \
	  ! autovideosink \
	demux. ! queue ! audioconvert ! tee name=rawaud \
	  ! wavescope style=lines shader=none \
	  ! alpha \
	  ! video/x-raw, width=${SRC_WIDTH}, height=${OSCOPE_HEIGHT} \
	  ! videobox border-alpha=0 top=-${SRC_HEIGHT} right=-${VU_WIDTH} \
	  ! mix. \
  rawaud. \
    ! spectrascope \
    ! alpha \
    ! video/x-raw, width=${VU_WIDTH}, height=${TOTAL_HEIGHT} \
    ! videobox border-alpha=0 left=-${SRC_WIDTH} \
	  ! mix. \
  rawaud. \
    ! autoaudiosink
