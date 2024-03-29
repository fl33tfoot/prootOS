import subprocess
import time
import os
import hashlib
import json
import shutil
import datetime

import env
from env import log

# folder directories
ROOT = env.SYSTEM
MOUNT_POINT = env.MOUNT
DEST_POINT = env.SYSTEM_ANIM

SOURCE_POINT = env.ROOT_ANIM
BACKUP_POINT = env.ROOT_BACKUP

# animation fps
def anim_fps():
    # placeholder animation speed in ms, 17ms = about 60 fps, 100ms = 10 fps
    return 100

# mount device function
def mount_usb_device(device):
    print("USB storage device detected:")
    print(f"{device}\n")

    # create the usb mount folder if it doesn't exist
    if not os.path.exists(MOUNT_POINT):
        os.mkdir(MOUNT_POINT)

    # mount the bitch (non-sexually)
    proc_mount = subprocess.run(["mount", device, MOUNT_POINT], capture_output=True)

    if proc_mount.returncode == 0:
        print("USB storage mounted at {}".format(MOUNT_POINT))
    else:
        if not os.path.ismount(MOUNT_POINT):
            print("USB storage not mounted: ")
            print(proc_mount.stderr.decode())
            return False

    # check for the faces folder in the usb
    if not os.path.exists(SOURCE_POINT):
        print("anim folder not found. Copying current structure...")

        # run first time copy
        try:
            shutil.copytree(DEST_POINT, SOURCE_POINT, dirs_exist_ok=True)
            print("First time copy successful.")

        except:
            critical_fuckywucky(device)
        finally:
            print("Waiting 120 seconds before next copy...")
            time.sleep(120)

        return False

    # create the backup folder for first time runs
    if not os.path.exists(BACKUP_POINT):
        os.makedirs(BACKUP_POINT, exist_ok=True)
        print("anim folder detected, however 'backup' was not found. Creating...")

    return True

# first run
def create_hashes_file(device):
    # json array
    gifs = []

    # recurse thru all gifs and get file hashes and animation times
    for folder in os.listdir(SOURCE_POINT):
        discovered_path = os.path.join(SOURCE_POINT, folder)

        if os.path.isdir(discovered_path):
            # copy everything over
            shutil.copytree(os.path.join(SOURCE_POINT, folder), os.path.join(DEST_POINT, folder), dirs_exist_ok=True)

            for file in os.listdir(os.path.join(DEST_POINT, folder)):
                if file.endswith('.gif'):
                    folder_page = folder.replace('page', '')
                    file_path = os.path.join(os.path.join(DEST_POINT, folder), file)
                    md5_hash = hashlib.md5(open(file_path, 'rb').read()).hexdigest()
                    gifs.append({
                        'page': folder_page,
                        'filename': file,
                        'hash': md5_hash,
                        'anim_time': anim_fps()
            })

    # commit to json
    hashes_file = os.path.join(DEST_POINT, 'hashes.json')

    try:
        # OHHHHH JSON, TELL ME WHAT YOURE CHASIN'
        # CUS THE write() WONT EVER GIVE YOU WHAT YOU WANT
        with open(hashes_file, 'w') as f:
            json.dump(gifs, f, indent=4)

        print("Populating 'hashes.json' file...")
    except:
        critical_fuckywucky(device)

