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
                       
v=v0.0.0-701-gb6007e9 # 

v=v0.0.0-600-gbba0e3e # LCA image on My Atlys #1
v=v0.0.0-639-g956a8b3 # last ver pass    b'HDMI2USB>'

v=v0.0.2-81-gd0d3aea

board=atlys

. ~/.virtualenvs/modeswtich/bin/activate

# git clone https://github.com/timvideos/HDMI2USB-firmware-prebuilt.git
# cd ~/HDMI2USB-firmware-prebuilt/atlys/firmware/unstable
mkdir -p ~/HDMI2USB-firmware-prebuilt/archive/master/$v/$board/hdmi2usb
cd ~/HDMI2USB-firmware-prebuilt/archive/master/$v/$board/hdmi2usb

wget -N https://raw.githubusercontent.com/timvideos/HDMI2USB-firmware-prebuilt/master/archive/master/$v/$board/hdmi2usb/hdmi2usb.hex
wget -N https://raw.githubusercontent.com/timvideos/HDMI2USB-firmware-prebuilt/master/archive/master/$v/$board/hdmi2usb/atlys_hdmi2usb-hdmi2usbsoc-atlys.bit
# cd ~/lca/video-scripts/carl/atlys-firmware

openocd -f board/digilent_atlys.cfg -c "init; pld load 0 atlys_hdmi2usb-hdmi2usbsoc-atlys.bit; exit"

fxload -B libusb -D vid=0x16c0,pid=0x06ad -t fx2lp -I hdmi2usb.hex

# on a flashed Atlys:
sudo fxload -B libusb -D vid=0x1443,pid=0x0007 -t fx2lp -I hdmi2usb.hex

cd /sys/bus/pci/drivers/ehci-pci/
echo 0000:00:1a.0 > unbind
echo 0000:00:1a.0 > bind

flterm --port /dev/ttyVIZ0 --speed 115200 

mplayer tv:// -tv driver=v4l2:device=/dev/video

echo if you see yourself in a web cam, fix this:
grep HDMI2USB ~/.bashrc
echo vim ~/.bashrc
echo


