# Adapted for (and requires) uasyncio V3

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2016-2020 Peter Hinch
# buttons.py For TFT driver.
# Adapted for (and requires) uasyncio V3

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2016-2020 Peter Hinch

import uasyncio as asyncio
from tft.driver.ugui import Touchable, dolittle, print_centered
from tft.primitives.delay_ms import Delay_ms
from tft.driver.constants import *

# *********** PUSHBUTTON CLASSES ***********

# Button coordinates relate to bounding box (BB). x, y are of BB top left corner.
# likewise width and height refer to BB, regardless of button shape
# If font is None button will be rendered without text

class Button(Touchable):
    lit_time = 1000
    long_press_time = 1000
    def __init__(self, location, *, font, shape=CIRCLE, height=50, width=50, fill=True,
                 fgcolor=None, bgcolor=None, fontcolor=None, litcolor=None, text='',
                 callback=dolittle, args=[], onrelease=True, lp_callback=None, lp_args=[]):
        super().__init__(location, font, height, width, fgcolor, bgcolor, fontcolor, None, False, text, None)
        self.shape = shape
        self.radius = height // 2
        self.fill = fill
        self.litcolor = litcolor
        self.text = text
        self.callback = callback
        self.callback_args = args
        self.onrelease = onrelease
        self.lp_callback = lp_callback
        self.lp_args = lp_args
        self.lp = False # Long press not in progress
        self.orig_fgcolor = fgcolor
        if self.litcolor is not None:
            self.delay = Delay_ms(self.shownormal)
        self.litcolor = litcolor if self.fgcolor is not None else None

    def show(self):
        tft = self.tft
        x = self.location[0]
        y = self.location[1]
        if not self.visible:   # erase the button
            tft.usegrey(False)
            tft.fill_rectangle(x, y, x + self.width, y + self.height, self.bgcolor)
            return
        if self.shape == CIRCLE:  # Button coords are of top left corner of bounding box
            x += self.radius
            y += self.radius
            if self.fill:
                tft.fill_circle(x, y, self.radius, self.fgcolor)
            else:
                tft.draw_circle(x, y, self.radius, self.fgcolor)
            if self.font is not None and len(self.text):
                print_centered(tft, x, y, self.text, self.fontcolor, self.font)
        else:
            x1 = x + self.width
            y1 = y + self.height
            if self.shape == RECTANGLE: # rectangle
                if self.fill:
                    tft.fill_rectangle(x, y, x1, y1, self.fgcolor)
                else:
                    tft.draw_rectangle(x, y, x1, y1, self.fgcolor)
                if self.font  is not None and len(self.text):
                    print_centered(tft, (x + x1) // 2, (y + y1) // 2, self.text, self.fontcolor, self.font)
            elif self.shape == CLIPPED_RECT: # clipped rectangle
                if self.fill:
                    tft.fill_clipped_rectangle(x, y, x1, y1, self.fgcolor)
                else:
                    tft.draw_clipped_rectangle(x, y, x1, y1, self.fgcolor)
                if self.font  is not None and len(self.text):
                    print_centered(tft, (x + x1) // 2, (y + y1) // 2, self.text, self.fontcolor, self.font)

    def shownormal(self):
        self.fgcolor = self.orig_fgcolor
        self.show_if_current()

    def _touched(self, x, y): # Process touch
        if self.litcolor is not None:
            self.fgcolor = self.litcolor
            self.show() # must be on current screen
            self.delay.trigger(Button.lit_time)
        if self.lp_callback is not None:
            asyncio.create_task(self.longpress())
        if not self.onrelease:
            self.callback(self, *self.callback_args) # Callback not a bound method so pass self

    def _untouched(self):
        self.lp = False
        if self.onrelease:
            self.callback(self, *self.callback_args) # Callback not a bound method so pass self

    async def longpress(self):
        self.lp = True
        await asyncio.sleep_ms(self.long_press_time)
        if self.lp:
            self.lp_callback(self, *self.lp_args)

# Group of buttons, typically at same location, where pressing one shows
# the next e.g. start/stop toggle or sequential select from short list
class ButtonList:
    def __init__(self, callback=dolittle):
        self.user_callback = callback
        self.lstbuttons = []
        self.current = None # No current button
        self._greyed_out = False

    def add_button(self, *args, **kwargs):
        button = Button(*args, **kwargs)
        self.lstbuttons.append(button)
        active = self.current is None # 1st button added is active
        button.visible = active
        button.callback = self._callback
        if active:
            self.current = button
        return button

    def value(self, button=None):
        if button is not None and button is not self.current:
            old = self.current
            new = button
            self.current = new
            old.visible = False
            old.show()
            new.visible = True
            new.show()
            self.user_callback(new, *new.callback_args)
        return self.current

    def greyed_out(self, val=None):
        if val is not None and self._greyed_out != val:
            self._greyed_out = val
            for button in self.lstbuttons:
                button.greyed_out(val)
            self.current.show()
        return self._greyed_out

    def _callback(self, button, *args):
        old = button
        old_index = self.lstbuttons.index(button)
        new = self.lstbuttons[(old_index + 1) % len(self.lstbuttons)]
        self.current = new
        old.visible = False
        old.show()
        new.visible = True
        new.busy = True # Don't respond to continued press
        new.show()
        self.user_callback(new, *args) # user gets button with args they specified

# Group of buttons at different locations, where pressing one shows
# only current button highlighted and oes callback from current one
class RadioButtons:
    def __init__(self, highlight, callback=dolittle, selected=0):
        self.user_callback = callback
        self.lstbuttons = []
        self.current = None # No current button
        self.highlight = highlight
        self.selected = selected
        self._greyed_out = False

    def add_button(self, *args, **kwargs):
        button = Button(*args, **kwargs)
        self.lstbuttons.append(button)
        button.callback = self._callback
        active = len(self.lstbuttons) == self.selected + 1
        button.fgcolor = self.highlight if active else button.orig_fgcolor
        if active:
            self.current = button
        return button

    def value(self, button=None):
        if button is not None and button is not self.current:
            self._callback(button, *button.callback_args)
        return self.current

    def greyed_out(self, val=None):
        if val is not None and self._greyed_out != val:
            self._greyed_out = val
            for button in self.lstbuttons:
                button.greyed_out(val)
        return self._greyed_out

    def _callback(self, button, *args):
        for but in self.lstbuttons:
            if but is button:
                but.fgcolor = self.highlight
                self.current = button
            else:
                but.fgcolor = but.orig_fgcolor
            but.show()
        self.user_callback(button, *args) # user gets button with args they specified
