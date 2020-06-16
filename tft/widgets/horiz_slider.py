from tft.driver.ugui import Touchable, dolittle, get_stringsize
from tft.driver import TFT_io
# horiz_slider.py For TFT driver.
# Adapted for (and requires) uasyncio V3

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2016-2020 Peter Hinch

from tft.driver.constants import *
from tft.widgets.label import Label

class HorizSlider(Touchable):
    def __init__(self, location, *, font=None, height=30, width=200, divisions=10, legends=None,
                 fgcolor=None, bgcolor=None, fontcolor=None, slidecolor=None, border=None, 
                 cb_end=dolittle, cbe_args=[], cb_move=dolittle, cbm_args=[], value=0.0):
        height &= 0xfe # ensure divisible by 2
        super().__init__(location, font, height, width, fgcolor, bgcolor, fontcolor, border, True, None, value)
        self.divisions = divisions
        self.legends = legends if font is not None else None
        self.slidecolor = slidecolor
        super()._set_callbacks(cb_move, cbm_args, cb_end, cbe_args)
        slideheight = int(height / 1.3) & 0xfe # Ensure divisible by 2
        self.slidewidth = 6 # must be divisible by 2
                             # We draw an odd number of pixels:
        self.slidebytes = (slideheight + 1) * (self.slidewidth + 1) * 3
        self.slidebuf = bytearray(self.slidebytes)
        b = self.border
        self.pot_dimension = self.width - 2 * (b + self.slidewidth // 2)
        height = self.height - 2 * b
        ycentre = self.location[1] + b + height // 2
        self.slide_y0 = ycentre - slideheight // 2
        self.slide_y1 = ycentre + slideheight // 2 # slide Y coordinates
        self.slide_x = None # invalidate: slide has not yet been drawn
        # Prevent Label objects being added to display list when already there.
        self.drawn = False

    def show(self):
        tft = self.tft
        bw = self.border
        height = self.height - 2 * bw
        width = self.pot_dimension # Length of slot
        x = self.location[0] + bw + self.slidewidth // 2 # Allow space left and right slot for slider at extremes
        y = self.location[1] + bw
        if self._value is None or self.redraw: # Initialising
            self.redraw = False
            self.render_slide(tft, self.bgcolor) # Erase slide if it exists
            dy = height // 2 - 2 # slot is 4 pixels wide
            tft.draw_rectangle(x, y + dy, x + width, y + height - dy, self.fgcolor)
            if self.divisions > 0:
                dx = width / (self.divisions) # Tick marks
                for tick in range(self.divisions + 1):
                    xpos = int(x + dx * tick)
                    tft.draw_vline(xpos, y + 1, dy, self.fgcolor) # TODO Why is +1 fiddle required here?
                    tft.draw_vline(xpos, y + 2 + height // 2,  dy, self.fgcolor) # Add half slot width

            # Legends: if redrawing, they are already on the Screen's display list
            if self.legends is not None and not self.drawn:
                if len(self.legends) <= 1:
                    dx = 0
                else:
                    dx = width / (len(self.legends) -1)
                xl = x
                font = self.font
                for legend in self.legends:
                    offset = get_stringsize(legend, self.font)[0] / 2
                    loc = int(xl - offset), y - self.font.height() - bw - 1
                    Label(loc, font = font, fontcolor = self.fontcolor, value = legend)
                    xl += dx
            self.save_background(tft)
            if self._value is None:
                self.value(self._initial_value, show = False) # prevent recursion

        self.render_bg(tft)
        self.slide_x = self.update(tft) # Reflect new value in slider position
        self.save_background(tft)
        color = self.slidecolor if self.slidecolor is not None else self.fgcolor
        self.render_slide(tft, color)
        self.drawn = True

    def update(self, tft):
        x = self.location[0] + self.border + self.slidewidth // 2
        sliderpos = int(x + self._value * self.pot_dimension)
        return sliderpos - self.slidewidth // 2

    def slide_coords(self):
        return self.slide_x, self.slide_y0, self.slide_x + self.slidewidth, self.slide_y1

    def save_background(self, tft): # Read background under slide
        if self.slide_x is not None:
            tft.setXY(*self.slide_coords())
            TFT_io.tft_read_cmd_data_AS(0x2e, self.slidebuf, self.slidebytes)

    def render_bg(self, tft):
        if self.slide_x is not None:
            tft.setXY(*self.slide_coords())
            TFT_io.tft_write_data_AS(self.slidebuf, self.slidebytes)

    def render_slide(self, tft, color):
        if self.slide_x is not None:
            tft.fill_rectangle(*self.slide_coords(), color = color)

    def color(self, color):
        if color != self.fgcolor:
            self.fgcolor = color
            self.redraw = True
            self.show_if_current()

    def _touched(self, x, y): # Touched in bounding box. A drag will call repeatedly.
        self.value((x - self.location[0]) / self.pot_dimension)
