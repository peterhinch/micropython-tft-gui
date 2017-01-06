# vst.py Demo/test program for vertical slider class for Pyboard TFT GUI

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
import uasyncio as asyncio
from constants import *
from ugui import Slider, Button, ButtonList, Dial, Label, Screen
import font10
import font14
from tft_local import setup
from math import pi

def to_string(val):
    return '{:3.1f} ohms'.format(val * 10)

class VerticalSliderScreen(Screen):
    def __init__(self):
        super().__init__()
# Common args for the labels
        labels = { 'width' : 70,
                'fontcolor' : WHITE,
                'border' : 2,
                'fgcolor' : RED,
                'bgcolor' : (0, 40, 0),
                }
# Common args for all three sliders
        table = {'fontcolor' : WHITE,
                'legends' : ('0', '5', '10'),
                'cb_end' : self.callback,
                }
        btnquit = Button((390, 240), font = font14, callback = self.quit, fgcolor = RED,
            text = 'Quit', shape = RECTANGLE, width = 80, height = 30)
        self.dial1 = Dial((350, 10), fgcolor = YELLOW, border = 2, pointers = (0.9, 0.7))
        self.dial2 = Dial((350, 120), fgcolor = YELLOW, border = 2,  pointers = (0.9, 0.7)) 
        self.lstlbl = []
        for n in range(3):
            self.lstlbl.append(Label((80 * n, 240), font = font10, **labels))
        y = 5
        self.slave1 = Slider((80, y), font = font10,
            fgcolor = GREEN, cbe_args = ('Slave1',), cb_move = self.slave_moved, cbm_args = (1,), **table)
        self.slave2 = Slider((160, y), font = font10,
            fgcolor = GREEN, cbe_args = ('Slave2',), cb_move = self.slave_moved, cbm_args = (2,), **table)
        master = Slider((0, y), font = font10,
            fgcolor = YELLOW, cbe_args = ('Master',), cb_move = self.master_moved, value=0.5, border = 2, **table)
        loop = asyncio.get_event_loop()
        loop.create_task(self.thread1())
        loop.create_task(self.thread2())
    # On/Off toggle: enable/disable quit button and one slider
        bs = ButtonList(self.cb_en_dis)
        lst_en_dis = [self.slave1, btnquit]
        button = bs.add_button((280, 240), font = font14, fontcolor = BLACK, height = 30, width = 90,
                            fgcolor = GREEN, shape = RECTANGLE, text = 'Disable', args = [True, lst_en_dis])
        button = bs.add_button((280, 240), font = font14, fontcolor = BLACK, height = 30, width = 90,
                            fgcolor = RED, shape = RECTANGLE, text = 'Enable', args = [False, lst_en_dis])

# CALLBACKS
# cb_end occurs when user stops touching the control
    def callback(self, slider, device):
        print('{} returned {}'.format(device, slider.value()))

    def master_moved(self, slider):
        val = slider.value()
        self.slave1.value(val)
        self.slave2.value(val)
        self.lstlbl[0].value(to_string(val))

# Either slave has had its slider moved (by user or by having value altered)
    def slave_moved(self, slider, idx):
        val = slider.value()
        self.lstlbl[idx].value(to_string(val))

    def quit(self, button):
        Screen.shutdown()

    def cb_en_dis(self, button, disable, itemlist):
        for item in itemlist:
            item.greyed_out(disable)

# THREADS
    async def thread1(self):
        angle = 0
        while True:
            await asyncio.sleep_ms(100)
            delta = self.slave1.value()
            angle += pi * 2 * delta / 10
            self.dial1.value(angle)
            self.dial1.value(angle /10, 1)

    async def thread2(self):
        angle = 0
        while True:
            await asyncio.sleep_ms(100)
            delta = self.slave2.value()
            angle += pi * 2 * delta / 10
            self.dial2.value(angle)
            self.dial2.value(angle /10, 1)

def test():
    print('Test TFT panel...')
    setup()
    Screen.set_grey_style(desaturate = False) # dim
    Screen.change(VerticalSliderScreen)       # Run it!

test()
