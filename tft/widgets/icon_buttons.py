# buttons.py For TFT driver.
# Adapted for (and requires) uasyncio V3

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2016-2020 Peter Hinch
# icon_buttons.py For TFT driver.
# Adapted for (and requires) uasyncio V3

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2016-2020 Peter Hinch

import uasyncio as asyncio
from tft.driver.ugui import Touchable, dolittle
from tft.driver.constants import *
from tft.primitives.delay_ms import Delay_ms

# Button/checkbox whose appearance is defined by icon bitmaps

class IconButton(Touchable):
    long_press_time = 1000
    def __init__(self, location, *, icon_module, flash=0, toggle=False, state=0,
                 callback=dolittle, args=[], onrelease=True, lp_callback=None, lp_args=[]):
        self.draw = icon_module.draw
        self.num_icons = len(icon_module._icons)
        super().__init__(location, None, icon_module.height,
                         icon_module.width, None, None, None, None, False, 0, 0)
        self.callback = callback
        self.callback_args = args
        self.onrelease = onrelease
        self.lp_callback = lp_callback
        self.lp_args = lp_args
        self.lp = False # Long press not in progress
        self.flash = int(flash * 1000)  # Compatibility
        self.toggle = toggle
        if state >= self.num_icons or state < 0:
            raise ugui_exception('Invalid icon index {}'.format(state))
        self.state = state
        if self.flash > 0:
            if self.num_icons < 2:
                raise ugui_exception('Need > 1 icon for flashing button')
            self.delay = Delay_ms(self._show, (0,))

    def show(self):
        self._show(self.state)

    def _show(self, state):
        tft = self.tft
        self.state = state
        x = self.location[0] + self.width // 2 # Centre relative
        y = self.location[1] + self.height // 2
        color_idx = 1 if self.greyed_out() else 0
        try:
            self.draw(x, y, state, tft.drawBitmap, color_idx) # TODO bodge to deal with old style icons ?????
        except TypeError:
            self.draw(x, y, state, tft.drawBitmap)

    def value(self, val=None):
        if val is not None:
            val = int(val)
            if val >= self.num_icons or val < 0: 
                raise ugui_exception('Invalid icon index {}'.format(val))
            if val != self.state:
                self._show(val)
                self.callback(self, *self.callback_args) # Callback not a bound method so pass self
        return self.state

    def _touched(self, x, y): # Process touch
        if self.flash > 0:
            self._show(1)
            self.delay.trigger(self.flash)
        elif self.toggle:
            self.state = (self.state + 1) % self.num_icons
            self._show(self.state)
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

# Group of buttons at different locations, where pressing one shows
# only current button highlighted and does callback from current one
class IconRadioButtons:
    def __init__(self, callback=dolittle, selected=0):
        self.user_callback = callback
        self.setbuttons = set()
        self.selected = selected
        self._greyed_out = False

    def add_button(self, *args, **kwargs):
        if self.selected == len(self.setbuttons):
            kwargs['state'] = 1
        else:
            kwargs['state'] = 0
        button = IconButton(*args, **kwargs) # Create and show
        self.setbuttons.add(button)
        button.callback = self._callback
        return button

    def value(self, but=None):
        if but is not None:
            if but not in self.setbuttons:
                raise ugui_exception('Button not a member of this radio button')
            else:
                if but.value() == 0:
                    self._callback(but, *but.callback_args)
        resultset = {x for x in self.setbuttons if x.state ==1}
        assert len(resultset) == 1, 'We have > 1 button selected'
        return resultset.pop()

    def greyed_out(self, val=None):
        if val is not None and self._greyed_out != val:
            self._greyed_out = val
            for button in self.setbuttons:
                button.greyed_out(val)
        return self._greyed_out

    def _callback(self, button, *args):
        for but in self.setbuttons:
            if but is button:
                but._show(1)
            else:
                but._show(0)
        self.user_callback(button, *args) # Args for button just pressed

