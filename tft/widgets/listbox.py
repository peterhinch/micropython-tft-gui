# listbox.py For TFT driver.
# Adapted for (and requires) uasyncio V3

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2016-2020 Peter Hinch

from tft.driver.ugui import Touchable, dolittle, print_left
from tft.driver.constants import *

# *********** LISTBOX CLASS ***********

class Listbox(Touchable):
    def __init__(self, location, *, font, elements, width=250, value=0, border=2,
                 fgcolor=None, bgcolor=None, fontcolor=None, select_color=LIGHTBLUE,
                 callback=dolittle, args=[]):
        self.entry_height = font.height() + 2 # Allow a pixel above and below text
        bw = border if border is not None else 0 # Replicate Touchable ctor's handling of self.border
        height = self.entry_height * len(elements) + 2 * bw
        super().__init__(location, font, height, width, fgcolor, bgcolor, fontcolor, border, False, value, None)
        super()._set_callbacks(callback, args)
        self.select_color = select_color
        fail = False
        try:
            self.elements = [s for s in elements if type(s) is str]
        except:
            fail = True
        else:
            fail = len(self.elements) == 0
        if fail:
            raise ValueError('elements must be a list or tuple of one or more strings')
        if value >= len(self.elements):
            value = 0
        self._value = value # No callback until user touches

    def show(self):
        tft = self.tft
        bw = self.border
        clip = self.width - 2 * bw
        length = len(self.elements)
        x = self.location[0]
        y = self.location[1]
        xs = x + bw # start and end of text field
        xe = x + self.width - 2 * bw
        tft.fill_rectangle(xs, y + 1, xe, y - 1 + self.height - 2 * bw, self.bgcolor)
        for n in range(length):
            ye = y + n * self.entry_height
            if n == self._value:
                tft.fill_rectangle(xs, ye + 1, xe, ye + self.entry_height - 1, self.select_color)
            print_left(tft, xs, ye + 1, self.elements[n], self.fontcolor, self.font, clip)

    def textvalue(self, text=None): # if no arg return current text
        if text is None:
            return self.elements[self._value]
        else: # set value by text
            try:
                v = self.elements.index(text)
            except ValueError:
                v = None
            else:
                if v != self._value:
                    self.value(v)
            return v

    def _touched(self, x, y):
        dy = y - (self.location[1])
        self._initial_value = dy // self.entry_height

    def _untouched(self):
        if self._initial_value is not None:
            self._value = -1  # Force update on every touch
            self.value(self._initial_value, show = True)
            self._initial_value = None
