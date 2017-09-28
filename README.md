Geiger counter
==============

Geiger counter with Si3-BG Geiger tube. It is very insensitive and it  requires 400V to operate. With some modifications in hardware it can be adapted for use with other (more sensitive) tubes.


Schematics (Hardware)
---------------------

In schematics you can find the source in KiCAD. The circuit consists is a simple buck converter with NE555 that increases voltage from 5V to approx. 400V. I suggest using 555 chip from Texas instruments. The rest is simple 2x16 lcd display module pinout, power supply with switch and pin configuration for codecting nodeMCU module with ESP8266.

There are many ways on how to improve the basic circuit ;).


Software installation instructions
----------------------------------

1. To upload micropython run 'flash.sh'. The esp8266 board should be connected as ttyUSB0, otherwise change the script.
2. To upload geiger-muller counter firmware run 'uploadfw.sh ssid_name channel_number'. (again, be sure board is connected as ttyUSB0.
3. Reset and enjoy



if you want to autostart firmware add line
put main.py into mpfshellscript

