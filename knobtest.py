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
from ugui import Knob, Dial, Label, Button, ButtonList, Screen, Dropdown, Listbox
from font14 import font14
from font10 import font10
from tft_local import setup
from math import pi

class KnobScreen(Screen):
    def __init__(self):
        super().__init__()
        Button((390, 240), font = font14, callback = self.quit, fgcolor = RED,
            text = 'Quit', shape = RECTANGLE, width = 80, height = 30)
        self.dial = Dial((120, 0), fgcolor = YELLOW, border = 2, pointers = (0.9, 0.7))
        k0 = Knob((0, 0), fgcolor = GREEN, bgcolor=(0, 0, 80), color = (168,63,63), border = 2,
                cb_end = self.callback, cbe_args = ['Knob1'], cb_move = self.knob_moved, cbm_args = (0,))
        k1 = Knob((0, 120), fgcolor = WHITE, border = 2, arc = pi * 1.5,
                cb_end = self.callback, cbe_args = ['Knob2'], cb_move = self.knob_moved, cbm_args = (1,))
# Dropdown
        self.lbl_dd = Label((120, 120), font = font14, width = 100, border = 2, bgcolor = (0, 40, 0), fgcolor = RED)
        self.dropdown = Dropdown((280, 0), font = font14, width = 100, callback = self.cbdb,
                                 elements = ('Dog', 'Cat', 'Rat', 'Goat', 'Snake', 'Pig'))

        Button((280, 70), font = font14, callback = self.set_dropdown, fgcolor = BLUE,
            text = 'Reset', shape = RECTANGLE, width = 80, height = 30) # Test of set by value
        Button((280, 120), font = font14, callback = self.set_bytext, args = ('Snake',), fgcolor = CYAN,
            fontcolor = BLACK, text = 'Snake', shape = RECTANGLE, width = 80, height = 30) # test set by text
# Listbox
        self.listbox = Listbox((370, 70), font = font14, width = 105,
                               bgcolor = GREY, fgcolor = YELLOW, select_color = BLUE,
                               elements = ('aardvark', 'zebra', 'armadillo', 'warthog'),
                               callback = self.cblb)
# On/Off toggle grey style
        self.lbl_style = Label((170, 210), font = font10, value = 'Current style: grey')
        bstyle = ButtonList(self.cb_style)
        bstyle.add_button((170, 240), font = font14, fontcolor = WHITE, height = 30, width = 90,
                            fgcolor = RED, shape = RECTANGLE, text = 'Dim', args = (False,))
        bstyle.add_button((170, 240), font = font14, fontcolor = WHITE, height = 30, width = 90,
                          fgcolor = GREEN, shape = RECTANGLE, text = 'Grey', args = (True,))
# On/Off toggle enable/disable
        bs = ButtonList(self.cb_en_dis)
        self.lst_en_dis = (bstyle, k0, k1, self.dropdown, self.listbox)
        bs.add_button((280, 240), font = font14, fontcolor = BLACK, height = 30, width = 90,
                      fgcolor = GREEN, shape = RECTANGLE, text = 'Disable', args = (True,))
        bs.add_button((280, 240), font = font14, fontcolor = BLACK, height = 30, width = 90,
                      fgcolor = RED, shape = RECTANGLE, text = 'Enable', args = (False,))

# CALLBACKS
# cb_end occurs when user stops touching the control
    def callback(self, knob, control_name):
        print('{} returned {}'.format(control_name, knob.value()))

    def knob_moved(self, knob, pointer):
        val = knob.value() # range 0..1
        self.dial.value(2 * (val - 0.5) * pi, pointer)

    def quit(self, button):
        Screen.tft.clrSCR()
        Screen.objsched.stop()

    def cb_en_dis(self, button, disable):
        for item in self.lst_en_dis:
            item.greyed_out(disable)

    def cb_style(self, button, desaturate):
        self.lbl_style.value(''.join(('Current style: ', 'grey' if desaturate else 'dim')))
        Screen.set_grey_style(desaturate = desaturate)

    def cbdb(self, dropdown):
        self.lbl_dd.value(dropdown.textvalue())

    def cblb(self, listbox):
        print(listbox.textvalue())

    def set_dropdown(self, button):
        self.dropdown.value(0)

    def set_bytext(self, button, txt):
        self.dropdown.textvalue(txt)

def test():
    print('Test TFT panel...')
    setup()
    Screen.change(KnobScreen)

test()
