import time
import board
import adafruit_nunchuk
import asyncio

import env
import display
from env import log
from display import show, kill

# last index of animation fle
last_page = 0
last_anim = 0

i2c = 0
nc = 0

# suppress log entrys after 5 times until next run
log_suppress = 0

## Debug function
def debug():
    global last_page, last_anim

    print("Page:{} Index:{}".format(last_page, last_anim))

def wait_for_i2c():
    global log_suppress, i2c, nc

    try:
        i2c = board.I2C()
        nc = adafruit_nunchuk.Nunchuk(i2c)
    except Exception as e:
        if log_suppress == 5:
            log("I2C communcation error: {} (Is your nunchuk connection secure?)".format(e), err_id=12)
            log("Controller log supression threshold reached. No further logs will be sent until next run")
            log_suppress += 1
        elif log_suppress < 5:
            log("I2C communcation error: {} (Is your nunchuk connection secure?)".format(e), err_id=12)
            log("Reintializing connection...")
            log_suppress += 1
        time.sleep(2)
        return False
    return True

## Main loop
def main():
    global i2c, nc, last_page, last_anim

    page = 0
    anim = 0

    log("Initializing I2C nunchuk...")
    while True:
        while not wait_for_i2c():
            wait_for_i2c()

        try:
            log("I2C nunchuk connected!")
            while True:

                x, y = nc.joystick
                z = nc.buttons.Z
                c = nc.buttons.C

                # Get button presses/page
                if z and c:
                    page = 4
                elif z and not c:
                    page = 3
                elif c and not z:
                    page = 2
                else:
                    page = 1

                # Get joystick axes (animations)
                if y >= 192:
                    if x >= 192:
                        anim = 2
                    elif x <= 64:
                        anim = 8
                    else:
                        anim = 1
                elif y <= 64:
                    if x >= 192:
                        anim = 4
                    elif x <=64:
                        anim = 6
                    else:
                        anim = 5
                else:
                    if x >= 192:
                        anim = 3
                    elif x <= 64:
                        anim = 7
                    else:
                        anim = 0


                if not last_anim == anim or not last_page == page:
                    last_anim = anim
                    last_page = page
#                    debug()

                    show([page, anim])

                # Refresh speed
                time.sleep(env.sensitivity)
        except Exception as e:
            log("I2C communcation interrupted: {}".format(e), err_id=12)
        except KeyboardInterrupt:
            log("Captured keyboard interrupt? Goodbye!")
            kill()
            quit()

if __name__ == "__main__":
    main()
    print("Run this via __init__.py please :3")