# update hashes.json with new file hashes if they've changed
def update_hashes_file():

    # load json if its there
    hashes_file = os.path.join(DEST_POINT, 'hashes.json')
    with open(hashes_file) as f:
        data = json.load(f)

    # recurse thru mounted files
    for folder in os.listdir(SOURCE_POINT):
        if os.path.isdir(os.path.join(SOURCE_POINT, folder)):
            for file in os.listdir(os.path.join(SOURCE_POINT, folder)):
                if file.endswith('.gif'):
                    face_path = os.path.join(os.path.join(SOURCE_POINT, folder), file)
                    dest_path = os.path.join(os.path.join(DEST_POINT, folder), file)
                    folder_page = folder.replace('page', '')

                    # find matching files
                    matching_file = next((gif for gif in data if (gif['page'] == folder_page and gif['filename'] == file)), None)

                    # if the face is new (exists in mounted usb anims folder but not in system anims)
                    if not os.path.exists(dest_path):
                        # copy and add hash to json
                        shutil.copy2(face_path, os.path.join(DEST_POINT, folder))
                        hash_value = hashlib.md5(open(face_path, 'rb').read()).hexdigest()
                        if matching_file:
                            matching_file['hash'] = hash_value
                        else:
                            data.append({
                                'page': folder_page,
                                'filename': file,
                                'hash': hash_value,
                                'anim_time': anim_fps()
                            })
                        print("File '{}' from folder '{}' has been copied successfully and added to the hash list.".format(file, folder))

                    # if the anim already exists
                    elif matching_file:
                        # get new hash for comparison
                        faces_folder_hash = hashlib.md5(open(face_path, 'rb').read()).hexdigest()
                        if faces_folder_hash != matching_file['hash']:
                            # hashes are different, overwrite system anim with mounted usb anim
                            shutil.copy2(face_path, os.path.join(DEST_POINT, folder))
                            # rewrite hash with new hash
                            matching_file['hash'] = faces_folder_hash
                            print("Hash for '{}' from folder '{}' has been updated".format(file, folder))
                        else:
                            print("Hashes are the same for '{}' from '{}', skipping".format(file, folder))

    with open(hashes_file, 'w') as f:
        json.dump(data, f, indent=4)

def dump_current_files():
    shutil.rmtree(DEST_POINT)

def critical_fuckywucky(device):
    try:
        with open (os.path.join((MOUNT_POINT + "/protogen"), 'SOMETHING_IS_VERY_WRONG'), 'w') as fp:
            pass
    except:
        with open (os.path.join(MOUNT_POINT, 'SOMETHING_IS_VERY_WRONG'), 'w') as fp:
            pass
    finally:
        print("SOMETHING IS VERY WRONG.")
        subprocess.run(["umount", device])

# compress anim folder for backup
def compress_and_copy():
    shutil.make_archive(os.path.join(BACKUP_POINT, 'anim_{}'.format(env.timestamp())), 'zip', DEST_POINT)

def main():
    while True:
        # check block devices for new usb connections
        lsblk_output = subprocess.check_output(["lsblk", "-o", "NAME,TRAN"], universal_newlines=True)
        lines = lsblk_output.strip().split("\n")

        if len(lines) > 1:
            device_info = lines[1].split()

            if len(device_info) >= 2:
                device_name = device_info[0]
                transport_type = device_info[1]

                # a new usb has appeared!
                if transport_type == "usb":
                    if mount_usb_device("/dev/{}1".format(device_name)):
                        hashes_file = os.path.join(DEST_POINT, 'hashes.json')

                        # check hashes.json for first time creation
                        if not os.path.exists(hashes_file):
                            print("There is a 'faces' folder but no 'hashes.json'! Is this a first time run?")
                            print("Creating 'hashes.json' file...")
                            create_hashes_file('/dev/{}1'.format(device_name))
                            print("Created a 'hashes.json' file successfully")

                            # back up all changes
                            print("Running first backup")
                            compress_and_copy()
                            print("Backed up successfully")

                        elif os.path.exists(hashes_file):
                            # back up before any changes
                            print("Backing up before any changes...")
                            compress_and_copy()
                            print("Backed up successfully")

                            # transfer new anims
                            print("Updating the file hashes")
                            #update_hashes_file()
                            dump_current_files()
                            create_hashes_file('/dev/{}1'.format(device_name))

                        # transfer complete, unmount
                        print("Transfer completed")
                        subprocess.run(["umount", "/dev/{}1".format(device_name)])
                        print("Waiting 120 seconds before next copy...")
                        time.sleep(120)
        time.sleep(2)
