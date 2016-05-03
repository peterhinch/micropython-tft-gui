from font10 import font10
from tft_local import setup
from ugui import Knob, Dial, Label, Button, WHITE, YELLOW, GREEN, RED, CLIPPED_RECT
from math import pi

# CALLBACKS
# cb_end occurs when user stops touching the control
def callback(knob, control_name):
    print('{} returned {}'.format(control_name, knob.value()))

def knob_moved(knob, dial):
    val = knob.value() # range 0..1
    dial.show(2 * (val - 0.5) * pi)

def doquit(button):
    button.objsched.stop()

def test():
    print('Test TFT panel...')
    objsched, tft, touch = setup()
    tft.backlight(100) # light on
    Button(objsched, tft, touch, (400, 240), font = font10, callback = doquit, fgcolor = RED,
           height = 30, text = 'Quit', shape = CLIPPED_RECT)
    dial1 = Dial(tft, (120, 0), fgcolor = YELLOW, border = 2, pointers = (0.9, 0.7))
    Knob(objsched, tft, touch, (0, 0), fgcolor = GREEN, bgcolor=(0, 0, 80), color = (168,63,63), border = 2,
         cb_end = callback, cbe_args = ['Knob1'], cb_move = knob_moved, cbm_args = [dial1]) #, arc = pi * 1.5)
    Knob(objsched, tft, touch, (0, 120), fgcolor = WHITE, border = 2,
         cb_end = callback, cbe_args = ['Knob2'], arc = pi * 1.5)
    objsched.run()                                          # Run it!

test()
