# Shutdown handler
Once installed in a pinball machine, you don't want to just pull the
power plug on the raspberry pi. It's better to shutdown the system first.

I connected a toggle-switch (the original power switch of my EM machine)
to one of the raspi GPIOs. This program checks if the switch was toggled
periodically and then shuts down the system nicely.

## Building
Follow instruction to install the
[bcm2835](https://www.airspayce.com/mikem/bcm2835/) library. Then

```bash
./build.sh                  # compile
sudo ./shutdown_handler &   # run in background
```

## Run on boot
add the following to `/etc/rc.local`
```bash
<absolute path to file>/shutdown_handler &
```
