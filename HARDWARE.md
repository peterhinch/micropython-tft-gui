# Hardware notes

The easiest way to acquire these displays is to search eBay for SSD1963.

# Minimal connections for TFT display

These notes are intended for users not intending to use Robert Hammelrath's excellent PCB, which
has features including the ability to power down the display to conserve power when not in use.

Most 4.3 inch and 5 inch displays have a 40 way 0.1 inch connector with the following pinout.
Pins are usually marked on the PCB. Pins marked - are defined as no connect. Signals in parentheses
are not required by the driver and are no-connect. Most 7 inch displays use a different connector.

The table below is laid out looking at the underside of the display with the socket to the left and
the display underside to the right. L and R denote the left and right TFT connector pins when
viewed in this way. Check your own display to ensure it conforms to this pinout!


| Signal  | Pyboard | L   | R   | Pyboard | Signal   |
|:-------:|:-------:|:---:|:---:|:-------:|:--------:|
| -       |         | 20  | 40  |         | -        |
| LED-A   | Y3   [1]| 19  | 39  |         | -        |
| V-LED   | 3.3V [2]| 18  | 38  |         | (SD_CS)  |
| REST    | Y9      | 17  | 37  |         | (SD_DIN) |
| (FCS)[3]|         | 16  | 36  |         | (SD_CLK) |
| CS      | Gnd     | 15  | 35  |         | (SD_DO)  |
| (DB15)  |         | 14  | 34  | Y1      | T_IRQ    |
| (DB14)  |         | 13  | 33  | Y2      | T_DO     |
| (DB13)  |         | 12  | 32  |         | -        |
| (DB12)  |         | 11  | 31  | X11     | T_DIN    |
| (DB11)  |         | 10  | 30  | Gnd     | T_CS     |
| (DB10)  |         | 9   | 29  | X12     | T_CLK    |
| (DB9)   |         | 8   | 28  | X8      | DB7      |
| (DB8)   |         | 7   | 27  | X7      | DB6      |
| Rd      | Y10     | 6   | 26  | X6      | DB5      |
| Wr      | Y11     | 5   | 25  | X5      | DB4      |
| Rs      | Y12     | 4   | 24  | X4      | DB3      |
| -       |         | 3   | 23  | X3      | DB2      |
| 3.3V    | 3.3V    | 2   | 22  | X2      | DB1      |
| Gnd     | Gnd     | 1   | 21  | X1      | DB0      |

Notes:  
[1] Pin 19 controls backlight brightness. The TFT driver supports brightness control using PWM.  
[2] Some displays show no connection on pin 18. On others it's the backlight power source.  
[3] This is a chip select for an onboard 2MB Flash chip. It is unused by the driver.  
The TFT driver tft.py uses pin Y4 for power control: with suitable hardware this enables power to
be conserved by powering the display down when not in use. It also uses pin Y3 and timer 4 for
backlight brightness control. Pin 19 can be linked to 3.3V if full brightness is always required.

Signal descriptions:
Signals T_* are the touch panel controller chip connections.  
Signals (SD_*) are for the onboard SD card which is unused.  
DB0-15 is the parallel bidirectional data bus (lower 8 bits only are used).  
Rd, Wr, Rs (read, write, command/data) are the active low bus control signals.  
CS is the active low chip select (always selected).  
REST is the controller reset.

# Power

I have run a 4.3 inch display from the Pyboard's 3.3V output for short periods but only when
running the Pyboard from 5V. It's not recommended as the 4.3 inch display takes over 200mA at full
baklight brightness which, with the Pyboard's own current draw, pushes the power dissipation of the
Pyboard's regulator.

One solution is to power the Pyboard and the display from a common 3.3V supply. An efficient way of
doing this is to use a Pololu switch mode DC converter: part numbers S7V8F3 or D24V5F3 are
suggested depending on your input voltage range. If you adopt this approach there is an issue if
using a USB connection to the Pyboard. In this case the Pyboard draws power from the USB cable, and
its 3.3V pin becomes an output: the Pyboard 3.3V pin should be disconnected from the Pololu
regulator output, which then powers the display only.

A debugging option which avoids this difficulty is to ignore USB and to use UART(1) via an FTDI
adaptor, connecting only RXD, TXD and GND and powering the entire system from the 3.3V source.

If the system is always to be powered by USB an option is to connect a Pololu S7V8F3 to the Pyboard
Vin pin (which will be an output in this case), and use its 3.3V output to power the display. If
doing this, use a good quality USB cable capable of handing the current involved.

# Pyboard Free Pins

The following I/O pins are unused by the interface and code:

Y5-Y8, X9, X10, X17-X22, P18-P21 (LED pins)  
Ranges are inclusive.

If not using brightness or power control it seems that _in extremis_ Pins Y3 and Y4 could be freed:
they are initialised by the TFT constructor but could subsequently be re-defined and used for other
purposes, along with timer 4. Note Robert Hammelrath is the author of this module; I haven't
actually tried this...