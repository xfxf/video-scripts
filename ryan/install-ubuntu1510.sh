#!/bin/sh

# installation on a fresh Ubuntu 15.10 desktop system

# disable apt auto update
sudo echo """APT::Periodic::Update-Package-Lists "0";
APT::Periodic::Download-Upgradeable-Packages "0";
APT::Periodic::AutocleanInterval "0";
""" > /etc/apt/apt.conf.d/10periodic

# disable screensaver / auto blank+lock / etc
gsettings set org.gnome.desktop.screensaver lock-enabled false
gsettings set org.gnome.settings-daemon.plugins.power active false
gsettings set org.gnome.settings-daemon.plugins.power idle-dim false
gsettings set org.gnome.desktop.session idle-delay 0

sudo apt-get update
sudo apt-get -uy dist-upgrade
sudo apt-get install git ffmpeg python-tk gstreamer1.0-alsa gstreamer1.0-plugins-bad gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-ugly gstreamer1.0-tools libgstreamer1.0-0 python3 python3-gi gir1.2-gstreamer-1.0

mkdir ~/lca
cd ~/lca

git clone https://github.com/xfxf/video-scripts.git
git clone https://github.com/voc/voctomix.git
#git clone https://github.com/timvideos/HDMI2USB-firmware-prebuilt.git
 
