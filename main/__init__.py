# library imports
import time
from importlib import reload

# fix bjorked config
import setup
setup.main()

# project imports
import pupdate
import upload
import nunchuk
import env
from env import log

if __name__ == "__main__":

    log("{} is waking up... good morning!".format(env.protogen))

    log("Update check!")
    update.main()

    log("Starting USB hotplug listener!")
    log(".... when i want it working")

    log("System hardware check: {} archetype, {} controller".format(env.archetype, ((env.controller + " " + env.pwc) if (env.controller == "wireless") else env.controller)))
    if env.archetype == "basic":
        nunchuk.main()
        pass
    elif env.archetype == "advanced":
        pass
    else:
        log("I dont know what archetype I have! Goodbye!", err_id=11)
        exit()
