// Shut down the system if a GPIO pin changes state
// Runs as root
#include <bcm2835.h>
#include <stdio.h>

#define PIN 16

int main(int argc, char **argv)
{
    if (!bcm2835_init())
    return 1;

    // Set as input
    bcm2835_gpio_fsel(PIN, BCM2835_GPIO_FSEL_INPT);
    //  with a pullup
    bcm2835_gpio_set_pud(PIN, BCM2835_GPIO_PUD_UP);

    uint8_t val, old_val = bcm2835_gpio_lev(PIN);
    while (1)
    {
        // Read pin state
        val = bcm2835_gpio_lev(PIN);
        if(val != old_val){
            old_val = val;
            printf("!!! Shutdown !!!\n");
            system("pkill mpf --signal SIGINT");
            delay(1000);
            system("shutdown now");
            break;
        }
        delay(1000);
    }

    bcm2835_close();
    return 0;
}

