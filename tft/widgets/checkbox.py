# checkbox.py For TFT driver.
# Adapted for (and requires) uasyncio V3

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2016-2020 Peter Hinch

from tft.driver.ugui import Touchable, dolittle
from tft.driver.constants import *

class Checkbox(Touchable):
    def __init__(self, location, *, height=30, fillcolor=None,
                 fgcolor=None, bgcolor=None, callback=dolittle, args=[], value=False, border=None):
        super().__init__(location, None, height, height, fgcolor, bgcolor, None, border, False, value, None)
        super()._set_callbacks(callback, args)
        self.fillcolor = fillcolor

    def show(self):
        if self._initial_value is None:
            self._initial_value = True
            value = self._value # As passed to ctor
            if value is None:
                self._value = False # special case: don't execute callback on initialisation
            else:
                self._value = not value # force redraw
                self.value(value)
                return
        self._show()

    def _show(self):
        tft = self.tft
        bw = self.border
        x = self.location[0] + bw
        y = self.location[1] + bw
        height = self.height - 2 * bw
        x1 = x + height
        y1 = y + height
        if self._value:
            if self.fillcolor is not None:
                tft.fill_rectangle(x, y, x1, y1, self.fillcolor)
        else:
            tft.fill_rectangle(x, y, x1, y1, self.bgcolor)
        tft.draw_rectangle(x, y, x1, y1, self.fgcolor)
        if self.fillcolor is None and self._value:
            tft.draw_line(x, y, x1, y1, self.fgcolor)
            tft.draw_line(x, y1, x1, y, self.fgcolor)

    def _touched(self, x, y): # Was touched
        self.value(not self._value) # Upddate and refresh

