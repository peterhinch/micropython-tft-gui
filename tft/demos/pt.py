# pt.py Test/demo of graph plotting extension for Pybboard TFT GUI
# Adapted for (and requires) uasyncio V3

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2016-2020 Peter Hinch

import uasyncio as asyncio
from math import sin, cos, pi
from cmath import rect

from tft.driver.plot import PolarGraph, PolarCurve, CartesianGraph, Curve
from tft.driver.ugui import Screen
from tft.driver.constants import *
from tft.driver.tft_local import setup

from tft.widgets.label import Label
from tft.widgets.buttons import Button

from tft.fonts import font14
from tft.fonts import font10

# STANDARD BUTTONS

def quitbutton(x, y):
    def quit(button):
        Screen.shutdown()
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

# Tests overlaying a plot with another screen
class BackScreen(Screen):
    def __init__(self):
        super().__init__()
        Label((0, 0), font = font10, value = 'Ensure back refreshes properly')
        backbutton(390, 242)

# Base screen with pushbuttons to launch demos.
class BaseScreen(Screen):
    def __init__(self):
        super().__init__()
        Label((0, 0), font = font14, value = 'plot module demo.')
        Label((0, 100), font = font10, value = 'RT: simulate realtime data acquisition.')
        Label((0, 140), font = font10, value = 'Over, Lines: test clipping.')
        fwdbutton(0, 242, PolarScreen, 'Polar')
        fwdbutton(100, 242, XYScreen, 'XY')
        fwdbutton(200, 242, RealtimeScreen, 'RT')
        fwdbutton(0, 200, PolarORScreen, 'Over')
        fwdbutton(100, 200, DiscontScreen, 'Lines')
        quitbutton(390, 242)

# Simple polar plot.
class PolarScreen(Screen):
    def __init__(self):
        super().__init__()
        backbutton(390, 242)
        fwdbutton(390, 0, BackScreen)
        g = PolarGraph((10, 10), border = 4)
        clearbutton(390, 70, g)
        curve = PolarCurve(g, self.populate)
        refreshbutton(390, 140, (curve,))

    def populate(self, curve):
        def f(theta):
            return rect(sin(3 * theta), theta) # complex
        nmax = 150
        for n in range(nmax + 1):
            theta = 2 * pi * n / nmax
            curve.point(f(theta))

# Test clipping
class PolarORScreen(Screen):
    def __init__(self):
        super().__init__()
        backbutton(390, 242)
        fwdbutton(390, 0, BackScreen)
        g = PolarGraph((10, 10), border = 4)
        clearbutton(390, 70, g)
        curve = PolarCurve(g, self.populate, (1,))
        curve1 = PolarCurve(g, self.populate, (rect(1, pi/5),), color=RED)
        refreshbutton(390, 140, (curve, curve1))

    def populate(self, curve, rot):
        def f(theta):
            return rect(1.15*sin(5 * theta), theta)*rot # complex
        nmax = 150
        for n in range(nmax + 1):
            theta = 2 * pi * n / nmax
            curve.point(f(theta))

# Simple Cartesian plot with asymmetric axis and two curves.
class XYScreen(Screen):
    def __init__(self):
        super().__init__()
        backbutton(390, 242)
        fwdbutton(390, 0, BackScreen)
        g = CartesianGraph((10, 10), yorigin = 2) # Asymmetric y axis
        clearbutton(390, 70, g)
        curve1 = Curve(g, self.populate_1, (lambda x : x**3 + x**2 -x,)) # args demo
        curve2 = Curve(g, self.populate_2, color = RED)
        refreshbutton(390, 140, (curve1, curve2))

    def populate_1(self, curve, func):
        x = -1
        while x < 1.01:
            y = func(x)
            curve.point(x, y)
            x += 0.1

    def populate_2(self, curve):
        x = -1
        while x < 1.01:
            y = x**2
            curve.point(x, y)
            x += 0.1

# Test of discontinuous curves and those which provoke clipping
class DiscontScreen(Screen):
    def __init__(self):
        super().__init__()
        backbutton(390, 242)
        fwdbutton(390, 0, BackScreen)
        g = CartesianGraph((10, 10))
        clearbutton(390, 70, g)
        curve1 = Curve(g, self.populate_1, (1.1,))
        curve2 = Curve(g, self.populate_1, (1.05,), color=RED)
        curve3 = Curve(g, self.populate_3, color=BLUE)
        refreshbutton(390, 140, (curve1, curve2, curve3))

    def populate_3(self, curve):
        for x, y in ((-2, -0.2), (-2, 0.2), (-0.2, -2), (0.2, -2), (2, 0.2), (2, -0.2), (0.2, 2), (-0.2, 2)):
            curve.point(x, y)
            curve.point(0,0)
            curve.point()

    def populate_1(self, curve, mag):
        theta = 0
        delta = pi/32
        while theta <= 2 * pi:
            curve.point(mag*sin(theta), mag*cos(theta))
            theta += delta

# Simulate slow real time data acquisition and plotting
class RealtimeScreen(Screen):
    def __init__(self):
        super().__init__()
        self.aqu_task = None
        backbutton(390, 242)
        fwdbutton(390, 0, BackScreen)
        cartesian_graph = CartesianGraph((10, 10))
        self.clearbutton(390, 70, cartesian_graph)
        curve = Curve(cartesian_graph, self.populate)
        refreshbutton(390, 140, (curve,))

    def populate(self, curve):
        self.aqu_task = asyncio.create_task(self.acquire(curve))
        self.reg_task(self.aqu_task, True)

    async def acquire(self, curve):
        x = -1
        await asyncio.sleep(0)
        while x < 1.01:
            y = max(1 - x * x, 0) # possible precision issue
            curve.point(x, y ** 0.5)
            x += 0.05
            await asyncio.sleep_ms(250)
        x = 1
        while x > -1.01:
            y = max(1 - x * x, 0)
            curve.point(x, -(y ** 0.5))
            x -= 0.05
            await asyncio.sleep_ms(250)

    def clearbutton(self, x, y, graph):
        def clear(button):
            self.aqu_task.cancel()
            graph.clear()
        return Button((x, y), height = 30, font = font14, fontcolor = BLACK, callback = clear,
            fgcolor = GREEN,  text = 'Clear', shape = RECTANGLE, width = 80)


def pt():
    print('Testing plot module...')
    setup()
    Screen.change(BaseScreen)

pt()
