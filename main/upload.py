import subprocess
import time
import os
import hashlib
import json
import shutil
import zipfile
import pdb 

import env
from env import log

# the joystick directions/animations to have per "page" on basic configurations
#basic_page = ["default", "top", "top_right", "right", "bot_right", "bot", "bot_left", "left", "top_left"]
basic_page = env.BASIC_ANIMS_PAGE

# the file schema and data to store per animation
file_schema = {
    "filepath": "",
    "filehash": "",
    "streamfile": "",
    "fps": env.get_anim_default_fps(),
    "converted": False,
    "bindings": {
        "audio": "",
        "scripts": ""
    }
}

# buffer hashfile variable
current_hashfile = {}

# list of validated .gif files to make my life easier
valid_gifs = []

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
    proc_mount = subprocess.run(["mount", device, env.MOUNT], capture_output=True)

    if not proc_mount.returncode == 0:
        log("Mount failure: {}".format(proc_mount.stderr.decode()), err_id=11)
        return False

    log("Mounted successfully")
    return True


def get_md5(file_path):
    # Open the file in binary mode
    with open(file_path, 'rb') as file:
        md5_hash = hashlib.md5()

        # compensate for large ah ah gifs since most people arent gonna be smart enough to
        # upload gifs with alpha channels, maybe i should add a method for this in the future?
        for chunk in iter(lambda: file.read(4096), b''):
            md5_hash.update(chunk)

    return md5_hash.hexdigest()


def refresh_hashfile(ext_caller=False):
    global current_hashfile

    try:
        with open(env.SYSTEM_HASHFILE, 'r') as cfg:
            if ext_caller:
                return json.load(cfg)
            else:
                current_hashfile = json.load(cfg)
            log("Hashfile configuration loaded successfully")
            return True
    except Exception as e:
        log("Unable to open hashes.json: {}".format(e), err_id=106)
    return False


def write_hashfile(data):
    if not os.path.exists(env.SYSTEM_HASHFILE):
        log("*gasp* there's no hashes.json! Is this your first time {}-chan?".format(env.protogen))

    try:
        # OHHHHH JSON, TELL ME WHAT YOURE CHASIN'
        # CUS THE write() WONT EVER GIVE YOU WHAT YOU WANT
        log("Updating hashes.json...")

        with open(env.SYSTEM_HASHFILE, 'w') as hf:
            json.dump(data, hf, indent=4)

        return True

    except Exception as e:
        log("Error writing hashfile: {}".format(e), err_id=14)
        return False


# checks to make sure the archetype of the hashfile matches the configuration
def check_hashfile_type(archetype=env.archetype):
    global current_hashfile

    if refresh_hashfile():
        if current_hashfile['0']['hashfile_archetype'] == archetype:
            return True
    return False


# double checks to make sure folders actually exist and arent empty
def check_file_validity(path=env.ROOT_ANIM):
    global valid_gifs

    # reset this every time
    valid_gifs = []

    directories = [entry for entry in os.listdir(path) if os.path.isdir(os.path.join(path, entry))]
    for folder in directories:
        if not os.listdir(path + "/" + folder):
            log("Folder '{}' is empty, skipping...".format(folder), err_id=105)
            continue
        else:
            gif_files = [file for file in os.listdir(path + "/" + folder) if file.endswith('.gif')]

            if not gif_files:
                log("Folder '{}' contains no .gif files, skipping...".format(folder), err_id=105)
                continue
            else:
                for gif in gif_files:
                    # for basic archetypes, the file structure has to be in digits in order for the
                    # pages to properly populate on controllers, this loop checks that

                    # if the gif name isnt boot.gif
                    if (env.archetype == 'basic') and (gif != 'boot.gif'):
                        # or if the name isnt 0-8.gif
                        if (not gif[:-4].isdigit()) or (int(gif[:-4]) not in range(9)):
                            log("Invalid filename: '{}' in '{}'! Basic architecture filenames must be single digits between 0-8 and ending in .gif! Skipping...".format(gif, path), err_id=104)
                            continue

                    # otherwise we are gucci for advanced archetypes
                    valid_gifs.append("{}/{}/{}".format(path, folder, gif))

    if len(valid_gifs) <= 0:
        log("No valid .gif files found in {}!".format(path), err_id=105)
        return False

    valid_gifs.sort()
    log("{} valid gifs found in {}".format(len(valid_gifs), path))
    return True

