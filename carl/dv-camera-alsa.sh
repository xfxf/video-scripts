#!/bin/bash

    gst-launch-1.0 \
        dv1394src !\
            multiqueue !\
	    dvdemux name=demux \
	    alsasrc device=$VOC_ALSA_DEV  provide-clock=false !\
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
          	tcpclientsink port=1000$1 host=$VOC_CORE \
        t. !\
            queue !\
            fpsdisplaysink sync=false

