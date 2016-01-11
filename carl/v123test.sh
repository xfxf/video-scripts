#!/bin/bash -ex

cd ~/lca/video-scripts/carl

wget -Nc http://c3voc.mazdermind.de/testfiles/avsync.ts

numbers="$1"
for (( i=0; i<${#numbers}; i++ )); do
        ./source-avsync-test-clip-looped-as-cam-x.sh ${numbers:$i:1} &
        sleep .3
done
 
exit
./source-avsync-test-clip-looped-as-cam-x.sh 0 & 
sleep .3

./source-avsync-test-clip-looped-as-cam-x.sh 1 & 
sleep .3

./source-avsync-test-clip-looped-as-cam-x.sh 2 