# hashfile creation
def update_hashes():
    global current_hashfile
    global valid_gifs

    new = 0
    removed = 0
    updated = 0
    unchanged = 0

    usb_hashes = {}

    log("Populating hashes.json...")

    usb_hashes['0'] = {
        'hashfile_archetype': env.archetype
    }

    if os.path.exists(env.SYSTEM_HASHFILE):
        refresh_hashfile()

    for file_path in valid_gifs:
        # file name w extension
        file = os.path.basename(file_path)
        # file name w/o extension
        anim_name = os.path.splitext(file)[0]
        # destination folder path akin to usb path
        dest_path = os.path.join(env.SYSTEM_ANIM, os.path.dirname(file_path).split('/')[-1])
        # default folder page for adv archetypes
        folder_page = '1'

        if env.archetype == 'basic':
            # toss out any invalid folder names and make the user cry about it
            try:
                folder_page = os.path.dirname(file_path).split('/')[-1].lower().replace('page', '').replace(' ', '')
            except ValueError:
                folder_page = '0'

        # set a few dict variables here for simplicity
        dict_page = ('0' if file == "boot.gif" else folder_page if env.archetype == 'basic' else '1')
        dict_key = ('boot_anim' if file == "boot.gif" else basic_page[int(anim_name)] if env.archetype == 'basic' else anim_name)

        new_hash = get_md5(file_path)

        # make the folder page hash if it doesnt exist
        if not usb_hashes.get(folder_page):
            usb_hashes[folder_page] = {}

        # add entry into the hashes list
        usb_hashes[dict_page][dict_key] = {
            'filepath': os.path.join(dest_path, file),
            'filehash': new_hash,
            'streamfile': '',
            'fps': env.get_anim_default_fps(),
            'converted': False,
            'bindings': {
                'audio': '',
                'scripts': ''
            }
        }

        if os.path.exists(env.SYSTEM_HASHFILE):
            try:
                old_entry = current_hashfile.get(dict_page).get(dict_key)
                old_hash = old_entry.get('filehash', None)

                # file is unchanged
                if old_hash == new_hash:
                    # update the new json with the old values and don't copy anything over
                    usb_hashes[dict_page][dict_key]['streamfile'] = old_entry.get('streamfile', '')
                    usb_hashes[dict_page][dict_key]['converted'] = True if not old_entry.get('streamfile', '') == '' else False

                    unchanged += 1
                    continue

                # else if file doesn't exist
                elif old_hash == None:
                    log("Discovered new animation '{}'!".format(file))

                    new += 1

                # file is changed
                elif old_hash != new_hash:
                    log("Updating previous animation '{}'...".format(file))

                    # remove old files
                    if os.path.exists(old_entry.get('streamfile')):
                        os.remove(old_entry.get('streamfile'))

                    updated += 1

            except AttributeError as e:
                log("Discovered new animation '{}'!".format(file))

                new += 1
            except Exception as e:
                log("Error cross referencing '{}' in hashfile: {}".format(file, e), err_id=14)
                continue

        # create the destination folder path if it doesn't exist and copy the file over
        if not os.path.exists(dest_path):
            shutil.copytree(os.path.dirname(file_path), dest_path, dirs_exist_ok=True)

        if not file_path == os.path.join(dest_path, file):
            shutil.copy(file_path, os.path.join(dest_path, file))

    if os.path.exists(env.SYSTEM_HASHFILE):
        log("Completed animation file cross referencing. Cleaning up old files...")

        # for every page in the current hashfile
        # multiple pages on basic archetypes, only one page on advanced
        for page_key, page_value in current_hashfile.items():
            # for every animation in the page
            for anim_key, anim_values in page_value.items():
                try:
                    if anim_values.get('filepath').replace(env.SYSTEM, env.ROOT) not in valid_gifs:
                        old_filepath = anim_values.get('filepath')
                        old_streamfile = anim_values.get('streamfile')

                        try:
                            log("File '{}' no longer exists! Removing...".format(old_filepath))
                            if os.path.exists(old_filepath):
                                os.remove(old_filepath)

                            if os.path.exists(old_streamfile):
                                os.remove(old_streamfile)

                            removed += 1
                        except Exception as f:
                            log("Error while removing file '{}': {}...".format(old_filepath, f), err_id=108)
                            continue

                except AttributeError as e:
                    continue
                except Exception as e:
                    log("Error parsing gif filepath while cleaning: {}".format(e), err_id=14)
                    continue

    log("Finished animation hash check: {} new, {} updated, {} removed, {} unchanged".format(new, updated, removed, unchanged))
    return write_hashfile(usb_hashes)


# backup animations
def backup():
    log("Backup started! YIPPPEEEEEEEEEE")

    try:
        shutil.make_archive(os.path.join(env.ROOT_BACKUP, "anim_{}".format(env.timestamp())), "zip", env.SYSTEM_ANIM)
        log("Backup successful")

        try:
            shutil.copy(env.SYSTEM_CONFIGFILE, env.ROOT_MAIN)
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

            # check to make sure the device isnt a goofy ah ah imposter (if the partition's dev folder is valid)
            if (len(dev) >= 2) and (dev[1] == "usb"):
                # a new usb has appeared!
                usb = "/dev/{}1".format(dev[0])
                log("A new usb has appeared! ({})".format(usb))

                # check if the mount is successful
                if mount(usb):

                    # first time filesystem path creation, copy current file tree over
                    if not os.path.exists(env.ROOT_ANIM):
                        log("First time this USB is being used, copying current system filestructure...")
                        try:
                            shutil.copytree(env.SYSTEM_ANIM, env.ROOT_ANIM, dirs_exist_ok=True)
                            log("First time copy successful")
                        except Exception as e:
                            log("Error creating file tree on mount resource: {}".format(e), err_id=14)

                    # update hashfile normally if it already exists
                    else:
                        if refresh_hashfile():
                            if len(str(current_hashfile)) <= 15:
                                os.remove(env.SYSTEM_HASHFILE)
                                log("Hashfile empty, recreating...")

                        # lets update it normally if the file isnt empty
                        try:
                            # backup before any changes
                            backup()

                            if not os.path.exists(env.SYSTEM_HASHFILE):
                                check_file_validity(env.SYSTEM_ANIM)
                                update_hashes()
                            # make sure that the hashfile doesnt overwrite between
                            # the basic and advanced archetype schemas
                            elif check_hashfile_type():
                                check_file_validity()
                                update_hashes()

                            else:
                                raise Exception("Hashfile has a different archetype. Was this modified manually? Or has hardware changed?")

                        except Exception as e:
                            log("{}".format(e), err_id=103)

                    # transfer complete
                    unmount(usb)
                    log("Automatic USB detection deferred for 120 seconds")
                    time.sleep(120)
                    log("Automatic USB detection active")
                else:
                    # mount fails
                    log("Continuing as usual...")
        time.sleep(2)


if __name__ == "__main__":
#    pdb.set_trace()
    main()
