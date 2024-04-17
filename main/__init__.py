# library imports
import time
import asyncio
from importlib import reload

# fix bjorked config
import setup
setup.main()

# project imports
import pupdate
import animconvert
import display
import upload
import nunchuk
import env
from env import log

def main():
    log("{} is waking up... good morning!".format(env.protogen))

    log("Update check!")
    pupdate.main()

    log("Starting USB hotplug listener!")
    log(".... when i want it working")

    log("---")
    log("ARCHETYPE: {}".format(env.archetype))
    log("CONTROLLER: {}".format((env.controller + " " + env.pwc) if (env.controller == "wireless") else env.controller))

    log("---")


    if env.archetype == "basic":
        nunchuk.main()
        pass
    elif env.archetype == "advanced":
        pass
    else:
        log("I dont know what archetype I have! Goodbye!", err_id=11)
        exit()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        display.kill()
        exit()
