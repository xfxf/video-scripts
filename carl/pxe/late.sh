# late_command.sh

# called from the Ubuntu installer, from this line in the preseed file:
# d-i preseed/late_command string cd /target/tmp && wget http://$url/lc/late.sh && chmod u+x late.sh && chroot /target /tmp/late.sh $(debconf-get mirror/suite) $(debconf-get passwd/username)

set -x

suite=$1 # oneiric, saucy, trusty, utopic, vivid, wily
nuser=$2 # juser

# url=(hostname) of pxe server
# passed from append= in /var/lib/tftpboot/pxelinux.cfg/default 
SHAZ=$url

hostname=$(hostname)
ip=$(getent hosts $hostname | cut -d' ' -f 1)

type="${hostname#r?}"
if [ "$type" != "$hostname" ]; then
  room="${hostname%$type}"
  room="${room#r}"
  mix="r${room}mix"
else
  room=0
  type=standalone
  mix=localhost
fi


## ssh greating: cpu, ubuntu ver, firewire guids
# add the cpu name/speed and ubuntu flavor to login greeting
PROFDIR=/etc/profile.d
if [ -d $PROFDIR ]; then
  echo grep -E \"\(name\|MHz\)\" /proc/cpuinfo > $PROFDIR/showcpu.sh 
  echo lsb_release -d -c > $PROFDIR/showrelease.sh 
  echo uname -a > $PROFDIR/showkernel.sh 

  # echo "cd /sys/devices/virtual/dmi/id" > $PROFDIR/showproduct_name.sh 
  # echo "echo \$(cat sys_vendor) \$(cat product_version) \$(cat product_name)" >> $PROFDIR/showproduct_name.sh 
  # echo cd >> $PROFDIR/showproduct_name.sh 

  cat <<EOT > $PROFDIR/showproduct_name.sh 
cd /sys/devices/virtual/dmi/id
echo \$(cat sys_vendor) \$(cat product_version) \$(cat product_name)
cd
EOT

  cat <<EOT > $PROFDIR/show_fwguid.sh
if [ -d /sys/bus/firewire/devices/ ]; then
  echo
  find /sys/bus/firewire/devices/ -name "fw?" -exec printf "{} " \; -exec cat {}/guid \;
  echo
fi
EOT

fi

# # beep on firewire card add/remove
cd /etc/udev/rules.d
# this breaks things all to hell
# wget http://$SHAZ/lc/fw-beep.rules
cd

# disable ixo-usb-jtag for Opsis boards

CONF=/lib/udev/rules.d/85-ixo-usb-jtag.rules
if [ -f $CONF ]; then
  sed -e '/5440/ s/^#*/# /' -i $CONF
fi



## disable screensaver, blank screen on idle, blank screen on lid close
# https://wiki.gnome.org/action/show/Projects/dconf/SystemAdministrators
# gconftool-2 --direct --config-source=xml:readwrite:/etc/gconf/gconf.xml.defaults --type bool --set /apps/gnome-screensaver/idle_activation_enabled false

mkdir -p /etc/dconf/db/site.d/locks
mkdir -p /etc/dconf/profile
cd /etc/dconf/profile
cat <<EOT >user
user-db:user
system-db:site
EOT

mkdir -p /etc/dconf/db/site.d/
cd /etc/dconf/db/site.d/

cat <<EOT >20-recording-mixer
[org/gnome/desktop/screensaver]
idle-activation-enabled=false
lock-enabled=false

[org/gnome/desktop/session]
idle-delay=uint32 0

[org/gnome/settings-daemon/plugins/power]
lid-close-ac-action='nothing'
lid-close-battery-action='nothing'
idle-dim-ac=false
idle-dim=false
sleep-display-ac=uint32 0
sleep-display-battery=uint32 0

[com/ubuntu/update-manager]
check-dist-upgrades=false

[com/canonical/indicator/power]
show-time=true

[com/canonical/indicator/datetime]
show-date=true
show-day=true
time-format='24-hour'
show-locations=true
show-seconds=true

[org/gnome/desktop/interface]
clock-show-seconds=true

EOT
dconf update


## don't check for updates (so no 'UPDATE ME!' dialog.)
CONF=/etc/update-manager/release-upgrades
if [ -f $CONF ]; then
  sed -i "/^Prompt=normal/s/^.*$/Prompt=never/" $CONF
fi

# use local time server
CONF=/etc/openntpd/ntpd.conf
if [ -f $CONF ]; then
  echo "server $SHAZ" >$CONF
  if [ "$type" = "mix" ]; then
    echo "listen on *" >>$CONF
  elif [ "$type" != "standalone" ]; then
    echo "server $mix" >>$CONF
  fi
