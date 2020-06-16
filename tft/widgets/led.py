# led.py For TFT driver.
# Adapted for (and requires) uasyncio V3

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2016-2020 Peter Hinch

from tft.driver.ugui import NoTouch
from tft.driver.constants import *

class LED(NoTouch):
    def __init__(self, location, *, border=None, height=30, fgcolor=None, bgcolor=None, color=RED):
        super().__init__(location, None, height, height, fgcolor, bgcolor, None, border, False, False)
        self._value = False
        self._color = color
        self.radius = (self.height - 2 * self.border) / 2
        self.x = location[0] + self.radius + self.border
        self.y = location[1] + self.radius + self.border

    def show(self):
        tft = self.tft
        color = self._color if self._value else BLACK
        tft.fill_circle(int(self.x), int(self.y), int(self.radius), color)
        tft.draw_circle(int(self.x), int(self.y), int(self.radius), self.fgcolor)

    def color(self, color):
        self._color = color
        self.show_if_current()

