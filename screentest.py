# screentest.py Test/demo of multiple screens for Pybboard TFT GUI

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
from ugui import Knob, Dial, Label, Button, RadioButtons, ButtonList, Meter, Screen, Slider, Checkbox, LED, GUI
from font14 import font14
from font10 import font10
from tft_local import setup
from math import pi

# STANDARD BUTTONS

def quitbutton(x, y):
    def quit(button):
        tft = button.tft
        tft.clrSCR()
        GUI.objsched.stop()
    Button((x, y), height = 30, font = font14, callback = quit, fgcolor = RED,
           text = 'Quit', shape = RECTANGLE, width = 80)

def fwdbutton(x, y, screen, text='Next'):
    def fwd(button, screen):
        Screen.change(screen)
    Button((x, y), height = 30, font = font14, callback = fwd, args = [screen], fgcolor = RED,
           text = text, shape = RECTANGLE, width = 80)

def backbutton(x, y):
    def back(button):
        Screen.back()
    Button((x, y), height = 30, font = font14, fontcolor = BLACK, callback = back,
           fgcolor = CYAN,  text = 'Back', shape = RECTANGLE, width = 80)

# SCREEN CREATION

# Demo of subclassing a screen to use callbacks
class BackScreen(Screen):
    def __init__(self):
        super().__init__()
        Label((0, 0), font = font14, width = 400, value = 'Ensure back refreshes properly')
        backbutton(390, 242)
        self.open_args = ['Opening']
        self.hide_args = ['Hiding']

    def on_open(self, text):
        print(text)

    def on_hide(self, text):
        print(text)

class BaseScreen(Screen):
    def __init__(self, knob_screen, slider_screen, assorted_screen):
        super().__init__()
        fwdbutton(0, 242, knob_screen, 'Knobs')
        fwdbutton(100, 242, slider_screen, 'Sliders')
        fwdbutton(200, 242, assorted_screen, 'Various')
        quitbutton(390, 242)

class KnobScreen(Screen):
    labels = { 'width' : 70,
            'fontcolor' : WHITE,
            'border' : 2,
            'fgcolor' : RED,
            'bgcolor' : (0, 40, 0),
            }

    def __init__(self, next_screen):
        super().__init__()
        backbutton(390, 242)
        fwdbutton(0, 242, next_screen)
        labels = self.labels
        lstlbl = []
        for n in range(2):
            lstlbl.append(Label((120, 120 + 40 * n), font = font10, **labels))
        lbl_1 = Label((120, 120), font = font10, **labels)
        lbl_2 = Label((120, 160), font = font10, **labels)
        meter1 = Meter((320, 0), font=font10, legends=('0','5','10'), pointercolor = YELLOW, fgcolor = GREEN)
        dial1 = Dial((120, 0), fgcolor = YELLOW, border = 2, pointers = (0.9, 0.7))
        Knob((0, 0), fgcolor = GREEN, bgcolor=(0, 0, 80), color = (168,63,63), border = 2,
            cb_end = self.callback, cbe_args = ['Knob1'], cb_move = self.knob_moved, cbm_args = [dial1, 0, lbl_1, meter1])
        Knob((0, 120), fgcolor = WHITE, border = 2, cb_move = self.knob_moved, cbm_args = [dial1, 1, lbl_2],
            cb_end = self.callback, cbe_args = ['Knob2'], arc = pi * 1.5)

    def callback(self, knob, control_name):
        print('{} returned {}'.format(control_name, knob.value()))

    def knob_moved(self, knob, dial, pointer, label, meter=None):
        val = knob.value() # range 0..1
        dial.value(2 * (val - 0.5) * pi, pointer)
        label.value('{:3.1f}'.format(val))
        if meter is not None:
            meter.value(val)

