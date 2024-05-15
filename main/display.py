import json
import os
import subprocess
import signal

import env
from env import log
from upload import refresh_hashfile

override = False
displaying = False
current_anim = ""

basic_page = env.BASIC_ANIMS_PAGE
anims = refresh_hashfile(True)

# set the base cmd options
base_cmd = " ".join([env.LIV_PATH,
               "--led-no-drop-privs",
               "--led-brightness={}".format(env.MATRIX_BRIGHTNESS),
               "--led-slowdown-gpio={}".format(env.MATRIX_GPIO_SLOWDOWN),
               "--led-cols={}".format(env.MATRIX_COLS),
               "--led-rows={}".format(env.MATRIX_ROWS),
               "--led-gpio-mapping={}".format(env.MATRIX_TYPE),
               "--led-chain={}".format(env.MATRIX_DAISY_CHAIN),
               "--led-limit-refresh={}".format(env.MATRIX_REFRESH_RATE_LIMIT)
           ])

# play animations from streamfile
def show(index, loops=0, time=0):
    global displaying, override, current_anim

    if env.archetype == "basic":
        # if the folder or animation file at the index doesnt exist, skip it
        if (anims.get(str(index[0])) is None) or (anims[str(index[0])].get(basic_page[index[1]]) is None):
            log("Animation at {} doesn't exist! Skipping...".format(index))
            return True

        # otherwise the new anim path is here
        new_anim = anims[str(index[0])][basic_page[index[1]]]

    elif env.archetype == "advanced":
        # this should never happen because the buttons on the gui are created
        # dynamically upon every refresh, but just in case....
        if not os.path.exists(index['streamfile']):
            log("Animation at {} doesn't exist! Skipping...".format(index["streamfile"]), err_id=110)
            return True

        # here's the streamfile info, all nice and easy
        new_anim = index

    # if the animation is the same as the current one, do nothing
    if current_anim == new_anim:
        return True

    current_anim = new_anim
    streamfile_path = current_anim.get('streamfile') if env.archetype == "basic" else index['streamfile']

    if not override:

        if displaying:
            if kill():
                displaying = False

        # set the animation base framerate
        args = "-D{}".format((current_anim.get('fps') if env.archetype == "basic" else index['fps']))

        if (loops == 0) and (time == 0):
            args = args + " --led-daemon"
        else:
            if loops > 0:
                args = args + "-l{} ".format(loops)

            if time > 0:
                args = args + "-t{}".format(time)
#            args = ("-l{} ".format(loops) if loops <= 0 else "") + ("-t{}".format(time if time <= 0 else ""))

        log(" ".join([base_cmd, args, streamfile_path]))

        try:
            if not displaying:
                lib_show = subprocess.Popen(" ".join([base_cmd, args, streamfile_path]), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                if lib_show.returncode is not None:
                    raise Exception("Error with subprocess.Popen: [ERRNO] {} [STDERR] {}".format(lib_show.returncode, lib_show.stderr.decode("utf-8")))

                displaying = True
            else:
                raise Exception("Attempted new animation while another was playing")

        except Exception as e:
            log("Error while trying to display animation '{}': {}".format(os.path.basename(streamfile_path), e), err_id=11)
            return False

        return True


# kill animations
def kill():
    global displaying

    if displaying:
        try:
            pids_raw = subprocess.check_output(["pidof", "led-image-viewer"]).strip()
            pids = pids_raw.decode().split()
#            log("Process IDs: {}".format(pids))

            for pid in pids:
#                log("Killing PID {}...".format(pid))
                os.kill(int(pid), signal.SIGKILL)


        except Exception as e:
            log("Unable to kill the active animation: {}".format(e), err_id=11)
            return False
    else:
        log("Not displaying any animations!")

    return True

# display important system animations
def show_system(anim_id, loops=0, time=0):
    global displaying, override

    override = True

    if displaying:
        kill()

    if (loops == 0) and (time == 0):
        args = "--led-daemon"
    else:
        args = ("-l{} ".format(loops) if loops <= 0 else "") + ("-t{}".format(time if time <= 0 else ""))

    sys_anim_path = env.RUNTIME_ANIMS_DIR + "/" + env.RUNTIME_ANIMS[anim_id]

    try:
        subprocess.run("{} {} {}".format(env.LIV_PATH, args, sys_anim_path), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        displaying = True
    except Exception as e:
        log("Error while trying to display system animation '{}': {}".format(env.RUNTIME_ANIMS[anim_id], e), err_id=11)
        return False


# display text
def show_text(msg, time=None):
    global displaying, override
    pass


# future menu integration
def show_menu():
    global displaying, override
    pass

def show_boot():

    pass

def get_status():
    return [current_anim, override, displaying]

def main():
    if not os.path.exists(env.RUNTIME_ANIMS_DIR):
        os.makedirs(env.RUNTIME_ANIMS_DIR, exist_ok=True)

    pass


if __name__ == "__main__":
    main()
