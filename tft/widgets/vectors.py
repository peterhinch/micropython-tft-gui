# vectors.py Extension to ugui providing vector display

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2019 Peter Hinch

import cmath
from tft.driver.ugui import Screen, NoTouch
from tft.driver.constants import *

conj = lambda v : v.real - v.imag * 1j  # Complex conjugate

# Draw a vector in complex coordinates. Origin and end are complex.
# End is relative to origin.
def pline(tft, origin, vec, color):
    xs, ys = origin.real, origin.imag
    tft.draw_line(round(xs), round(ys), round(xs + vec.real), round(ys - vec.imag), color)

# Draw an arrow; origin and vec are complex, scalar lc defines length of chevron.
# cw and ccw are unit vectors of +-3pi/4 radians for chevrons.
def arrow(tft, origin, vec, lc, color):
    ccw = cmath.exp(3j * cmath.pi/4)  # Unit vectors
    cw = cmath.exp(-3j * cmath.pi/4)
    length, theta = cmath.polar(vec)
    uv = cmath.rect(1, theta)  # Unit rotation vector
    start = -vec
    if length > 3 * lc:  # If line is long
        ds = cmath.rect(lc, theta)
        start += ds  # shorten to allow for length of tail chevrons
    chev = lc + 0j
    pline(tft, origin, vec, color)  # Origin to tip
    pline(tft, origin, start, color)  # Origin to tail
    pline(tft, origin + conj(vec), chev*ccw*uv, color)  # Tip chevron
    pline(tft, origin + conj(vec), chev*cw*uv, color)
    if length > lc:  # Confusing appearance of very short vectors with tail chevron
        pline(tft, origin + conj(start), chev*ccw*uv, color)  # Tail chevron
        pline(tft, origin + conj(start), chev*cw*uv, color)

# Vector display
class Pointer:
    def __init__(self, dial):
        dial.vectors.add(self)
        self.dial = dial
        self.color = BLACK  # SYS_FGCOLOR
        self.val = 0j

    def value(self, v=None, color=None):
        if isinstance(color, tuple):
            self.color = color
        dial = self.dial
        if v is not None:
            if isinstance(v, complex):
                l = cmath.polar(v)[0]
                newval = v /l if l > 1 else v  # Max length = 1.0
            else:
                raise ValueError('Pointer value must be complex.')
            if v != self.val and dial.screen is Screen.current_screen:
                self.show(newval)
            self.val = newval
            dial.show_if_current()
        return self.val

    def show(self, newval=None):
        dial = self.dial
        tft = dial.tft
        color = self.color
        vor = dial.vor  # Dial's origin as a vector
        r = dial.radius * (1 - dial.TICKLEN)
        if dial.arrow:
            if newval is None:  # Refresh
                arrow(tft, vor, r * self.val, 5, color)
            else:
                arrow(tft, vor, r * self.val, 5, dial.bgcolor)
                arrow(tft, vor, r * newval, 5, color)
        else:
            if newval is None:  # Refresh
                pline(tft, vor, r * self.val, color)
            else:
                pline(tft, vor, r * self.val, dial.bgcolor)  # Erase old
                pline(tft, vor, r * newval, color)


class VectorDial(NoTouch):
    TICKLEN = 0.1
    def __init__(self, location, *, height=100, fgcolor=None, bgcolor=None, border=None,
                 ticks=4, arrow=False, pip=None):
        super().__init__(location, None, height, height, fgcolor, bgcolor, None, border, 0, 0)
        self.arrow = arrow
        self.pip = self.fgcolor if pip is None else pip
        border = self.border # border width
        radius = height / 2 - border
        self.radius = radius
        self.ticks = ticks
        self.xorigin = location[0] + border + radius
        self.yorigin = location[1] + border + radius
        self.vor = self.xorigin + 1j * self.yorigin  # Origin as a vector
        self.vectors = set()
        self.drawn = False

    def show(self):
        # cache bound variables
        tft = self.tft
        ticks = self.ticks
        radius = self.radius
        xo = self.xorigin
        yo = self.yorigin
        vor = self.vor
        if self.redraw:  # An overlaying screen has closed. Force redraw.
            self.redraw = False
            self.drawn = False
        if not self.drawn:
            self.drawn = True
            vtstart = (1 - self.TICKLEN) * radius + 0j  # start of tick
            vtick = self.TICKLEN * radius + 0j  # tick
            vrot = cmath.exp(2j * cmath.pi/ticks)  # unit rotation
            for _ in range(ticks):
                pline(tft, vor + conj(vtstart), vtick, self.fgcolor)
                vtick *= vrot
                vtstart *= vrot
            tft.draw_circle(xo, yo, radius, self.fgcolor)

        vshort = 1000  # Length of shortest vector
        for v in self.vectors:
            val = v.value() * radius  # val is complex
            vshort = min(vshort, cmath.polar(val)[0])
            v.show()
        if isinstance(self.pip, tuple) and vshort > 9:
            tft.fill_circle(xo, yo, 3, self.pip)
