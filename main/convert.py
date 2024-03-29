import os
import time
import json
from rgbmatrix import RGBMatrix, RGBMatrixOptions

# current user
user = (subprocess.run(["grep", "1000", "/etc/passwd"], capture_output=True)).stdout.decode().split(":")[0]

# folder directories
SYSTEM = "/home/{}/protogen".format(user)
MOUNT = SYSTEM + "/usb"
ROOT = MOUNT + "/protogen"

# matrix options
options = RGBMatrixOptions()
options.hardware_mapping = 'adafruit-hat'
options.rows = 32
options.cols = 64
options.chain_length = 2
#options.pixel_mapper_config = "Rotate:180"
options.show_refresh_rate = 0
#options.gpio_slowdown = 3
options.brightness = 75
#options.disable_hardware_pulsing = 1Q
matrix = RGBMatrix(options=options)
