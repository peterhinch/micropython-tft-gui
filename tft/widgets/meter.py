# meter.py For TFT driver.
# Adapted for (and requires) uasyncio V3

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2016-2020 Peter Hinch

from tft.driver.ugui import NoTouch, print_centered
from tft.driver import TFT_io
from tft.driver.constants import *

class Meter(NoTouch):
    def __init__(self, location, *, font=None, height=200, width=30,
                 fgcolor=None, bgcolor=None, pointercolor=None, fontcolor=None,
                 divisions=10, legends=None, value=0):
        border = 5 if font is None else 1 + font.height() / 2
        NoTouch.__init__(self, location, font, height, width, fgcolor, bgcolor, fontcolor, border, value, None) # super() provoked Python bug
        border = self.border # border width
        self.ptrbytes = 3 * (self.width + 1) # 3 bytes per pixel
        self.ptrbuf = bytearray(self.ptrbytes) #???
        self.x0 = self.location[0]
        self.x1 = self.location[0] + self.width
        self.y0 = self.location[1] + border + 2
        self.y1 = self.location[1] + self.height - border
        self.divisions = divisions
        self.legends = legends
        self.pointercolor = pointercolor if pointercolor is not None else self.fgcolor
        self.ptr_y = None # Invalidate old position

    def show(self):
        tft = self.tft
        width = self.width
        dx = 5
        x0 = self.x0
        x1 = self.x1
        y0 = self.y0
        y1 = self.y1
        height = y1 - y0
        if self.divisions > 0:
            dy = height / (self.divisions) # Tick marks
            for tick in range(self.divisions + 1):
                ypos = int(y0 + dy * tick)
                tft.draw_hline(x0, ypos, dx, self.fgcolor)
                tft.draw_hline(x1 - dx, ypos, dx, self.fgcolor)

        if self.legends is not None and self.font is not None: # Legends
            if len(self.legends) <= 1:
                dy = 0
            else:
                dy = height / (len(self.legends) -1)
            yl = self.y1 # Start at bottom
            for legend in self.legends:
                print_centered(tft, int(self.x0 + self.width /2), int(yl), legend, self.fontcolor, self.font)
                yl -= dy

        if self.ptr_y is not None: # Restore background if it was saved
            tft.setXY(x0, self.ptr_y, x1, self.ptr_y)
            TFT_io.tft_write_data_AS(self.ptrbuf, self.ptrbytes)
        self.ptr_y = int(self.y1 - self._value * height) # y position of slider
        tft.setXY(x0, self.ptr_y, x1, self.ptr_y) # Read background
        TFT_io.tft_read_cmd_data_AS(0x2e, self.ptrbuf, self.ptrbytes)
        tft.draw_hline(x0, self.ptr_y, width, self.pointercolor) # Draw pointer

