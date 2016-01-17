#!/bin/bash -ex

 gst-launch-1.0 \
     tcpserversrc port=10000 ! queue ! decodebin ! fpsdisplaysink
