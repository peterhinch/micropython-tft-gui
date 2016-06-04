# ugui.py Micropython GUI library for TFT displays
# The MIT License (MIT)
#
# Copyright (c) 2016 Peter Hinch
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import TFT_io
import math
from delay import Delay
from tft import TFT
from constants import *

TWOPI = 2 * math.pi

# *********** UTILITY FUNCTIONS ***********

class ugui_exception(Exception):
    pass

# replaces lambda *_ : None owing to issue #2023
def dolittle(*_):
    pass

def get_stringsize(s, font):
    hor = 0
    for c in s:
        _, vert, cols = font.get_ch(ord(c))
        hor += cols
    return hor, vert

def print_centered(tft, x, y, s, color, font, clip=False, scroll=False):
    old_style = tft.getTextStyle()
    length, height = get_stringsize(s, font)
    tft.setTextStyle(color, None, 2, font)
    tft.setTextPos(x - length // 2, y - height // 2, clip, scroll)
    tft.printString(s)
    tft.setTextStyle(*old_style)

def print_left(tft, x, y, s, color, font, clip=False, scroll=False):
    old_style = tft.getTextStyle()
    tft.setTextStyle(color, None, 2, font)
    tft.setTextPos(x, y,  clip, scroll)
    tft.printString(s)
    tft.setTextStyle(*old_style)

def dim(color, factor): # Dim a color
    if color is not None:
        return tuple(int(x / factor) for x in color)

# *********** TFT_G CLASS ************
# Subclass TFT to enable greying out of controls
# Some TFT methods call drawHLine and drawVLine: the bound variable 'raw` forces them
# to use the color of the calling method
class TFT_G(TFT):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._is_grey = False
        self._grey = GREY
        self._factor = 2 # Default grey-out methd: dim colors

    def _getcolor(self, color):
        if self._is_grey:
            if self._factor:
                color = dim(color, self._factor)
            else:
                color = self._grey
        return color

    def grey_color(self, *, color=GREY, factor=0): # User override for grey
        if factor > 0:
            self._factor = factor
        else:
            self._factor = 0
            self._grey = color

    def skeleton(self): # Determine type of greying
        return self._factor == 0

    def usegrey(self, val): # tft.usegrey(True) sets greyed-out
        self._is_grey = val

    def draw_rectangle(self, x1, y1, x2, y2, color):
        self.drawRectangle(x1, y1, x2, y2, self._getcolor(color))

    def fill_rectangle(self, x1, y1, x2, y2, color):
        if self._is_grey:
            if self._factor:
                self.fillRectangle(x1, y1, x2, y2, self._getcolor(color))
            else:
                self.fillRectangle(x1, y1, x2, y2, self.getBGColor()) # Blank space
                self.drawRectangle(x1, y1, x2, y2, self._getcolor(color))
        else:
            self.fillRectangle(x1, y1, x2, y2, color)

    def draw_clipped_rectangle(self, x1, y1, x2, y2, color):
        self.drawClippedRectangle(x1, y1, x2, y2, self._getcolor(color))

    def fill_clipped_rectangle(self, x1, y1, x2, y2, color):
        if self._is_grey:
            if self._factor:
                self.fillClippedRectangle(x1, y1, x2, y2, self._getcolor(color))
            else: # greyed out controls drawn as skeleton on screen bgcolor
                self.fillClippedRectangle(x1, y1, x2, y2, self.getBGColor())
                self.drawClippedRectangle(x1, y1, x2, y2, self._getcolor(color))
        else:
            self.fillClippedRectangle(x1, y1, x2, y2, color)

    def draw_circle(self, x, y, radius, color):
        self.drawCircle(x, y, radius, self._getcolor(color))

    def fill_circle(self, x, y, radius, color):
        if self._is_grey:
            if self._factor:
                self.fillCircle(x, y, radius, self._getcolor(color))
            else: # greyed out controls drawn as skeleton on screen bgcolor
                self.fillCircle(x, y, radius, self.getBGColor())
                self.drawCircle(x, y, radius, self._getcolor(color))
        else:
            self.fillCircle(x, y, radius, color)

    def draw_vline(self, x, y, l, color):
        self.drawVLine(x, y, l, self._getcolor(color))

    def draw_hline(self, x, y, l, color):
        self.drawHLine(x, y, l, self._getcolor(color))

    def draw_line(self, x1, y1, x2, y2, color):
        self.drawLine(x1, y1, x2, y2, self._getcolor(color))

# *********** BASE CLASSES ***********

class GUI(object):
    tft = None
    objtouch = None
    objsched = None
    @classmethod
    def setup(cls, objsched, tft, objtouch):
        cls.objsched = objsched
        cls.objtouch = objtouch
        cls.tft = tft

    @classmethod
    def get_tft(cls, greyed_out=False):
        cls.tft.usegrey(greyed_out)
        return cls.tft

    @classmethod
    def set_grey_style(cls, *, color=GREY, factor=0):
        cls.tft.grey_color(color = color, factor = factor)
        for obj in Screen.current_screen.displaylist:
            if obj.enabled and obj.greyed_out():
                obj.redraw = True # Redraw static content
                obj.draw_border()
                obj.show()

class Screen(GUI):
    current_screen = None

    @classmethod
    def show(cls):
        for obj in cls.current_screen.displaylist:
            if obj.enabled: # In a buttonlist only show enabled button
                obj.redraw = True # Redraw static content
                obj.draw_border()
                obj.show()

    @classmethod
    def change(cls, new_screen, forward=True):
        if forward:
            new_screen.parent = cls.current_screen
        cls.current_screen = new_screen
        cls.tft.clrSCR()
        cls.show()

    @classmethod
    def back(cls):
        parent = cls.current_screen.parent
        if parent is not None:
            cls.change(parent, False)

    @classmethod
    def addobject(cls, obj):
        if isinstance(obj, Touchable):
            cls.current_screen.touchlist.append(obj)
        cls.current_screen.displaylist.append(obj)

    @classmethod
    def _touchtest(cls): # Singleton thread tests all touchable instances
        touch_panel = cls.objtouch
        while True:
            yield
            if touch_panel.ready:
                x, y = touch_panel.get_touch_async()
                for obj in Screen.current_screen.touchlist:
                    if obj.enabled and not obj.greyed_out():
                        obj._trytouch(x, y)
            elif not touch_panel.touched:
                for obj in Screen.current_screen.touchlist:
                    if obj.was_touched:
                        obj.was_touched = False # Call _untouched once only
                        obj.busy = False
                        obj._untouched()

    def __init__(self):
        self.touchlist = []
        self.displaylist = []
        if Screen.current_screen is None: # Initialising class and thread
            objsched = GUI.objsched
            if objsched is None:
                raise OSError('GUI class is not initialised.')
            objsched.add_thread(self._touchtest()) # One thread only
        Screen.current_screen = self
        self.parent = None

    def run(self):
        self.current_screen = self
        self.show()
        self.objsched.run()

# Base class for all displayable objects
class NoTouch(object):
    def __init__(self, location, font, height, width, fgcolor, bgcolor, fontcolor, border):
        Screen.addobject(self)
        self.location = location
        self.font = font
        self.height = height
        self.width = width
        self.fill = bgcolor is not None
        self.enabled = True # Available to user/subclass
        self._greyed_out = False
        tft = GUI.get_tft(False)
        self.fgcolor = fgcolor if fgcolor is not None else tft.getColor()
        self.bgcolor = bgcolor if bgcolor is not None else tft.getBGColor()
        self.fontcolor = fontcolor if fontcolor is not None else tft.getColor()
        self.hasborder = border is not None
        self.border = 0 if border is None else border

    def greyed_out(self):
        return self._greyed_out # Subclass may be greyed out

# Called by Screen.show(). Draw background and bounding box if required
    def draw_border(self):
        tft = GUI.get_tft(self.greyed_out())
        x = self.location[0]
        y = self.location[1]
        if self.fill:
            tft.fill_rectangle(x, y, x + self.width, y + self.height, self.bgcolor)
        if self.hasborder: # Draw a bounding box
            tft.draw_rectangle(x, y, x + self.width, y + self.height, self.fgcolor)
        return self.border if self.hasborder else 0 # border width in pixels

# Base class for touch-enabled classes.
class Touchable(NoTouch):
    def __init__(self, location, font, height, width, fgcolor, bgcolor, fontcolor, border, can_drag):
        super().__init__(location, font, height, width, fgcolor, bgcolor, fontcolor, border)
        self.can_drag = can_drag
        self.busy = False
        self.was_touched = False
        self.redraw = True # Force drawing of static part of image

    def greyed_out(self, val=None):
        if val is not None and self._greyed_out != val:
            self._greyed_out = val
            GUI.get_tft(self.greyed_out())
            self.draw_border()
            self.redraw = True
            self.show()
        return self._greyed_out

    def _trytouch(self, x, y): # If touched in bounding box, process it otherwise do nothing
        x0 = self.location[0]
        x1 = self.location[0] + self.width
        y0 = self.location[1]
        y1 = self.location[1] + self.height
        if x0 <= x <= x1 and y0 <= y <= y1:
            self.was_touched = True
            if not self.busy or self.can_drag:
                self._touched(x, y) # Called repeatedly for draggable objects
                self.busy = True # otherwise once only

    def _untouched(self): # Default if not defined in subclass
        pass

# *********** DISPLAYS: NON-TOUCH CLASSES FOR DATA DISPLAY ***********

class Label(NoTouch):
    def __init__(self, location, *, font, border=None, width, fgcolor=None, bgcolor=None, fontcolor=None, text=''):
        super().__init__(location, font, None, width, fgcolor, bgcolor, fontcolor, border)
        self.height = self.font.bits_vert
        self.height += 2 * self.border  # Height determined by font and border
        self.text = text

    def show(self, text=None):
        tft = GUI.get_tft(self.greyed_out())
        bw = self.border
        if text is not None:
            self.text = text
        else:
            text = self.text
        if text:
            x = self.location[0]
            y = self.location[1]
            tft.fill_rectangle(x + bw, y + bw, x + self.width - bw, y + self.height - bw, self.bgcolor)
            print_left(tft, x + bw, y + bw, text, self.fontcolor, self.font, self.width - 2 * bw)

# class displays angles. Angle 0 is vertical, +ve increments are clockwise.
class Dial(NoTouch):
    def __init__(self, location, *, height=100, fgcolor=None, bgcolor=None, border=None, pointers=(0.9,), ticks=4):
        NoTouch.__init__(self, location, None, height, height, fgcolor, bgcolor, None, border) # __super__ provoked Python bug
        border = self.border # border width
        radius = height / 2 - border
        self.radius = radius
        self.ticks = ticks
        self.xorigin = location[0] + border + radius
        self.yorigin = location[1] + border + radius
        self.pointers = tuple(z * self.radius for z in pointers) # Pointer lengths
        self.angles = [None for _ in pointers]

    def show(self, angle=None, pointer=0):
        tft = GUI.get_tft(self.greyed_out())
        ticks = self.ticks
        radius = self.radius
        ticklen = 0.1 * radius
        for tick in range(ticks):
            theta = 2 * tick * math.pi / ticks
            x_start = int(self.xorigin + radius * math.sin(theta))
            y_start = int(self.yorigin - radius * math.cos(theta))
            x_end = int(self.xorigin + (radius - ticklen) * math.sin(theta))
            y_end = int(self.yorigin - (radius - ticklen) * math.cos(theta))
            tft.draw_line(x_start, y_start, x_end, y_end, self.fgcolor)
        tft.draw_circle(self.xorigin, self.yorigin, radius, self.fgcolor)

        if self.angles[pointer] is not None:
            self._drawpointer(self.angles[pointer], pointer, self.bgcolor) # erase old
        if angle is not None:
            self._drawpointer(angle, pointer, self.fgcolor) # draw new
            self.angles[pointer] = angle # update old

    def _drawpointer(self, radians, pointer, color):
        tft = GUI.get_tft(self.greyed_out())
        length = self.pointers[pointer]
        x_end = int(self.xorigin + length * math.sin(radians))
        y_end = int(self.yorigin - length * math.cos(radians))
        tft.draw_line(int(self.xorigin), int(self.yorigin), x_end, y_end, color)

class LED(NoTouch):
    def __init__(self, location, *, border=None, height=30, fgcolor=None, bgcolor=None, color=RED):
        super().__init__(location, None, height, height, fgcolor, bgcolor, None, border)
        self.radius = (self.height - 2 * self.border) / 2
        self.x = location[0] + self.radius + self.border
        self.y = location[1] + self.radius + self.border
        self.color = color

    def show(self, color=BLACK): # Light the LED 
        tft = GUI.get_tft(self.greyed_out())
        tft.fill_circle(int(self.x), int(self.y), int(self.radius), color)
        tft.draw_circle(int(self.x), int(self.y), int(self.radius), self.fgcolor)

    def on(self, color=None): # Light in current color
        if color is not None:
            self.color = color
        self.show(self.color)

    def off(self):
        self.show(BLACK)

class Meter(NoTouch):
    def __init__(self, location, *, font=None, height=200, width=30,
                 fgcolor=None, bgcolor=None, pointercolor=None, fontcolor=None,
                 divisions=10, legends=None, value=0):
        border = 5 if font is None else 1 + font.bits_vert / 2
        NoTouch.__init__(self, location, font, height, width, fgcolor, bgcolor, fontcolor, border) # __super__ provoked Python bug
        border = self.border # border width
        self.ptrbytes = 3 * (self.width + 1) # 3 bytes per pixel
        self.ptrbuf = bytearray(self.ptrbytes) #???
        self.x0 = self.location[0]
        self.x1 = self.location[0] + self.width
        self.y0 = self.location[1] + border + 2
        self.y1 = self.location[1] + self.height - border
        self.divisions = divisions
        self.legends = legends
        self.pointercolor = pointercolor if pointercolor is not None else fgcolor
        self._value = value
        self._old_value = -1 # invalidate
        self.ptr_y = -1 # Invalidate old position
        self.show()

    def show(self):
        tft = GUI.get_tft(self.greyed_out())
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

        y0 = self.ptr_y
        y1 = y0
        if self.ptr_y >= 0: # Restore background
            tft.setXY(x0, y0, x1, y1)
            TFT_io.tft_write_data_AS(self.ptrbuf, self.ptrbytes)
        ptrpos = int(self.y1 - self._value * height)
        y0 = ptrpos
        y1 = ptrpos
        tft.setXY(x0, y0, x1, y1) # Read background
        TFT_io.tft_read_cmd_data_AS(0x2e, self.ptrbuf, self.ptrbytes)
        self.ptr_y = y0
        tft.draw_hline(x0, y0, width, self.pointercolor) # Draw pointer

    def value(self, val=None):
        if val is not None:
            self._value = min(max(val, 0.0), 1.0)
            if self._value != self._old_value:
                self._old_value = self._value
                self.show()
        return self._value

class IconGauge(NoTouch):
    def __init__(self, location, *, icon_module, initial_icon=0):
        NoTouch.__init__(self, location, None, icon_module.height, icon_module.width, None, None, None, None)
        self.draw = icon_module.draw
        self.num_icons = len(icon_module._icons)
        self.state = initial_icon
        self._value = initial_icon / self.num_icons

    def show(self):
        tft = GUI.get_tft(self.greyed_out())
        x = self.location[0]
        y = self.location[1]
        self.draw(x, y, self.state, tft.drawBitmap)

    def icon(self, icon_index): # select icon by index
        if icon_index >= self.num_icons or icon_index < 0: 
            raise ugui_exception('Invalid icon index {}'.format(icon_index))
        else:
            self.state = int(icon_index)
            self.show()

    def value(self, val=None): # Float
        if val is not None:
            self._value = max(min(val, 1.0), 0.0)
            self.state = min(int(self._value * self.num_icons), self.num_icons -1)
            self.show()
        return self._value

# *********** PUSHBUTTON AND CHECKBOX CLASSES ***********

# Button coordinates relate to bounding box (BB). x, y are of BB top left corner.
# likewise width and height refer to BB, regardless of button shape
# If font is None button will be rendered without text

class Button(Touchable):
    lit_time = 1
    long_press_time = 1
    def __init__(self, location, *, font, shape=CIRCLE, height=50, width=50, fill=True,
                 fgcolor=None, bgcolor=None, fontcolor=None, litcolor=None, text='',
                 callback=dolittle, args=[], onrelease=False, lp_callback=None, lp_args=[]):
        super().__init__(location, font, height, width, fgcolor, bgcolor, fontcolor, None, False)
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
            self.delay = Delay(GUI.objsched, self.shownormal)
        self.litcolor = litcolor if self.fgcolor is not None else None

    def show(self):
        tft = GUI.get_tft(self.greyed_out())
        x = self.location[0]
        y = self.location[1]
        if not self.enabled:   # erase the button
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
        self.show()

    def _touched(self, x, y): # Process touch
        if self.litcolor is not None:
            self.fgcolor = self.litcolor
            self.show()
            self.delay.trigger(Button.lit_time)
        if self.lp_callback is not None:
            GUI.objsched.add_thread(self.longpress())
        if not self.onrelease:
            self.callback(self, *self.callback_args) # Callback not a bound method so pass self

    def _untouched(self):
        self.lp = False
        if self.onrelease:
            self.callback(self, *self.callback_args) # Callback not a bound method so pass self

    def longpress(self):
        self.lp = True
        yield
        yield self.long_press_time
        if self.lp:
            self.lp_callback(self, *self.lp_args)

# Group of buttons, typically at same location, where pressing one shows
# the next e.g. start/stop toggle or sequential select from short list
class ButtonList(object):
    def __init__(self, callback=dolittle):
        self.user_callback = callback
        self.lstbuttons = []
        self.current = None # No current button
        self._greyed_out = False

    def add_button(self, *args, **kwargs):
        button = Button(*args, **kwargs)
        self.lstbuttons.append(button)
        active = self.current is None # 1st button added is active
        button.enabled = active
        button.callback = self._callback
        if active:
            self.current = button
        return button

    def value(self, button=None):
        if button is not None and button is not self.current:
            old = self.current
            new = button
            self.current = new
            old.enabled = False
            old.show()
            new.enabled = True
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
        old.enabled = False
        old.show()
        new.enabled = True
        new.busy = True # Don't respond to continued press
        new.show()
        self.user_callback(new, *args) # user gets button with args they specified

# Group of buttons at different locations, where pressing one shows
# only current button highlighted and oes callback from current one
class RadioButtons(object):
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

class Checkbox(Touchable):
    def __init__(self, location, *, height=30, fillcolor=None,
                 fgcolor=None, bgcolor=None, callback=dolittle, args=[], value=False, border=None):
        super().__init__(location, None, height, height, fgcolor, bgcolor, None, border, False)
        self.callback = callback
        self.callback_args = args
        self.fillcolor = fillcolor
        self._value = value
        self.initialised = False

    def show(self):
        if not self.initialised:
            self.initialised = True
            value = self._value # As passed to ctor
            if value is None:
                self._value = False # special case: don't execute callback on initialisation
            else:
                self._value = not value # force redraw
                self.value(value)
                return
        self._show()

    def _show(self):
        tft = GUI.get_tft(self.greyed_out())
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

    def value(self, val=None):
        if val is not None:
            val = bool(val)
            if val != self._value:
                self._value = val
                self.callback(self, *self.callback_args) # Callback not a bound method so pass self
                self._show()
        return self._value

    def _touched(self, x, y): # Was touched
        self.value(not self._value) # Upddate and refresh

# Button/checkbox whose appearance is defined by icon bitmaps

class IconButton(Touchable):
    long_press_time = 1
    def __init__(self, location, *, icon_module, flash=0, toggle=False, state=0,
                 callback=dolittle, args=[], onrelease=False, lp_callback=None, lp_args=[]):
        self.draw = icon_module.draw
        self.num_icons = len(icon_module._icons)
        super().__init__(location, None, icon_module.height,
                         icon_module.width, None, None, None, None, False)
        self.callback = callback
        self.callback_args = args
        self.onrelease = onrelease
        self.lp_callback = lp_callback
        self.lp_args = lp_args
        self.lp = False # Long press not in progress
        self.flash = flash
        self.toggle = toggle
        if state >= self.num_icons or state < 0:
            raise ugui_exception('Invalid icon index {}'.format(state))
        self.state = state
        if self.flash > 0:
            if self.num_icons < 2:
                raise ugui_exception('Need > 1 icon for flashing button')
            self.delay = Delay(GUI.objsched, self._show, (0,))

    def show(self):
        self._show(self.state)

    def _show(self, state):
        tft = GUI.get_tft(self.greyed_out())
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
            GUI.objsched.add_thread(self.longpress())
        if not self.onrelease:
            self.callback(self, *self.callback_args) # Callback not a bound method so pass self

    def _untouched(self):
        self.lp = False
        if self.onrelease:
            self.callback(self, *self.callback_args) # Callback not a bound method so pass self

    def longpress(self):
        self.lp = True
        yield
        yield self.long_press_time
        if self.lp:
            self.lp_callback(self, *self.lp_args)

# Group of buttons at different locations, where pressing one shows
# only current button highlighted and does callback from current one
class IconRadioButtons(object):
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

# *********** SLIDER CLASSES ***********
# A slider's text items lie outside its bounding box (area sensitive to touch)

class Slider(Touchable):
    def __init__(self, location, *, font=None, height=200, width=30, divisions=10, legends=None,
                 fgcolor=None, bgcolor=None, fontcolor=None, slidecolor=None, border=None, 
                 cb_end=dolittle, cbe_args=[], cb_move=dolittle, cbm_args=[], value=0.0):
        width &= 0xfe # ensure divisible by 2
        super().__init__(location, font, height, width, fgcolor, bgcolor, fontcolor, border, True)
        self.divisions = divisions
        self.legends = legends if font is not None else None
        self.slidecolor = slidecolor
        self.cb_end = cb_end
        self.cbe_args = cbe_args
        self.cb_move = cb_move
        self.cbm_args = cbm_args
        slidewidth = int(width / 1.3) & 0xfe # Ensure divisible by 2
        self.slideheight = 6 # must be divisible by 2
                             # We draw an odd number of pixels:
        self.slidebytes = (self.slideheight + 1) * (slidewidth + 1) * 3
        self.slidebuf = bytearray(self.slidebytes)
        self._old_value = -1 # Invalidate
        b = self.border
        self.pot_dimension = self.height - 2 * (b + self.slideheight // 2)
        width = self.width - 2 * b
        xcentre = self.location[0] + b + width // 2
        self.slide_x0 = xcentre - slidewidth // 2
        self.slide_x1 = xcentre + slidewidth // 2 # slide X coordinates
        self.slide_y = -1 # Invalidate old position
        self.value(value)

    def show(self):
        tft = GUI.get_tft(self.greyed_out())
        bw = self.border
        x = self.location[0] + bw
        y = self.location[1] + bw + self.slideheight // 2 # Allow space above and below slot
        width = self.width - 2 * bw
        height = self.pot_dimension # Height of slot
        dx = width // 2 - 2 
        tft.draw_rectangle(x + dx, y, x + width - dx, y + height, self.fgcolor)

        if self.divisions > 0:
            dy = height / (self.divisions) # Tick marks
            for tick in range(self.divisions + 1):
                ypos = int(y + dy * tick)
                tft.draw_hline(x + 1, ypos, dx, self.fgcolor)
                tft.draw_hline(x + 2 + width // 2, ypos, dx, self.fgcolor) # Add half slot width

        if self.legends is not None: # Legends
            if len(self.legends) <= 1:
                dy = 0
            else:
                dy = height / (len(self.legends) -1)
            yl = y + height # Start at bottom
            fhdelta = self.font.bits_vert / 2
            for legend in self.legends:
                print_left(tft, x + self.width, int(yl - fhdelta), legend, self.fontcolor, self.font)
                yl -= dy

        sh = self.slideheight # Handle slider
        x0 = self.slide_x0
        y0 = self.slide_y
        x1 = self.slide_x1
        y1 = y0 + sh
        if self.slide_y >= 0: # Restore background
            tft.setXY(x0, y0, x1, y1)
            TFT_io.tft_write_data_AS(self.slidebuf, self.slidebytes)
        sliderpos = int(y + height - self._value * height)
        y0 = sliderpos - sh // 2
        y1 = sliderpos + sh // 2
        tft.setXY(x0, y0, x1, y1) # Read background
        TFT_io.tft_read_cmd_data_AS(0x2e, self.slidebuf, self.slidebytes)
        self.slide_y = y0
        color = self.slidecolor if self.slidecolor is not None else self.fgcolor
        tft.fill_rectangle(x0, y0, x1, y1, color) # Draw slider

    def value(self, val=None, color=None):
        if color is not None and color != self.fgcolor:
            self.fgcolor = color
            self.show() # save new underlying color
        if val is not None:
            self._value = min(max(val, 0.0), 1.0)
            if self._value != self._old_value:
                self._old_value = self._value
                self.cb_move(self, *self.cbm_args) # Callback not a bound method so pass self
                self.show()
        return self._value

    def _touched(self, x, y): # Touched in bounding box. A drag will call repeatedly.
        self.value((self.location[1] + self.height - y) / self.pot_dimension)

    def _untouched(self): # User has released touchpad or touched elsewhere
        self.cb_end(self, *self.cbe_args) # Callback not a bound method so pass self

class HorizSlider(Touchable):
    def __init__(self, location, *, font=None, height=30, width=200, divisions=10, legends=None,
                 fgcolor=None, bgcolor=None, fontcolor=None, slidecolor=None, border=None, 
                 cb_end=dolittle, cbe_args=[], cb_move=dolittle, cbm_args=[], value=0.0):
        height &= 0xfe # ensure divisible by 2
        super().__init__(location, font, height, width, fgcolor, bgcolor, fontcolor, border, True)
        self.divisions = divisions
        self.legends = legends if font is not None else None
        self.slidecolor = slidecolor
        self.cb_end = cb_end
        self.cbe_args = cbe_args
        self.cb_move = cb_move
        self.cbm_args = cbm_args
        slideheight = int(height / 1.3) & 0xfe # Ensure divisible by 2
        self.slidewidth = 6 # must be divisible by 2
                             # We draw an odd number of pixels:
        self.slidebytes = (slideheight + 1) * (self.slidewidth + 1) * 3
        self.slidebuf = bytearray(self.slidebytes)
        self._old_value = -1 # Invalidate
        b = self.border
        self.pot_dimension = self.width - 2 * (b + self.slidewidth // 2)
        height = self.height - 2 * b
        ycentre = self.location[1] + b + height // 2
        self.slide_y0 = ycentre - slideheight // 2
        self.slide_y1 = ycentre + slideheight // 2 # slide Y coordinates
        self.slide_x = -1 # Invalidate old position
        self.value(value)

    def show(self):
        tft = GUI.get_tft(self.greyed_out())
        bw = self.border
        x = self.location[0] + bw + self.slidewidth // 2 # Allow space left and right slot for slider at extremes
        y = self.location[1] + bw
        height = self.height - 2 * bw
        width = self.pot_dimension # Length of slot
        dy = height // 2 - 2 # slot is 4 pixels wide
        tft.draw_rectangle(x, y + dy, x + width, y + height - dy, self.fgcolor)

        if self.divisions > 0:
            dx = width / (self.divisions) # Tick marks
            for tick in range(self.divisions + 1):
                xpos = int(x + dx * tick)
                tft.draw_vline(xpos, y + 1, dy, self.fgcolor) # TODO Why is +1 fiddle required here?
                tft.draw_vline(xpos, y + 2 + height // 2,  dy, self.fgcolor) # Add half slot width

        if self.legends is not None: # Legends
            if len(self.legends) <= 1:
                dx = 0
            else:
                dx = width / (len(self.legends) -1)
            xl = x
            for legend in self.legends:
                offset = get_stringsize(legend, self.font)[0] / 2
                print_left(tft, int(xl - offset), y - self.font.bits_vert, legend, self.fontcolor, self.font)
                xl += dx

        sw = self.slidewidth # Handle slider
        x0 = self.slide_x
        y0 = self.slide_y0
        x1 = x0 + sw
        y1 = self.slide_y1
        if self.slide_x >= 0: # Restore background
            tft.setXY(x0, y0, x1, y1)
            TFT_io.tft_write_data_AS(self.slidebuf, self.slidebytes)
        sliderpos = int(x + self._value * width)
        x0 = sliderpos - sw // 2
        x1 = sliderpos + sw // 2
        tft.setXY(x0, y0, x1, y1) # Read background
        TFT_io.tft_read_cmd_data_AS(0x2e, self.slidebuf, self.slidebytes)
        self.slide_x = x0
        color = self.slidecolor if self.slidecolor is not None else self.fgcolor
        tft.fill_rectangle(x0, y0, x1, y1, color) # Draw slider

    def value(self, val=None, color=None):
        if color is not None and color != self.fgcolor:
            self.fgcolor = color
            self.show() # save new underlying color
        if val is not None:
            self._value = min(max(val, 0.0), 1.0)
            if self._value != self._old_value:
                self._old_value = self._value
                self.cb_move(self, *self.cbm_args) # Callback not a bound method so pass self
                self.show()
        return self._value

    def _touched(self, x, y): # Touched in bounding box. A drag will call repeatedly.
        self.value((x - self.location[0]) / self.pot_dimension)

    def _untouched(self): # User has released touchpad or touched elsewhere
        self.cb_end(self, *self.cbe_args) # Callback not a bound method so pass self

# *********** CONTROL KNOB CLASS ***********

class Knob(Touchable):
    def __init__(self, location, *, height=100, arc=TWOPI, ticks=9, value=0.0,
                 fgcolor=None, bgcolor=None, color=None, border=None,
                 cb_end=dolittle, cbe_args=[], cb_move=dolittle, cbm_args=[]):
        Touchable.__init__(self, location, None, height, height, fgcolor, bgcolor, None, border, True)
        border = self.border # Geometry: border width
        radius = height / 2 - border
        self.arc = min(max(arc, 0), TWOPI) # Usable angle of control
        self.radius = radius
        self.xorigin = location[0] + border + radius
        self.yorigin = location[1] + border + radius
        self.ticklen = 0.1 * radius
        self.pointerlen = radius - self.ticklen - 5
        self.ticks = max(ticks, 2) # start and end of travel

        self.cb_end = cb_end # Callbacks
        self.cbe_args = cbe_args
        self.cb_move = cb_move
        self.cbm_args = cbm_args

        self._old_value = None # data: invalidate
        self.initial_value = value
        self._value = -1
        self.color = color

    def show(self):
        tft = GUI.get_tft(self.greyed_out())
        if self._value == -1 or self.redraw: # Initialising
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
            if self._value == -1:
                self.value(self.initial_value) # recurse
                return # so I'm out of here
        if self._old_value is not None: # An old pointer needs erasing
            if self.greyed_out() and tft.skeleton():
                tft.usegrey(False) # greyed out 'skeleton' style
                color = tft.getBGColor() # erase to screen background
            else:
                color = self.bgcolor if self.color is None else self.color # Fill color
            self._drawpointer(self._old_value, color) # erase old
            GUI.get_tft(self.greyed_out()) # Reset GUI greyed-out status

        self._drawpointer(self._value, self.fgcolor) # draw new
        self._old_value = self._value # update old

    def value(self, val=None):
        if val is not None:
            val = min(max(val, 0.0), 1.0)
            if val != self._value:
                self._value = val  # Update value for callback
                self.cb_move(self, *self.cbm_args) # Callback not a bound method so pass self
                self.show()
        return self._value

    def _touched(self, x, y): # Touched in bounding box. A drag will call repeatedly.
        dy = self.yorigin - y
        dx = x - self.xorigin
        if (dx**2 + dy**2) / self.radius**2 < 0.5:
            return # vector too short
        alpha = math.atan2(dx, dy) # axes swapped: orientate relative to vertical
        arc = self.arc
        alpha = min(max(alpha, -arc / 2), arc / 2) + arc / 2
        self.value(alpha /arc)

    def _untouched(self): # User has released touchpad or touched elsewhere
        self.cb_end(self, *self.cbe_args) # Callback not a bound method so pass self

    def _drawpointer(self, value, color):
        tft = GUI.get_tft(self.greyed_out())
        arc = self.arc
        length = self.pointerlen
        angle = value * arc - arc / 2
        x_end = int(self.xorigin + length * math.sin(angle))
        y_end = int(self.yorigin - length * math.cos(angle))
        tft.draw_line(int(self.xorigin), int(self.yorigin), x_end, y_end, color)