fi
echo 'DAEMON_OPTS="-f /etc/openntpd/ntpd.conf -s"' >/etc/default/openntpd


# disable "incomplete language support" dialog
case $suite in
  percise)
  rm -f /var/lib/update-notifier/user.d/incomplete*
  ;;
esac


CONF=/usr/share/gnome/autostart/libcanberra-login-sound.desktop 
if [ -f $CONF ]; then
  echo X-GNOME-Autostart-enabled=false >> $CONF
fi


# work around bug:
# https://bugs.launchpad.net/ubuntu/+source/gnome-control-center/+bug/792636
# if [ -f /etc/UPower/UPower.conf ]; then
#   sed -i "/^IgnoreLid=false/s/^.*$/IgnoreLid=true/" \
#     /etc/UPower/UPower.conf 
# fi

# wget http://mirrors.us.kernel.org/ubuntu//pool/universe/i/ipxe/grub-ipxe_1.0.0+git-4.d6b0b76-0ubuntu2_all.deb
# there is some problem with this right now, so pfft.
# something to do with needing pxe.  I bed I need to use gdebi?
# dpkg -i grub-ipxe_1.0.0+git-4.d6b0b76-0ubuntu2_all.deb

## enable autologin of $nuser
# sed docs http://www.opengroup.org/onlinepubs/009695399/utilities/sed.html

case $suite in
  trusty|utopic|vivid|wily)
  CONF=/etc/lightdm
  if [ -d $CONF ]; then
    cd $CONF
    mkdir lightdm.conf.d
    cd lightdm.conf.d
    cat <<EOT > 12-autologin.conf
[SeatDefaults]
autologin-user=$nuser
EOT
  fi ;;
  oneiric | precise)
  CONF=/etc/lightdm/lightdm.conf
  if [ -f $CONF ]; then
    printf "autologin-user=%s\n" $nuser >> $CONF
  fi ;;
  natty)
  sed -i \
	 -e '/^\[daemon\]$/aAutomaticLoginEnable=true' \
         -e "/^\[daemon\]$/aAutomaticLogin=$nuser" \
       /etc/gdm/gdm.conf-custom
  ;; 
  maveric)
  cat <<EOT >/etc/gdm/custom.conf
[daemon]
AutomaticLoginEnable=true
AutomaticLogin=$nuser
EOT
;;
esac

# install here and not 
# d-i pkgsel/include string squid-deb-proxy-client
# https://launchpad.net/bugs/889656
# debian-installer "installer stops using proxy"

# apt-get install --force-yes --assume-yes \
# 	squid-deb-proxy-client

## remove apt proxy used for install 
# squid-deb-proxy-client has been installed for production 
# Acquire::http::Proxy "http://cp333:8000/";
CONF=/etc/apt/apt.conf
if [ -f $CONF ]; then
  sed -i "/^Acquire::http::Proxy/s/^.*$//" $CONF 
fi

## turn off tracker indexing (slows down the box)
CONF=/home/$nuser/.config/tracker/tracker.cfg
if [ -f $CONF ]; then
  sed -i "/^EnableIndexing=true/s/^.*$/EnableIndexing=false/" $CONF
fi

cd /etc
rm hosts
wget http://$SHAZ/lc/hosts

## create network manager configs: static ip, dhcp, whacky make up 169 IP
# http://trac.linexa.de/wiki/development/BootCD-booting
# ...Createastaticnetworkmanagerfileforeth0
CONF=/etc/NetworkManager/system-connections
if [ -d $CONF ]; then
  get_nm_conf() {
  INI=$1.conf
  wget http://$SHAZ/lc/nm/$INI
  _uuid="$(uuidgen)"
  sed -i "s|@UUID@|${_uuid}|" $INI
  chmod 600 $INI
  }

  cd $CONF
  get_nm_conf 10.0.0.1
  get_nm_conf 10.0.0.2
  get_nm_conf 192.168.0.1
  get_nm_conf dhcpipv4
  get_nm_conf auto-magic
  get_nm_conf $(hostname)
 
  # Try to deal with Network Manager's desire to create this file 
  get_nm_conf "Wired connection 1"
  mv "Wired connection 1.conf" "Wired connection 1"

fi

cat <<EOT >> /etc/exports
# /home/$nuser/Videos  192.168.1.0/16(rw,async,no_subtree_check)
# /home/$nuser/Videos  10.0.0.1/32(rw,async,no_subtree_check)
# /home/$nuser/Videos  room100.local(rw,async,no_subtree_check)
EOT

## add modules that needs to be added:
cat <<EOT >> /etc/modules
## snd-hda-intel sound for HP laptops Intel 82801I (ICH9 Family) HD Audio
# snd-hda-intel
# hotplug ec card slot - like firewire cards
# acpiphp
# pciehp
# yenta_socket
EOT

