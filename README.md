# Fan-Tas-Tic-machine
Game Rules for the Fan-Tas-Tic pinball machine

# Installing everything on the Raspberry PI from scratch
Objective is to setup a Raspberry Pi 3+ to run MPF version 0.54 with audio and LED panel support.

The MPF team recommends the `KivyPie` distribution, which is based on debian jessie and __hopelessly outdated__.
So I will use an up-to-date raspian image instead (based on debian buster).

Follow these steps to mount and run the .img file locally in a virtual machine on a debian or ubuntu host PC.

```bash
# Download, verify and unzip a raspios_lite image.
# You can use a newer one as long as it is based on debian buster
wget https://downloads.raspberrypi.org/raspios_lite_armhf/images/raspios_lite_armhf-2021-01-12/2021-01-11-raspios-buster-armhf-lite.zip

echo "d49d6fab1b8e533f7efc40416e98ec16019b9c034bc89c59b83d0921c2aefeef  2021-01-11-raspios-buster-armhf-lite.zip" | sha256sum -c
# 2021-01-11-raspios-buster-armhf-lite.zip: OK

unzip 2021-01-11-raspios-buster-armhf-lite.zip

# Make the image file bigger to gain some free space
dd if=/dev/zero bs=1M count=2048 >> 2021-01-11-raspios-buster-armhf-lite.img

# mount image as loopfs, so the virtual machine can see it
sudo losetup -P /dev/loop0 2021-01-11-raspios-buster-armhf-lite.img

# use gparted to resize the /dev/loop0p2 partition to its full size
sudo gparted /dev/loop0

# Mount the partition
mkdir mnt
mkdir mnt/boot
sudo mount -o rw /dev/loop0p2 mnt
sudo mount -o rw /dev/loop0p1 mnt/boot

# Enter it as a virtual machine
sudo apt install systemd-container
sudo systemd-nspawn -b -D mnt/

# raspian should boot ... now carry out the installation steps below.
```

# Actual installation steps in raspian

```bash
# login as pi, raspberry

# change password for user pi
passwd

# Set hostname to fantastic, add wifi credentials
sudo raspi-config

# Enable ssh access, reserve a CPU core for the LED panel
sudo touch /boot/ssh
sudo nano /boot/cmdline.txt
    # append this to the list of space-separated commands
    isolcpus=3

sudo nano /boot/config.txt
    # Can't use on-board audio as hardware timer is needed for LED panel
    # Make sure `dtparam=audio=on` is commented out

#-------------------------
# Libraries
#-------------------------
# Need pulseaudio for mpf mc
# See: https://groups.google.com/g/mpf-users/c/KFKunVnfJE8
sudo apt update
sudo apt upgrade
sudo apt install build-essential git sox python3-pip \
    python3-numpy cython3 libopenjp2-7 libtiff5 \
    libgstreamer1.0-dev gstreamer1.0-plugins-base \
    libgl1-mesa-dev libgles2-mesa-dev libsdl2-ttf-dev \
    libsdl2-dev libsdl2-mixer-dev libsdl2-image-dev \
    libmtdev-dev pulseaudio

#-------------------------
# Mission Pinball
#-------------------------
sudo pip3 install mpf==0.54 mpf-mc==0.54

# Install MPF Fan-Tas-Tic platform driver
sudo pip3 install git+https://github.com/yetifrisstlama/Fan-Tas-Tic-platform.git

#-------------------------
# Machine files
#-------------------------
git clone https://github.com/yetifrisstlama/Fan-Tas-Tic-machine.git

# Set some permissions, stupid but needed
cd ~/Fan-Tas-Tic-machine/
chmod g+s .

# bundle up all machine files.
# This needs to be re-done whenever the machine config was modified
mpf build production_bundle

#-------------------------
# LED panel driver
#-------------------------
cd ~
git clone https://github.com/hzeller/rpi-rgb-led-matrix.git
cd rpi-rgb-led-matrix
git checkout ede58e8d0dfdb9cfff7c3cf6c32733a644b2efd5
make
sudo make install-python PYTHON=$(which python3)

#-------------------------
# Shutdown switch handler
#-------------------------
# bcm2835 library is required
# see also: https://www.airspayce.com/mikem/bcm2835/
cd ~
wget http://www.airspayce.com/mikem/bcm2835/bcm2835-1.68.tar.gz
tar -xvf bcm2835-1.68.tar.gz
cd bcm2835-1.68/
./configure
make
sudo make install
cd ~/Fan-Tas-Tic-machine/shutdown
make

#-------------------------
# systemd units
#-------------------------
cd ~/Fan-Tas-Tic-machine/shutdown
sudo cp *.service /etc/systemd/system
sudo systemctl daemon-reload
sudo systemctl enable shutdown_handler
sudo systemctl enable fantastic
sudo systemctl enable fantastic_mc

#-------------------------
# done
#-------------------------
# To exit the virtual machine and clean up:
sudo halt
# or alternatively, 3 times CTRL+]

# on host: unmount image file
sudo umount -R mnt/
sudo losetup -D

# copy the image to a SD card (make sure /dev/mmcblk0 is correct)
sudo dd bs=1M status=progress if=2021-01-11-raspios-buster-armhf-lite.img of=/dev/mmcblk0
sync

# See here on how to configure to wifi credentials before boot:
# https://raspberrytips.com/raspberry-pi-wifi-setup/
```

