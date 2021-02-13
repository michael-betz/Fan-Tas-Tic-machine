# Fan-Tas-Tic-machine
Game Rules for the Fan-Tas-Tic pinball machine

# Installing everything from scratch

Fastest is to start with KivyPie

```bash
wget http://kivypie.mitako.eu/kivy-pie-1.0.zip
unzip kivy-pie-1.0.zip
# insert a SD card and make sure it appears as `/dev/mmcblk0`
sudo dd bs=4M if=kivy-pie-1.0.img of=/dev/mmcblk0 conv=fsync

# mount SD card (file manager) ...

# enable SSH server
touch /media/$USER/xsysroot/ssh

# Add your wifi credentials in wpa-ssid / wpa-psk
vim /media/$USER/xsysroot/interfaces

# The above doesn't seem to work anymore ...
# so mount the system partition and add the wifi credentials to:
vim /media/$USER/<...>/etc/network/interfaces

# Reserve a CPU core for the LED panel
vim /media/$USER/xsysroot/cmdline.txt
    # append this to the list of space-separated commands
    isolcpus=3
```

Unmount, stick it in the raspberry pi, hope that it boots and connects to wifi. Then ssh into it: `ssh sysop@kivypie`.
Default password for sysop and sudo: `posys`. Better change that!

```bash
# Expand partition to SD card size
sudo umount /tmp
sudo pipaos-config --expand-rootfs
sudo reboot now

# Update and install stuff
sudo umount /tmp
sudo apt update
sudo apt upgrade
sudo apt-get install -y build-essential libbz2-dev libssl-dev libreadline-dev libsqlite3-dev tk-dev libpng-dev libfreetype6-dev libncurses5-dev sox

# Install python 3.6.6 ... like this because there is no package in raspian :(
curl -L https://github.com/pyenv/pyenv-installer/raw/master/bin/pyenv-installer | bash

# add the following to ~/.bashrc:
vim ~/.bashrc
    export PATH="/home/sysop/.pyenv/bin:$PATH"
    eval "$(pyenv init -)"
    eval "$(pyenv virtualenv-init -)"

source ~/.bashrc
sudo umount /tmp
pyenv install 3.6.6
pyenv global 3.6.6

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
git checkout 295c411cebe7e0eab25542cf54414edf799c6327
pip3 install -e .

# Install Mission Pinball Media Controller
cd ~/mpfdev
git clone https://github.com/missionpinball/mpf-mc.git
cd mpf-mc
git checkout 10249a4b494d6c0e62f6e52ff91f1b982e8ce15a
vim setup.py
    # comment-out line 612:
    #'ffpyplayer==4.2.0;platform_system!="Windows"'
pip3 install -e .

# Install Mission Pinball Fan-Tas-Tic platform driver
cd ~/mpfdev
git clone https://github.com/yetifrisstlama/Fan-Tas-Tic-platform.git
cd Fan-Tas-Tic-platform
git checkout 53ce0c4dd1288a8593bb532f194353135734a09e
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
