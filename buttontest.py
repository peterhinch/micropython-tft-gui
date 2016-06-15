# buttontest.py Test/demo of pushbutton classes for Pybboard TFT GUI

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
from ugui import Button, ButtonList, RadioButtons, Checkbox, Label, GUI, Screen
from font14 import font14
from tft_local import setup

# Callbacks

def callback(button, arg, label):
    label.value(arg)

def quit(button):
    GUI.tft.clrSCR()
    GUI.objsched.stop()

def cbcb(checkbox, label):
    if checkbox.value():
        label.value('True')
    else:
        label.value('False')

def cbreset(button, checkbox1, checkbox2, buttonset, bs0, radiobuttons, rb0, label):
    checkbox1.value(False)
    checkbox2.value(False)
    buttonset.value(bs0)
    radiobuttons.value(rb0)
    label.value('Short')

def cb_en_dis(button, disable, itemlist):
    for item in itemlist:
        item.greyed_out(disable)

# These tables contain args that differ between members of a set of related buttons
table = [
    {'fgcolor' : GREEN, 'text' : 'Yes', 'args' : ['Oui'], 'fontcolor' : (0, 0, 0)},
    {'fgcolor' : RED, 'text' : 'No', 'args' : ['Non']},
    {'fgcolor' : BLUE, 'text' : '???', 'args' : ['Que?'], 'fill': False},
    {'fgcolor' : GREY, 'text' : 'Rats', 'args' : ['Rats'], 'shape' : CLIPPED_RECT},
]

# similar buttons: only tabulate data that varies
table2 = [
    {'text' : 'P', 'args' : ['p']},
    {'text' : 'Q', 'args' : ['q']},
    {'text' : 'R', 'args' : ['r']},
    {'text' : 'S', 'args' : ['s']},
]

# A Buttonset with two entries

table3 = [
     {'fgcolor' : GREEN, 'shape' : CLIPPED_RECT, 'text' : 'Start', 'args' : ['Live']},
     {'fgcolor' : RED, 'shape' : CLIPPED_RECT, 'text' : 'Stop', 'args' : ['Die']},
]

table4 = [
    {'text' : '1', 'args' : ['1']},
    {'text' : '2', 'args' : ['2']},
    {'text' : '3', 'args' : ['3']},
    {'text' : '4', 'args' : ['4']},
]

labels = { 'width' : 70,
          'fontcolor' : WHITE,
          'border' : 2,
          'fgcolor' : RED,
          'bgcolor' : (0, 40, 0),
          'font' : font14,
          }

def test():
    print('Testing TFT...')
    setup()
    my_screen = Screen()
# Uncomment this line to see 'skeleton' style greying-out:
#    GUI.tft.grey_color()

# Labels
    lstlbl = []
    for n in range(5):
        lstlbl.append(Label((350, 40 * n), **labels))

# Button assortment
    x = 0
    for t in table:
        t['args'].append(lstlbl[2])
        Button((x, 0), font = font14, callback = callback, **t)
        x += 70

# Highlighting buttons
    x = 0
    for t in table2:
        t['args'].append(lstlbl[2])
        Button((x, 60), fgcolor = GREY, fontcolor = BLACK, litcolor = WHITE,
               font = font14, callback = callback, **t)
        x += 70

# On/Off toggle
    x = 0
    bs = ButtonList(callback)
    bs0 = None
    for t in table3: # Buttons overlay each other at same location
        t['args'].append(lstlbl[2])
        button = bs.add_button((x, 120), font = font14, fontcolor = BLACK, **t)
        if bs0 is None:
            bs0 = button

# Radio buttons
    x = 0
    rb = RadioButtons(BLUE, callback) # color of selected button
    rb0 = None
    for t in table4:
        t['args'].append(lstlbl[3])
        button = rb.add_button((x, 180), font = font14, fontcolor = WHITE,
                               fgcolor = (0, 0, 90), height = 40, width = 40, **t)
        if rb0 is None:
            rb0 = button
        x += 60

# Checkbox
    cb1 = Checkbox((300, 0), callback = cbcb, args = [lstlbl[0]])
    cb2 = Checkbox((300, 50), fillcolor = RED, callback = cbcb, args = [lstlbl[1]])

# Reset button
    Button((300, 240), font = font14, callback = cbreset, fgcolor = BLUE,
           text = 'Reset', args = [cb1, cb2, bs, bs0, rb, rb0, lstlbl[4]], fill = True, shape = RECTANGLE,
           height = 30, width = 80,
           lp_callback=callback, lp_args=['long', lstlbl[4]])
# Quit
    Button((390, 240), font = font14, callback = quit, fgcolor = RED, text = 'Quit', shape = RECTANGLE,
           height = 30, width = 80)
# On/Off toggle 
    bs_en = ButtonList(cb_en_dis)
    lst_en_dis = [cb1, cb2, rb, bs]
    button = bs_en.add_button((200, 240), font = font14, fontcolor = BLACK, height = 30, width = 90,
                           fgcolor = GREEN, shape = RECTANGLE, text = 'Disable', args = [True, lst_en_dis])
    button = bs_en.add_button((200, 240), font = font14, fontcolor = BLACK, height = 30, width = 90,
                           fgcolor = RED, shape = RECTANGLE, text = 'Enable', args = [False, lst_en_dis])
    my_screen.run()                                          # Run it!

test()
