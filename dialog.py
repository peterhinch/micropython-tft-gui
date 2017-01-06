# dialog.py Test/demo of modal dialog box for Pybboard TFT GUI

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
from ugui import Button, Label, Screen, Aperture, DialogBox
import font14
import font10
from tft_local import setup
# STANDARD BUTTONS

def quitbutton(x, y):
    def quit(button):
        Screen.shutdown()
    Button((x, y), height = 30, font = font14, callback = quit, fgcolor = RED,
           text = 'Quit', shape = RECTANGLE, width = 80)

def fwdbutton(x, y, cls_screen, *, text='Next', args=[], kwargs={}):
    def fwd(button):
        Screen.change(cls_screen, args = args, kwargs = kwargs)
    Button((x, y), height = 30, font = font14, callback = fwd, fgcolor = RED,
           text = text, shape = RECTANGLE, width = 80)

# Demo of creating a dialog manually
class UserDialogBox(Aperture):
    def __init__(self):
        height = 150
        width = 220
        super().__init__((20, 20), height, width, bgcolor = DARKGREEN)
        y = self.height - 50
        Button(self.locn(20, y), height = 30, width = 80, font = font14, fontcolor = BLACK, fgcolor = RED,
               text = 'Cat', shape = RECTANGLE,
               callback = self.back, args = ('Cat',))
        Button(self.locn(120, y), height = 30, width = 80, font = font14, fontcolor = BLACK, fgcolor = GREEN,
               text = 'Dog', shape = RECTANGLE,
               callback = self.back, args = ('Dog',))
        Button(self.locn(width - 26, 1), height = 25, width = 25, font = font10,
               fgcolor = RED,  text = 'X', shape = RECTANGLE,
               callback = self.back, args = ('Close',))

    def back(self, button, text):
        Aperture.value(text)
        Screen.back()

class BaseScreen(Screen):
    def __init__(self):
        super().__init__()
        Label((0, 0), font = font14, value = 'Dialog box demonstration.')
        Label((0, 100), font = font10, value = 'User written and gdialog generated')
        self.lbl_result = Label((10, 50), font = font10, fontcolor = WHITE, width = 70, border = 2,
                                fgcolor = RED, bgcolor = DARKGREEN)
# User written dialog
        fwdbutton(195, 242, UserDialogBox, text = 'User')
# Dialog built using gdialog.py DialogBox
        dialog_elements = (('Yes', GREEN), ('No', RED), ('Foo', YELLOW))
        fwdbutton(0, 242, DialogBox, text = 'Gen', args = (font14,),
                  kwargs = {'elements' : dialog_elements, 'label' : 'Test dialog'})
        quitbutton(390, 242)

    def on_open(self):
        self.lbl_result.value(Aperture.value())

def test():
    setup()
    Screen.change(BaseScreen)

test()
