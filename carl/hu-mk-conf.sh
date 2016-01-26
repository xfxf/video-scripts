#!/bin/bash -ex

tee hdmi2usb.cmd <<EOT
video_mode 9
video_matrix connect input0 output0
video_matrix connect input0 output1
video_matrix connect input0 encoder
encoder on
encoder quality 85
EOT

