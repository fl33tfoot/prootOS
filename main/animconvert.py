import os
import subprocess

import env
from env import log
from upload import refresh_hashfile, write_hashfile

current_hashfile = None

def convert(gif_dir, gif_name):
    base_gif = gif_dir + '/' + gif_name

    lib_convert = subprocess.run([env.LIV_PATH,
                                  "--led-no-drop-privs",
                                  "--led-brightness={}".format(env.MATRIX_BRIGHTNESS),
                                  "--led-slowdown-gpio={}".format(env.MATRIX_GPIO_SLOWDOWN),
                                  "--led-cols={}".format(env.MATRIX_COLS),
                                  "--led-rows={}".format(env.MATRIX_ROWS),
                                  "--led-gpio-mapping={}".format(env.MATRIX_TYPE),
                                  "--led-chain={}".format(env.MATRIX_DAISY_CHAIN),
                                  "--led-limit-refresh={}".format(env.MATRIX_REFRESH_RATE_LIMIT),
                                  "-D{}".format(1000 // env.MATRIX_FPS),
                                  "{}".format(base_gif + ".gif"),
                                  "-O{}".format(base_gif + env.STREAMFILE_EXTENSION)], capture_output=True)

    try:
        if lib_convert.returncode != 0:
            raise Exception
    except Exception as e:
        log("Error while converting '{}': {}".format(gif_name, e), err_id=109)
        log("RAW STDOUT: {}".format(lib_convert.stdout.decode()), err_id=109)
        return False

    return True


def main():
    global current_hashfile

    current_hashfile = refresh_hashfile(True)
    count = 0
    converted = current_hashfile

    # for every page in the current hashfile
    # multiple pages on basic archetypes, only one page on advanced
    for page_key, page_value in converted.items():
        # for every animation in the page
        for anim_key, anim_values in page_value.items():
            # if the animation's converted value is false
            try:
                if not anim_values.get('converted'):
                    base_path = os.path.dirname(anim_values.get('filepath'))
                    file = os.path.splitext(os.path.basename(anim_values.get('filepath')))[0]

                    if convert(base_path, file):
                        anim_values['converted'] = True
                        anim_values['streamfile'] = base_path + '/' + file + env.STREAMFILE_EXTENSION
                        log("Converted '{}' successfully".format(file + env.STREAMFILE_EXTENSION))
                        count += 1
                    else:
                        log("Skipping...", err_id=109)
                        continue
                # ignore if the file already has the converted flag toggled
                else:
                    continue
            except AttributeError:
                continue

    log("Converted {} files successfully".format(count))
    log("Writing changes to hashes.json...")
    return write_hashfile(converted)


if __name__ == "__main__":
    main()
