# ibt.py Test/demo of icon based pushbutton classes for Pybboard TFT GUI

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
from ugui import IconButton, IconGauge, IconRadioButtons, Label, Screen
from tft_local import setup
from font10 import font10
from font14 import font14
import radiobutton, checkbox, flash, threestate, iconswitch, gauge, traffic # icon files

def lr(n): # y coordinate from logical row
    return 10 + 50 * n

class IconButtonScreen(Screen):
    def __init__(self):
        super().__init__()
# Label common attributes
        labels = { 'width' : 70,
                'fontcolor' : WHITE,
                'border' : 2,
                'fgcolor' : RED,
                'bgcolor' : (0, 40, 0),
                'font' : font14,
                }
# Static labels
        Label((90, 0), font = font10, value = 'Flashing buttons')
        Label((90, 18), font = font10, value = '(RH responds to long press)')
        Label((244, lr(1) + 5), font = font10, value = 'Reset radio button')
        Label((244, lr(2) + 5), font = font10, value = 'Reset checkbox')
        Label((244, lr(3) + 5), font = font10, value = 'Disable rb, checkbox')
        Label((370, 243), font = font14, value = 'Quit')
# Dynamic labels
        self.lstlbl = []
        for n in range(4):
            self.lstlbl.append(Label((400, lr(n)), **labels))
# Flashing buttons (RH one responds to long press)
        IconButton((10, lr(0)), icon_module = flash, flash = 1.0,
                callback = self.callback, args = ('A', 0))
        IconButton((50, lr(0)), icon_module = flash, flash = 1.0,
                callback = self.callback, args = ('Short', 0),
                lp_callback = self.callback, lp_args = ('Long', 0), onrelease = False)
# Quit button
        IconButton((420, 240), icon_module = radiobutton, callback = self.quit)
# Radio buttons
        rb = IconRadioButtons(callback = self.callback)
        rb0 = rb.add_button((10, lr(1)), icon_module = radiobutton, args = ('1', 1))
        rb.add_button((50, lr(1)), icon_module = radiobutton, args = ('2', 1))
        rb.add_button((90, lr(1)), icon_module = radiobutton, args = ('3', 1))
        rb.add_button((130, lr(1)), icon_module = radiobutton, args = ('4', 1))
# Checkbox
        cb = IconButton((10, lr(2)), icon_module = threestate, toggle = True,
                        callback = self.cbcb, args =(2,))
# Traffic light state change button
        IconButton((10, lr(4)), icon_module = traffic, toggle = True)
# Reset buttons
        IconButton((200, lr(1)), icon_module = radiobutton, callback = self.rb_cancel, args = (rb, rb0))
        IconButton((200, lr(2)), icon_module = radiobutton, callback = self.cb_cancel, args = (cb,))
# Switch
        sw = IconButton((10, lr(3)), icon_module = iconswitch, callback = self.cbswitch, toggle = True, args = (3,))
# Disable Checkbox
        IconButton((200, lr(3)), icon_module = checkbox, toggle = True,
                        callback = self.cb_en_dis, args =((cb, rb, sw),))
# Gauge
        ig = IconGauge((80, lr(5)), icon_module = gauge)
        Screen.objsched.add_thread(self.mainthread(ig))


# CALLBACKS
# Default CB displays text on a label
    def callback(self, button, arg, idx_label):
        self.lstlbl[idx_label].value(arg)

# Checkbox CB
    def cbcb(self, checkbox, idx_label):
        self.lstlbl[idx_label].value(('False', '???', 'True')[checkbox.value()])

# CB for button 'reset radio button': test radiobutton response to value change
    def rb_cancel(self, button, radiobutton, rb0):
        radiobutton.value(rb0)

# CB for button 'reset checkbox': test checkbox response to forced change
    def cb_cancel(self, button, checkbox):
        checkbox.value(0)

# Switch CB
    def cbswitch(self, button, idx_label):
        self.lstlbl[idx_label].value(str(button.value()))

# Quit button CB
    def quit(self, button):
        Screen.tft.clrSCR()
        Screen.objsched.stop()

# Enable/disable CB
    def cb_en_dis(self, button, itemlist):
        for item in itemlist:
            item.greyed_out(button.value() > 0)


# THREAD: keep the gauge moving
    def mainthread(self, objgauge):
        INC = 0.05
        oldvalue = 0
        inc = INC
        yield
        while True:
            oldvalue += inc
            if oldvalue >= 1.0:
                oldvalue = 1.0
                inc = -INC
            elif oldvalue <= 0:
                oldvalue = 0
                inc = INC
            objgauge.value(oldvalue)
            yield 0.1

def test():
    print('Testing TFT...')
    setup()
    Screen.change(IconButtonScreen)

test()
