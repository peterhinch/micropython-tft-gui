
# dial.py For TFT driver.
# Adapted for (and requires) uasyncio V3

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2016-2020 Peter Hinch

import math
from tft.driver.ugui import NoTouch
from tft.driver.constants import *

# class displays angles. Angle 0 is vertical, +ve increments are clockwise.
class Dial(NoTouch):
    def __init__(self, location, *, height=100, fgcolor=None, bgcolor=None, border=None, pointers=(0.9,), ticks=4):
        NoTouch.__init__(self, location, None, height, height, fgcolor, bgcolor, None, border, 0, 0) # __super__ provoked Python bug
        border = self.border # border width
        radius = height / 2 - border
        self.radius = radius
        self.ticks = ticks
        self.xorigin = location[0] + border + radius
        self.yorigin = location[1] + border + radius
        self.pointers = tuple(z * self.radius for z in pointers) # Pointer lengths
        self.angles = [None for _ in pointers]
        self.new_value = None

    def show(self):
        tft = self.tft
        ticks = self.ticks
        radius = self.radius
        ticklen = 0.1 * radius
        for tick in range(ticks):
            theta = 2 * tick * math.pi / ticks
            x_start = int(self.xorigin + radius * math.sin(theta))
            y_start = int(self.yorigin - radius * math.cos(theta))
            x_end = int(self.xorigin + (radius - ticklen) * math.sin(theta))
            y_end = int(self.yorigin - (radius - ticklen) * math.cos(theta))
            tft.draw_line(x_start, y_start, x_end, y_end, self.fgcolor)
        tft.draw_circle(self.xorigin, self.yorigin, radius, self.fgcolor)
        for idx, ang in enumerate(self.angles):
            if ang is not None:
                self._drawpointer(ang, idx, self.bgcolor) # erase old
        if self.new_value is not None:
            self.angles[self.new_value[1]] = self.new_value[0]
            self.new_value = None

        for idx, ang in enumerate(self.angles):
            if ang is not None:
                self._drawpointer(ang, idx, self.fgcolor)

    def value(self, angle, pointer=0):
        if pointer > len(self.pointers):
            raise ValueError('pointer index out of range')
        self.new_value = [angle, pointer]
        self.show_if_current()

    def _drawpointer(self, radians, pointer, color):
        tft = self.tft
        length = self.pointers[pointer]
        x_end = int(self.xorigin + length * math.sin(radians))
        y_end = int(self.yorigin - length * math.cos(radians))
        tft.draw_line(int(self.xorigin), int(self.yorigin), x_end, y_end, color)

