# knobtest.py Test/demo of Knob and Dial classes for Pybboard TFT GUI

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
from ugui import Knob, Dial, Label, Button, ButtonList, GUI
from font14 import font14
from tft_local import setup
from math import pi

# CALLBACKS
# cb_end occurs when user stops touching the control
def callback(knob, control_name):
    print('{} returned {}'.format(control_name, knob.value()))

def knob_moved(knob, dial, pointer):
    val = knob.value() # range 0..1
    dial.value(2 * (val - 0.5) * pi, pointer)

def quit(button):
    GUI.tft.clrSCR()
    GUI.objsched.stop()

def cb_en_dis(button, disable, itemlist):
    for item in itemlist:
        item.greyed_out(disable)

def cb_style(button, skeleton):
    if skeleton:
        GUI.set_grey_style(desaturate = True)
    else:
        GUI.set_grey_style(desaturate = False)

def test():
    print('Test TFT panel...')
    my_screen = setup()
    Button((390, 240), font = font14, callback = quit, fgcolor = RED,
           text = 'Quit', shape = RECTANGLE, width = 80, height = 30)
    dial1 = Dial((120, 0), fgcolor = YELLOW, border = 2, pointers = (0.9, 0.7))
    k0 = Knob((0, 0), fgcolor = GREEN, bgcolor=(0, 0, 80), color = (168,63,63), border = 2,
              cb_end = callback, cbe_args = ['Knob1'], cb_move = knob_moved, cbm_args = [dial1, 0])
    k1 = Knob((0, 120), fgcolor = WHITE, border = 2, arc = pi * 1.5,
              cb_end = callback, cbe_args = ['Knob2'], cb_move = knob_moved, cbm_args = [dial1, 1])
# On/Off toggle grey style
    bstyle = ButtonList(cb_style)
    button = bstyle.add_button((170, 240), font = font14, fontcolor = WHITE, height = 30, width = 90,
                           fgcolor = RED, shape = RECTANGLE, text = 'Dim', args = [False])
    button = bstyle.add_button((170, 240), font = font14, fontcolor = WHITE, height = 30, width = 90,
                           fgcolor = GREEN, shape = RECTANGLE, text = 'Grey', args = [True])
# On/Off toggle enable/disable
    bs = ButtonList(cb_en_dis)
    lst_en_dis = [bstyle, k0, k1]
    button = bs.add_button((280, 240), font = font14, fontcolor = BLACK, height = 30, width = 90,
                           fgcolor = GREEN, shape = RECTANGLE, text = 'Disable', args = [True, lst_en_dis])
    button = bs.add_button((280, 240), font = font14, fontcolor = BLACK, height = 30, width = 90,
                           fgcolor = RED, shape = RECTANGLE, text = 'Enable', args = [False, lst_en_dis])
    my_screen.run()                                          # Run it!

test()
