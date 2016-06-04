from constants import *
from ugui import Knob, Dial, Label, Button, Screen, GUI
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
    Screen.tft.clrSCR()
    Screen.objsched.stop()


def fwd(button, screen):
    Screen.change(screen)

def backbutton(x, y):
    def back(button):
        Screen.back()
    Button((x, y), height = 30, font = font14, fontcolor = BLACK, callback = back, fgcolor = CYAN,
           text = 'Back', shape = RECTANGLE, width = 80)

def create_screen_1():
    backbutton(200, 220)
    dial1 = Dial((120, 0), fgcolor = YELLOW, border = 2, pointers = (0.9, 0.7))
    Knob((0, 0), fgcolor = GREEN, bgcolor=(0, 0, 80), color = (168,63,63), border = 2,
         cb_end = callback, cbe_args = ['Knob1'], cb_move = knob_moved, cbm_args = [dial1]) #, arc = pi * 1.5)
    Knob((0, 120), fgcolor = WHITE, border = 2, cb_end = callback, cbe_args = ['Knob2'], arc = pi * 1.5)

def create_screen_0(s1):
    screen = Screen()
    Button((0, 220), height = 30, font = font14, callback = fwd, args = [s1], fgcolor = RED,
           text = 'Next', shape = RECTANGLE, width = 80)

    Button((390, 220), height = 30, font = font14, callback = quit, fgcolor = RED,
           text = 'Quit', shape = RECTANGLE, width = 80)
    return screen

def test():
    print('Test TFT panel...')
    s1 = setup()
    create_screen_1()
    s0 = create_screen_0(s1)
    s0.run()                                          # Run it!

test()
