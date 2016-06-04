from constants import *
from ugui import Knob, Dial, Label, Button, ButtonList, GUI
from font14 import font14
from tft_local import setup
from math import pi

# CALLBACKS
# cb_end occurs when user stops touching the control
def callback(knob, control_name):
    print('{} returned {}'.format(control_name, knob.value()))

def knob_moved(knob, dial):
    val = knob.value() # range 0..1
    dial.show(2 * (val - 0.5) * pi)

def quit(button):
    GUI.tft.clrSCR()
    GUI.objsched.stop()

def cb_en_dis(button, disable, itemlist):
    for item in itemlist:
        item.greyed_out(disable)

def cb_style(button, skeleton):
    if skeleton:
        GUI.set_grey_style()
    else:
        GUI.set_grey_style(factor = 2)

def test():
    print('Test TFT panel...')
    my_screen = setup()
    Button((390, 240), font = font14, callback = quit, fgcolor = RED,
           text = 'Quit', shape = RECTANGLE, width = 80, height = 30)
    dial1 = Dial((120, 0), fgcolor = YELLOW, border = 2, pointers = (0.9, 0.7))
    k0 = Knob((0, 0), fgcolor = GREEN, bgcolor=(0, 0, 80), color = (168,63,63), border = 2,
         cb_end = callback, cbe_args = ['Knob1'], cb_move = knob_moved, cbm_args = [dial1]) #, arc = pi * 1.5)
    k1 = Knob((0, 120), fgcolor = WHITE, border = 2, cb_end = callback, cbe_args = ['Knob2'], arc = pi * 1.5)
# On/Off toggle grey style
    bstyle = ButtonList(cb_style)
    button = bstyle.add_button((170, 240), font = font14, fontcolor = WHITE, height = 30, width = 90,
                           fgcolor = GREEN, shape = RECTANGLE, text = 'Grey', args = [True])
    button = bstyle.add_button((170, 240), font = font14, fontcolor = WHITE, height = 30, width = 90,
                           fgcolor = RED, shape = RECTANGLE, text = 'Dim', args = [False])
# On/Off toggle enable/disable
    bs = ButtonList(cb_en_dis)
    lst_en_dis = [bstyle, k0, k1]
    button = bs.add_button((280, 240), font = font14, fontcolor = BLACK, height = 30, width = 90,
                           fgcolor = GREEN, shape = RECTANGLE, text = 'Disable', args = [True, lst_en_dis])
    button = bs.add_button((280, 240), font = font14, fontcolor = BLACK, height = 30, width = 90,
                           fgcolor = RED, shape = RECTANGLE, text = 'Enable', args = [False, lst_en_dis])
    my_screen.run()                                          # Run it!

test()
