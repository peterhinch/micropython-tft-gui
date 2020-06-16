# tft_local.py Configuration for Pybboard TFT GUI

# This file is intended for definition of the local hardware. It's also a
# convenient place to store constants used on a project such as colors.

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2016-2020 Peter Hinch

from tft.driver.tft import LANDSCAPE
from tft.driver.touch_bytecode import TOUCH
from tft.driver.ugui import Screen, TFT_G

def setup():
    tft = TFT_G("SSD1963", "LB04301", LANDSCAPE)
    touch = TOUCH("XPT2046", True, confidence = 50, margin = 50)
    # (-3886,-0.1287,-3812,-0.132,-3797,-0.07685,-3798,-0.07681))
    tft.backlight(100) # light on: remove this line if you don't have backlight control hardware
    Screen.setup(tft, touch)
