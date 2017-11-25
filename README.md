# Fan-Tas-Tic-machine
Game Rules for the Fan-Tas-Tic pinball machine

# Installing everything from scratch

## Raspi setup
(written 10/24/2017)

	* Get a 16 GB SD card
	* Download and install Raspian on it

```bash
wget http://vx2-downloads.raspberrypi.org/raspbian_lite/images/spbian_lite-2017-09-08/2017-09-07-raspbian-stretch-lite.zipunzip 2017-09-07-raspbian-stretch-lite.zip
sudo dd bs=4M if=2017-09-07-raspbian-stretch-lite.img of=/dev/mmcblk0 nv=fsync
touch /media/michael/boot/ssh
```

  * boot up, connnect to wired ethernet, ssh in, default password is `raspberry`

```bash
ssh pi@raspberrypi
passwd
sudo passwd
sudo nano /etc/wpa_supplicant/wpa_supplicant.conf
```  

add

		network={
		    ssid="testing"
		    psk="testingPassword"
		}

now wifi is up.

```bash
sudo raspi-config --> hostname: fantastic  --> timezone: US/Pacific
sudo apt-get update
sudo apt-get upgrade

sudo apt-get install vim git python3-pip libopenjp2-7-dev \
libblas-dev libsdl2-dev libsdl2-image-dev libsdl2-ttf-dev \
liblapack-dev libsdl2-mixer-dev libgstreamer1.0-dev \
# gstreamer1.0-plugins-{bad,base,good,ugly} \
# gstreamer1.0-{omx,alsa}

sudo pip3 install Cython==0.24.1
sudo pip3 install Pillow
sudo pip3 install numpy
sudo pip3 install git+https://github.com/kivy/kivy.git@master

mkdir mpfdev
cd mpfdev
git clone https://github.com/yetifrisstlama/mpf.git
git clone https://github.com/missionpinball/mpf-mc.git
git clone https://github.com/missionpinball/mpf-examples.git
git clone https://github.com/hzeller/rpi-rgb-led-matrix.git
cd mpf
git checkout fantastic
sudo pip3 install -e .
cd ../mpf-mc
sudo pip3 install -e .

sudo vim /etc/modprobe.d/blacklist-rgb-matrix.conf
--> add `blacklist snd_bcm2835`
sudo update-initramfs -u
sudo reboot
cd ~/mpfdev/rpi-rgb-led-matrix
sudo make install-python PYTHON=$(which python3)

cd ~
git clone https://github.com/yetifrisstlama/Fan-Tas-Tic-machine.git
```






