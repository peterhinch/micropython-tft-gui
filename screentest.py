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
        tft = GUI.get_tft()
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

def create_back_screen():
    Label((0, 0), font = font14, width = 400, value = 'Ensure back refreshes properly')
    backbutton(390, 242)

def create_knob_screen(next_screen):
    labels = { 'width' : 70,
            'fontcolor' : WHITE,
            'border' : 2,
            'fgcolor' : RED,
            'bgcolor' : (0, 40, 0),
            }
    def callback(knob, control_name):
        print('{} returned {}'.format(control_name, knob.value()))

    def knob_moved(knob, dial, pointer, label, meter=None):
        val = knob.value() # range 0..1
        dial.value(2 * (val - 0.5) * pi, pointer)
        label.value('{:3.1f}'.format(val))
        if meter is not None:
            meter.value(val)

    screen = Screen()
    backbutton(390, 242)
    fwdbutton(0, 242, next_screen)
    lstlbl = []
    for n in range(2):
        lstlbl.append(Label((120, 120 + 40 * n), font = font10, **labels))
    meter1 = Meter((320, 0), font=font10, legends=('0','5','10'), pointercolor = YELLOW, fgcolor = GREEN)
    dial1 = Dial((120, 0), fgcolor = YELLOW, border = 2, pointers = (0.9, 0.7))
    Knob((0, 0), fgcolor = GREEN, bgcolor=(0, 0, 80), color = (168,63,63), border = 2,
        cb_end = callback, cbe_args = ['Knob1'], cb_move = knob_moved, cbm_args = [dial1, 0, lstlbl[0], meter1])
    Knob((0, 120), fgcolor = WHITE, border = 2, cb_move = knob_moved, cbm_args = [dial1, 1, lstlbl[1]],
        cb_end = callback, cbe_args = ['Knob2'], arc = pi * 1.5)
    return screen

def create_slider_screen(next_screen):
# cb_end occurs when user stops touching the control
    def callback(slider, device):
        print('{} returned {}'.format(device, slider.value()))

    def master_moved(slider, slave1, slave2, label):
        val = slider.value()
        slave1.value(val)
        slave2.value(val)
        label.value(to_string(val))

# Either slave has had its slider moved (by user or by having value altered)
    def slave_moved(slider, label):
        val = slider.value()
        label.value(to_string(val))

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
            'cb_end' : callback,
            }

    def to_string(val):
        return '{:3.1f} ohms'.format(val * 10)

    screen = Screen()
    backbutton(390, 242)
    fwdbutton(0, 242, next_screen)
    lstlbl = []
    for n in range(3):
        lstlbl.append(Label((80 * n, 215), font = font10, **labels))
    y = 5
    slave1 = Slider((80, y), font = font10,
           fgcolor = GREEN, cbe_args = ('Slave1',), cb_move = slave_moved, cbm_args = [lstlbl[1]], **table)
    slave2 = Slider((160, y), font = font10,
           fgcolor = GREEN, cbe_args = ('Slave2',), cb_move = slave_moved, cbm_args = [lstlbl[2]], **table)
    master = Slider((0, y), font = font10,
           fgcolor = YELLOW, cbe_args = ('Master',), cb_move = master_moved, 
           cbm_args = (slave1, slave2, lstlbl[0]), value=0.5, border = 2, **table)

    return screen

def create_assorted_screen(next_screen):
    def callback(button, arg, label): # Callback for radio button
        label.value(arg)

    def cbcb(checkbox, label, led, test): # Callback for checkbox
        if test:
            led.value(checkbox.value())
        else:
            color = RED if checkbox.value() else YELLOW
            led.color(color)
        if checkbox.value():
            label.value('True')
        else:
            label.value('False')

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

    screen = Screen()
    backbutton(390, 242)
    fwdbutton(0, 242, next_screen)
    lstlbl = []
    for n in range(5):
        lstlbl.append(Label((350, 40 * n), **labels))
    led = LED((440, 0), border = 2)
    cb1 = Checkbox((300, 0), callback = cbcb, args = [lstlbl[0], led, False])
    cb2 = Checkbox((300, 50), fillcolor = RED, callback = cbcb, args = [lstlbl[1], led, True])

# On/Off toggle
    x = 0
    bs = ButtonList(callback)
    bs0 = None
    for t in buttonlist: # Buttons overlay each other at same location
        t['args'].append(lstlbl[2])
        button = bs.add_button((x, 120), font = font14, fontcolor = BLACK, **t)
        if bs0 is None:
            bs0 = button
# Radio buttons
    x = 0
    rb = RadioButtons(BLUE, callback) # color of selected button
    for t in radiobuttons:
        t['args'].append(lstlbl[3])
        button = rb.add_button((x, 180), font = font14, fontcolor = WHITE,
                               fgcolor = (0, 0, 90), height = 40, width = 40, **t)
        x += 60
    return screen


def create_base_screen(knob_screen, slider_screen, assorted_screen):
    screen = Screen()
    Label((0, 0), font = font14, width = 400, value = 'Screen change demo')
    fwdbutton(0, 242, knob_screen, 'Knobs')
    fwdbutton(100, 242, slider_screen, 'Sliders')
    fwdbutton(200, 242, assorted_screen, 'Various')
    quitbutton(390, 242)
    return screen

def test():
    print('Test TFT panel...')
    back_screen = setup()
    create_back_screen() # Most deeply nested screen first
    knob_screen = create_knob_screen(back_screen)
    slider_screen = create_slider_screen(back_screen)
    assorted_screen = create_assorted_screen(back_screen)
    base_screen = create_base_screen(knob_screen, slider_screen, assorted_screen)
    base_screen.run()                                          # Run it!

test()
