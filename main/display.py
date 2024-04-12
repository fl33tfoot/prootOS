import os
import subprocess

import env
from env import log

override = False
displaying = False

# play animations from streamfile
def show(streamfile_path, loops=0, time=0):
    global displaying, override

    lib_show = subprocess.run([env.LIV_PATH,
                               "--led-no-drop-privs",
                               "--led-brightness={}".format(env.MATRIX_BRIGHTNESS),
                               "--led-slowdown-gpio={}".format(env.MATRIX_GPIO_SLOWDOWN),
                               "--led-cols={}".format(env.MATRIX_COLS),
                               "--led-rows={}".format(env.MATRIX_ROWS),
                               "--led-gpio-mapping={}".format(env.MATRIX_TYPE),
                               "--led-chain={}".format(env.MATRIX_DAISY_CHAIN),
                               "--led-limit-refresh={}".format(env.MATRIX_REFRESH_RATE_LIMIT),
                               "-D{}".format(1000 // env.MATRIX_FPS),
                               "{}".format(base_gif + ".gif")], capture_output=True)

    if not override:
        if displaying:
            kill()

        if (loops == 0) and (time == 0):
            args = "--led-daemon"
        else:
            args = ("-l{} ".format(loops) if loops <= 0 else "") + ("-t{}".format(time if time <= 0 else ""))

        try:
            subprocess.run("{} {} {}".format(env.LIV_PATH, args, streamfile_path), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            displaying = True
        except Exception as e:
            log("Error while trying to display animation '{}': {}".format(os.path.basename(streamfile_path), e), err_id=11)
            return False

        return True


# kill animations
def kill():
    global displaying

    if displaying:
        try:
            subprocess.run('pgrep -f led-image-viewe | sudo xargs kill -s SIGINT', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            displaying = False
        except Exception as e:
            log("Unable to kill the active animation: {}".format(e), err_id=11)
            return False
    else:
        log("Not displaying any animations!")

    return True

# display important system animations
def show_system(anim_id, async, loops=0, time=0):
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

def main():
    if not os.path.exists(env.RUNTIME_ANIMS_DIR):
        os.makedirs(env.RUNTIME_ANIMS_DIR, exist_ok=True)


    pass


if __name__ == "__main__":
    main()
