import json
import os
from importlib import reload

import env
from env import log

default_config = {
    "preferences": {
        "name": "unknown protogen",
        "comm": False,
        "uuid": 0,
        "default_fps": 10,
        "allow_destructive_repairs": False,
        "controller": "wired",
        "preferred_wireless_controller": "any",
        "led_brightness": 100
    },
    "system": {
        "os_version": "1.5.0",
        "os_archetype": "basic",
        "update_server": "api.southpawstudios.org",
        "update_port": 3260,
        "wifi_ssid": "",
        "wifi_pw": ""
    },
    "basic": {
        "sensitivity": 0.1,
        "volume": 10000
    },
    "advanced": {
        "sensitivity": 0.1,
        "volume": 10000,
        "rgb": False,
        "audio": False
    },
    "devices": {
        "pairing_failures": 0,
        "wiimote_a": "",
        "wiimote_b": "",
        "joycon_a": "",
        "joycon_b": "",
        "speaker_a": ""
    }
}


def update_config_features():
    global default_config
    new_options = 0

    try:
        with open(env.SYSTEM_CONFIGFILE, 'r') as cfg:
            current_config = json.load(cfg)
    except Exception as e:
        log("Unable to load config file correctly. Check your configuration for extra commas. also pls no edit the config if you dunno what ur doing :3",
            err_id=102)
        exit()

    try:
        log("Checking for new config...")

        for section, data in default_config.items():
            if section in current_config:
                for key, value in data.items():
                    if key not in current_config[section]:
                        log("Incrementally updating section '{}' with new config item '{}'".format(section, key))
                        current_config[section][key] = value
                        new_options += 1
            else:
                current_config[section] = data

        with open(env.SYSTEM_CONFIGFILE, 'w') as cfg:
            json.dump(current_config, cfg, indent=4)

        if new_options > 0:
            log("Successfully added {} new config option(s)".format(new_options))
            log("Reloading environment variables...")
            reload(env)
        else:
            log("No new configuration to add")

    except Exception as e:
        log("Error performing incremental config update: {}".format(e), err_id=11)
        return False
    return True


def overwrite_config(sections=["system", "basic", "advanced"]):
    global default_config

    with open(env.SYSTEM_CONFIGFILE, 'r') as cfg:
        current_config = json.load(cfg)

    try:
        overwrite_these = sections

        for section, data in default_config.items():
            if section in overwrite_these:
                current_config[section] = data

        log("Overwriting default values...")
        with open(env.SYSTEM_CONFIGFILE, 'w') as cfg:
            json.dump(current_config, cfg, indent=4)
        log("Successfully overwrote default configuration")

    except Exception as e:
        log("Error overwriting default configuration: {}".format(e), err_id=11)
        return False

    return True


def make_default_config():
    global default_config

    try:
        log("Generating first time config...")
        # input information here at a future date for customization
        # for now its manual input :P

        log("Writing config file...")
        with open(env.SYSTEM_CONFIGFILE, 'w') as cfg:
            json.dump(default_config, cfg, indent=4)
        log("Successfully wrote config file")

        reload(env)

    except Exception as e:
        log("Error creating config file: {}".format(e), err_id=11)
        return False
    return True


def update_version():
    global default_config

    new_version = str(default_config["system"]["os_version"])

    v1 = list(map(int, str(env.version).split(".")))
    v2 = list(map(int, new_version.split(".")))

    while len(v1) < len(v2):
        v1.append(0)
    while len(v2) < len(v1):
        v2.append(0)

    for cur, lat in zip(v1, v2):
        if cur > lat:
            pass
        elif cur < lat:
            try:
                log("Writing new version number...")
                with open(env.SYSTEM_CONFIGFILE, 'r') as cfg:
                    current_config = json.load(cfg)

                current_config["system"]["os_version"] = new_version

                with open(env.SYSTEM_CONFIGFILE, 'w') as cfg:
                    json.dump(current_config, cfg, indent=4)
                log("Reloading environment variables...")
                reload(env)

            except Exception as e:
                log("Error updating 'version' property in config.json: {}".format(e), err_id=11)
                return False
    return True


def reset_bt_devices():
    log("Resetting wireless device MAC config...")
    if overwrite_config(["devices"]):
        log("All wireless device MAC addresses have been reset to default. They will need to be re-paired")
    else:
        log("Error resetting MAC addresses, refer to previous exception", err_id=11)
        return False
    return True


def repair_config():
    log("Attemping a soft repair of the config...")
    if update_config_features():
        log("Soft repair successful")
    elif env.destructive_repairs:
        log("Soft repair unsuccessful. Attempting an authorized destructive repair...")
        if overwrite_config():
            log("Destructive repair successful. Please reboot")
        else:
            log("Destructive repair unsuccessful")
            log("SOMETHING'S FUCKED, MR. WHITE...")
            exit()
    else:
        log("Soft repair unsuccessful. Destructive repair is not authorized, exiting...")
        exit()


def main():
    if os.path.exists(env.SYSTEM_CONFIGFILE):
        update_config_features()
        update_version()
    else:
        make_default_config()
    return True


if __name__ == "__main__":
    #    overwrite_config(["preferences"])
    #    update_config_features()

    if os.path.exists(env.SYSTEM_CONFIGFILE):
        confirm = input(
            "WARNING! Do you want to overwrite your current configuration with default values? (y/N): ").lower()
        if ("y" or "yes" or "confirm") in confirm:
            log("Received manual user confirmation for overwriting config.json")
            overwrite_config()
            update_version()

        confirm = input("Reset wireless controllers? (y/N): ").lower()
        if ("y" or "yes" or "confirm") in confirm:
            log("Received manual user confirmation for resetting wireless controller config")
            reset_bt_devices()
    else:
        make_default_config()
