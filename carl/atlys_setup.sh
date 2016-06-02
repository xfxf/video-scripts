#!/bin/bash -x

v=v0.0.0-606-g3a5f323 # doesn't boot - nothing when usb plugged in or lsusb
v=v0.0.0-623-g5ac1879 # no boot
v=v0.0.0-632-g342039c # uvc color bars, no ttyACM0, 16c0:06ad Van Ooijen
v=v0.0.0-635-g7fe1321 # no boot
v=v0.0.0-639-g956a8b3 # noise
v=v0.0.0-639-g956a8b3 # uvc bars, no ttyACM0, 16c0:06ad Van Ooijen
v=v0.0.0-650-g5721f74 # ditto (can't seem to get it out of jtag mode)
v=v0.0.0-654-gbca243b # ditto
v=v0.0.0-658-g0d326d4 # ditto
v=v0.0.0-663-g54d888a # ditto 

v=v0.0.0-699-gb505665  # noise on hdmi out and encoder stream
                       # atlys - dirty bars on romboot 
                       

board=atlys

# git clone https://github.com/timvideos/HDMI2USB-firmware-prebuilt.git
# cd ~/HDMI2USB-firmware-prebuilt/atlys/firmware/unstable
cd ~/HDMI2USB-firmware-prebuilt/archive/master/$v/$board/hdmi2usb

# cd ~/lca/video-scripts/carl/atlys-firmware

openocd -f board/digilent_atlys.cfg -c "init; pld load 0 atlys_hdmi2usb-hdmi2usbsoc-atlys.bit; exit"

fxload -B libusb -D vid=0x16c0,pid=0x06ad -t fx2lp -I hdmi2usb.hex
flterm --port /dev/ttyVIZ0 --speed 115200 
flterm --port /dev/ttyACM0 --speed 115200

mplayer tv:// -tv driver=v4l2:device=/dev/video1

echo if you see yourself in a web cam, fix this:
grep HDMI2USB ~/.bashrc
echo vim ~/.bashrc
echo


