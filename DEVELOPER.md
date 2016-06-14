# Developer notes for micropython-gui

These notes are intended for those wishing to implement new controls or displays for this library.
This document is a work in progress, is incomplete and may contain errors.

# Introduction

GUI objects comprise displays and controls. They differ in that displays don't respond to touch
whereas controls do. Displays are subclassed from the ``NoTouch`` class. Controls are subclassed
from ``Touchable`` (which is itself subclassed from ``NoTouch``. Understanding the functionality of
these base classes is crucial to maintaining consistency and avoiding code duplication.

GUI objects have a ``value`` method which is the principal user interface. It accesses an
underlying ``_value`` variable which may be of various types. If called with no arguments it
returns the current ``_value``. Called with a single argument it checks for a difference with the
current ``_value`` and, if there is one, updates ``_value``. It updates the control using the
``show`` method outlined below. The intention here is that the value of controls and displays can
programmatically be altered. On occasion the ``value`` method will need to be subclassed, for
example if data validation, modification or type conversion is required.

GUI objects must implement a ``show`` method capable of being called with no arguments. This
should display the object: the underlying code will call it without arguments when a screen is
displayed (for example after a screen change). By default it is also called without arguments when
a control's value changes. Its behaviour can be modified by ``NoTouch`` bound variables
``initial_value`` and ``redraw``. The aim here is to avoid the situation where a value change
redraws the entire control which can lead to flicker, especially in the case of controls whose
value changes in response to a drag. These variables are discussed in detail below.

Touchable objects must implement a ``_touched`` method which determines how the control responds to
a touch. The method receives the pixel coordinates of the touch (which will be within the control's
bounding box).

The other user interface is the ``greyed_out`` method. Called without args it returns the current
disabled state of the control (``True`` if disabled). Called with a boolean (allowable only for
touchable controls) it greys out (``True``) or enables (``False``) the control, with its appearance
reflecting the change. Disabled controls should still respond to programmatic changes (calls to
``value``).

# Overall design

The ``Screen` class is at the core of the GUI functionality, and some familiarity with it is
necessary for designers of controls and displays. The class maintains two instance variables
``touchlist`` and ``displaylist``. These contain the touchable controls and the display objects on
that screen. Objects are automatically added to the correct list by the ``addobject`` class method,
which is called by the ``NoTouch`` constructor.

The ``Screen`` class has a class variable ``current_screen`` which holds the ``Screen`` instance
which is current. Currency carries two implications. When GUI objects are instantiated, they are
assigned to the current screen. And when a ``Screen`` is displayed by a call to ``Screen.show``,
the class method finds the correct instance in that variable; i.e. the current screen is the one
visible on the physical hardware.

The ``Screen`` class controls touch response. When the first ``Screen`` object is instatiated a
thread ``Screen._touchtest`` is initiated. This runs forever and tests whether the screen is being
touched. If it is, it checks each touchable object on the current screen to see if it is currently
capable of responding to touch. If it is, the object's ``_trytouch`` method is called. The
``Touchable`` class has a default method which serves for most controls. If the screen is not being
touched, the thread checks each touchable object on the current screen to see if it was formerly
being touched. If it was, the formerly touched status is cleared down and the object's ``_untouched``
method is called. This enables release callbacks to be implemented. Again a default method is
provided by the ``Touchable`` class.

The ``Screen`` class also provides class methods for changing the current screen and reverting to
the previous one. These clear the screen and call the ``Screen.show`` class method, which redraws
all objects on the newly current screen. It does this via the object's ``draw_border`` and ``show``
methods, called without arguments.

The ``Screen`` class is subclassed from the ``GUI`` class. This has a ``setup`` class method which
is called from ``tft_local`` after initialising the hardware. It stores the tft, touchscreen and
scheduler instances in class methods for access throughout the library. It also supports the
``set_grey_style`` class method and the ``get_tft`` method. This provides access to the TFT. It
accepts the greyed-out status of the control instance as its argument and instructs the ``TFT_G``
class of the correct greyed-out status to use.

In practice, controls and displays access the TFT by means of the ``tft`` property of the ``NoTouch``
base class. This sets the greyed out status of the ``TFT_G`` and returns the instance.

Access to the TFT module is mediated by the ``TFT_G`` class. This is subclassed from the TFT
module's ``TFT`` class. Its purpose is to handle the colors of greyed out controls: for consistency
its graphics primitives are used throughout the GUI in preference to those of the underlying ``TFT``
class.

# class NoTouch

Constructor arguments (all mandatory, positional):

 1. ``location`` 2-tuple defining the location of the top left corner of the control in screen
 coords.
 2. ``font`` Font object to use (may be ``None`` if control has no text elements).
 3. ``height`` Height in pixels. In the ``Label`` class it is ``None`` and computed in the
 constructor.
 4. ``width`` Width in pixels.
 5. ``fgcolor`` 3-tuple defining the foreground color, or ``None``. If ``None`` the screen's
 foreground color is used.
 6. ``bgcolor`` 3-tuple defining the background color, or ``None``. If a color is provided the
 control will be filled with a background of this color (see knobtest.py).
 7. ``fontcolor`` 3-tuple defining the font color, or ``None``. If ``None`` the screen's foreground
 color is used.
 8. ``border`` Integer or ``None``. If an integer ``n`` is provided a single pixel border will be
 drawn around the control, separated from it by ``n`` pixels.
 9. ``value`` The starting value for the contol. Data types are various, but clearly the ``show``
 method must be able to display them. Floats are constrained to the 0 to 1.0 limits used throughout.
 10. ``initial_value`` Typically ``None``. This may be used to enable ``show`` to identify the
 first time the control has been displayed. It is stored in the ``initial_value`` bound variable
 and otherwise unused by the ``Touchable`` and ``NoTouch`` classes.

Bound variables:

 * ``fgcolor`` Foreground color. See fontcolor below.
 * ``bgcolor`` Background color. See fontcolor below.
 * ``fontcolor`` These should be used in all methods, notably in constructors, as they reflect the
 defaults applied by the superclass where the user passed ``None`` to the constructor.
 * ``screen`` The screen object on which this instance should be drawn. This is set to the current
 screen by the ``NoTouch`` constructor.
 * ``redraw`` Set by the GUI system. When set the ``show`` method must redraw the entire control.
 If the ``show`` method is to avoid redrawing the entire control on every call, it should clear
 the flag down when drawing the elements which are intended to persist.
 * ``location`` The following are simply storage for the constructor args described above.
 * ``_value``
 * ``_initial_value`` Available for any purpose, notably initialisation detection.
 * ``font``
 * ``height``
 * ``width``
 * ``fill`` True if a ``bgcolor`` was provided to the constructor.
 * ``enabled`` For compound cotrols only (pseudo controls consisting of more than one physical
 control). Currently only the ``ButtonList`` sets it ``False` and ``Button`` honours it. If ``False``
 the control will be invisible.
 * ``_greyed_out`` Always ``False`` in the case of displays (which don't respond to touch).
 * ``border`` Border width in pixels. 0 if there is no border.
 * `callback`` Callback function on value change. Primarily for control classes: default is a
 null function.
 * ``args`` Args for above, default [].
 * ``cb_end`` Callback on touch release: for control classes.
 * ``cbe_args`` Args for above, default [].

Methods:

 * ``greyed_out`` No args. Returns ``True`` if the control is disabled.
 * ``show_if_current`` No args. Calls the ``show`` method (defined in the subclass) if the
 control is on the current screen. Useful in custom ``value`` methods.
 * ``value`` The default user interface. Positional args ``val`` default None, ``show`` default
 ``True``. If  called without args, returns the control's current value. If ``val`` is provided it
 checks the type: if it is a ``float`` it is constrained to 0 <= val <= 1.0. If the value has
 changed it updates it, calls the callback, and calls the control's ``show`` method if it is on the
 current screen. The optional ``show`` argument is set ``False`` by the ``show`` method where that
 method calls the control's ``value`` method. This prevents needless recursion.

Property:
 * ``tft`` Returns the ``TFT_G`` instance with greyed_out status set to that of ``self``.

# class Touchable (subclass of NoTouch)
 
Constructor arguments (all mandatory, positional). These are as described above, except 10.

 1. ``location``
 2. ``font``
 3. ``height``
 4. ``width``
 5. ``fgcolor``
 6. ``bgcolor``
 7. ``fontcolor``
 8. ``border``
 9. ``value``
 10. ``can_drag`` True if the control must respond to drag events.
 11. ``initial_value``

Bound variables (not usually needed by subclasses):

As per ``NoTouch`` plus:
 * ``can_drag`` True if the control must respond to drag events. Such events cause repeated calls
 to the ``_touched`` method.
 * ``busy`` This is used by controls which do not respond to drag events to ensure that the
 ``_touched`` method of such controls is called once only. It is set by ``_trytouch`` and cleared
 by the ``Screen._touchtest`` thread when the touch ceases.
 * ``was_touched`` This is set by the ``_trytouch`` method and cleared by the ``Screen._touchtest``
 thread: it forms an interlock to ensure the ``_untouched`` method is called once only when a touch
 ends.

Methods:

As per``NoTouch`` plus:
 * ``greyed_out`` Overridden method, optional boolean arg ``val`` default ``None``. If the arg is
 not supplied, returns the current greyed-out status. If the arg is supplied, and differs from the
 current status, updates the current status, redraws the control and returns the new status.
 * ``_untouched`` Called by the ``Screen._touchtest`` thread when the touch ceases. Calls the
 ``cb_end`` callback. Can be overridden in subclasses.
 * ``_trytouch`` Called by the ``Screen._touchtest`` thread when the touch panel is touched and the
 object is on the current screen and responsive to touch. If the touch is within the object's
 bounding box, it calls the ``_touched`` method. All touchable controls must implement this method,
 which determines how the control should respond when touched.
 * ``_set_callbacks`` Called from subclass constructors to set the callback functions and args.

 