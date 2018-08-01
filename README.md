# Fan-Tas-Tic-machine
Game Rules for the Fan-Tas-Tic pinball machine

# Installing everything from scratch

Fastest is to start with KivyPie

```bash
wget http://kivypie.mitako.eu/kivy-pie-1.0.zip
unzip kivy-pie-1.0.zip
sudo dd bs=4M if=kivy-pie-1.0.img of=/dev/mmcblk0 conv=fsync
touch /media/michael/boot/ssh
vim /media/michael/boot/interfaces

	iface wlan0 inet dhcp
	        wpa-ssid "ssid"
	        wpa-psk "password"

vim /boot/cmdline.txt --> add isolcpus=3
```

boot it up and ssh into it `sysop@kivypie` Password: `posys`.

```bash
sudo pipaos-config --expand-rootfs
sudo umount /tmp

git clone https://github.com/yetifrisstlama/Fan-Tas-Tic-machine.git
mkdir mpfdev
cd mpfdev
git clone https://github.com/missionpinball/mpf.git
git clone https://github.com/missionpinball/mpf-mc.git
git clone https://github.com/missionpinball/mpf-examples.git
git clone https://github.com/hzeller/rpi-rgb-led-matrix.git
git checkout 0.50.x

sudo apt-get install -y build-essential libbz2-dev libssl-dev libreadline-dev libsqlite3-dev tk-dev libpng-dev libfreetype6-dev
curl -L https://github.com/pyenv/pyenv-installer/raw/master/bin/pyenv-installer | bash
source ~/.bashrc
pyenv install 3.6.6
pyenv global 3.6.6

pip3 install cython
pip3 install numpy

cd mpf
git checkout fantastic
pip3 install -e .

cd ../mpf-mc
vim setup.py  --> line 467:   if not have_cython or True:
pip3 install -e .

cd ../rpi-rgb-led-matrix
sudo make install-python PYTHON=$(which python3)
sudo vim /etc/modprobe.d/blacklist-rgb-matrix.conf
--> add `blacklist snd_bcm2835`
```

### Kivy nearest neighbor hack

Now `sudo mpf both -t` does run but DMD looks blurry. Apply the patch from
https://github.com/kivy/kivy/issues/5249 to fix it. Watch out with tab and sapces etc.

```bash
vim ~/.pyenv/versions/3.6.6/lib/python3.6/site-packages/kivy/core/text/__init__.py
```

line 688

```python
texture = Texture.create(size=(width, height),
                         mipmap=self.options['mipmap'],
                         callback=self._texture_fill)
texture.flip_vertical()
texture.add_reload_observer(self._texture_refresh)
#switching off linear interpolation
+ texture.mag_filter="nearest"
+ texture.min_filter="nearest"
self.texture = texture
```

### Samba

```bash
sudo apt-get install samba
sudo smbpasswd -a sysop
sudo vim /etc/samba/smb.conf
[pihome]
   comment= Pi Home
   path=/home/pi
   browseable=Yes
   writeable=Yes
   only guest=no
   create mask=0777
   directory mask=0777
   public=no
sudo /etc/init.d/samba restart
```
access from ubuntu: `smb://fantastic/fantastic/`

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

# Start on boot
add the following to `/etc/rc.local`
```bash
/home/sysop/start.sh &
```

Will start mpf in a screen session. To see it running use `sudo screen -r`
