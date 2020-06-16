# dialog.py Test/demo of modal dialog box for Pybboard TFT GUI
# Adapted for (and requires) uasyncio V3

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2016-2020 Peter Hinch

from tft.driver.constants import *
from tft.driver.tft_local import setup
from tft.driver.ugui import Screen, Aperture

from tft.widgets.dialog import DialogBox
from tft.widgets.buttons import Button
from tft.widgets.label import Label

from tft.fonts import font14
from tft.fonts import font10

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
