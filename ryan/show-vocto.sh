#!/bin/sh

gst-launch-1.0 \
	tcpclientsrc "host=192.168.0.10" port=15000 \
	! matroskademux name=demux \
	! autovideosink