# dvswitch schroot
cd /var/lib/schroot
mkdir -p tarballs chroots/dvswitch
cd tarballs
wget http://$SHAZ/lc/dvswitch.tar.xz
cd ../chroots/dvswitch
tar -xf /var/lib/schroot/tarballs/dvswitch.tar.xz

cat > /etc/schroot/chroot.d/dvswitch <<EOF
[dvswitch]
description=oneiric-amd64 chroot for running dvswitch
groups=videoteam,root
root-groups=sbuild,root
type=directory
directory=/var/lib/schroot/chroots/dvswitch
EOF

## grab some home made utilities 
# cd /sbin
# APP=async-test
# wget http://$SHAZ/lc/$APP
# chmod 777 $APP 
# chown $nuser:$nuser $APP 

# rest of script does things in defaunt users home dir (~)
cd /home/$nuser

# create ~/.ssh, gen private key
# ssh-keygen -f ~/.ssh/id_rsa -N ""

mkdir .ssh
cd .ssh
wget http://$SHAZ/lc/ssh/id_rsa
wget http://$SHAZ/lc/ssh/id_rsa.pub
wget http://$SHAZ/lc/ssh/authorized_keys
wget http://$SHAZ/lc/ssh/config
# wget http://$SHAZ/lc/ssh/known_hosts
chmod 600 config authorized_keys id_rsa
chmod 644 id_rsa.pub 
cd ..
chmod 700 .ssh
chown -R $nuser:$nuser .ssh

# add 'private' keys - inscure, they are publicly avalibe on this box.
# wget --overwrite http://$SHAZ/lc/sshkeys.tar
# tar xf sshkeys.tar

# cd sshkeys
# wget -N http://$SHAZ/lc/sshd_config
# cd ..
# cp -f sshkeys/* /etc/ssh
# rm -rf sshkeys sshkeys.tar

## add public keys of people who can log in as $USER
# mkdir .ssh
# chmod -R 700 .ssh
# chown $nuser:$nuser .ssh
# cd .ssh
# wget http://$SHAZ/lc/authorized_keys
# chmod -R 600 authorized_keys
# chown $nuser:$nuser authorized_keys
# cd ..

# make time command report just total seconds.
printf "\nTIMEFORMAT=%%E\n" >> .bashrc
# printf "\nexport DISPLAY=:0.0\n" >> .bashrc

# so that bits of this script work on a live box later for testing
printf "\nexport nuser=$nuser\n" >> .bashrc
printf "export SHAZ=$SHAZ\n" >> .bashrc

printf "\n# Vocto settings:\n" >> .bashrc
printf "export HDMI2USB=/dev/video0\n" >> .bashrc
printf "export VOC_PULSE_DEV=''\n" >> .bashrc
printf "# For slave, replace this with hostname of box running vocto core\n" >> .bashrc
printf "export VOC_CORE=$mix\n" >> .bashrc
# printf "\n# for core, hostname of box running grabber\n" >> .bashrc
# printf "export VOC_SLAVE=\n" >> .bashrc

printf "\n# DVswitch settings:\n" >> .bashrc
printf "export DVS_CAM=r${room}cam\n" >> .bashrc
printf "export DVS_GRAB=r${room}grab\n" >> .bashrc
printf "export DVS_ALSA_DEV='hw:1,0' # or maybe 'hw:CARD=CODEC'\n" >> .bashrc

## create ~/bin
# ~/bin gets added to PATH if it exists when the shell is started.
# so make it now so that it is in PATH when it is needed later. 
mkdir -p bin temp .mplayer .config/autostart .config/conky
chown -R $nuser:$nuser bin temp .mplayer .config 

## generic .dvswitchrc, good for testing and production master, slave needs to be tweaked.
cat <<EOT > .dvswitchrc
MIXER_HOST=$mix
MIXER_PORT=2000
# MIXER_HOST=10.0.0.1
# MIXER_HOST=192.168.0.1
# MIXER_HOST=0.0.0.0
EOT
chown -R $nuser:$nuser .dvswitchrc

cat <<EOT > veyepar.cfg
[global]
client=lca 
show=lca2016 
EOT
chown -R $nuser:$nuser .dvswitchrc


cd .config/autostart
wget http://$SHAZ/lc/conky/conky.desktop
chown $nuser:$nuser conky.desktop
cd ../conky
wget http://$SHAZ/lc/conky/conkyrc
chown $nuser:$nuser conkyrc

cd /home/$nuser

