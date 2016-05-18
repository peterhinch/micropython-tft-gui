# Hardware notes

The easiest way to acquire these displays is to search eBay for SSD1963.

# Minimal connections for TFT display

These notes are intended for users not intending to use Robert Hammelrath's excellent PCB.

Most 4.3 inch and 5 inch displays have a 40 way 0.1 inch connector with the following pinout.
Pins are usually marked on the PCB. Pins marked - are defined as no connect. Signals in parentheses
are not required by the driver and are no-connect. Most 7 inch displays use a different connector.

Looking at the underside of the display (i.e. viewing the socket) with the socket to your left and
the display underside to your right, pin 1 is at bottom left. L and R below denote the left and
right TFT connector pins as viewed in this way.


| Signal  | Pyboard | L   | R   | Pyboard | Signal   |
|:-------:|:-------:|:---:|:---:|:-------:|:--------:|
| Gnd     | Gnd     | 1   | 21  | X1      | DB0      |
| 3.3V    | 3.3V    | 2   | 22  | X2      | DB1      |
| -       |         | 3   | 23  | X3      | DB2      |
| Rs      | Y12     | 4   | 24  | X4      | DB3      |
| Wr      | Y11     | 5   | 25  | X5      | DB4      |
| Rd      | Y10     | 6   | 26  | X6      | DB5      |
| (DB8)   |         | 7   | 27  | X7      | DB6      |
| (DB9)   |         | 8   | 28  | X8      | DB7      |
| (DB10)  |         | 9   | 29  | X12     | T_CLK    |
| (DB11)  |         | 10  | 30  | Gnd     | T_CS     |
| (DB12)  |         | 11  | 31  | X11     | T_DIN    |
| (DB13)  |         | 12  | 32  |         | -        |
| (DB14)  |         | 13  | 33  | Y2      | T_DO     |
| (DB15)  |         | 14  | 34  | Y1      | T_IRQ    |
| CS      | Gnd     | 15  | 35  |         | (SD_DO)  |
| (FCS)[1]|         | 16  | 36  |         | (SD_CLK) |
| REST    | Y9      | 17  | 37  |         | (SD_DIN) |
| V-LED   | 3.3V [2]| 18  | 38  |         | (SD_CS)  |
| LED-A   | Y3   [3]| 19  | 39  |         | -        |
| -       |         | 20  | 40  |         | -        |

Notes:  
[1] This is a chip select for an onboard 2MB Flash chip. It is unused by the driver.  
[2] Some displays show no connection on pin 18. On others it's the backlight power source.  
[3] Pin 19 controls backlight brightness. The TFT driver supports brightness control using PWM.
This pin can be linked to 3.3V if full bightness is always required.

Signals T_* are the touch panel controller chip connections.  
Signals (SD_*) are for the onboard SD card which is unused.

# Power

I have run a 4.3 inch display from the Pyboard's 3.3V output for short periods but only when
running the Pyboard from 5V. It's not recommended as the 4.3 inch display takes over 200mA at full
baklight brightness which, with the Pyboard's own current draw, pushes the power dissipation of the
Pyboard's regulator.

One solution is to power the Pyboard and the display from a common 3.3V supply. A good way of doing
this efficiently is to use a Pololu S7V8F3 or D24V5F3 depending on your input voltage range.

There is an issue if using a USB connection to the Pyboard. In this case the Pyboard draws power
from the USB, and its 3.3V pin becomes an output. The Pyboard 3.3V pin should then be disconnected
from the Pololu regulator output, which powers the display only.

A debugging option which avoids this difficulty is to ignore USB and to use UART(1) via an FTDI
adaptor, connecting only RXD, TXD and GND and powering the system from a 3.3V source.