We plug the SD card into the raspberry PI 3 and boot it.
Then SSH into it.

The pinball machine should initialize on boot. If not, check the systemd logs (see below).

```bash
# remote login over ssh
ssh pi@fantastic

# expand filesystem, set timezone, add wifi credentials (optional)
sudo raspi-config
sudo shutdown now
```

# Managing the pinball services
there's 3 services running:
  * `shutdown_handler`: checks if the power switch was toggled and shuts down the raspberry pi
  * `fantastic`: Mission Pinball. Handles game rules, coils, switches, lights
  * `fantastic_mc`: Mission Pinball Media Controller. Handles sounds and the graphics on the LED panel.

use these commands to interact with the services

```bash
# see log output in real-time
journalctl -u <service_name> -ef

# see service status
systemctl status <service_name>

# start / stop a service
sudo systemctl start <service_name>
sudo systemctl stop <service_name>

# register / de-register start on boot
sudo systemctl enable <service_name>
sudo systemctl disable <service_name>
```

# SD card images
How to take and restore a backup image of the SD card. Done from a debian / Ubuntu host PC.

Make sure to replace `/dev/mmcblk0` with the right device name of the SD card.

## Verify backup

```bash
echo "118c98b50cb85ea80b86e64bf514cb31d35d781c62c47d2e0ccaad224fed4372  fantastic_2021_02_17.img.gz" | sha256sum -c
fantastic_2021_02_17.img.gz: OK
```

## Create Backup

```bash
$ sudo dd bs=1M status=progress if=/dev/mmcblk0 | gzip --best > sd_backup.img.gz
```

## Restore Backup

Warning `/dev/mmcblk0` will be overwritten. Make sure it's the SD card.

```bash
$ gzip -dc fantastic_2021_02_17.img.gz | sudo dd bs=1M status=progress of=/dev/mmcblk0
```

# Playfield simulation (`mpf monitor`)
This allows you to run mpf on a host PC and interact with the virtual playfield with the mpf monitor command. This is ideal for developing and testing new game rules.

I had to build and install python 3.7 manually on my debian-testing machine. You can also use [`pyenv`](https://github.com/pyenv/pyenv).

```bash
wget https://www.python.org/ftp/python/3.7.9/Python-3.7.9.tgz
tar -xvf Python-3.7.9.tgz
cd Python-3.7.9/
./configure --prefix=/usr/local
make -j4
sudo make install
```

Then create the virtual python environment and install mpf 0.54

```bash
mkvirtualenv --python python3.7 mpf
python --version
# Python 3.7.9
pip install mpf==0.54 mpf-mc==0.54 mpf-monitor==0.54
pip install numpy pyqt5
```

You can always go back to this environment later with `workon mpf`.

Now let's get the machine directory ready ...

```bash
cd Fan-Tas-Tic-machine
nano config/config.yaml
# comment out the `fantastic:` block
# we don't need this hardware configuration for simulation
```

Start the mpf-monitor and make it display the playing field, then start mpf and everything should come to life.

```bash
mpf monitor &
# Enable `Show playfield window` under Monitor tab

mpf mc &
# the simulated DMD window should pop up labeled `Fan-Tas-Tic Pinball`

mpf -Xt
# the machine should come to life
```

In the playfield window, squares represent switches, which you can left-click to activate them and right-click to latch them. Circles represent LEDs.
