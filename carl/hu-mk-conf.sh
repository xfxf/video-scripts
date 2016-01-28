#!/bin/bash -ex

tee hdmi2usb.cmd <<EOT
video_mode 9
video_matrix connect input1 output0
video_matrix connect input1 output1
video_matrix connect input1 encoder
encoder on
encoder quality 75
EOT

