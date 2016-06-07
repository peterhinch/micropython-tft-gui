from plot import PolarGraph, PolarCurve, CartesianGraph, Curve
from math import sin, pi
from constants import *
from tft_local import setup
from cmath import rect

# Polar test: plot an arbitrary function of theta over 2pi radians
# Usage plot.pt(lambda t : (sin(t) ** 2, t))
def pt(f = lambda theta : (sin(3 * theta), theta)):
    setup()
    g = PolarGraph((10, 10), border = 4)
    c = PolarCurve(g)
    nmax = 150
    for n in range(nmax +1):
        theta = 2 * pi * n / nmax
        c.point(rect(*f(theta))) # c.point() takes complex arg

# Cartesian test
def ct():
    setup()
    g = CartesianGraph((10, 10))
    c = Curve(g)
    x = -1
    while x < 1.01:
        y = x**3
        c.point(x, y)
        x += 0.1
    c1 = Curve(g, color=RED)
    x = -1
    while x < 1.01:
        y = x**2
        c1.point(x, y)
        x += 0.1

