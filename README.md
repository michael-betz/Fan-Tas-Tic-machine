# Fan-Tas-Tic-machine
Game Rules for the Fan-Tas-Tic pinball machine

# Installing everything on the Raspberry PI from scratch
Note that the MPF team recommends using an alternative linux distribution called `KivyPie`. However it has not been updated in a while, so we're going to use the lightest version of Raspian in a headless setup (no monitor, only ssh access).

Start by setting up a raspian SD card, according to
https://www.raspberrypi.org/software/operating-systems/#raspberry-pi-os-32-bit

You can use a newer raspian image, as long as it has python3.7 installed, which is generally the case for debian buster based ones.

We plug this SD card into the raspberry PI 3 and boot it once, such that the filesystem gets expanded. Connect it with an ethernet cable to your home router, such that it gets an IP address over DHCP. Then SSH into it.

```bash
# For Direct ethernet connection (no DHCP)
sudo ip addr add dev enp0s31f6 169.254.173.1/24
ssh pi@169.254.173.63

# with DHCP... default password: raspberry
ssh pi@raspberrypi

# change default password
passwd

# expand filesystem, set timezone, add wifi credentials (optional)
sudo raspi-config
sudo shutdown now
```

The actual installation steps.

```bash
# login as pi, raspberry

# change password for user pi
passwd

# Set hostname to fantastic
sudo raspi-config

# system update
sudo apt update
sudo apt upgrade
sudo apt install build-essential git sox screen python3-pip python3-numpy libopenjp2-7
libtiff5 libgstreamer1.0-0 libsdl2-2.0-0 libsdl2-image-2.0-0 libsdl2-mixer-2.0-0 libsdl2-ttf-2.0-0 libgl1

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

#-------------------------
# Install LED panel driver
#-------------------------
cd ~
git clone https://github.com/hzeller/rpi-rgb-led-matrix.git
cd rpi-rgb-led-matrix
git checkout 6801ede6b1de6902e0d0d99bc92676b98a73639e
make
sudo make install-python PYTHON=$(which python3)

# Reserve a CPU core for the LED panel
sudo touch /boot/ssh
sudo nano /boot/cmdline.txt
    # append this to the list of space-separated commands
    isolcpus=3

# need to disable rpi internal sound
sudo nano /etc/modprobe.d/blacklist-rgb-matrix.conf
    blacklist snd_bcm2835

# Make C-media USB the default sound-card
sudo nano /etc/modprobe.d/alsa-base.conf
    options snd-usb-audio index=0
    options snd_bcm2835 index=1

#-------------------------
# Install Mission Pinball
#-------------------------
sudo pip3 install mpf==0.54 mpf-mc==0.54

# Install MPF Fan-Tas-Tic platform driver
sudo pip3 install git+https://github.com/yetifrisstlama/Fan-Tas-Tic-platform.git

#-------------------------
# Install machine files
#-------------------------
git clone https://github.com/yetifrisstlama/Fan-Tas-Tic-machine.git

# Optional: convert music to .wav files
# mkdir sounds/music
# cd oggmusic
# ./convert.sh
# or just link the .ogg files ...
cd Fan-Tas-Tic-machine
ln -s $HOME/Fan-Tas-Tic-machine/oggmusic/ sounds/music

# Make the shutdown switch handler
cd ~/Fan-Tas-Tic-machine/shutdown
make
```

Do a manual test-run if mpf starts. The -a option makes it re-generate all cache files, which seems to be needed on the first run only.

```bash
cd ~/Fan-Tas-Tic-machine
sudo mpf -at
```

As mpf-mc is not running, it should power up the 24 V relay and stop at:

```
INFO : BCPClientSocket : Connecting BCP to 'local_display' at localhost:5050...
```

Pushing the flipper buttons should show events in the console:

```
INFO : SwitchController : <<<<<<< 's_flipper_right' active >>>>>>>
```

If everything works, generate the production files

```bash
mpf build production_bundle
```

# Start on boot, Shutdown on switch toggle
Copy and enable the 2 systemd service files:

```bash
sudo cp shutdown/shutdown_handler.service /etc/systemd/system/
sudo cp shutdown/fantastic.service /etc/systemd/system/

sudo systemctl daemon-reload

sudo systemctl enable shutdown_handler
sudo systemctl start shutdown_handler
systemctl status shutdown_handler
    ● shutdown_handler.service - FanTasTic shutdown switch

sudo systemctl enable fantastic
sudo systemctl start fantastic
systemctl status fantastic
    ● fantastic.service - FanTasTic pinball machine

# See log file:
journalctl -u fantastic -ef
```


add the following lines to `/etc/rc.local` before `exit 0`

```bash
sudo nano /etc/rc.local
    /home/pi/Fan-Tas-Tic-machine/shutdown/shutdown_handler &
    /home/pi/Fan-Tas-Tic-machine/start.sh &
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

# Playfield simulation (`mpf monitor`)
This allows you to run mpf on a host PC and interact with the virtual playfield with the mpf monitor command. This is ideal for developing and testing new game rules.

I had to build and install python 3.6 manually on my debian-testing machine (this old python version was not included anymore in apt)

```bash
wget https://www.python.org/ftp/python/3.6.10/Python-3.6.10.tgz
tar -xvf Python-3.6.10.tgz
cd Python-3.6.10/
./configure --prefix=/usr/local --enable-optimizations
make -j4
sudo make install
```

Then create the virtual python environment and install mpf 0.54

```bash
mkvirtualenv --python python3.6 mpf
python --version
# Python 3.6.10
pip install mpf==0.54 mpf-mc==0.54 mpf-monitor==0.54
pip install numpy pyqt5
```

You can always go back to this environment later with `workon mpf`.

Now let's get the machine directory ready ...

```bash
# copy music files in the right place (no need to convert to .wav)
cd Fan-Tas-Tic-machine
mkdir sounds/music
cp oggmusic/*.ogg sounds/music

vim config/config.yaml
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

In the playfield window, squares represent switches, which you can left-click to activate them. Circles represent LEDs.


# Installing directly into the .img file
We can do the installation either on the raspi itself (easier) or in a virtual machine on a host PC (faster). For the latter, follow these steps to run and modify the .img file locally.

```bash
# Download and unzip raspian image.
wget https://downloads.raspberrypi.org/raspios_lite_armhf/images/raspios_lite_armhf-2021-01-12/2021-01-11-raspios-buster-armhf-lite.zip
unzip 2021-01-11-raspios-buster-armhf-lite.zip

# Make the image file bigger to gain some free space
dd if=/dev/zero bs=1M count=2048 >> 2021-01-11-raspios-buster-armhf-lite.img

# mount image as loopfs
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

# ... carry out the install steps above ...

sudo halt
sudo umount mnt/boot
sudo umount mnt
sudo losetup -D

# Now we have a modified raspian image with MPF pre-installed
# copy it to SD and boot
```
