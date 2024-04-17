import os
import subprocess
import datetime
import json
import inspect

## environment variables
# current timestamp
def now():
    return datetime.datetime.now()
def timestamp():
    return now().strftime("%Y_%m_%d-%H_%M_%S")

# current user
user = (subprocess.run(["grep", "1000", "/etc/passwd"], capture_output=True)).stdout.decode().split(":")[0]

## file directories
# system hierarchy
SYSTEM = "/home/{}/protogen".format(user)
SYSTEM_ANIM = SYSTEM + "/anim"
SYSTEM_MAIN = SYSTEM + "/main"
SYSTEM_LOGFILE = SYSTEM + "/main/output.log"
SYSTEM_CONFIGFILE = SYSTEM + "/main/config.json"
SYSTEM_HASHFILE = SYSTEM + "/anim/hashes.json"
MOUNT = SYSTEM + "/usb"

# streamfile extension for compiled animations
STREAMFILE_EXTENSION = ".proot"
LIV_PATH = SYSTEM + "/main/led-image-viewer"
TS_PATH = SYSTEM + "/main/text-scroller"
RUNTIME_ANIMS_DIR = SYSTEM + "/main/sys_anim"
RUNTIME_ANIMS = ["uploading", "downloading", "converting", "update", "error", "update_wifi", "usb", "ok"]
BASIC_ANIMS_PAGE = ["default", "top", "top_right", "right", "bot_right", "bot", "bot_left", "left", "top_left"]

# usb mount hierarchy
ROOT = MOUNT + "/protogen"
ROOT_ANIM = MOUNT + "/protogen/anim"
ROOT_MAIN = MOUNT + "/protogen/main"
ROOT_BACKUP = MOUNT + "/protogen/backup"

## log function
# err_id: 0 - informational, see README.md
# msg: error message
def log(msg, err_id=0):
    if not os.path.exists(SYSTEM_LOGFILE):
        with open (SYSTEM_LOGFILE, "w") as logfile:
            logfile.write("Hello World! You're probably wondering how I got here :3\n")
    with open (SYSTEM_LOGFILE, "a") as logfile:
        entry = ("[{}] {}{}: {}".format(
            # timestamp but user friendly
            now().strftime("%Y/%m/%d @ %H:%M:%S"),
            # either error id or ok
            ("(ERR {}) ".format(err_id) if (err_id > 0) else "(  OK  ) "),
            # function caller script name
            inspect.stack()[1].filename.split("/")[-1],
            # log message
            msg
        ))
        # print entry to both logfile and stdout
        print(entry, file=logfile)
        print(entry)

# refresh config function just in case i need a critical config option
def refresh_config():
    try:
        with open(SYSTEM_CONFIGFILE, 'r') as cfg:
            return json.load(cfg)
    except Exception as e:
        log("Unable to open config.json: {}".format(e), err_id=102)
    return None

if os.path.exists(SYSTEM_CONFIGFILE):
    config = refresh_config()

    ## json variables
    try:
        if config is None:
            raise Exception("Empty configuration variable (not loaded properly?)")

        # hardware archetype, either basic or advanced configuration
        archetype = config["system"]["os_archetype"].lower()
        # protogen name
        protogen = config["preferences"]["name"].upper()
        # controller sensitivity (update rate in seconds)
        sensitivity = config[archetype]["sensitivity"]
        # proot-os version
        version = config["system"]["os_version"]
        # in the rare event of corrupt config, this option will yield a higher
        # operational success rate at the cost of possible lost config
        destructive_repairs = config["preferences"]["allow_destructive_repairs"]
        # controller interface type and preferred wireless controller
        # wired - nunchuk only
        # wireless - joycon, wiimote
        controller = config["preferences"]["controller"]
        pwc = config["preferences"]["preferred_wireless_controller"]

        # setup matrix preferences
        MATRIX_COLS = 64
        MATRIX_ROWS = 32
        MATRIX_GPIO_SLOWDOWN = 2
        MATRIX_BRIGHTNESS = 10 if config["preferences"]["led_brightness"] < 10 else config["preferences"]["led_brightness"]
        MATRIX_TYPE = "adafruit-hat-pwm"
        MATRIX_FPS = config["preferences"]["default_fps"]
        MATRIX_DAISY_CHAIN = 2
        MATRIX_REFRESH_RATE_LIMIT = 0

        log("JSON variables initialized successfully")

    except (Exception, AttributeError, KeyError) as e:
        log("Error setting JSON variables: {}".format(e))

## functions
# default animation fps when not manually specified
def get_anim_default_fps():
    # animation speed in ms, 17ms = about 60 fps, 100ms = 10 fps, default 10
    return MATRIX_BRIGHTNESS

if __name__ == "__main__":
    print("This is a supplementary environment variable script. Congrats, nothing happened :3")