APP=x.sh
cat <<EOT > $APP
#!/bin/bash -x
wget -N http://$SHAZ/lc/hook.sh
chmod u+x hook.sh
./hook.sh \$*
EOT
chmod 744 $APP
chown $nuser:$nuser $APP

APP=upbox.py
wget -N http://$SHAZ/lc/$APP
chmod 744 $APP
chown $nuser:$nuser $APP

## script to install analog clock
APP=inst_clocky.sh
cat <<EOT >> $APP
#!/bin/bash -x
# sudo apt-get install python-wxgtk2.8
git clone git://github.com/CarlFK/clocky.git
EOT
chmod 744 $APP
chown $nuser:$nuser $APP

## script to install vocto and lca scripts
APP=inst_voc.sh
cat <<EOT >> $APP
#!/bin/bash -x

mkdir ~/lca
cd ~/lca

git clone http://avserver/git/video-scripts.git
git clone http://avserver/git/voctomix.git
EOT
chmod 744 $APP
chown $nuser:$nuser $APP

set -ex

mkdir lca
cd lca

git clone http://$SHAZ/git/video-scripts.git
git clone http://$SHAZ/git/voctomix.git
git clone http://$SHAZ/git/clocky.git
git clone http://$SHAZ/git/dvsmon.git
git clone http://$SHAZ/git/HDMI2USB-firmware-prebuilt.git

wget http://$SHAZ/lc/Desktop/dsotm.png 
wget http://$SHAZ/lc/Desktop/GRABBER.GIF 
wget http://$SHAZ/lc/Desktop/dvcam.png 
wget http://$SHAZ/lc/Desktop/clock.jpg
wget http://$SHAZ/lc/Desktop/high-voltage-sign-russian.png
wget http://$SHAZ/avsync.ts

# make a default settings file
cd video-scripts/carl
./hu-mk-conf.sh
cd ../..

# install melt encoder
wget http://$SHAZ/lc/shotcut-debian7-x86_64-160102.tar.bz2
tar xvjf shotcut-debian7-x86_64-160102.tar.bz2
cd ../bin
ln -s /home/$nuser/lca/Shotcut/Shotcut.app/melt
cd ..

mkdir Desktop
cd Desktop

APP=1-voc.desktop
cat <<EOT > $APP
[Desktop Entry]
Version=1.0
Name=1 Vocto Recording System
GenericName=Wooo Go!
Comment=No Comment
Type=Application
Icon=/home/$nuser/lca/dsotm.png
Vendor=TimVideos
Exec=/usr/bin/gnome-terminal --command /home/$nuser/lca/video-scripts/carl/ra.sh
EOT
chmod 744 $APP
chown $nuser:$nuser $APP

APP=2-dvcam.desktop
cat <<EOT > $APP
[Desktop Entry]
Version=1.0
Name=2 DV Cam
Type=Application
Icon=/home/$nuser/lca/dvcam.png
Vendor=TimVideos
Exec=/usr/bin/xterm /home/$nuser/lca/video-scripts/carl/dvcam-loop.sh
EOT
chmod 744 $APP
chown $nuser:$nuser $APP

APP=3-grabber.desktop
cat <<EOT > $APP
[Desktop Entry]
Version=1.0
Name=3 Screen Grabber
Type=Application
Icon=/home/$nuser/lca/GRABBER.GIF
Vendor=TimVideos
Exec=/usr/bin/xterm /home/$nuser/lca/video-scripts/carl/grab-loop.sh
EOT
chmod 744 $APP
chown $nuser:$nuser $APP


APP=4-kill_vocto.desktop
cat <<EOT > $APP
[Desktop Entry]
Version=1.0
Name=4 Kill Vocto
Type=Application
Icon=/home/$nuser/lca/high-voltage-sign-russian.png
Vendor=TimVideos
Exec=/usr/bin/pkill screen
EOT
chmod 744 $APP
chown $nuser:$nuser $APP

APP=9-dvsmon.desktop
cat <<EOT > $APP
[Desktop Entry]
Name=9 DVswitch Launcher
Comment=Manages DVswitch components
Exec=/home/$nuser/lca/dvsmon/prod.sh
Terminal=true
Type=Application
Icon=/home/$nuser/lca/dvsmon/dvswitch-logo.svg
Categories=AudioVideo;
EOT
chmod 744 $APP
chown $nuser:$nuser $APP

APP=20-clocky.desktop
cat <<EOT > $APP
[Desktop Entry]
Name=20 Clocky
Comment=Thankyou David Goodger
Exec=/home/$nuser/lca/clocky/wxclock.py
Type=Application
Icon=/home/$nuser/lca/clock.jpg
Categories=AudioVideo;
EOT
chmod 744 $APP
chown $nuser:$nuser $APP


cd ..

chown $nuser:$nuser -R Desktop lca


