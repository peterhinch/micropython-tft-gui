# plot.py Graph plotting extension for Pybboard TFT GUI

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
from ugui import GUI, NoTouch
from constants import *
from math import pi
from cmath import rect

class Curve(object):
    def __init__(self, graph, populate, args=[], origin=(0, 0), excursion=(1, 1), color=YELLOW):
        self.graph = graph
        self.populate = populate
        self.callback_args = args
        self.origin = origin
        self.excursion = excursion
        self.color = color
        self.graph.addcurve(self)
        self.lastpoint = None

    def point(self, x, y):
        pt = self._scale(x, y)
        if self.lastpoint is not None:
            self.graph.line(self.lastpoint, pt, self.color)
        self.lastpoint = pt

    def show(self):
        self.graph.addcurve(self) # May have been removed by clear()
        self.lastpoint = None
        self.populate(self, *self.callback_args)

    def _scale(self, x, y):
        x0, y0 = self.origin
        xr, yr = self.excursion
        return (x - x0) / xr, (y - y0) / yr

class PolarCurve(Curve): # Points are complex
    def __init__(self, graph, populate, color=YELLOW):
        super().__init__(graph, populate, color=color)

    def point(self, z):
        if self.lastpoint is not None:
            self.graph.line(self.lastpoint, z, self.color)
        self.lastpoint = z

class Graph(object):
    def __init__(self, location, height, width, gridcolor):
        border = self.border # border width
        self.x0 = self.location[0] + border
        self.x1 = self.location[0] + self.width - border
        self.y0 = self.location[1] + border
        self.y1 = self.location[1] + self.height - border
        self.gridcolor = gridcolor
        self.curves = set()

    def addcurve(self, curve):
        self.curves.add(curve)

    def clear(self):
        tft = GUI.get_tft()
        self.curves = set()
        tft.fill_rectangle(self.x0, self.y0, self.x1, self.y1, self.bgcolor)
        self.show()

class CartesianGraph(NoTouch, Graph):
    def __init__(self, location, *, height=250, width = 250, fgcolor=WHITE, bgcolor=None, border=None,
                 gridcolor=LIGHTGREEN, xdivs=10, ydivs=10, xorigin=5, yorigin=5):
        NoTouch.__init__(self, location, None, height, width, fgcolor, bgcolor, None, border, None, None)
        Graph.__init__(self, location, height, width, gridcolor)
        self.xdivs = xdivs
        self.ydivs = ydivs
        self.xorigin = xorigin
        self.yorigin = yorigin
        height -= 2 * self.border
        width -= 2 * self.border
        self.x_axis_len = max(xorigin, xdivs - xorigin) * width / xdivs # Max distance from origin in pixels
        self.y_axis_len = max(yorigin, ydivs - yorigin) * height / ydivs
        self.xp_origin = self.x0 + xorigin * width / xdivs # Origin in pixels
        self.yp_origin = self.y0 + (ydivs - yorigin) * height / ydivs

    def show(self):
        tft = GUI.get_tft()
        x0 = self.x0
        x1 = self.x1
        y0 = self.y0
        y1 = self.y1
        if self.ydivs > 0:
            height = y1 - y0
            dy = height / (self.ydivs) # Y grid line
            for line in range(self.ydivs + 1):
                color = self.fgcolor if line == self.yorigin else self.gridcolor
                ypos = int(y1 - dy * line)
                tft.draw_hline(x0, ypos, x1 - x0, color)
        if self.xdivs > 0:
            width = x1 - x0
            dx = width / (self.xdivs) # X grid line
            for line in range(self.xdivs + 1):
                color = self.fgcolor if line == self.xorigin else self.gridcolor
                xpos = int(x0 + dx * line)
                tft.draw_vline(xpos, y0, y1 - y0, color)
        for curve in self.curves:
            curve.show()

    def line(self, start, end, color): # start and end relative to origin and scaled -1 .. 0 .. +1
        tft = GUI.get_tft()
        xs = int(self.xp_origin + start[0] * self.x_axis_len)
        ys = int(self.yp_origin - start[1] * self.y_axis_len)
        xe = int(self.xp_origin + end[0] * self.x_axis_len)
        ye = int(self.yp_origin - end[1] * self.y_axis_len)
        tft.drawLine(xs, ys, xe, ye, color)

class PolarGraph(NoTouch, Graph):
    def __init__(self, location, *, height=250, fgcolor=WHITE, bgcolor=None, border=None,
                 gridcolor=LIGHTGREEN, adivs=3, rdivs=4):
        super().__init__(location, None, height, height, fgcolor, bgcolor, None, border, None, None)
        Graph.__init__(self, location, height, height, gridcolor)
        self.adivs = 2 * adivs # No. of divisions of Pi radians
        self.rdivs = rdivs # No. of divisions of radius
        height -= 2 * self.border
        self.radius = int(height / 2) # Unit: pixels
        self.xp_origin = self.x0 + self.radius # Origin in pixels
        self.yp_origin = self.y0 + self.radius

    def show(self):
        tft = GUI.get_tft()
        x0 = self.x0
        y0 = self.y0
        radius = self.radius
        diam = 2 * radius
        if self.rdivs > 0:
            for r in range(1, self.rdivs + 1):
                tft.draw_circle(self.xp_origin, self.yp_origin, int(radius * r / self.rdivs), self.gridcolor)
        if self.adivs > 0:
            v = complex(1)
            m = rect(1, pi / self.adivs)
            for _ in range(self.adivs):
                self.line(-v, v, self.gridcolor)
                v *= m
        tft.draw_vline(x0 + radius, y0, diam, self.fgcolor)
        tft.draw_hline(x0, y0 + radius, diam, self.fgcolor)
        for curve in self.curves:
            curve.show()

    def line(self, start, end, color): # start and end are complex, 0 <= magnitude <= 1
        tft = GUI.get_tft()
        xs = int(self.xp_origin + start.real * self.radius)
        ys = int(self.yp_origin - start.imag * self.radius)
        xe = int(self.xp_origin + end.real * self.radius)
        ye = int(self.yp_origin - end.imag * self.radius)
        tft.draw_line(xs, ys, xe, ye, color)
