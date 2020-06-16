# knob.py For TFT driver.
# Adapted for (and requires) uasyncio V3

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2016-2020 Peter Hinch

import math
from tft.driver.ugui import Touchable, dolittle, TWOPI
from tft.driver.constants import *

# *********** CONTROL KNOB CLASS ***********

class Knob(Touchable):
    def __init__(self, location, *, height=100, arc=TWOPI, ticks=9, value=0.0,
                 fgcolor=None, bgcolor=None, color=None, border=None,
                 cb_end=dolittle, cbe_args=[], cb_move=dolittle, cbm_args=[]):
        Touchable.__init__(self, location, None, height, height, fgcolor, bgcolor, None, border, True,  None, value)
        border = self.border # Geometry: border width
        radius = height / 2 - border
        self.arc = min(max(arc, 0), TWOPI) # Usable angle of control
        self.radius = radius
        self.xorigin = location[0] + border + radius
        self.yorigin = location[1] + border + radius
        self.ticklen = 0.1 * radius
        self.pointerlen = radius - self.ticklen - 5
        self.ticks = max(ticks, 2) # start and end of travel
        super()._set_callbacks(cb_move, cbm_args, cb_end, cbe_args)
        self._old_value = None # data: invalidate
        self.color = color

    def show(self):
        tft = self.tft
        if self._value is None or self.redraw: # Initialising
            self.redraw = False
            arc = self.arc
            ticks = self.ticks
            radius = self.radius
            ticklen = self.ticklen
            for tick in range(ticks):
                theta = (tick / (ticks - 1)) * arc - arc / 2
                x_start = int(self.xorigin + radius * math.sin(theta))
                y_start = int(self.yorigin - radius * math.cos(theta))
                x_end = int(self.xorigin + (radius - ticklen) * math.sin(theta))
                y_end = int(self.yorigin - (radius - ticklen) * math.cos(theta))
                tft.draw_line(x_start, y_start, x_end, y_end, self.fgcolor)
            if self.color is not None:
                tft.fill_circle(self.xorigin, self.yorigin, radius - ticklen, self.color)
            tft.draw_circle(self.xorigin, self.yorigin, radius - ticklen, self.fgcolor)
            tft.draw_circle(self.xorigin, self.yorigin, radius - ticklen - 3, self.fgcolor)
            if self._value is None:
                self.value(self._initial_value, show = False)

        if self._old_value is not None: # An old pointer needs erasing
            if self.greyed_out() and tft.skeleton():
                tft.usegrey(False) # greyed out 'skeleton' style
                color = tft.getBGColor() # erase to screen background
            else:
                color = self.bgcolor if self.color is None else self.color # Fill color
            self._drawpointer(self._old_value, color) # erase old
            self.tft # Reset Screen greyed-out status

        self._drawpointer(self._value, self.fgcolor) # draw new
        self._old_value = self._value # update old

    def _touched(self, x, y): # Touched in bounding box. A drag will call repeatedly.
        dy = self.yorigin - y
        dx = x - self.xorigin
        if (dx**2 + dy**2) / self.radius**2 < 0.5:
            return # vector too short
        alpha = math.atan2(dx, dy) # axes swapped: orientate relative to vertical
        arc = self.arc
        alpha = min(max(alpha, -arc / 2), arc / 2) + arc / 2
        self.value(alpha / arc)

    def _drawpointer(self, value, color):
        tft = self.tft
        arc = self.arc
        length = self.pointerlen
        angle = value * arc - arc / 2
        x_end = int(self.xorigin + length * math.sin(angle))
        y_end = int(self.yorigin - length * math.cos(angle))
        tft.draw_line(int(self.xorigin), int(self.yorigin), x_end, y_end, color)

