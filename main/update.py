import time
import subprocess
import os
import shutil
import zipfile
import socket

import env
from env import log

# current user
user = env.user
current_version = str(env.version)
latest_version = current_version


# folder directories
SYSTEM = env.SYSTEM
MOUNT = env.MOUNT
ROOT = env.ROOT

# unmount device function
def unmount(device):
    try:
        log("Unmounting {}...".format(device))
        subprocess.run(["umount", device])
    except:
        log("Unmount failed", err_id=11)
        raise Exception

    log("Unmounted successfully")

# mount device function
def mount(device):
    # mount the bitch (non-sexually)
    log("Mounting {}...".format(device))
    proc_mount = subprocess.run(["mount", device, MOUNT], capture_output=True)

    if not proc_mount.returncode == 0:
        log("Mount failure: {}".format(proc_mount.stderr.decode()), err_id=11)
        raise Exception

    log("Mounted successfully")

# extract and update
def update():
    # check if the folder hierarchy even exists
    if not os.path.exists(ROOT):
        os.makedirs(ROOT, exist_ok=True)
        log("File structure not formatted, reboot and try again.", err_id=100)
        raise Exception

    # now check if the update zip exists
    update_file = os.path.join(ROOT, 'update.zip')
    if os.path.exists(update_file):
        try:
            with zipfile.ZipFile(update_file, 'r') as zip:
                zip.extractall(SYSTEM)
        except Exception as e:
            log("Extraction failed: {}".format(e), err_id=11)
            raise Exception
    else:
        log("Update file not found. Was it moved or renamed?", err_id=101)
        raise Exception

    log("Update completed successfully! Removing update.zip...")
    os.remove(update_file)

def check_internet():
    socket.setdefaulttimeout(1)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect(("8.8.8.8", 53))
        s.connect(("1.1.1.1", 53))
        return True
    except:
        return False

# check version
def up_to_date():
    global current_version, latest_version

    log("Current version is {}".format(current_version))

    try:
        # open socket to get latest version online
        pass
    except Exception as e:
        log("Error retrieving version: {}".format(e), err_id=13)
        return False

    latest_version = str(1.6)

    v1 = list(map(int, current_version.split(".")))
    v2 = list(map(int, latest_version.split(".")))

    while len(v1) < len(v2):
        v1.append(0)
    while len(v2) < len(v1):
        v2.append(0)

    for cur, lat in zip(v1, v2):
        if cur > lat:
            log("Latest version is {}, no updates available".format(latest_version))
            return False
        elif cur < lat:
            log("Latest version is {}, update available!".format(latest_version))
            return True

    log("You're up to date!".format(latest_version))
    return False

# online update check
def update_online():

    return False

# search usb function
def main():
    # check block devices for new usb connections
    lsblk_output = subprocess.check_output(["lsblk", "-o", "NAME,TRAN"], universal_newlines=True)
    lines = lsblk_output.strip().split("\n")

    if len(lines) > 1:
        dev = lines[1].split()
        # dev[0] is the device name
        # dev[1] is the transport type

        # check to make sure the device isnt a goofy ah ah imposter
        if ((len(dev) >= 2) and (dev[1] == "usb")):
            # a new usb has appeared!
            if dev[1] == "usb":
                usb = "/dev/{}1".format(dev[0])
                log("A new usb has appeared! ({})".format(usb))

                try:
                    mount(usb)
                    update()
                except:
                    log("Update failed")
                finally:
                    # transfer complete, unmount
                    unmount(usb)
                    return True
    log("No USB detected, checking internet connection...")

    if check_internet():
        log("Internet is accessible! Checking for updates")
        up_to_date()
    else:
        log("No internet, skipping update check")
    return False

if __name__ == "__main__":
    main()
