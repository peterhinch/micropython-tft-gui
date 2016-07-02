# hst.py Demo/test for Horizontal Slider class for Pyboard TFT GUI

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
from constants import *
from ugui import HorizSlider, Button, ButtonList, Dial, Label, LED, Meter, Screen
from font10 import font10
from font14 import font14
from tft_local import setup
import pyb

# CALLBACKS
# cb_end occurs when user stops touching the control
def to_string(val):
    return '{:3.1f} ohms'.format(val * 10)

class HorizontalSliderScreen(Screen):
    def __init__(self):
        super().__init__()
# Common args for the labels
        labels = { 'width' : 70,
                'fontcolor' : WHITE,
                'border' : 2,
                'fgcolor' : RED,
                'bgcolor' : (0, 40, 0),
                }

# Common arguments for all three sliders
        table = {'fontcolor' : WHITE,
                'legends' : ('0', '5', '10'),
                'cb_end' : self.slide_release,
                }

        self.led = LED((420, 0), border = 2)
        meter1 = Meter((320, 0), font=font10, legends=('0','5','10'), pointercolor = YELLOW, fgcolor = GREEN)
        meter2 = Meter((360, 0), font=font10, legends=('0','5','10'), pointercolor = YELLOW)
        btnquit = Button((390, 240), font = font14, callback = self.quit, fgcolor = RED,
            text = 'Quit', shape = RECTANGLE, width = 80, height = 30)
# Create labels
        x = 230
        lstlbl = []
        for n in range(3):
            lstlbl.append(Label((x, 40 + 60 * n), font = font10, **labels))
# Sliders
        x = 10
        self.slave1 = HorizSlider((x, 100), font = font10, fgcolor = GREEN, cbe_args = ('Slave1',),
                            cb_move = self.slave_moved, cbm_args = (lstlbl[1],), **table)
        self.slave2 = HorizSlider((x, 160), font = font10, fgcolor = GREEN, cbe_args = ('Slave2',),
                            cb_move = self.slave_moved, cbm_args = (lstlbl[2],), **table)
        master = HorizSlider((x, 40), font = font10, fgcolor = YELLOW, cbe_args = ('Master',),
                            cb_move = self.master_moved, slidecolor=RED, border = 2,
                            cbm_args = (lstlbl[0],), value=0.5, **table)
# On/Off toggle: enable/disable
        bs = ButtonList(self.cb_en_dis)
        self.lst_en_dis = [self.slave1, btnquit]
        button = bs.add_button((280, 240), font = font14, fontcolor = BLACK, height = 30, width = 90,
                            fgcolor = GREEN, shape = RECTANGLE, text = 'Disable', args = (True,))
        button = bs.add_button((280, 240), font = font14, fontcolor = BLACK, height = 30, width = 90,
                            fgcolor = RED, shape = RECTANGLE, text = 'Enable', args = (False,))
# Threads to test meters
        Screen.objsched.add_thread(self.testmeter(meter1))
        Screen.objsched.add_thread(self.testmeter(meter2))

    def slide_release(self, slider, control_name):
        print('{} returned {}'.format(control_name, slider.value()))

    def master_moved(self, slider, label):
        val = slider.value()
        self.slave1.value(val)
        self.slave2.value(val)
        label.value(to_string(val))
        self.led.value(val > 0.8)

# Either slave has had its slider moved (by user or by having value altered)
    def slave_moved(self, slider, label):
        val = slider.value()
        if val > 0.8:
            slider.color(RED)
        else:
            slider.color(GREEN)
        label.value(to_string(val))

    def quit(self, button):
        Screen.tft.clrSCR()
        Screen.objsched.stop()

    def cb_en_dis(self, button, disable):
        for item in self.lst_en_dis:
            item.greyed_out(disable)
# Meters move linearly between random values
    def testmeter(self, meter):
        oldvalue = 0
        yield
        while True:
            val = pyb.rng() / 2**30
            steps = 20
            delta = (val - oldvalue) / steps
            for _ in range(steps):
                oldvalue += delta
                meter.value(oldvalue)
                yield 0.1

def test():
    print('Test TFT panel...')
    setup()
    Screen.change(HorizontalSliderScreen)

test()
