# Fan-Tas-Tic-machine
Game Rules for the Fan-Tas-Tic pinball machine

# Installing everything from scratch
Objective is to setup a Raspberry Pi 3+ to run MPF version 0.54 with audio and LED panel support. Sounds easy, should be easy, is easy ;). Just stick to the recipe.

You'll need a Debian or Ubuntu host PC to setup the SD card image.

# Installing directly into the .img file
For the installation, mount the .img file on the host PC and run it in a chroot environment.

```bash
# Download and unzip kivypie image
wget http://kivypie.mitako.eu/kivy-pie-1.0.zip
unzip kivy-pie-1.0.zip

# Make the image file bigger to gain some free space
dd if=/dev/zero bs=1M count=4096 >> kivy-pie-1.0.img

# mount image as loopfs
sudo losetup -P /dev/loop0 kivy-pie-1.0.img

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

# ... carry out the install steps in the next section  ...
# then

sudo halt
sudo umount mnt/boot
sudo umount mnt
sudo losetup -D

# Now we have a modified kivypie image with MPF pre-installed
# insert a SD card and make sure it appears as `/dev/mmcblk0`
sudo dd bs=1M if=kivy-pie-1.0.img of=/dev/mmcblk0 conv=fsync

# enable SSH server
touch /boot/ssh

# mount the system partition and add the wifi credentials to:
nano /etc/network/interfaces

# Reserve a CPU core for the LED panel
nano /boot/cmdline.txt
    # append this to the list of space-separated commands
    isolcpus=3

```



# Install steps
In virtual machine or on Raspberry Pi over ssh.

Unmount, stick it in the raspberry pi, hope that it boots and connects to wifi. Then ssh into it: `ssh sysop@kivypie`.
Default password for sysop and sudo: `posys`. Better change that!

```bash
# Expand partition to SD card size
sudo mount -o remount,size=256M /tmp  # make tmp bigger temporarily
sudo pipaos-config --expand-rootfs
sudo reboot now

# Update and install stuff
sudo mount -o remount,size=256M /tmp
sudo apt update
sudo apt upgrade
sudo apt-get install -y build-essential libbz2-dev libssl-dev libreadline-dev libsqlite3-dev tk-dev libpng-dev libfreetype6-dev libncurses5-dev sox

# Install python 3.6.13 ... like this because there is no package in raspian :(
curl -L https://github.com/pyenv/pyenv-installer/raw/master/bin/pyenv-installer | bash

# add the following to ~/.bashrc:
vim ~/.bashrc
    export PATH="/home/sysop/.pyenv/bin:$PATH"
    eval "$(pyenv init -)"
    eval "$(pyenv virtualenv-init -)"

source ~/.bashrc
pyenv install 3.6.13
pyenv global 3.6.13

pip3 install cython
pip3 install numpy

# Delete all the KivyPie demo crap
cd ~
rm -rf *

# Clone game rules and helper scripts
git clone https://github.com/yetifrisstlama/Fan-Tas-Tic-machine.git

# Convert music to .wav files
cd Fan-Tas-Tic-machine
mkdir sounds/music
cd oggmusic
./convert.sh

# Follow instruction to install bcm2835 library
# https://www.airspayce.com/mikem/bcm2835/
# then compile auto-shutdown handler
mkdir mpfdev
cd mpfdev/
wget http://www.airspayce.com/mikem/bcm2835/bcm2835-1.68.tar.gz
tar -xvf bcm2835-1.68.tar.gz
cd bcm2835-1.68/
./configure
make
sudo make install
cd ~/Fan-Tas-Tic-machine/shutdown
make

# Install Mission Pinball Framework
cd ~/mpfdev
git clone https://github.com/missionpinball/mpf.git
cd mpf
git checkout 0.54
pip3 install -e .

# Install Mission Pinball Media Controller
cd ~/mpfdev
git clone https://github.com/missionpinball/mpf-mc.git
cd mpf-mc
git checkout 0.54
# couldn't get ffpyplayer to compile on jessie, too bad
vim setup.py
    # comment-out line 640
    #'ffpyplayer==4.3.1'
pip3 install -e .

# Install Mission Pinball Fan-Tas-Tic platform driver
cd ~/mpfdev
git clone https://github.com/yetifrisstlama/Fan-Tas-Tic-platform.git
cd Fan-Tas-Tic-platform
pip3 install -e .

# Install LED panel driver
cd ~/mpfdev
git clone https://github.com/hzeller/rpi-rgb-led-matrix.git
cd rpi-rgb-led-matrix
git checkout d18ba4a4654480572f7c43fb37e1aa9c9b6ab627
make
sudo make install-python PYTHON=$(which python3)

# need to disable rpi internal sound
sudo vim /etc/modprobe.d/blacklist-rgb-matrix.conf
    blacklist snd_bcm2835

# Make C-media USB the default sound-card
sudo vim /etc/modprobe.d/alsa-base.conf
    options snd-usb-audio index=0
    options snd_bcm2835 index=1
```

Do a manual test-run if mpf starts. The -a option makes it re-generate all cache files, which seems to be needed on the first run only.

```bash
cd ~/Fan-Tas-Tic-machine
sudo /home/sysop/.pyenv/shims/mpf -at
```

As mpf-mc is not running, it should power up the 24 V relay and stop at:

```
INFO : BCPClientSocket : Connecting BCP to 'local_display' at localhost:5050...
```

Pushing the flipper buttons should show events in the console:

```
INFO : SwitchController : <<<<<<< 's_flipper_right' active >>>>>>>
```

# Start on boot, Shutdown on switch toggle
add the following lines to `/etc/rc.local` before `exit 0`

```bash
/home/sysop/Fan-Tas-Tic-machine/shutdown/shutdown_handler &
/home/sysop/Fan-Tas-Tic-machine/start.sh &
```

This will start mpf in a screen session on boot. To see it running use `sudo screen -r`

# SD card images
How to take and restore a backup image of the SD card. Done from a debian / Ubuntu host PC.

Make sure to replace `/dev/mmcblk0` with the right device name of the SD card.

## Verify backup

```bash
$ echo "edb61e63e22c11887f58ae24c08769faf378f264b4e64562865c9c46fa145b87  fantastic_2021_02_12.img.gz" | sha256sum -c
fantastic_2021_02_12.img.gz: OK
```

## Create Backup

```bash
$ sudo dd bs=1M status=progress if=/dev/mmcblk0 | gzip --best > fantastic_2021_02_12.img.gz
```

## Restore Backup

Warning `/dev/mmcblk0` will be overwritten. Make sure it's the SD card.

```bash
$ gzip -dc fantastic_2021_02_12.img.gz | sudo dd bs=1M status=progress of=/dev/mmcblk0
```
