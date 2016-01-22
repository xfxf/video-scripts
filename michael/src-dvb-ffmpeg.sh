#!/bin/sh
ffmpeg -y \
        -f mpegts \
	-i /dev/dvb/adapter0/dvr0 \
	-vf scale=1280x720 \
	-c:v rawvideo \
	-c:a pcm_s16le \
	-pix_fmt yuv420p \
	-f matroska \
	-r 30 \
	tcp://localhost:10000
