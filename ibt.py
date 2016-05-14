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

from ugui import IconButton, IconRadioButtons, Label, WHITE, RED
from tft_local import setup
from font10 import font10
from font14 import font14
import radiobutton, checkbox, switch, mdesign # icon files
import gc
gc.collect()

def callback(button, arg, label):
    label.show(arg)

def cbcb(checkbox, label):
    label.show(('False', '???', 'True')[checkbox.value()])

def rb_cancel(button, radiobutton, rb0):
    radiobutton.value(rb0) # Test radiobutton response to forced change

def cb_cancel(button, checkbox):
    checkbox.value(0) # Test checkbox response to forced change

def cbswitch(button, label):
    label.show(str(button.value()))

def quit(button):
    button.tft.clrSCR()
    button.objsched.stop()

labels = { 'width' : 70,
          'fontcolor' : WHITE,
          'border' : 2,
          'fgcolor' : RED,
          'bgcolor' : (0, 40, 0),
          'font' : font14,
          }

def lr(n): # y coordinate from logical row
    return 10 + 50 * n

def test():
    print('Testing TFT...')
    objsched, tft, touch = setup()
    tft.backlight(100) # light on
    Label(tft, (90, lr(0) + 5), font = font10, width = 150, text = 'Flashing buttons')
    Label(tft, (244, lr(1) + 5), font = font10, width = 150, text = 'Reset radio button')
    Label(tft, (244, lr(2) + 5), font = font10, width = 150, text = 'Reset checkbox')
    Label(tft, (370, 243), font = font14, width = 70, text = 'Quit')
    lstlbl = []
    for n in range(4):
        lstlbl.append(Label(tft, (400, lr(n)), **labels))

    IconButton(objsched, tft, touch, (10, lr(0)), icon_module = mdesign, flash = 1.0, callback = callback, args = ['A', lstlbl[0]])
    IconButton(objsched, tft, touch, (50, lr(0)), icon_module = radiobutton, flash = 1.0, callback = callback, args = ['B', lstlbl[0]])
    IconButton(objsched, tft, touch, (420, 240), icon_module = radiobutton, callback = quit)
    rb = IconRadioButtons(callback = callback)
    rb0 = rb.add_button(objsched, tft, touch, (10, lr(1)), icon_module = radiobutton, args = ['1', lstlbl[1]])
    rb.add_button(objsched, tft, touch, (50, lr(1)), icon_module = radiobutton, args = ['2', lstlbl[1]])
    rb.add_button(objsched, tft, touch, (90, lr(1)), icon_module = radiobutton, args = ['3', lstlbl[1]])
    rb.add_button(objsched, tft, touch, (130, lr(1)), icon_module = radiobutton, args = ['4', lstlbl[1]])

    cb = IconButton(objsched, tft, touch, (10, lr(2)), icon_module = checkbox, toggle = True, callback = cbcb, args =[lstlbl[2]])
    IconButton(objsched, tft, touch, (200, lr(1)), icon_module = radiobutton, callback = rb_cancel, args = [rb, rb0])
    IconButton(objsched, tft, touch, (200, lr(2)), icon_module = radiobutton, callback = cb_cancel, args = [cb])
    IconButton(objsched, tft, touch, (10, lr(3)), icon_module = switch, callback = cbswitch, toggle = True, args = [lstlbl[3]])
    objsched.run()

test()
