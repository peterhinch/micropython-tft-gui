# slider.py For TFT driver.
# Adapted for (and requires) uasyncio V3

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2016-2020 Peter Hinch

from tft.driver.ugui import Touchable, dolittle
from tft.driver import TFT_io
from tft.driver.constants import *
from tft.widgets.label import Label
# A slider's text items lie outside its bounding box (area sensitive to touch)

class Slider(Touchable):
    def __init__(self, location, *, font=None, height=200, width=30, divisions=10, legends=None,
                 fgcolor=None, bgcolor=None, fontcolor=None, slidecolor=None, border=None, 
                 cb_end=dolittle, cbe_args=[], cb_move=dolittle, cbm_args=[], value=0.0):
        width &= 0xfe # ensure divisible by 2
        super().__init__(location, font, height, width, fgcolor, bgcolor, fontcolor, border, True, None, value)
        self.divisions = divisions
        self.legends = legends if font is not None else None
        self.slidecolor = slidecolor
        super()._set_callbacks(cb_move, cbm_args, cb_end, cbe_args)
        slidewidth = int(width / 1.3) & 0xfe # Ensure divisible by 2
        self.slideheight = 6 # must be divisible by 2
                             # We draw an odd number of pixels:
        self.slidebytes = (self.slideheight + 1) * (slidewidth + 1) * 3
        self.slidebuf = bytearray(self.slidebytes)
        b = self.border
        self.pot_dimension = self.height - 2 * (b + self.slideheight // 2)
        width = self.width - 2 * b
        xcentre = self.location[0] + b + width // 2
        self.slide_x0 = xcentre - slidewidth // 2
        self.slide_x1 = xcentre + slidewidth // 2 # slide X coordinates
        self.slide_y = None # Invalidate slide position
        # Prevent Label objects being added to display list when already there.
        self.drawn = False

    def show(self):
        tft = self.tft
        bw = self.border
        width = self.width - 2 * bw
        height = self.pot_dimension # Height of slot
        x = self.location[0] + bw
        y = self.location[1] + bw + self.slideheight // 2 # Allow space above and below slot
        if self._value is None or self.redraw: # Initialising
            self.redraw = False
            self.render_slide(tft, self.bgcolor) # Erase slide if it exists
            dx = width // 2 - 2 
            tft.draw_rectangle(x + dx, y, x + width - dx, y + height, self.fgcolor)
            if self.divisions > 0:
                dy = height / (self.divisions) # Tick marks
                for tick in range(self.divisions + 1):
                    ypos = int(y + dy * tick)
                    tft.draw_hline(x + 1, ypos, dx, self.fgcolor)
                    tft.draw_hline(x + 2 + width // 2, ypos, dx, self.fgcolor) # Add half slot width

            # Legends: if redrawing, they are already on the Screen's display list
            if self.legends is not None and not self.drawn:
                if len(self.legends) <= 1:
                    dy = 0
                else:
                    dy = height / (len(self.legends) -1)
                yl = y + height # Start at bottom
                fhdelta = self.font.height() / 2
                font = self.font
                for legend in self.legends:
                    loc = (x + self.width, int(yl - fhdelta))
                    Label(loc, font = font, fontcolor = self.fontcolor, value = legend)
                    yl -= dy
            self.save_background(tft)
            if self._value is None:
                self.value(self._initial_value, show = False) # Prevent recursion
        self.render_bg(tft)
        self.slide_y = self.update(tft) # Reflect new value in slider position
        self.save_background(tft)
        color = self.slidecolor if self.slidecolor is not None else self.fgcolor
        self.render_slide(tft, color)
        self.drawn = True

    def update(self, tft):
        y = self.location[1] + self.border + self.slideheight // 2
        sliderpos = int(y + self.pot_dimension - self._value * self.pot_dimension)
        return sliderpos - self.slideheight // 2

    def slide_coords(self):
        return self.slide_x0, self.slide_y, self.slide_x1, self.slide_y + self.slideheight

    def save_background(self, tft): # Read background under slide
       if self.slide_y is not None:
           tft.setXY(*self.slide_coords())
           TFT_io.tft_read_cmd_data_AS(0x2e, self.slidebuf, self.slidebytes)

    def render_bg(self, tft):
       if self.slide_y is not None:
           tft.setXY(*self.slide_coords())
           TFT_io.tft_write_data_AS(self.slidebuf, self.slidebytes)

    def render_slide(self, tft, color):
        if self.slide_y is not None:
            tft.fill_rectangle(*self.slide_coords(), color = color)

    def color(self, color):
        if color != self.fgcolor:
            self.fgcolor = color
            self.redraw = True
            self.show_if_current()

    def _touched(self, x, y): # Touched in bounding box. A drag will call repeatedly.
        self.value((self.location[1] + self.height - y) / self.pot_dimension)

