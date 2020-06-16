# buttons.py For TFT driver.
# Adapted for (and requires) uasyncio V3

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2016-2020 Peter Hinch
# dropdown.py For TFT driver.
# Adapted for (and requires) uasyncio V3

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2016-2020 Peter Hinch

from tft.driver.ugui import Screen, Aperture, Touchable, dolittle, print_left
from tft.driver.constants import *
from tft.widgets.listbox import Listbox

class _ListDialog(Aperture):
    def __init__(self, location, dropdown, width):
        border = 1 # between Aperture border and list
        dd = dropdown
        font = dd.font
        elements = dd.elements
        entry_height = font.height() + 2 # Allow a pixel above and below text
        height = entry_height * len(elements) + 2 * border
        lb_location = location[0] + border, location[1] + border
        lb_width = width - 2 * border
        super().__init__(location, height, width)
        self.listbox = Listbox(lb_location, font = font, elements = elements, width = lb_width,
                               border = None, fgcolor = dd.fgcolor, bgcolor = dd.bgcolor,
                               fontcolor = dd.fontcolor, select_color = dd.select_color,
                               value = dd.value(), callback = self.callback)
        self.dropdown = dd

    def callback(self, obj_listbox):
        if obj_listbox._initial_value is not None: # a touch has occurred
            val = obj_listbox.textvalue()
            Screen.back()
            if self.dropdown is not None: # Part of a Dropdown
                self.dropdown.value(obj_listbox.value()) # Update it
 
class Dropdown(Touchable):
    def __init__(self, location, *, font, elements, width=250, value=0,
                 fgcolor=None, bgcolor=None, fontcolor=None, select_color=LIGHTBLUE,
                 callback=dolittle, args=[]):
        border = 2
        self.entry_height = font.height() + 2 # Allow a pixel above and below text
        height = self.entry_height + 2 * border
        super().__init__(location, font, height, width, fgcolor, bgcolor, fontcolor, border, False, value, None)
        super()._set_callbacks(callback, args)
        self.select_color = select_color
        self.elements = elements

    def show(self):
        tft = self.tft
        bw = self.border
        clip = self.width - (self.height + 2 * bw)
        x, y = self.location[0], self.location[1]
        self._draw(tft, x, y)
        if self._value is not None:
            print_left(tft, x + bw, y + bw + 1, self.elements[self._value], self.fontcolor, self.font, clip)

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

    def _draw(self, tft, x, y):
        self.fill = True
        self.draw_border()
        tft.draw_vline(x + self.width - self.height, y, self.height, self.fgcolor)
        xcentre = x + self.width - self.height // 2 # Centre of triangle
        ycentre = y + self.height // 2
        halflength = (self.height - 8) // 2
        length = halflength * 2
        if length > 0:
            tft.draw_hline(xcentre - halflength, ycentre - halflength, length, self.fgcolor)
            tft.draw_line(xcentre - halflength, ycentre - halflength, xcentre, ycentre + halflength, self.fgcolor)
            tft.draw_line(xcentre + halflength, ycentre - halflength, xcentre, ycentre + halflength, self.fgcolor)

    def _touched(self, x, y):
        if len(self.elements) > 1:
            location = self.location[0], self.location[1] + self.height + 1
            args = (location, self, self.width - self.height)
            Screen.change(_ListDialog, args = args)
