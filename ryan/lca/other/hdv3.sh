#!/bin/bash

#export GST_DEBUG_DUMP_DOT_DIR=/tmp/
export GST_DEBUG=*:3

export HOST=localhost
#export HOST=192.168.0.15

    gst-launch-1.0 \
        hdv1394src blocksize="4136" !\
            multiqueue !\
	    tsdemux name=demux \
	    demux. !\
            	queue !\
		mpegaudioparse !\
		mad !\
           	audioconvert !\
		audio/x-raw,format=S16LE,channels=2,layout=interleaved,rate=48000 !\
		queue !\
		fakesink sync=false \
	     demux. !\
		queue !\
		mpegvideoparse !\
		mpeg2dec !\
	    	deinterlace !\
		videorate !\
		videoscale !\
		videoconvert !\
		video/x-raw,format=I420,width=1280,height=720,framerate=30/1,pixel-aspect-ratio=1/1 !\
		queue !\
		xvimagesink sync=false

