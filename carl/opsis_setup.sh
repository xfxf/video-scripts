
v=v0.0.0-431-g717dfa8 # opsis_hdmi2usb-hdmi2usbsoc-opsis.bin does not exist
v=v0.0.0-639-g956a8b3 # noise
v=v0.0.0-606-g3a5f323 # doesn't boot - nothing when usb plugged in or lsusb
v=v0.0.0-632-g342039c # uvc color bars, no ttyACM0, 16c0:06ad Van Ooijen
v=v0.0.0-635-g7fe1321 # no boot
v=v0.0.0-639-g956a8b3 # uvc bars, no ttyACM0, 16c0:06ad Van Ooijen
v=v0.0.0-650-g5721f74 # ditto (can't seem to get it out of jtag mode)
v=v0.0.0-654-gbca243b # ditto
v=v0.0.0-658-g0d326d4 # ditto
v=v0.0.0-663-g54d888a # ditto 

v=v0.0.0-699-gb505665 # noise on hdmi out and encoder stream
                      # uvc broken stream
v=v0.0.0-623-g5ac1879 # 

ln -sf ~/src/tv/HDMI2USB-firmware-prebuilt/archive/master/$v/opsis/hdmi2usb

cd /tmp
ln -sf ~/HDMI2USB-firmware-prebuilt/archive/master/$v/opsis/hdmi2usb

cd
git clone https://github.com/timvideos/HDMI2USB-firmware-prebuilt.git

git clone https://github.com/mithro/HDMI2USB-mode-switch.git
cd HDMI2USB-mode-switch
git checkout opsis-prod

# repeat these 3 lines until it works
sudo ./hdmi2usb-mode-switch.py --mode=serial --verbose
sudo ./hdmi2usb-mode-switch.py --mode=jtag --verbose
sudo ./hdmi2usb-mode-switch.py --verbose --flash-gateware /tmp/hdmi2usb/opsis_hdmi2usb-hdmi2usbsoc-opsis.bin

# power cycle to get it out of jtag mode

openocd -f board/numato_opsis.cfg -c 'init; xc6s_print_dna xc6s.tap; jtagspi_init 0 ~/HDMI2USB-mode-switch/flash_proxy/opsis/bscan_spi_xc6slx45t.bit; jtagspi_program /tmp/hdmi2usb/opsis_hdmi2usb-hdmi2usbsoc-opsis.bin 0x0; exit'

mplayer tv:// -tv driver=v4l2:device=/dev/video1