class SliderScreen(Screen):
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
            }

    def __init__(self, next_screen):
        super().__init__()
        backbutton(390, 242)
        fwdbutton(0, 242, next_screen)
        lstlbl = []
        for n in range(3):
            lstlbl.append(Label((80 * n, 215), font = font10, **self.labels))
        y = 5
        slave1 = Slider((80, y), font = font10,
            fgcolor = GREEN, cb_end = self.callback, cbe_args = ('Slave1',), cb_move = self.slave_moved, cbm_args = [lstlbl[1]], **self.table)
        slave2 = Slider((160, y), font = font10,
            fgcolor = GREEN, cb_end = self.callback, cbe_args = ('Slave2',), cb_move = self.slave_moved, cbm_args = [lstlbl[2]], **self.table)
        master = Slider((0, y), font = font10,
            fgcolor = YELLOW, cb_end = self.callback, cbe_args = ('Master',), cb_move = self.master_moved, 
            cbm_args = (slave1, slave2, lstlbl[0]), value=0.5, border = 2, **self.table)


# cb_end occurs when user stops touching the control
    def callback(self, slider, device):
        print('{} returned {}'.format(device, slider.value()))

    def master_moved(self, slider, slave1, slave2, label):
        val = slider.value()
        slave1.value(val)
        slave2.value(val)
        label.value(self.to_string(val))

# Either slave has had its slider moved (by user or by having value altered)
    def slave_moved(self, slider, label):
        val = slider.value()
        label.value(self.to_string(val))

    def to_string(self, val):
        return '{:3.1f} ohms'.format(val * 10)


class AssortedScreen(Screen):
    labels = { 'width' : 70,
            'fontcolor' : WHITE,
            'border' : 2,
            'fgcolor' : RED,
            'bgcolor' : (0, 40, 0),
            'font' : font14,
            }

    radiobuttons = [
        {'text' : '1', 'args' : ['1']},
        {'text' : '2', 'args' : ['2']},
        {'text' : '3', 'args' : ['3']},
        {'text' : '4', 'args' : ['4']},
    ]

    buttonlist = [
        {'fgcolor' : GREEN, 'shape' : CLIPPED_RECT, 'text' : 'Start', 'args' : ['Live']},
        {'fgcolor' : RED, 'shape' : CLIPPED_RECT, 'text' : 'Stop', 'args' : ['Die']},
    ]

    def __init__(self, next_screen):
        super().__init__()
        backbutton(390, 242)
        fwdbutton(0, 242, next_screen)
        lstlbl = []
        for n in range(4):
            lstlbl.append(Label((350, 40 * n), **self.labels))
        self.led = LED((440, 0), border = 2)
        Checkbox((300, 0), callback = self.cbcb, args = [lstlbl[0], False])
        Checkbox((300, 50), fillcolor = RED, callback = self.cbcb, args = [lstlbl[1], True])

# On/Off toggle
        x = 0
        bs = ButtonList(self.callback)
        bs0 = None
        for t in self.buttonlist: # Buttons overlay each other at same location
            t['args'].append(lstlbl[2])
            button = bs.add_button((x, 120), font = font14, fontcolor = BLACK, **t)
            if bs0 is None:
                bs0 = button
# Radio buttons
        x = 0
        rb = RadioButtons(BLUE, self.callback) # color of selected button
        for t in self.radiobuttons:
            t['args'].append(lstlbl[3])
            button = rb.add_button((x, 180), font = font14, fontcolor = WHITE,
                                fgcolor = (0, 0, 90), height = 40, width = 40, **t)
            x += 60

    def callback(self, button, arg, label): # Callback for radio button
        label.value(arg)

    def cbcb(self, checkbox, label, test): # Callback for checkbox
        if test:
            self.led.value(checkbox.value())
        else:
            color = RED if checkbox.value() else YELLOW
            self.led.color(color)
        if checkbox.value():
            label.value('True')
        else:
            label.value('False')

class base_screen(Screen):
    def __init__(self, knob_screen, slider_screen, assorted_screen):
        super().__init__()
        Label((0, 0), font = font14, width = 400, value = 'Screen change demo')
        fwdbutton(0, 242, knob_screen, 'Knobs')
        fwdbutton(100, 242, slider_screen, 'Sliders')
        fwdbutton(200, 242, assorted_screen, 'Various')
        quitbutton(390, 242)

def test():
    print('Test TFT panel...')
    setup()
    back_screen = BackScreen() # Most deeply nested screen first
    knob_screen = KnobScreen(back_screen)
    slider_screen = SliderScreen(back_screen)
    assorted_screen = AssortedScreen(back_screen)
    base_screen = BaseScreen(knob_screen, slider_screen, assorted_screen)
    base_screen.run()                                          # Run it!

test()
