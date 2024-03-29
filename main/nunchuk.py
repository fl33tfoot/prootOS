import time
import board
import adafruit_nunchuk

import env
from env import log

# current indexes for the animation files
page = 0
anim = 0

i2c = 0
nc = 0

# suppress log entrys after 5 times until next run
log_suppress = 0

# populated animation file array
files = [[]]

# Search for new animations

# Convert if not converted already

# Populate animation list

## Display daemon function
def show_anim():
    pass

## Debug function
def debug():
    global page, anim

    print("Page:{} Index:{}".format(page,anim))

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
    global i2c, nc, page, anim

    log("Initializing I2C nunchuk...")
    while True:
        while not wait_for_i2c():
            wait_for_i2c()

        try:
            log("I2C nunchuk connected!")
            while True:
                debug()

                x, y = nc.joystick
                z = nc.buttons.Z
                c = nc.buttons.C

                # Get button presses/page
                if z and c:
                    page = 2
                elif z and not c:
                    page = 3
                elif c and not z:
                    page = 1
                else:
                    page = 0

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

                # Refresh speed
                time.sleep(env.sensitivity)
        except Exception as e:
                log("I2C communcation interrupted: {}".format(e), err_id=12)

if __name__ == "__main":
    print("Run this via __init__.py please :3")
