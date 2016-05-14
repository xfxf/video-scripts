#!/bin/bash -x

# sudo apt-add-repository --yes ppa:timvideos/fpga-support
# sudo apt-add-repository --yes ppa:timvideos/dvswitch
# sudo apt-add-repository --yes ppa:carlfk/ppa
# sudo apt-get update && sudo apt-get --assume-yes upgrade
# sudo apt-get --assume-yes install vizzini-dkms
# sudo apt-get --assume-yes install openocd fxload flterm
# sudo apt-get --assume-yes install libftdi1 libusb-dev libftdi-dev ixo-usb-jtag
# sudo apt-get --assume-yes install dvsource-v4l2-other gstreamer1.0-libav

# git clone https://github.com/timvideos/HDMI2USB-firmware-prebuilt.git
# cd ~/HDMI2USB-firmware-prebuilt/atlys/firmware/unstable
cd ~/HDMI2USB-firmware-prebuilt/archive/master/v0.0.0-639-g956a8b3/atlys/hdmi2usb

# cd ~/lca/video-scripts/carl/atlys-firmware

openocd -f board/digilent_atlys.cfg -c "init; pld load 0 atlys_hdmi2usb-hdmi2usbsoc-atlys.bit; exit"

fxload -B libusb -D vid=0x16c0,pid=0x06ad -t fx2lp -I hdmi2usb.hex
flterm --port /dev/ttyVIZ0 --speed 115200 
flterm --port /dev/ttyACM0 --speed 115200

mplayer tv:// -tv driver=v4l2:device=$HDMI2USB

echo if you see yourself in a web cam, fix this:
grep HDMI2USB ~/.bashrc
echo vim ~/.bashrc
echo


