#!/bin/bash

#gst-launch-1.0 hdv1394src ! decodebin ! fpsdisplaysink

#gst-launch-1.0 dv1394src ! decodebin ! videoconvert ! videorate ! fpsdisplaysink sync=false

#gst-launch-1.0 dv1394src ! dvdemux name=demux ! queue ! audioconvert ! fakesink demux. ! queue ! dvdec ! deinterlace ! videoconvert ! videorate ! videoscale ! video/x-raw,format=I420,width=1280,height=720,framerate=30/1,pixel-aspect-ratio=1/1 ! fpsdisplaysink sync=false

export GST_DEBUG=*:3
export HOST=192.168.0.15

    gst-launch-1.0 \
        dv1394src !\
            multiqueue !\
	    dvdemux name=demux \
	    demux. !\
            	queue !\
	    	audioconvert !\
	    	audio/x-raw,format=S16LE,channels=2,layout=interleaved,rate=48000 !\
	    	queue !\
		mux. \
	     demux. !\
		dvdec !\
	    	deinterlace !\
		videoconvert !\
	    	videorate !\
 	    	videoscale !\
		video/x-raw,format=I420,width=1280,height=720,framerate=30/1,pixel-aspect-ratio=1/1 !\
		tee name=t !\
		queue !\
		mux. \
	     matroskamux name=mux !\
            	tcpclientsink port=10000 host=$HOST \
             t. !\
                queue !\
                fpsdisplaysink sync=false

