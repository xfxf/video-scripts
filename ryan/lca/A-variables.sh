#!/bin/sh

# where videos are stored
export ROOMNAME="TestRoom"
export RECDIR="/home/juser/Videos/"

# IP address of voctocore in relation to this computer
export VOCTOCOREIP="localhost"
export VOCTOOPTIONS="-vv"

# this computers source (running on voctocore PC)
export SCRIPT="3a-hdmi2usb-v4l-alsa.sh"
export PORT="10000"
export DEVICE="/dev/video0"

# used from 0-go.sh - ignored if ran on a remote machine
export REMOTEIP="192.168.1.5"
export REMOTEUSER="juser"
export REMOTESCRIPT="3b-hdmi2usb-v4l-blankaudio.sh"

