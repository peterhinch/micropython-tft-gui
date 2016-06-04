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
from constants import *
from ugui import Slider, Button, ButtonList, Dial, Label, GUI
from font10 import font10
from font14 import font14
from tft_local import setup
from math import pi

# CALLBACKS
# cb_end occurs when user stops touching the control
def callback(slider, device):
    print('{} returned {}'.format(device, slider.value()))

def to_string(val):
    return '{:3.1f} ohms'.format(val * 10)

def master_moved(slider, slave1, slave2, label):
    val = slider.value()
    slave1.value(val)
    slave2.value(val)
    label.show(to_string(val))

# Either slave has had its slider moved (by user or by having value altered)
def slave_moved(slider, label):
    val = slider.value()
    label.show(to_string(val))

def quit(button):
    GUI.tft.clrSCR()
    GUI.objsched.stop()

def cb_en_dis(button, disable, itemlist):
    for item in itemlist:
        item.greyed_out(disable)

# THREADS
def mainthread(slider, dial):
    angle = 0
    yield
    while True:
        yield 0.1
        delta = slider.value()
        angle += pi * 2 * delta / 10
        dial.show(angle)
        dial.show(angle /10, 1)

# DATA
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

def test():
    print('Test TFT panel...')
    my_screen = setup()
    GUI.set_grey_style() # grey out
    btnquit = Button((390, 240), font = font14, callback = quit, fgcolor = RED,
           text = 'Quit', shape = RECTANGLE, width = 80, height = 30)
    dial1 = Dial((350, 10), fgcolor = YELLOW, border = 2, pointers = (0.9, 0.7))
    dial2 = Dial((350, 120), fgcolor = YELLOW, border = 2,  pointers = (0.9, 0.7)) 
    lstlbl = []
    for n in range(3):
        lstlbl.append(Label((80 * n, 240), font = font10, **labels))
    y = 5
    slave1 = Slider((80, y), font = font10,
           fgcolor = GREEN, cbe_args = ('Slave1',), cb_move = slave_moved, cbm_args = [lstlbl[1]], **table)
    slave2 = Slider((160, y), font = font10,
           fgcolor = GREEN, cbe_args = ('Slave2',), cb_move = slave_moved, cbm_args = [lstlbl[2]], **table)
    master = Slider((0, y), font = font10,
           fgcolor = YELLOW, cbe_args = ('Master',), cb_move = master_moved, 
           cbm_args = (slave1, slave2, lstlbl[0]), value=0.5, border = 2, **table)
    GUI.objsched.add_thread(mainthread(slave1, dial1))
    GUI.objsched.add_thread(mainthread(slave2, dial2))
# On/Off toggle: enable/disable quit button and one slider
    bs = ButtonList(cb_en_dis)
    lst_en_dis = [slave1, btnquit]
    button = bs.add_button((280, 240), font = font14, fontcolor = BLACK, height = 30, width = 90,
                           fgcolor = GREEN, shape = RECTANGLE, text = 'Disable', args = [True, lst_en_dis])
    button = bs.add_button((280, 240), font = font14, fontcolor = BLACK, height = 30, width = 90,
                           fgcolor = RED, shape = RECTANGLE, text = 'Enable', args = [False, lst_en_dis])
    my_screen.run()                                          # Run it!

test()
