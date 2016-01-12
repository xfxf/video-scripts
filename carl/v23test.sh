#!/bin/bash -ex

cd ~/lca/video-scripts/carl

wget -Nc http://c3voc.mazdermind.de/testfiles/avsync.ts

./source-avsync-test-clip-looped-as-cam-x.sh 1 & 
sleep .3

./source-avsync-test-clip-looped-as-cam-x.sh 2 


