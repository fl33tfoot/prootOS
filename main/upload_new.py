import subprocess
import time
import os
import hashlib
import json
import shutil
import datetime

import env
from env import log

# the joystick directions/animations to have per "page" on basic configurations
basic_page = ["default", "top", "top_right", "right", "bot_right", "bot", "bot_left", "left", "top_left"]

# the file schema and data to store per animation
file_schema = {
     "filename": "",
     "filehash": "",
     "streamfile": "",
     "fps": env.get_anim_default_fps(),
     "converted": False
}

# buffer hashfile variable
hashfile = None

# unmount device function
def unmount(device):
    try:
        log("Unmounting {}...".format(device))
        subprocess.run(["umount", device])
    except Exception as e:
        log("Unmount failed: {}".format(e), err_id=11)
        return False

    log("Unmounted successfully")
    return True

# mount device function
def mount(device):
    # mount the bitch (non-sexually)
    log("Mounting {}...".format(device))
    proc_mount = subprocess.run(["mount", device, MOUNT], capture_output=True)

    if not proc_mount.returncode == 0:
        log("Mount failure: {}".format(proc_mount.stderr.decode()), err_id=11)
        return False

    log("Mounted successfully")
    return True

# checks to make sure the archetype of the hashfile matches the configuration
def check_hashfile_type(archetype=env.archetype):
    pass

# double checks to make sure folders actually exist and arent empty
def check_file_validity():
    pass

# updates the hashfile with any changes
def update_hashes():
    pass

# initial hashfile creation
def create_hashes():
    # json array
    gifs = []


    log("Populating hashes.json...")
    for folder in os.listdir(env.SYSTEM_ANIM):
        discovered_path = os.path.join(env.SYSTEM_ANIM, folder)

        if os.path.isdir(discovered_path):

            for file in os.listdir(os.path.join(env.SYSTEM_ANIM, folder)):
                if file.endswith('.gif')
                    folder_page = folder.replace('page', '')
                    file_path = os.path.join(os.path.join(env.SYSTEM_ANIM, folder), file)
                    md5_hash = hashlib.md5(open(file_path, 'rb').read()).hexdigest()

                    anim_direction = file.replace('.gif', '')

                    gifs['folder_page'][basic_page[anim_direction]].append({
                        'filename': file,
                        'filehash': md5_hash,
                        'fps': env.get_anim_default_fps(),
                        'converted': False
                    })
                    log("Discovered animation '{}' for the first time!".format(file))

    try:
        # OHHHHH JSON, TELL ME WHAT YOURE CHASIN'
        # CUS THE write() WONT EVER GIVE YOU WHAT YOU WANT
        log("Writing hashes.json...")

        with open(env.SYSTEM_HASHFILE, 'w') as f:
            json.dump(gifs, f, indent=4)
    except:
        check_file_validity()

    pass

# backup animations
def backup():
    log("Backup started! YIPPPEEEEEEEEEE")
    try:
        shutil.make_archive(os.path.join(env.ROOT_BACKUP, "anim_{}".format(env.timestamp())), "zip", env.SYSTEM_ANIM)
        log("Backup successful")

        try:
            shutil.copy(env.SYSTEM_CONFIGFILE,env.ROOT_MAIN)
            log("Config backup successful")
        except Exception as e:
            raise Exception("Config backup unsuccessful: {}".format(e))

    except Exception as e:
        log("Backup failed: {}".format(e), err_id=14)
        return False
    return True


def main():
    while True:
        # check block devices for new usb connections
        lsblk_output = subprocess.check_output(["lsblk", "-o", "NAME,TRAN"], universal_newlines=True)
        lines = lsblk_output.strip().split("\n")

        # if the device has a partition
        # technically the partitions on the storage device but who cares lol this is a hacky usb storage discovery method
        if len(lines) > 1:
            dev = lines[1].split()
            # dev[0] is the device name
            # dev[1] is the transport type

            # check to make sure the device isnt a goofy ah ah imposter (if the partion's dev folder is valid)
            if ((len(dev) >= 2) and (dev[1] == "usb")):
                # a new usb has appeared!
                usb = "/dev/{}1".format(dev[0])
                log("A new usb has appeared! ({})".format(usb))

                # check if the mount is successful
                if mount(usb):
#                    if not os.path.exists(env.SYSTEM_ANIM):
#                        os.makedirs(env.SYSTEM_ANIM, exist_ok=True)

                    # first time filesystem path creation, copy current file tree over
                    if not os.path.exists(env.ROOT_ANIM)
                        log("First time this USB is being used, copying current system filestructure...")
                        try:
                            create_hashes(usb)
                            shutil.copytree(env.SYSTEM_ANIM, env.ROOT_ANIM, dirs_exist_ok=True)
                            log("First time copy successful")
                        except Exception as e:
                            log("Error creating file tree on mount resource: {}".format(e), err_id=14)
                    
                    
                    


                    # first time hash creation
                    if not os.path.exists(env.SYSTEM_HASHFILE):
                        log("*gasp* there's no hashes.json! Is this your first time {}-chan?".format(env.protogen))

                        try:
                            log("Creating hashes.json...")

                            os.makedirs(env.SYSTEM_HASHFILE, exist_ok=True)
                            os.makedirs(env.SYSTEM_CONFIGFILE, exist_ok=True)
                            create_hashes(usb)

                            log("Created hashes.json and populated it with the current files")
                            backup()

                        except Exception as e:
                            log("Unable to create hashes.json: {}".format(e),err_id=14)

                    # update hashfile normally if it already exists
                    else:
                        try:
                            # backup before any changes
                            backup()

                            # make sure that the hashfile doesnt overwrite between the basic and advanced archetype schemas
                            if check_hashfile_type():
                                update_hashes(usb)
                            else:
                                raise Exception("Hashfile has a different archetype. Was this modified manually? Or has hardware changed?")

                        except Exception as e:
                            log("{}".format(e), err_id=103)

                    # transfer complete
                    unmount(usb)
                    log("USB detection deferred for 120 seconds")
                    time.sleep(120)
                    log("Automatic USB detection active")
                else:
                    # mount fails
                    log("Continuing as usual...")
        time.sleep(2)



if __name__ == "__main__":
    main()
