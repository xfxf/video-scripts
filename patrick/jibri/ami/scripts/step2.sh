#!/bin/bash -eu

set -o pipefail
export DEBIAN_FRONTEND=noninteractive 

echo "Step 2! 🍻"

echo "Java..."

apt -y install openjdk-8-jre-headless

export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64/jre/bin/java

# echo "export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64/jre/bin/java" >> ~/.bashrc

echo "More things..."

apt -y install \
  unzip \
  ffmpeg \
  alsa-utils \
  icewm \
  xdotool \
  xserver-xorg-input-void \
  xserver-xorg-video-dummy

echo "snd-aloop" | tee -a /etc/modules

echo "Load snd-aloop..."

modprobe snd-aloop

echo "Install Chrome..."

curl -sS -o - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | tee -a /etc/apt/sources.list.d/google-chrome.list
apt update
apt -y install google-chrome-stable

mkdir -p /etc/opt/chrome/policies/managed
echo '{ "CommandLineFlagSecurityWarningsEnabled": false }' | tee -a /etc/opt/chrome/policies/managed/managed_policies.json

echo "Installing chromedriver..."

CHROME_DRIVER_VERSION=`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`
wget -N http://chromedriver.storage.googleapis.com/$CHROME_DRIVER_VERSION/chromedriver_linux64.zip -P ~/

unzip ~/chromedriver_linux64.zip -d ~/
rm ~/chromedriver_linux64.zip

sudo mv -f ~/chromedriver /usr/local/bin/chromedriver
sudo chown root:root /usr/local/bin/chromedriver
sudo chmod 0755 /usr/local/bin/chromedriver

##

wget -qO - https://download.jitsi.org/jitsi-key.gpg.key | apt-key add -
echo 'deb https://download.jitsi.org stable/' | tee -a /etc/apt/sources.list.d/jitsi-stable.list
apt update

apt -y install jibri

usermod -aG adm,audio,video,plugdev jibri