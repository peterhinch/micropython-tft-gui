# plot module

This provides a rudimentary means of displaying two dimensional Cartesian (xy) and polar graphs on
TFT displays using the SSD1963 driver. It is an optional extension to the MicroPython GUI library:
this should be installed, configured and tested before use.

# Python files

 1. plot.py The plot library
 2. pt.py Test program.

plot.py should be installed as frozen bytecode.

# concepts

## Graph classes

A user program first instantiates a graph object (``PolarGraph`` or ``CartesianGraph``). This
creates an empty graph image upon which one or more curves may be plotted. Graphs are GUI display
objects: they do not respond to touch.

## Curve classes

The user program then instantiates one or more curves (``Curve`` or ``PolarCurve``) as appropriate
to the graph. Curves may be assigned colors to distinguish them.

A curve is plotted by means of a user defined ``populate`` callback. This assigns points to the
curve in the order in which they are to be plotted. The curve will be displayed on the graph as a
sequence of straight line segments between successive points.

## Coordinates

Graph objects are sized and positioned in terms of TFT screen pixel coordinates, with (0, 0) being
the top left corner of the display, with x increasing to the right and y increasing downwards.

Scaling is provided on Cartesian curves enabling user defined ranges for x and y values. Points on
polar curves aredefined as Python ``complex`` types and should lie within the unit circle. Points
which are out of range will be displayed beyond the confines of the graph, being clipped only by
the physical limits of the display.

# Graph classes

## Class CartesianGraph

Constructor.  
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

Method:
 * ``clear`` Removes all curves from the graph and re-displays the grid.

## Class PolarGraph

Constructor.  
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

Method:
 * ``clear`` Removes all curves from the graph and re-displays the grid.

# Curve classes

## class Curve

The Cartesian curve constructor takes the following positional arguments:

Mandatory argument:
 1. ``graph`` The ``CartesianGraph`` instance.

Optional arguments:
 2. ``populate`` A callback function to populate the curve. See below. Default: a null function.
 3. ``args`` List or tuple of arguments for ``populate`` callback. Default [].
 4. ``origin`` 2-tuple containing x and y values for the origin. Default (0, 0).
 5. ``excursion`` 2-tuple containing scaling values for x and y. Default (1, 1).
 6. ``color`` Default YELLOW.

Methods:
 * ``point`` Arguments x, y. Defaults ``None``. Adds a point to the curve. If a
 prior point exists a line will be drawn between it and the current point. If a
 point is out of range or if either arg is ``None`` no line will be drawn.
 Passing no args enables discontinuous curves to be plotted.
 * ``show`` No args. This can be used to redraw a curve which has been erased by the graph's
 ``clear`` method. In practice likely to be used when plotting changing data from sensors.

The ``populate`` callback may take one or more positional arguments. The first argument is always
the ``Curve`` instance. Subsequent arguments are any specified in the curve's constructor's
``args``. It should repeatedly call the curve's ``point`` method to plot the curve before
returning.

If ``populate`` is not provided the curve may be plotted by successive calls to the ``point``
method. This may be of use where data points are acquired in real time, and realtime plotting is
required.

### Scaling

To plot x values from 1000 to 4000 we would set the ``origin`` x value to 1000 and the ``excursion``
x value to 3000. The ``excursion`` values scale the plotted values to fit the corresponding axis.

## class PolarCurve

The constructor takes the following positional arguments:

Mandatory argument:
 1. ``graph`` The ``CartesianGraph`` instance.

Optional arguments:
 2. ``populate`` A callback function to populate the curve. See below. Default: a null function.
 3. ``args`` List or tuple of arguments for ``populate`` callback. Default [].
 4. ``color`` Default YELLOW.

Methods:
 * ``point`` Argument z, default ``None``. Normally a ``complex``. Adds a point
 to the curve. If a prior point exists a line will be drawn between it and the
 current point. If the arg is ``None`` or lies outside the unit circle no line
 will be drawn. Passing no args enables discontinuous curves to be plotted.
 * ``show`` No args. This can be used to redraw a curve which has been erased by the graph's
 ``clear`` method. In practice likely to be used when plotting changing data from sensors.

The ``populate`` callback may take one or more positional arguments. The first argument is always
the ``Curve`` instance. Subsequent arguments are any specified in the curve's constructor's
``args``. It should repeatedly call the curve's ``point`` method to plot the curve before
returning.

If ``populate`` is not provided the curve may be plotted by successive calls to the ``point``
method. This may be of use where data points are acquired in real time, and realtime plotting is
required.

### Scaling

Complex points should lie within the unit circle to be drawn within the grid.
