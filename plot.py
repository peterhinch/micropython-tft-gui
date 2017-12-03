# plot.py Graph plotting extension for Pybboard TFT GUI
# Now clips out of range lines

# The MIT License (MIT)
#
# Copyright (c) 2017 Peter Hinch
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
from ugui import NoTouch, dolittle, Screen
from constants import *
from math import pi
from cmath import rect


class Curve(object):
    @staticmethod
    def _clp(badpoint, point):  # 1st point is bad, 2nd is don't know
        xn, yn = point
        xs, ys = badpoint
        if ys > 1:
            xs = xn + (1 - yn)*(xs - xn)/(ys - yn)
            ys = 1
        if ys < -1:
            xs = xn + (1 + yn)*(xs - xn)/(yn - ys)
            ys = -1
        if xs > 1:
            ys = yn + (1 - xn)*(ys - yn)/(xs - xn)
            xs = 1
        if xs < -1:
            ys = yn + (1 + xn)*(ys - yn)/(xn - xs)
            xs = -1
        return xs, ys

    @staticmethod
    def _outcode(point):
        x, y = point
        oc = 1 if y > 1 else 0
        oc |= 2 if y < -1 else 0
        oc |= 4 if x > 1 else 0
        oc |= 8 if x < -1 else 0
        return oc

    def __init__(self, graph, populate=dolittle, args=[], origin=(0, 0), excursion=(1, 1), color=YELLOW):
        self.graph = graph
        self.populate = populate
        self.callback_args = args
        self.origin = origin
        self.excursion = excursion
        self.color = color
        self.graph.addcurve(self)
        self.lastpoint = None
        self.newpoint = None

    def point(self, x=None, y=None):
        if x is None or y is None:
            self.newpoint = None
            self.lastpoint = None
            return

        np = self._scale(x, y)  # In-range points scaled to +-1 bounding box
        self.newpoint = np
        if self.lastpoint is None:  # Nothing to plot. Save for next line.
            # Can leave lastpoint outside bounding box.
            self.lastpoint = self.newpoint
            return

        self._clip()  # Clip to +-1 box
        if self.newpoint is not None:  # At least part of line was in box
            self.graph.line(self.lastpoint, self.newpoint, self.color)
        self.lastpoint = np  # Scaled but not clipped

    # If self.newpoint and self.lastpoint are valid clip them so that both lie
    # in +-1 range. If both are outside the box return None.
    def _clip(self):
        oc1 = self._outcode(self.newpoint)
        oc2 = self._outcode(self.lastpoint)
        if oc1 == 0 and oc2 == 0:  # OK to plot
            return
        if oc1 & oc2:  # Nothing to do
            self.newpoint = None
            return
        if oc1:
            self.newpoint = self._clp(self.newpoint, self.lastpoint)
        if oc2:
            self.lastpoint = self._clp(self.lastpoint, self.newpoint)

    def show(self):
        self.graph.addcurve(self) # May have been removed by clear()
        self.lastpoint = None
        self.populate(self, *self.callback_args)

    def _scale(self, x, y):  # Scale to +-1.0
        x0, y0 = self.origin
        xr, yr = self.excursion
        xs = (x - x0) / xr
        ys = (y - y0) / yr
        return xs, ys

class PolarCurve(Curve): # Points are complex
    def __init__(self, graph, populate=dolittle, args=[], color=YELLOW):
        super().__init__(graph, populate, args, color=color)

    def point(self, z=None):
        if z is None:
            self.newpoint = None
            self.lastpoint = None
            return

        np = self._scale(z.real, z.imag)  # In-range points scaled to +-1 bounding box
        self.newpoint = np
        if self.lastpoint is None:  # Nothing to plot. Save for next line.
            # Can leave lastpoint outside bounding box.
            self.lastpoint = self.newpoint
            return

        self._clip()  # Clip to +-1 box
        if self.newpoint is not None:  # At least part of line was in box
            start = self.lastpoint[0] + self.lastpoint[1]*1j
            end = self.newpoint[0] + self.newpoint[1]*1j
            self.graph.line(start, end, self.color)
        self.lastpoint = np  # Scaled but not clipped


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
        tft = Screen.get_tft()
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
        tft = self.tft
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
        tft = self.tft
        xs = int(self.xp_origin + start[0] * self.x_axis_len)
        ys = int(self.yp_origin - start[1] * self.y_axis_len)
        xe = int(self.xp_origin + end[0] * self.x_axis_len)
        ye = int(self.yp_origin - end[1] * self.y_axis_len)
        tft.drawLine(xs, ys, xe, ye, color)

class PolarGraph(NoTouch, Graph):
    def __init__(self, location, *, height=250, fgcolor=WHITE, bgcolor=None, border=None,
                 gridcolor=LIGHTGREEN, adivs=3, rdivs=4):
        NoTouch.__init__(self, location, None, height, height, fgcolor, bgcolor, None, border, None, None)
        Graph.__init__(self, location, height, height, gridcolor)
        self.adivs = 2 * adivs # No. of divisions of Pi radians
        self.rdivs = rdivs # No. of divisions of radius
        height -= 2 * self.border
        self.radius = int(height / 2) # Unit: pixels
        self.xp_origin = self.x0 + self.radius # Origin in pixels
        self.yp_origin = self.y0 + self.radius

    def show(self):
        tft = self.tft
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
        tft = self.tft
        xs = int(self.xp_origin + start.real * self.radius)
        ys = int(self.yp_origin - start.imag * self.radius)
        xe = int(self.xp_origin + end.real * self.radius)
        ye = int(self.yp_origin - end.imag * self.radius)
        tft.draw_line(xs, ys, xe, ye, color)
