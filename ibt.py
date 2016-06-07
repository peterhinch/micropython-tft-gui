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
from ugui import IconButton, IconGauge, IconRadioButtons, Label, GUI
from tft_local import setup
from font10 import font10
from font14 import font14
import radiobutton, checkbox, flash, threestate, switch, gauge, traffic # icon files
#import gc

#gc.collect()
# CALLBACKS
# Default CB displays text on a label
def callback(button, arg, label):
    label.value(arg)

# Checkbox CB
def cbcb(checkbox, label):
    label.value(('False', '???', 'True')[checkbox.value()])

# CB for button 'reset radio button': test radiobutton response to value change
def rb_cancel(button, radiobutton, rb0):
    radiobutton.value(rb0)

# CB for button 'reset checkbox': test checkbox response to forced change
def cb_cancel(button, checkbox):
    checkbox.value(0)

# Switch CB
def cbswitch(button, label):
    label.value(str(button.value()))

# Quit button CB
def quit(button):
    GUI.tft.clrSCR()
    GUI.objsched.stop()

# Enable/disable CB
def cb_en_dis(button, itemlist):
    for item in itemlist:
        item.greyed_out(button.value() > 0)

# Label common attributes
labels = { 'width' : 70,
          'fontcolor' : WHITE,
          'border' : 2,
          'fgcolor' : RED,
          'bgcolor' : (0, 40, 0),
          'font' : font14,
          }

# THREAD: keep the gauge moving
def mainthread(objgauge):
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

def lr(n): # y coordinate from logical row
    return 10 + 50 * n

def test():
    print('Testing TFT...')
    my_screen = setup()
# Static labels
    Label((90, lr(0) + 5), font = font10, width = 150, value = 'Flashing buttons')
    Label((244, lr(1) + 5), font = font10, width = 150, value = 'Reset radio button')
    Label((244, lr(2) + 5), font = font10, width = 150, value = 'Reset checkbox')
    Label((244, lr(3) + 5), font = font10, width = 150, value = 'Disable rb, checkbox')
    Label((370, 243), font = font14, width = 70, value = 'Quit')
# Dynamic labels
    lstlbl = []
    for n in range(4):
        lstlbl.append(Label((400, lr(n)), **labels))
# Flashing buttons (RH one responds to long press)
    IconButton((10, lr(0)), icon_module = flash, flash = 1.0,
               callback = callback, args = ['A', lstlbl[0]])
    IconButton((50, lr(0)), icon_module = flash, flash = 1.0,
               callback = callback, args = ['Short', lstlbl[0]],
               lp_callback = callback, lp_args = ['Long', lstlbl[0]])
# Quit button
    IconButton((420, 240), icon_module = radiobutton, callback = quit)
# Radio buttons
    rb = IconRadioButtons(callback = callback)
    rb0 = rb.add_button((10, lr(1)), icon_module = radiobutton, args = ['1', lstlbl[1]])
    rb.add_button((50, lr(1)), icon_module = radiobutton, args = ['2', lstlbl[1]])
    rb.add_button((90, lr(1)), icon_module = radiobutton, args = ['3', lstlbl[1]])
    rb.add_button((130, lr(1)), icon_module = radiobutton, args = ['4', lstlbl[1]])
# Checkbox
    cb = IconButton((10, lr(2)), icon_module = threestate, toggle = True,
                    callback = cbcb, args =[lstlbl[2]])
# Traffic light state change button
    IconButton((10, lr(4)), icon_module = traffic, toggle = True)
# Reset buttons
    IconButton((200, lr(1)), icon_module = radiobutton, callback = rb_cancel, args = [rb, rb0])
    IconButton((200, lr(2)), icon_module = radiobutton, callback = cb_cancel, args = [cb])
# Switch
    sw = IconButton((10, lr(3)), icon_module = switch, callback = cbswitch, toggle = True, args = [lstlbl[3]])
# Disable Checkbox
    cb2 = IconButton((200, lr(3)), icon_module = checkbox, toggle = True,
                    callback = cb_en_dis, args =[[cb, rb, sw]])
# Gauge
    ig = IconGauge((80, lr(5)), icon_module = gauge)
    GUI.objsched.add_thread(mainthread(ig))
    my_screen.run()

test()
