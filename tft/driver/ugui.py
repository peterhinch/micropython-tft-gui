# ugui.py Micropython GUI library for TFT displays
# Adapted for (and requires) uasyncio V3

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2016-2020 Peter Hinch

import uasyncio as asyncio
import math
import gc
from tft.driver import TFT_io
from tft.primitives.delay_ms import Delay_ms
from tft.driver.tft import TFT
from tft.driver.constants import *

__version__ = (0, 7, 0)

TWOPI = 2 * math.pi
gc.collect()

# *********** UTILITY FUNCTIONS ***********

class _A():
    pass

ClassType = type(_A)

async def _g():
    pass
type_coro = type(_g())


class ugui_exception(Exception):
    pass

# replaces lambda *_ : None owing to issue #2023 (long ago fixed)
def dolittle(*_):
    pass

def get_stringsize(s, font):
    hor = 0
    for c in s:
        _, vert, cols = font.get_ch(c)
        hor += cols
    return hor, vert

def print_centered(tft, x, y, s, color, font, clip=False, scroll=False):
    old_style = tft.getTextStyle()
    length, height = get_stringsize(s, font)
    tft.setTextStyle(color, None, 2, font)
    tft.setTextPos(max(x - length // 2, 0), max(y - height // 2, 0), clip, scroll)
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

def desaturate(color, factor): # Desaturate and dim
    if color is not None:
        f = int(max(color) / factor)
        return (f, f, f)

# *********** TFT_G CLASS ************
# Subclass TFT to enable greying out of controls
# Some TFT methods call drawHLine and drawVLine: the bound variable 'raw` forces them
# to use the color of the calling method
class TFT_G(TFT):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._is_grey = False
        self._desaturate = True
        self._factor = 2 # Default grey-out methd: dim colors

    def _getcolor(self, color):
        if self._is_grey:
            if self._desaturate:
                color = desaturate(color, self._factor)
            else:
                color = dim(color, self._factor)
        return color

    def desaturate(self, value=None):
        if value is not None:
            self._desaturate = value
        return self._desaturate

    def dim(self, factor=None):
        if factor is not None:
            if factor <= 1:
                raise ValueError('Dim factor must be > 1')
            self._factor = factor
        return self._factor

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

class Screen:
    current_screen = None
    tft = None
    objtouch = None
    is_shutdown = asyncio.Event()

    @classmethod
    def setup(cls, tft, objtouch):
        cls.objtouch = objtouch
        cls.tft = tft

# get_tft() when called from user code, ensure greyed_out status is updated.
    @classmethod
    def get_tft(cls, greyed_out=False):
        cls.tft.usegrey(greyed_out)
        return cls.tft

    @classmethod
    def set_grey_style(cls, *, desaturate=True, factor=2):
        cls.tft.dim(factor)
        cls.tft.desaturate(desaturate)
        if Screen.current_screen is not None: # Can call before instantiated
            for obj in Screen.current_screen.displaylist:
                if obj.visible and obj.greyed_out():
                    obj.redraw = True # Redraw static content
                    obj.draw_border()
                    obj.show()

    @classmethod
    def show(cls):
        for obj in cls.current_screen.displaylist:
            if obj.visible: # In a buttonlist only show visible button
                obj.redraw = True # Redraw static content
                obj.draw_border()
                obj.show()

    @classmethod
    def change(cls, cls_new_screen, *, forward=True, args=[], kwargs={}):
        init = cls.current_screen is None
        if init:
            Screen() # Instantiate a blank starting screen
        else:  # About to erase an existing screen
            for entry in cls.current_screen.tasklist:
                if entry[1]:  # To be cancelled on screen change
                    entry[0].cancel()
        cs_old = cls.current_screen
        cs_old.on_hide() # Optional method in subclass
        if forward:
            if isinstance(cls_new_screen, ClassType):
                new_screen = cls_new_screen(*args, **kwargs) # Instantiate new screen
            else:
                raise ValueError('Must pass Screen class or subclass (not instance)')
            new_screen.parent = cs_old
            cs_new = new_screen
        else:
            cs_new = cls_new_screen # An object, not a class
        cls.current_screen = cs_new
        cs_new.on_open() # Optional subclass method
        cs_new._do_open(cs_old) # Clear and redraw
        cs_new.after_open() # Optional subclass method
        if init:
            try:
                asyncio.run(Screen.monitor())  # Starts and ends uasyncio
            finally:
                asyncio.new_event_loop()
                gc.collect()

    @classmethod
    async def monitor(cls):
        await cls.is_shutdown.wait()
        cls.is_shutdown.clear()
        for entry in cls.current_screen.tasklist:
            entry[0].cancel()
        await asyncio.sleep_ms(0)  # Allow subclass to cancel tasks
        cls.tft.clrSCR()
        cls.current_screen = None  # Ensure another demo can run

    @classmethod
    def back(cls):
        parent = cls.current_screen.parent
        if parent is not None:
            cls.change(parent, forward = False)

    @classmethod
    def addobject(cls, obj):
        if cls.current_screen is None:
            raise OSError('You must create a Screen instance')
        if isinstance(obj, Touchable):
            cls.current_screen.touchlist.append(obj)
        cls.current_screen.displaylist.append(obj)

    @classmethod
    def shutdown(cls):
        cls.is_shutdown.set()

    def __init__(self):
        self.touchlist = []
        self.displaylist = []
        self.tasklist = []  # Allow instance to register tasks for shutdown
        self.modal = False
        if Screen.current_screen is None: # Initialising class and task
            asyncio.create_task(self._touchtest()) # One task only
            asyncio.create_task(self._garbage_collect())
        Screen.current_screen = self
        self.parent = None

    async def _touchtest(self): # Singleton task tests all touchable instances
        touch_panel = Screen.objtouch
        while True:
            await asyncio.sleep_ms(0)
            if touch_panel.ready:
                x, y = touch_panel.get_touch_async()
                for obj in Screen.current_screen.touchlist:
                    if obj.visible and not obj.greyed_out():
                        obj._trytouch(x, y)
            elif not touch_panel.touched:
                for obj in Screen.current_screen.touchlist:
                    if obj.was_touched:
                        obj.was_touched = False # Call _untouched once only
                        obj.busy = False
                        obj._untouched()

    def _do_open(self, old_screen): # Aperture overrides
        show_all = True
        tft = Screen.get_tft()
# If opening a Screen from an Aperture just blank and redraw covered area
        if old_screen.modal:
            show_all = False
            x0, y0, x1, y1 = old_screen._list_dims()
            tft.fill_rectangle(x0, y0, x1, y1, tft.getBGColor()) # Blank to screen BG
            for obj in [z for z in self.displaylist if z.overlaps(x0, y0, x1, y1)]:
                if obj.visible:
                    obj.redraw = True # Redraw static content
                    obj.draw_border()
                    obj.show()
# Normally clear the screen and redraw everything
        else:
            tft.clrSCR()
            Screen.show()

    def on_open(self): # Optionally implemented in subclass
        return

    def after_open(self): # Optionally implemented in subclass
        return

    def on_hide(self): # Optionally implemented in subclass
        return

    def reg_task(self, task, on_change=False):  # May be passed a coro or a Task
        if isinstance(task, type_coro):
            task = asyncio.create_task(task)
        self.tasklist.append([task, on_change])

    async def _garbage_collect(self):
        while True:
            await asyncio.sleep_ms(100)
            gc.collect()
            gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())

# Very basic window class. Cuts a rectangular hole in a screen on which content may be drawn
class Aperture(Screen):
    _value = None
    def __init__(self, location, height, width, *, draw_border=True, bgcolor=None, fgcolor=None):
        Screen.__init__(self)
        self.location = location
        self.height = height
        self.width = width
        self.draw_border = draw_border
        self.modal = True
        tft = Screen.get_tft()
        self.fgcolor = fgcolor if fgcolor is not None else tft.getColor()
        self.bgcolor = bgcolor if bgcolor is not None else tft.getBGColor()

    def locn(self, x, y):
        return (self.location[0] + x, self.location[1] + y)

    def _do_open(self, old_screen):
        tft = Screen.get_tft()
        x, y = self.location[0], self.location[1]
        tft.fill_rectangle(x, y, x + self.width, y + self.height, self.bgcolor)
        if self.draw_border:
            tft.draw_rectangle(x, y, x + self.width, y + self.height, self.fgcolor)
        Screen.show()

    def _list_dims(self):
        x0 = self.location[0]
        x1 = self.location[0] + self.width
        y0 = self.location[1]
        y1 = self.location[1] + self.height
        return x0, y0, x1, y1

    @classmethod
    def value(cls, val=None): # Mechanism for testing the outcome of a dialog box
        if val is not None:
            cls._value = val
        return cls._value

# Base class for all displayable objects
class NoTouch:
    def __init__(self, location, font, height, width, fgcolor, bgcolor, fontcolor, border, value, initial_value):
        Screen.addobject(self)
        self.screen = Screen.current_screen
        self.redraw = True # Force drawing of static part of image
        self.location = location
        self._value = value
        self._initial_value = initial_value # Optionally enables show() method to handle initialisation
        self.font = font
        self.height = height
        self.width = width
        self.fill = bgcolor is not None
        self.visible = True # Used by ButtonList class for invisible buttons
        self._greyed_out = False # Disabled by user code
        tft = Screen.get_tft(False) # Not greyed out
        self.fgcolor = fgcolor if fgcolor is not None else tft.getColor()
        self.bgcolor = bgcolor if bgcolor is not None else tft.getBGColor()
        self.fontcolor = fontcolor if fontcolor is not None else tft.getColor()
        self.border = 0 if border is None else int(max(border, 0)) # width
        self.callback = dolittle # Value change callback
        self.args = []
        self.cb_end = dolittle # Touch release callbacks
        self.cbe_args = []

    @property
    def tft(self):
        return Screen.get_tft(self._greyed_out)

    def greyed_out(self):
        return self._greyed_out # Subclass may be greyed out

    def value(self, val=None, show=True): # User method to get or set value
        if val is not None:
            if type(val) is float:
                val = min(max(val, 0.0), 1.0)
            if val != self._value:
                self._value = val
                self._value_change(show)
        return self._value

    def _value_change(self, show): # Optional override in subclass
        self.callback(self, *self.args) # CB is not a bound method. 1st arg is self
        if show:
            self.show_if_current()

    def show_if_current(self):
        if self.screen is Screen.current_screen:
            self.show()

# Called by Screen.show(). Draw background and bounding box if required
    def draw_border(self):
        if self.screen is Screen.current_screen:
            tft = self.tft
            x = self.location[0]
            y = self.location[1]
            if self.fill:
                tft.fill_rectangle(x, y, x + self.width, y + self.height, self.bgcolor)
            if self.border > 0: # Draw a bounding box
                tft.draw_rectangle(x, y, x + self.width, y + self.height, self.fgcolor)
        return self.border # border width in pixels

    def overlaps(self, xa, ya, xb, yb): # Args must be sorted: xb > xa and yb > ya
        x0 = self.location[0]
        y0 = self.location[1]
        x1 = x0 + self.width
        y1 = y0 + self.height
        if (ya <= y1 and yb >= y0) and (xa <= x1 and xb >= x0):
            return True
        return False

# Base class for touch-enabled classes.
class Touchable(NoTouch):
    def __init__(self, location, font, height, width, fgcolor, bgcolor, fontcolor, border, can_drag, value, initial_value):
        super().__init__(location, font, height, width, fgcolor, bgcolor, fontcolor, border, value, initial_value)
        self.can_drag = can_drag
        self.busy = False
        self.was_touched = False

    def _set_callbacks(self, cb, args, cb_end=None, cbe_args=None):
        self.callback = cb
        self.args = args
        if cb_end is not None:
            self.cb_end = cb_end
            self.cbe_args = cbe_args

    def greyed_out(self, val=None):
        if val is not None and self._greyed_out != val:
            self._greyed_out = val
            self.draw_border()
            self.redraw = True
            self.show_if_current()
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
        self.cb_end(self, *self.cbe_args) # Callback not a bound method so pass self
