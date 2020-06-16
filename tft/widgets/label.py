# label.py For TFT driver.
# Adapted for (and requires) uasyncio V3

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2016-2020 Peter Hinch

from tft.driver.ugui import NoTouch, get_stringsize, print_left
from tft.driver.constants import *

class Label(NoTouch):
    def __init__(self, location, *, font, border=None, width=None, fgcolor=None, bgcolor=None, fontcolor=None, value=None):
        if width is None:
            if value is None:
                raise ValueError('If label value unspecified, must define the width')
            width, _ = get_stringsize(value, font) 
        super().__init__(location, font, None, width, fgcolor, bgcolor, fontcolor, border, value, None)
        self.height = self.font.height()
        self.height += 2 * self.border  # Height determined by font and border

    def show(self):
        tft = self.tft
        bw = self.border
        x = self.location[0]
        y = self.location[1]
        tft.fill_rectangle(x + bw, y + bw, x + self.width - bw, y + self.height - bw, self.bgcolor)
        if self._value is not None:
            print_left(tft, x + bw, y + bw, self._value, self.fontcolor, self.font, self.width - 2 * bw)
