import subprocess
import time
import os
import hashlib
import json
import shutil

import env
from env import log

# the joystick directions/animations to have per "page" on basic configurations
basic_page = ["default", "top", "top_right", "right", "bot_right", "bot", "bot_left", "left", "top_left"]

# the file schema and data to store per animation
file_schema = {
    "filepath": "",
    "filehash": "",
    "streamfile": "",
    "fps": env.get_anim_default_fps(),
    "converted": False
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
def check_file_validity(path=env.SYSTEM_ANIM):
    global valid_gifs

    # reset this every time
    valid_gifs = []

    for folder in os.listdir(path):
        if not os.listdir(folder):
            log("Folder '{}' is empty, skipping...".format(folder), err_id=105)
            continue
        else:
            gif_files = [file for file in os.listdir(folder) if file.endswith('.gif')]

            if not gif_files:
                log("Folder '{}' contains no .gif files, skipping...".format(folder), err_id=105)
                continue
            else:
                for gif in gif_files:
                    # for basic archetypes, the file structure has to be in digits in order for the
                    # pages to properly populate on controllers, this loop checks that
                    if (not gif[:-4].isdigit()) or (int(gif[:-4]) not in range(9)) and env.archetype == 'basic':
                        log("Invalid filename: '{}' in '{}'! Basic architecture filenames must be single digits between 0-8 and ending in .gif! Skipping...".format(
                            gif, path), err_id=104)
                    else:
                        # otherwise we are gucci for advanced archetypes
                        valid_gifs.append("{}/{}".format(path, gif))

    if len(valid_gifs) <= 0:
        log("No valid .gif files found in {}!".format(path), err_id=105)
        return False

    log("{} valid gifs found in {}".format(valid_gifs, path))
    return True


# updates the hashfile with any changes
def update_hashes():
    global current_hashfile
    global valid_gifs

    if not refresh_hashfile():
        return False

    updated_hashfile = current_hashfile

    # nasty ass 3d dict parsing below

    # for every page in the current hashfile
    # multiple pages on basic archetypes, only one page on advanced
    for page_key, page_value in updated_hashfile.items():
        # for every animation in the page
        for anim_key, anim_values in page_value.items():
            # if the animation's filepath is in the valid gifs from before
            if anim_values.get('filepath') in valid_gifs:
                # compare the md5 of the valid gifs retrieved from the mount path with the md5 of the current gif on the system
                potential_replacement = valid_gifs[valid_gifs.index(anim_values.get('filepath'))]

                if get_md5(potential_replacement) == anim_values.get('filehash'):
                    # skip if its the same
                    continue
                # else we need to overwrite it and update the json with the new hash
                # also set it to unconverted since it needs a new streamfile made
                else:
                    log("Updating hash for {}...".format(anim_values.get('filepath')))

                    try:
                        if os.path.exists(anim_values.get('streamfile')):
                            os.remove(anim_values.get('streamfile'))

                        shutil.copyfile(potential_replacement, anim_values.get('filepath'))
                        anim_values['filehash'] = get_md5(potential_replacement)
                        anim_values['converted'] = False
                    except Exception as e:
                        log("Error while updating hash for '{}': {}...".format(anim_values.get('filepath'), e),
                            err_id=107)

                    #
            # else if it's not in the valid gifs list, that means it was probably removed, as such we can delete the entry and the associated files
            else:
                # remove the file and keys
                try:
                    log("File '{}' no longer exists! Removing...".format(anim_values.get('filepath')))

                    if os.path.exists(anim_values.get('filepath')):
                        os.remove(anim_values.get('filepath'))

                    if os.path.exists(anim_values.get('streamfile')):
                        os.remove(anim_values.get('streamfile'))

                    del updated_hashfile[page_key][anim_key]
                except Exception as e:
                    log("Error while removing file '{}': {}...".format(anim_values.get('filepath'), e), err_id=108)

    return write_hashfile(updated_hashfile)


# initial hashfile creation
def create_hashes():
    global valid_gifs

    new_hashes = {}

    log("Populating hashes.json...")
    new_hashes['0'] = {
        'hashfile_archetype': env.archetype,
        'boot_anim': {
            'filepath': '',
            'filehash': '',
            'streamfile': '',
            'fps': env.get_anim_default_fps(),
            'converted': False
        }
    }

    # basic archetype schema sorting
    if env.archetype == 'basic':
        for file_path in valid_gifs:
            file = os.path.basename(file_path)

            # toss out any invalid folder names and make the user cry about it
            try:
                folder_page = int(
                    os.path.dirname(os.path.dirname(file_path)).lower().replace('page', '').replace(' ', ''))
            except ValueError:
                folder_page = 0

            # direction for basic controllers
            anim_direction = os.path.splitext(file)[0]

            # ignore 0 because im using it to store shit, and also so the index starts at 1
            if folder_page == 0:
                if file == "boot.gif":
                    new_hashes['0']['boot_anim'] = {
                        'filepath': file_path,
                        'filehash': get_md5(file_path),
                        'streamfile': '',
                        'fps': env.get_anim_default_fps(),
                        'converted': False
                    }
                else:
                    log("Skipping {} because the folder page isn't valid".format(file_path), err_id=104)
                    continue
            else:
                new_hashes[str(folder_page)][basic_page[anim_direction]] = {
                    'filepath': file_path,
                    'filehash': get_md5(file_path),
                    'streamfile': '',
                    'fps': env.get_anim_default_fps(),
                    'converted': False
                }

                log("Discovered animation '{}' for the first time!".format(file))

    # advanced archetype schema sorting
    elif env.archetype == 'advanced':
        for file_path in valid_gifs:
            file = os.path.basename(file_path)
            anim_name = os.path.splitext(file)[0]

            new_hashes['1'][anim_name] = {
                'filepath': file_path,
                'filehash': get_md5(file_path),
                'streamfile': '',
                'fps': env.get_anim_default_fps(),
                'converted': False
            }

    return write_hashfile(new_hashes)


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

                    # first time hash creation
                    if not os.path.exists(env.SYSTEM_HASHFILE):
                        log("*gasp* there's no hashes.json! Is this your first time {}-chan?".format(env.protogen))

                        try:
                            log("Creating hashes.json...")

                            os.makedirs(env.SYSTEM_HASHFILE, exist_ok=True)
                            check_file_validity()
                            create_hashes()

                            log("Created hashes.json and populated it with the current files")
                            backup()

                        except Exception as e:
                            log("Unable to create hashes.json: {}".format(e), err_id=14)

                    # update hashfile normally if it already exists
                    else:
                        try:
                            # backup before any changes
                            backup()

                            # make sure that the hashfile doesnt overwrite between the basic and advanced archetype
                            # schemas
                            if check_hashfile_type():
                                check_file_validity(env.ROOT_ANIM)
                                update_hashes()
                            else:
                                raise Exception(
                                    "Hashfile has a different archetype. Was this modified manually? Or has hardware changed?")

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
    main()
