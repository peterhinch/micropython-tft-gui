# micropython-gui

Provides a simple touch driven event based GUI interface for the Pyboard when used with a TFT
display. The latter should be based on SSD1963 controller with XPT2046 touch controller. Such
displays are available in electronics stores and on eBay. The software is based on drivers for the
TFT and touch controller from Robert Hammelrath together with a cooperative scheduler of my own
design.

It is targeted at hardware control and display applications.


# Pre requisites

## Pre installation

Before running the GUI the hardware should be tested and the display calibrated according to the
instructions on Robert Hammelrath's site. These resistive touch panels work best when activated by
a stylus or fingernail. They are also subject to jitter to a degree which varies between display
models: the touch library uses digital filtering to reduce the effect of jitter. This uses two
values ``confidence`` and ``margin`` which should be fine tuned to the model in use prior to
running the GUI. The optimum values, together with calibration data, should be stored in the file
tft_local.py listed below.

Users should familiarise themselves with building Micropython from source, and with the technique
for installing Python modules as persistent bytecode. Instructions on how to do this may be found
[here](http://forum.micropython.org/viewtopic.php?f=6&t=1776).

Some familiarity with callbacks and event driven programming will be of help in developing
applications.

## Python files

Documentation for the underlying libraries may be found at these sites:
[TFT driver](https://github.com/robert-hh/SSD1963-TFT-Library-for-PyBoard.git)
[XPT2046 driver](https://github.com/robert-hh/XPT2046-touch-pad-driver-for-PyBoard.git)
[Scheduler](https://github.com/peterhinch/Micropython-scheduler.git)

Hardware drivers:
 1. TFT_io.py Low level TFT driver.
 2. touch.py Touch controller driver.

Core files:
 1. tft.py TFT driver.
 2. usched.py Scheduler.
 3. delay.py Used with the scheduler for watchdog type delays.
 4. ugui.py The micro GUI library.
 5. tft_local.py Local hardware definition (user defined settings including optional calibration
 data).

Optional files:
 1. font10.py Font used by the test programs.
 2. font14.py Font used by the test programs.

Test/demo programs:
 1. vst.py A test program for vertical linear sliders.
 2. hst.py Tests horizontal slider controls, meters and LED.
 3. buttontest.py Pushbuttons and checkboxes.
 4. knobtest.py Rotary control test.

It should be noted that by the standards of the Pyboard this is a large library. Attempts to use it
in the normal way are likely to provoke memory errors owing to heap fragmentation. It is
recommended that the core and optional files are 'frozen' with the firmware as persistent bytecode,
with the possible exception of tft_local.py: keeping this in the filesystem facilitates adjusting
the ``confidence`` and ``margin`` values for best response. You may also want to freeze any other
fonts you plan to use. The hardware divers listed above cannot be frozen as they use inline
assembler and Viper code.

It is also wise to issue ctrl-D to soft reset the Pyboard before importing a module which uses the
library. The test programs require a ctrl-D before import.

Instructions on creating font files may be found in the README for the TFT driver.

# Concepts

### Coordinates

In common with most displays, the top left hand corner of the display is (0, 0) with increasing
values of x to the right, and increasing values of y downward. Display objects exist within a
rectangular bounding box; in the case of touch sensitive controls this corresponds to the sensitive
region. The location of the object is defined as the coordinates of the top left hand corner of the
bounding box. Locations are defined as a 2-tuple (x, y).

### Colours

These are defined as a 3-tuple (r, g, b) with values of red, green and blue in range 0 to 255. The
interface and this document uses the American spelling (color) throughout for consistency with the
TFT library.

### Callbacks

The interface is event driven. Optional callbacks may be provided which will be executed when a
given event occurs. A callback function receives positional arguments. The first is a reference to
the object raising the callback. Subsequent arguments are user defined, and are specified as a list
of items. Note that a list rather than a tuple should be used. Callbacks are optional, as are the
argument lists - by default a null function and an empty list are provided.

# Initialisation Code

The following initialisation code is required in any application:
```python
from tft_local import setup
objsched, tft, touch = setup()
tft.backlight(100) # light on
```
The second line produces instances of the scheduler, the tft display and the touch interface. These
are required when instantiating GUI classes.

# Displays

These classes provide ways to display data and are not touch sensitive.

## Class Label

Displays text in a fixed length field. Constructor mandatory positional arguments:
 1. ``tft`` The TFT object.
 2. ``location`` 2-tuple defining position.
Keyword only arguments:
 * ``font`` Mandatory. Font object to use.
 * ``width`` Mandatory. The width of the object in pixels.
 * ``border`` Border width in pixels - typically 2. If omitted, no border will be drawn.
 * ``fgcolor`` Color of border. Defaults to system color.
 * ``bgcolor`` Background color of object. Defaults to system background.
 * ``fontcolor`` Text color. Defaults to system text color.
 * ``text`` Initial text. Defaults to ''.
Method:
 * ``show`` Argument: ``text``. Displays the string in the label.

## Class Dial

Displays angles in a circular dial. Angles are in radians with zero represented by a vertical
pointer. Positive angles appear as clockwise rotation of the pointer. The object can display
multiple angles using pointers of differing lengths (e.g. clock face). Constructor mandatory
positional arguments:
 1. ``tft`` The TFT object.
 2. ``location`` 2-tuple defining position.
Keyword only arguments (all optional):
 * ``height`` Dimension of the square bounding box. Default 100 pixels.
 * ``fgcolor`` Color of border. Defaults to system color.
 * ``bgcolor`` Background color of object. Defaults to system background.
 * ``border`` Border width in pixels - typically 2. If omitted, no border will be drawn.
 * ``pointers`` Tuple of floats in range 0 to 0.9. Defines the length of each pointer as a
 proportion of the dial diameter. Default (0.9,) i.e. one pointer.
 * ``ticks`` Defines the number of graduations around the dial. Default 4.
Method:
 * ``show`` Displays an angle. Arguments: ``angle`` (mandatory), ``pointer`` the pointer index
 (default 0).

## Class LED

Displays a boolean state. Can display other information by varying the color. Constructor mandatory
positional arguments:
 1. ``tft`` The TFT object.
 2. ``location`` 2-tuple defining position.
Keyword only arguments (all optional):
 * ``height`` Dimension of the square bounding box. Default 30 pixels.
 * ``fgcolor`` Color of border. Defaults to system color.
 * ``bgcolor`` Background color of object. Defaults to system background.
 * ``border`` Border width in pixels - typically 2. If omitted, no border will be drawn.
 * ``color`` The color of the LED. Default RED.
Methods:
 * ``off`` No arguments. Turns the LED off.
 * ``on`` Optional arguemnt ``color``. Turns the LED on. By default it will use the ``color``
 specified in the constructor.

## Class Meter

This displays a single value in range 0.0 to 1.0 on a vertical linear meter. Constructor mandatory
positional arguments:
 1. ``tft`` The TFT object.
 2. ``location`` 2-tuple defining position.
Keyword only arguments:
 * ``height`` Dimension of the bounding box. Default 200 pixels.
 * ``width`` Dimension of the bounding box. Default 30 pixels.
 * ``font`` Font to use in any legends. Default: ``None`` No legends will be displayed.
 * ``legends`` A tuple of strings to display on the centreline of the meter. These should be
 short to physically fit. They will be displayed equidistantly along the vertical scale, with
 string 0 at the bottom. Default ``None``: no legends will be shown.
 * ``divisions`` Count of graduations on the meter scale. Default 10.
 * ``fgcolor`` Color of border. Defaults to system color.
 * ``bgcolor`` Background color of object. Defaults to system background.
 * ``fontcolor`` Text color. Defaults to system text color.
 * ``pointercolor`` Color of meter pointer. Defaults to ``fgcolor``.
 * ``value`` Initial value to display. Default 0.
Methods:
 * ``value`` Optional argument ``val``. If set, refreshes the meter display with a new value,
 otherwise returns its current value. Range 0.0 to 1.0.

# Controls

These classes provide touch-sensitive objects capable of both the display and entry of data. If the
user moves the control, its value will change and an optional callback will be executed. If a
thread alters a control's value, its appearance will change to reflect this.

## Class Slider

These emulate linear potentiometers. Vertical ``Slider`` and horizontal ``HorizSlider`` variants
are available. These are constructed and used similarly. The shortforms (v) or (h) are used below
to identify these variants. See the note above on callbacks.

Constructor mandatory positional arguments:
 1. ``objsched`` The scheduler instance.
 2. ``tft`` The TFT instance.
 3. ``objtouch`` The touch panel instance.
 4. ``location`` 2-tuple defining position.
 5. ``font`` Font to use for any legends.
Optional keyword only arguments:
 * ``height`` Dimension of the bounding box. Default 200 pixels (v), 30 (h).
 * ``width`` Dimension of the bounding box. Default 30 pixels (v), 200 (h).
 * ``divisions`` Number of graduations on the scale. Default 10.
 * ``legends`` A tuple of strings to display near the slider. These will be distributed equally
 along its length, starting at the bottom (v) or left (h).
 * ``fgcolor`` Color of foreground (the control itself). Defaults to system color.
 * ``bgcolor`` Background color of object. Defaults to system background.
 * ``fontcolor`` Text color. Defaults to system text color.
 * ``slidecolor`` Color for the slider. Defaults to the foreground color.
 * ``border`` Width of border. Default ``None``: no border will be drawn. If a value (typically 2)
 is provided, a border line will be drawn around the control.
 * ``cb_end`` Callback function which will run when the user stops touching the control.
 * ``cbe_args`` A list of arguments for the above callback. Default ``[]``.
 * ``cb_move`` Callback function which will run when the user moves the slider or the value is
 changed.
 * ``cbm_args`` A list of arguments for the above callback. Default ``[]``.
 * ``value`` The initial value. Default 0.0: slider will be at the bottom (v), left (h).
Methods:
 * ``value`` Optional argument ``val``. If set, moves the slider position to correspond to a new
 value, otherwise returns the control's current value. Range 0.0 to 1.0.

## Class Knob

This emulates a rotary control capable of being rotated through a predefined arc.

Constructor mandatory positional arguments:
 1. ``objsched`` The scheduler instance.
 2. ``tft`` The TFT instance.
 3. ``objtouch`` The touch panel instance.
 4. ``location`` 2-tuple defining position.
Optional keyword only arguments:
 * ``height`` Dimension of the square bounding box. Default 100 pixels.
 * ``arc`` Amount of movement available. Default 2*PI radians (360 degrees).
 * ``ticks`` Number of graduations around the dial. Default 9.
 * ``fgcolor`` Color of foreground (the control itself). Defaults to system color.
 * ``bgcolor`` Background color of object. Defaults to system background.
 * ``color`` Fill color for the control knob. Default: no fill.
 * ``border`` Width of border. Default ``None``: no border will be drawn. If a value (typically 2)
 is provided, a border line will be drawn around the control.
 * ``cb_end`` Callback function which will run when the user stops touching the control.
 * ``cbe_args`` A list of arguments for the above callback. Default ``[]``.
 * ``cb_move`` Callback function which will run when the user moves the knob or the value is
 changed.
 * ``cbm_args`` A list of arguments for the above callback. Default ``[]``.
 * ``value`` Initial value. Default 0.0: knob will be at its most counterclockwise position.
Methods:
 * ``value`` Optional argument ``val``. If set, moves the knob to correspond to a new value,
 otherwise returns the control's current value. Range 0.0 to 1.0.

## Class Checkbox

This provides for boolean data entry and display. In the ``True`` state the control can show an 'X'
or a filled block of color.

Constructor mandatory positional arguments:
 1. ``objsched`` The scheduler instance.
 2. ``tft`` The TFT instance.
 3. ``objtouch`` The touch panel instance.
 4. ``location`` 2-tuple defining position.
Optional keyword only arguments:
 * ``height`` Dimension of the square bounding box. Default 30 pixels.
 * ``fillcolor`` Fill color of checkbox when ``True``. Default ``None``: an 'X' will be drawn.
 * ``fgcolor`` Color of foreground (the control itself). Defaults to system color.
 * ``bgcolor`` Background color of object. Defaults to system background.
 * ``border`` Width of border. Default ``None``: no border will be drawn. If a value (typically 2)
 is provided, a border line will be drawn around the control.
 * ``callback`` Callback function which will run when the value changes.
 * ``args`` A list of arguments for the above callback. Default ``[]``.
 * ``value`` Initial value. Default ``False``.
Methods:
 * ``value`` Optional boolean argument ``val``. If provided updates the control's value, otherwise
 returns its current value.

## Class Button

This emulates a pushbutton, with a callback being executed each time the button is pressed. Buttons
may be any one of three shapes: CIRCLE, RECTANGLE or CLIPPED_RECT.

Constructor mandatory positional arguments:
 1. ``objsched`` The scheduler instance.
 2. ``tft`` The TFT instance.
 3. ``objtouch`` The touch panel instance.
 4. ``location`` 2-tuple defining position.
Mandatory keyword only argument:
 * ``font`` Font or button text
Optional keyword only arguments:
 * ``shape`` CIRCLE, RECTANGLE or CLIPPED_RECT. Default CIRCLE.
 * ``height`` Height of the bounding box. Default 50 pixels.
 * ``width`` Width of the bounding box. Default 50 pixels.
 * ``fill`` Boolean. If ``True`` the button will be filled with the current ``fgcolor``.
 * ``fgcolor`` Color of foreground (the control itself). Defaults to system color.
 * ``bgcolor`` Background color of object. Defaults to system background.
 * ``fontcolor`` Text color. Defaults to system text color.
 * ``litcolor`` If provided the button will display this color for one second after being pressed.
 * ``border`` Width of border. Default ``None``: no border will be drawn. If a value (typically 2)
 is provided, a border line will be drawn around the control.
 * ``text`` Shown in centre of button. Default ''.
 * ``show`` Boolean, default ``True``. If ``False`` button will not be displayed.
 * ``callback`` Callback function which runs when button is pressed.
 * ``args`` A list of arguments for the above callback. Default ``[]``.
There are no methods for normal access.

## Class Buttonset: a button with multiple states

A ``Buttonset`` groups a number of buttons together to implement a button which toggles between
states each time it is pressed. For example it might toggle between a green Start button and a red
Stop button. The buttons are defined and added in turn to the ``Buttonset`` object. Typically they
will be the same size, shape and location but will differ in color and/or text. At any time just
one of the buttons will be visible, initially the first to be added to the object.

Buttons in a ``Buttonset`` should not have callbacks. The ``Buttonset`` has its own user supplied
callback which will run each time the object is pressed. However each button can have its own list
of ``args``. The callback will receive the arguments of the currently visible button.

The constructor argument:
 * ``user_callback`` The callback function. Mandatory.

Methods:
 * ``add_button`` Adds a button to the ``Buttonset``. Arguments: as per the ``Button`` constructor.
 * ``run`` Called once all buttons have been added. No arguments. Displays first button and returns.

Typical usage is as follows:
```python
table = [
     {'fgcolor' : GREEN, 'shape' : CLIPPED_RECT, 'text' : 'Start', 'args' : ['Live']},
     {'fgcolor' : RED, 'shape' : CLIPPED_RECT, 'text' : 'Stop', 'args' : ['Die']},
]
bs = Buttonset(callback)
for t in table: # Buttons overlay each other at same location
    bs.add_button(objsched, tft, touch, (10, 10), font = font14, fontcolor = BLACK, **t)
bs.run()
```

## Class RadioButtons

These comprise a set of buttons at different locations. When a button is pressed, it becomes
highlighted and remains so until another button is pressed. A callback runs each time The
current button is changed.

Constructor positional arguments:
 * ``user_callback`` Callback when a new button is pressed. Mandatory.
 * ``highlight`` Color to use for the highlighted button. Mandatory.
 * ``selected`` Index of initial button to be highlighted. Default 0.

Methods:
 * ``add_button`` Adds a button to the ``Buttonset``. Arguments: as per the ``Button`` constructor.
 * ``run`` Called once all buttons have been added. No arguments. Displays object and returns.

Typical usage:
```python
table = [
    {'text' : '1', 'args' : ['1']},
    {'text' : '2', 'args' : ['2']},
    {'text' : '3', 'args' : ['3']},
    {'text' : '4', 'args' : ['4']},
]
x = 0
rb = RadioButtons(callback, BLUE) # color of selected button
for t in table:
    rb.add_button(objsched, tft, touch, (x, 180), font = font14, fontcolor = WHITE,
                    fgcolor = (0, 0, 90), height = 40, **t)
    x += 60 # Horizontal row of buttons
rb.run()
```