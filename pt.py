# pt.py Test/demo of graph plotting extension for Pybboard TFT GUI

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

from plot import PolarGraph, PolarCurve, CartesianGraph, Curve
from ugui import Button, Label, Screen, GUI
from constants import *
from tft_local import setup
from font14 import font14
from font10 import font10
from math import sin, pi
from cmath import rect

# STANDARD BUTTONS

def quitbutton(x, y):
    def quit(button):
        tft = GUI.get_tft()
        tft.clrSCR()
        GUI.objsched.stop()
    return Button((x, y), height = 30, font = font14, callback = quit, fgcolor = RED,
           text = 'Quit', shape = RECTANGLE, width = 80)

def fwdbutton(x, y, screen, text='Next'):
    def fwd(button, screen):
        Screen.change(screen)
    return Button((x, y), height = 30, font = font14, callback = fwd, args = [screen], fgcolor = RED,
           text = text, shape = RECTANGLE, width = 80)

def backbutton(x, y):
    def back(button):
        Screen.back()
    return Button((x, y), height = 30, font = font14, fontcolor = BLACK, callback = back,
           fgcolor = CYAN,  text = 'Back', shape = RECTANGLE, width = 80)

def clearbutton(x, y, graph):
    def clear(button):
        graph.clear()
    return Button((x, y), height = 30, font = font14, fontcolor = BLACK, callback = clear,
           fgcolor = GREEN,  text = 'Clear', shape = RECTANGLE, width = 80)

def refreshbutton(x, y, curvelist):
    def refresh(button):
        for curve in curvelist:
            curve.show()
    return Button((x, y), height = 30, font = font14, fontcolor = BLACK, callback = refresh,
           fgcolor = GREEN,  text = 'Refresh', shape = RECTANGLE, width = 80)

# SCREEN CREATION

def create_back_screen():
    Label((0, 0), font = font14, width = 400, value = 'Ensure back refreshes properly')
    backbutton(390, 242)

def create_base_screen(polar_screen, xy_screen, realtime_screen):
    screen = Screen()
    Label((0, 0), font = font14, width = 400, value = 'plot module demo')
    Label((0, 200), font = font10, width = 400, value = 'RT: simulate realtime data acquisition')
    fwdbutton(0, 242, polar_screen, 'Polar')
    fwdbutton(100, 242, xy_screen, 'XY')
    fwdbutton(200, 242, realtime_screen, 'RT')
    quitbutton(390, 242)
    return screen

def create_polar_screen(next_screen):
    def populate(curve):
        def f(theta):
            return rect(sin(3 * theta), theta) # complex
        nmax = 150
        for n in range(nmax + 1):
            theta = 2 * pi * n / nmax
            curve.point(f(theta))
    screen = Screen()
    backbutton(390, 242)
    fwdbutton(390, 0, next_screen)
    g = PolarGraph((10, 10), border = 4)
    clearbutton(390, 70, g)
    curve = PolarCurve(g, populate)
    refreshbutton(390, 140, (curve,))
    return screen

def create_xy_screen(next_screen):
    def populate_1(curve, func):
        x = -1
        while x < 1.01:
            y = func(x)
            curve.point(x, y)
            x += 0.1

    def populate_2(curve):
        x = -1
        while x < 1.01:
            y = x**2
            curve.point(x, y)
            x += 0.1

    screen = Screen()
    backbutton(390, 242)
    fwdbutton(390, 0, next_screen)
    g = CartesianGraph((10, 10), yorigin = 2) # Asymmetric y axis
    clearbutton(390, 70, g)
    curve1 = Curve(g, populate_1, (lambda x : x**3 + x**2 -x,)) # args demo
    curve2 = Curve(g, populate_2, color = RED)
    refreshbutton(390, 140, (curve1, curve2))
    return screen

# Simulate slow real time data acquisition and plotting
def create_rt_screen(next_screen):
    def populate(curve, buttonlist):
        GUI.objsched.add_thread(acquire(curve, buttonlist))

    def acquire(curve, buttonlist):
        yield
        for but in buttonlist:
            but.greyed_out(True)
        x = -1
        yield
        while x < 1.01:
            y = max(1 - x * x, 0) # possible precison issue
            curve.point(x, y ** 0.5)
            x += 0.05
            yield 0.25
        x = 1
        while x > -1.01:
            y = max(1 - x * x, 0)
            curve.point(x, -(y ** 0.5))
            x -= 0.05
            yield 0.25
        for but in buttonlist:
            but.greyed_out(False)

    screen = Screen()
    buttonlist = []
    buttonlist.append(backbutton(390, 242))
    buttonlist.append(fwdbutton(390, 0, next_screen))
    g = CartesianGraph((10, 10))
    buttonlist.append(clearbutton(390, 70, g))
    curve = Curve(g, populate, (buttonlist,))
    buttonlist.append(refreshbutton(390, 140, (curve,)))
    return screen

def pt():
    print('Testing plot module...')
    back_screen = setup()
    create_back_screen() # Most deeply nested screen first
    polar_screen = create_polar_screen(back_screen)
    xy_screen = create_xy_screen(back_screen)
    realtime_screen = create_rt_screen(back_screen)
    base_screen = create_base_screen(polar_screen, xy_screen, realtime_screen)
    base_screen.run()                                          # Run it!

pt()
