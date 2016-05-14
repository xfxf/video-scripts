
v=v0.0.0-699-gb505665

cd /tmp

ln -sf /home/carl/src/tv/HDMI2USB-firmware-prebuilt/archive/master/$v/opsis/hdmi2usb

cd
git clone https://github.com/mithro/HDMI2USB-mode-switch.git
cd HDMI2USB-mode-switch
git checkout opsis-prod

# repeat these 3 lines until it works
sudo ./hdmi2usb-mode-switch.py --mode=serial --verbose
sudo ./hdmi2usb-mode-switch.py --mode=jtag --verbose
sudo ./hdmi2usb-mode-switch.py --verbose --flash-gateware /tmp/hdmi2usb/opsis_hdmi2usb-hdmi2usbsoc-opsis.bin

# power cycle to get it out of jtag mode

