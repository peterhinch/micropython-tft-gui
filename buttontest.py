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
from ugui import Button, ButtonList, RadioButtons, Checkbox, Label, Screen
import font14
import font10
from tft_local import setup

class ButtonScreen(Screen):
    def __init__(self):
        super().__init__()
# These tables contain args that differ between members of a set of related buttons
        table = [
            {'fgcolor' : GREEN, 'text' : 'Yes', 'args' : ('Oui', 2), 'fontcolor' : (0, 0, 0)},
            {'fgcolor' : RED, 'text' : 'No', 'args' : ('Non', 2)},
            {'fgcolor' : BLUE, 'text' : '???', 'args' : ('Que?', 2), 'fill': False},
            {'fgcolor' : GREY, 'text' : 'Rats', 'args' : ('Rats', 2), 'shape' : CLIPPED_RECT,},
        ]
# Highlight buttons: only tabulate data that varies
        table_highlight = [
            {'text' : 'P', 'args' : ('p', 2)},
            {'text' : 'Q', 'args' : ('q', 2)},
            {'text' : 'R', 'args' : ('r', 2)},
            {'text' : 'S', 'args' : ('s', 2)},
        ]
# A Buttonset with two entries
        table_buttonset = [
            {'fgcolor' : GREEN, 'shape' : CLIPPED_RECT, 'text' : 'Start', 'args' : ('Live', 2)},
            {'fgcolor' : RED, 'shape' : CLIPPED_RECT, 'text' : 'Stop', 'args' : ('Die', 2)},
        ]

        table_radiobuttons = [
            {'text' : '1', 'args' : ('1', 3)},
            {'text' : '2', 'args' : ('2', 3)},
            {'text' : '3', 'args' : ('3', 3)},
            {'text' : '4', 'args' : ('4', 3)},
        ]

        labels = { 'width' : 70,
                'fontcolor' : WHITE,
                'border' : 2,
                'fgcolor' : RED,
                'bgcolor' : (0, 40, 0),
                'font' : font14,
                }

# Uncomment this line to see 'skeleton' style greying-out:
#        Screen.tft.grey_color()

# Labels
        self.lstlbl = []
        for n in range(5):
            self.lstlbl.append(Label((390, 40 * n), **labels))

# Button assortment
        x = 0
        for t in table:
            Button((x, 0), font = font14, callback = self.callback, **t)
            x += 70

# Highlighting buttons
        x = 0
        for t in table_highlight:
            Button((x, 60), fgcolor = GREY, fontcolor = BLACK, litcolor = WHITE,
                font = font14, callback = self.callback, **t)
            x += 70

# Start/Stop toggle
        self.bs = ButtonList(self.callback)
        self.bs0 = None
        for t in table_buttonset: # Buttons overlay each other at same location
            button = self.bs.add_button((0, 240), font = font14, fontcolor = BLACK, height = 30, **t)
            if self.bs0 is None: # Save for reset button callback
                self.bs0 = button

# Radio buttons
        x = 0
        self.rb = RadioButtons(BLUE, self.callback) # color of selected button
        self.rb0 = None
        for t in table_radiobuttons:
            button = self.rb.add_button((x, 140), font = font14, fontcolor = WHITE,
                                fgcolor = (0, 0, 90), height = 40, width = 40, **t)
            if self.rb0 is None: # Save for reset button callback
                self.rb0 = button
            x += 60

# Checkbox
        self.cb1 = Checkbox((340, 0), callback = self.cbcb, args = (0,))
        self.cb2 = Checkbox((340, 40), fillcolor = RED, callback = self.cbcb, args = (1,))

# Reset button
        self.lbl_reset = Label((200, 220), font = font10, value = 'Reset also responds to long press')
        self.btn_reset = Button((300, 240), font = font14, height = 30, width = 80,
                                fgcolor = BLUE, shape = RECTANGLE, text = 'Reset', fill = True,
                                callback = self.cbreset, args = (4,), onrelease = False,
                                lp_callback = self.callback, lp_args = ('long', 4))
# Quit
        self.btn_quit = Button((390, 240), font = font14, height = 30, width = 80,
                               fgcolor = RED, shape = RECTANGLE, text = 'Quit',
                               callback = self.quit)
# Enable/Disable toggle 
        self.bs_en = ButtonList(self.cb_en_dis)
        self.tup_en_dis = (self.cb1, self.cb2, self.rb, self.bs) # Items affected by enable/disable button
        self.bs_en.add_button((200, 240), font = font14, fontcolor = BLACK, height = 30, width = 90,
                              fgcolor = GREEN, shape = RECTANGLE, text = 'Disable', args = (True,))
        self.bs_en.add_button((200, 240), font = font14, fontcolor = BLACK, height = 30, width = 90,
                              fgcolor = RED, shape = RECTANGLE, text = 'Enable', args = (False,))

    def callback(self, button, arg, idx_label):
        self.lstlbl[idx_label].value(arg)

    def quit(self, button):
        Screen.shutdown()

    def cbcb(self, checkbox, idx_label):
        if checkbox.value():
            self.lstlbl[idx_label].value('True')
        else:
            self.lstlbl[idx_label].value('False')

    def cbreset(self, button, idx_label):
        self.cb1.value(False)
        self.cb2.value(False)
        self.bs.value(self.bs0)
        self.rb.value(self.rb0)
        self.lstlbl[idx_label].value('Short')

    def cb_en_dis(self, button, disable):
        for item in self.tup_en_dis:
            item.greyed_out(disable)

def test():
    print('Testing TFT...')
    setup()
    Screen.change(ButtonScreen)

test()
