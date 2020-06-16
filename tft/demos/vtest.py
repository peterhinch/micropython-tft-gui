# vtest.py Test/demo of VectorDial

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2019-2020 Peter Hinch

# Updated for uasyncio V3

import urandom
import time
from cmath import rect, pi
import uasyncio as asyncio

from tft.driver.ugui import Screen
from tft.driver.constants import *
from tft.driver.tft_local import setup

from tft.widgets.buttons import Button, ButtonList
from tft.widgets.label import Label
from tft.widgets.vectors import Pointer, VectorDial

from tft.fonts import font10, font14

def quitbutton(x=399, y=242):
    def quit(button):
        Screen.shutdown()
    Button((x, y), height = 30, font = font14, callback = quit, fgcolor = RED,
           text = 'Quit', shape = RECTANGLE, width = 80)

def fwdbutton(x, y, cls_screen, text='Next'):
    def fwd(button):
        Screen.change(cls_screen)
    Button((x, y), height = 30, font = font14, callback = fwd, fgcolor = RED,
           text = text, shape = RECTANGLE, width = 100)

def backbutton(x=399, y=242):
    def back(button):
        Screen.back()
    Button((x, y), height = 30, font = font14, fontcolor = BLACK, callback = back,
           fgcolor = CYAN,  text = 'Back', shape = RECTANGLE, width = 80)

class BackScreen(Screen):
    def __init__(self):
        super().__init__()
        Label((0, 0), font = font14, value = 'Ensure back refreshes properly')
        backbutton()

# Create a random vector. Interpolate between current vector and the new one.
# Change pointer color dependent on magnitude.
async def ptr_test(dial):
    ptr = Pointer(dial)
    v = 0j
    steps = 20  # No. of interpolation steps
    grv = lambda : urandom.getrandbits(16) / 2**15 - 1  # Random: range -1.0 to +1.0
    while True:
        v1 = grv() + 1j * grv()  # Random vector
        dv = (v1 - v) / steps  # Interpolation vector
        for _ in range(steps):
            v += dv
            mag = abs(v)
            if mag < 0.3:
                ptr.value(v, BLUE)
            elif mag < 0.7:
                ptr.value(v, GREEN)
            else:
                ptr.value(v, RED)
            await asyncio.sleep_ms(200)

# Analog clock demo. Note this could also be achieved using the Dial class.
async def aclock(dial, lbldate, lbltim):
    uv = lambda phi : rect(1, phi)  # Return a unit vector of phase phi
    days = ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday',
            'Sunday')
    months = ('January', 'February', 'March', 'April', 'May', 'June', 'July',
              'August', 'September', 'October', 'November', 'December')

    hrs = Pointer(dial)
    mins = Pointer(dial)
    secs = Pointer(dial)

    hstart =  0 + 0.7j  # Pointer lengths. Position at top.
    mstart = 0 + 1j
    sstart = 0 + 1j 

    while True:
        t = time.localtime()
        hrs.value(hstart * uv(-t[3] * pi/6 - t[4] * pi / 360), CYAN)
        mins.value(mstart * uv(-t[4] * pi/30), CYAN)
        secs.value(sstart * uv(-t[5] * pi/30), RED)
        lbltim.value('{:02d}.{:02d}.{:02d}'.format(t[3], t[4], t[5]))
        lbldate.value('{} {} {} {}'.format(days[t[6]], t[2], months[t[1] - 1], t[0]))
        await asyncio.sleep(1)

class VScreen(Screen):
    def __init__(self):
        super().__init__()
        labels = {'fontcolor' : WHITE,
                  'border' : 2,
                  'fgcolor' : RED,
                  'bgcolor' : DARKGREEN,
                  'font' : font10,
                  }

        fwdbutton(0, 242, BackScreen, 'Forward')
        quitbutton()
        # Set up random vector display with two pointers
        dial = VectorDial((0, 0), height = 200, ticks = 12, fgcolor = YELLOW, arrow = True)
        self.reg_task(ptr_test(dial))
        self.reg_task(ptr_test(dial))
        # Set up clock display: instantiate labels
        lbldate = Label((240, 210), width = 239, **labels)
        lbltim = Label((240, 235), width = 80, **labels)
        dial = VectorDial((240, 0), height = 200, ticks = 12, fgcolor = GREEN, pip = GREEN)
        self.reg_task(aclock(dial, lbldate, lbltim))

def test():
    print('Test TFT panel...')
    setup()
    Screen.change(VScreen)

test()
