# icon_gauge.py For TFT driver.
# Adapted for (and requires) uasyncio V3

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2016-2020 Peter Hinch

from tft.driver.ugui import NoTouch
from tft.driver.constants import *

class IconGauge(NoTouch):
    def __init__(self, location, *, icon_module, initial_icon=0):
        NoTouch.__init__(self, location, None, icon_module.height, icon_module.width, None, None, None, None,
                         initial_icon / len(icon_module._icons), None)
        self.draw = icon_module.draw
        self.num_icons = len(icon_module._icons)
        self.state = initial_icon

    def show(self):
        tft = self.tft
        x = self.location[0]
        y = self.location[1]
        self.draw(x, y, self.state, tft.drawBitmap)

    def icon(self, icon_index): # select icon by index
        if icon_index >= self.num_icons or icon_index < 0: 
            raise ugui_exception('Invalid icon index {}'.format(icon_index))
        else:
            self.state = int(icon_index)
            self.show_if_current()

    def _value_change(self, show):
        self.state = min(int(self._value * self.num_icons), self.num_icons -1)
        self.show_if_current()
