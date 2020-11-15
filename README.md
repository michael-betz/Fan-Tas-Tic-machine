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
touch /media/<...>/boot/ssh

# Add your wifi credentials
vim /media/<...>/boot/interfaces
    iface wlan0 inet dhcp
    wpa-ssid "ssid"
    wpa-psk "password"

# Reserve a CPU core for the LED panel
vim /boot/cmdline.txt
    add isolcpus=3
```

boot it up and ssh into it `sysop@kivypie`.
Default password: `posys`. Better change it!

```bash
sudo pipaos-config --expand-rootfs
sudo umount /tmp

sudo apt-get install -y git build-essential libbz2-dev libssl-dev libreadline-dev libsqlite3-dev tk-dev libpng-dev libfreetype6-dev
curl -L https://github.com/pyenv/pyenv-installer/raw/master/bin/pyenv-installer | bash
source ~/.bashrc
pyenv install 3.6.6
pyenv global 3.6.6

pip3 install cython
pip3 install numpy

# Clone game rules and helper scripts
git clone https://github.com/yetifrisstlama/Fan-Tas-Tic-machine.git

# Follow instruction to install bcm2835 library
# https://www.airspayce.com/mikem/bcm2835/
# then compile auto-shutdown handler
cd Fan-Tas-Tic-machine/shutdown
make

# Clone Mission Pinball + etc.
mkdir ~/mpfdev
cd ~/mpfdev
git clone https://github.com/missionpinball/mpf.git
git clone https://github.com/missionpinball/mpf-mc.git
git clone https://github.com/yetifrisstlama/Fan-Tas-Tic-platform.git
git clone https://github.com/hzeller/rpi-rgb-led-matrix.git

# Install Mission Pinball Framework
cd mpf
git checkout 295c411cebe7e0eab25542cf54414edf799c6327
pip3 install -e .

# Install Mission Pinball Media Controller
cd ../mpf-mc
git checkout 10249a4b494d6c0e62f6e52ff91f1b982e8ce15a
vim setup.py
    # comment-out line 612:
    #'ffpyplayer==4.2.0;platform_system!="Windows"'
pip3 install -e .

# Install Mission Pinball Fan-Tas-Tic platform driver
cd ~/mpfdev/Fan-Tas-Tic-platform
pip3 install -e .

# Install LED panel driver
cd ../rpi-rgb-led-matrix
git checkout d18ba4a4654480572f7c43fb37e1aa9c9b6ab627
make
sudo make install-python PYTHON=$(which python3)

# need to disable rpi internal sound
sudo vim /etc/modprobe.d/blacklist-rgb-matrix.conf
    blacklist snd_bcm2835
```
# Start on boot, Shutdown on switch toggle
add the following to `/etc/rc.local`
```bash
/home/sysop/Fan-Tas-Tic-machine/shutdown/shutdown_handler &
/home/sysop/Fan-Tas-Tic-machine/start.sh &
```
Will start mpf in a screen session. To see it running use `sudo screen -r`

### File access from remote PC

```bash
sshfs ~/sshfs sysop@fantastic:/home/sysop/mpfdev
```
... gotta love sshfs!!!

### SD card images

__Backup__

```bash
sudo dd bs=4M if=/dev/mmcblk0 | gzip > fantastic_17_11_26.gz
```

__Restore__

```bash
sudo gzip -dc fantastic_17_11_26.gz | dd bs=4M of=/dev/mmcblk0
```

# Get kivy running
With miniconda I had to do this to force the system libstdc++

```bash
mv /home/michael/miniconda3/lib/libstdc++.so.6 /home/michael/miniconda3/lib/libstdc++.so.6.bak
```

# Test Kivy
```python
>>> import os
>>> os.environ['LIBGL_DEBUG'] = 'verbose'
>>> import kivy
>>> from kivy.core.window import Window
```

