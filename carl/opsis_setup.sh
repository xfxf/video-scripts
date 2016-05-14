
v=v0.0.0-654-gbca243b # booted, /dev/video1 exists, but nothing comes out
v=v0.0.0-699-gb505665

# c4646dd6ad5ac3be4edb05f08d5f72aa2fcba8d5

cd /tmp

# ln -s /home/carl/src/tv/HDMI2USB-firmware-prebuilt/archive/master/v0.0.0-654-gbca243b/opsis/hdmi2usb
ln -sf /home/carl/src/tv/HDMI2USB-firmware-prebuilt/archive/master/$v/opsis/hdmi2usb

cd
git clone https://github.com/mithro/HDMI2USB-mode-switch.git
cd HDMI2USB-mode-switch
git checkout opsis-prod

sudo ./hdmi2usb-mode-switch.py --mode=serial --verbose
sudo ./hdmi2usb-mode-switch.py --mode=jtag --verbose
sudo ./hdmi2usb-mode-switch.py --verbose --flash-gateware /tmp/hdmi2usb/opsis_hdmi2usb-hdmi2usbsoc-opsis.bin
