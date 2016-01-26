#!/bin/bash

#export GST_DEBUG_DUMP_DOT_DIR=/tmp/
export GST_DEBUG=*:3

    gst-launch-1.0 \
        hdv1394src blocksize="4136" !\
	    tsdemux name=demux \
	    demux. !\
		queue !\
	    	mpegaudioparse !\
		mad !\
		queue !\
	 	autoaudiosink sync=false \
	    demux. !\
		queue !\
		mpegvideoparse !\
		mpeg2dec !\
	    	fpsdisplaysink sync=false

