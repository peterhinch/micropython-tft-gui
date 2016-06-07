# plot module

This provides a rudimentary means of displaying Cartesian and polar graphs on TFT displays using
the SSD1963 driver. It is an optional extension to the MicroPython GUI library: this should be
installed, configured and tested before use.

# Python files

 1. plot.py The plot library
 2. pt.py Test programs: run pt.ct() for a Cartesian graph, pt.pt() for polar.

# concepts

## Graph classes

A user program first instantiates a graph object (``PolarGraph`` or ``CartesianGraph``). This
creates an empty graph image upon which one or more curves may be plotted. Graphs are rendered
directly onto the display hardware: this means that they are transient images rather than GUI
controls. If the user code changes the current screen, on return the graph will be lost. Treating
them otherwise would consume unreasonable amounts of RAM.

## Curve classes

The user program then instantiates one or more curves (``Curve`` or ``PolarCurve``) as appropriate
to the graph. Curves may be assigned colors to distinguish them. Points are then assigned to a
curve in the order in which they are to be plotted. The curve will be displayed on the graph as a
sequence of straight line segments between successive points.

## Coordinates

Graph objects are defined in terms of TFT screen pixel coordinates, with (0, 0) being the top left
corner of the display, with x increasing to the right and y increasing downwards.

Scaling is provided on Cartesian curves enabling user defined ranges for x and y values. Points on
polar curves aredefined as Python ``complex`` types and should lie within the unit circle. Points
which are out of range will be displayed beyond the confines of the graph, being clipped only by
the physical limits of the display.

# Graph classes

## Class CartesianGraph

The only user access is via the constructor.  
Mandatory positional argument:  
 1. ``location`` 2-tuple defining position.

Keyword only arguments (all optional):  
 * ``height`` Dimension of the bounding box. Default 250 pixels.
 * ``width`` Dimension of the bounding box. Default 250 pixels.
 * ``fgcolor`` Color of the axis lines. Defaults to WHITE.
 * ``bgcolor`` Background color of graph. Defaults to system background.
 * ``border`` Width of border. Default ``None``: no border will be drawn.
 * ``gridcolor`` Color of grid. Default LIGHTGREEN.
 * ``xdivs`` Number of divisions (grid lines) on x axis. Default 10.
 * ``ydivs`` Number of divisions on y axis. Default 10.
 * ``xorigin`` Location of origin in terms of grid divisions. Default 5.
 * ``yorigin`` As ``xorigin``. The default of 5, 5 with 10 grid lines on each axis puts the origin
 at the centre of the graph. Settings of 0, 0 would be used to plot positive values only.

## Class PolarGraph

The only user access is via the constructor.  
Mandatory positional argument:  
 1. ``location`` 2-tuple defining position.

Keyword only arguments (all optional):  
 * ``height`` Dimension of the square bounding box. Default 250 pixels.
 * ``fgcolor`` Color of foreground (the axis lines). Defaults to WHITE.
 * ``bgcolor`` Background color of object. Defaults to system background.
 * ``border`` Width of border. Default ``None``: no border will be drawn.
 * ``gridcolor`` Color of grid. Default LIGHTGREEN.
 * ``adivs`` Number of angle divisions per quadrant. Default 3.
 * ``rdivs`` Number radius divisions. Default 4.

# Curve classes

## class Curve

The Cartesian curve constructor takes the following positional arguments:

 1. ``graph`` Mandatory. The ``CartesianGraph`` instance.
 2. ``origin`` 2-tuple containing x and y values for the origin. Default (0, 0).
 3. ``excursion`` 2-tuple containing scaling values for x and y. Default (1, 1).
 4. ``color`` Default YELLOW.

Method:
 * ``point`` Arguments x, y. Adds a point to the curve. If a prior point exists a line will be drawn
 between it and the current point.

### Scaling

To plot x values from 1000 to 4000 we would set the ``origin`` x value to 1000 and the ``excursion``
x value to 3000.

## class PolarCurve

The constructor takes the following positional arguments:
 1. ``graph`` Mandatory. The ``CartesianGraph`` instance.
 2. ``color`` Default YELLOW.

Method:
 * ``point`` Argument z which must be ``complex``. Adds a point to the curve. If a prior point
 exists a line will be drawn between it and the current point.

### Scaling

Complex points should lie within the unit circle to be drawn within the grid.
