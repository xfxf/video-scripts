#!/bin/bash -eu

set -o pipefail

export DEBIAN_FRONTEND=noninteractive 

apt -y update


apt -y install \
  linux-image-extra-virtual \
  awscli \
  curl \
  jq \
  apt-transport-https

apt-add-repository universe

apt -y update

# We need to remove the aws kernel (grumble grumble) because... I don't know why the generic kernel won't boot
# until we do, but... https://community.jitsi.org/t/cant-specify-a-custom-kernel-for-jibri-grub-crashes/105848/3
# suggested this.

# Unfortunately linux tries to stop you removing the running kernel (which makes sense in most cases).
# To script our way around this, based on https://askubuntu.com/a/1313030, we temporarily swap out 
# /usr/bin/linux-check-removal with something a little bit less safe

mv /usr/bin/linux-check-removal /usr/bin/linux-check-removal.orig
echo -e '#!/bin/sh\necho "Overriding default linux-check-removal script!"\nexit 0' | sudo tee /usr/bin/linux-check-removal
chmod +x /usr/bin/linux-check-removal

apt-get purge -y "linux-image*aws*"

# Restore safety (or something like that anyway)
mv /usr/bin/linux-check-removal.orig /usr/bin/linux-check-removal

update-grub

# reboot now :)