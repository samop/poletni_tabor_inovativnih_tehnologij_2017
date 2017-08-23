from machine import Pin, Timer, UART
from utime import ticks_ms, sleep
import os
import network
import socket

from nodemcu_gpio_lcd import GpioLcd




html = """HTTP/1.0 200 OK
Refresh: 2; url=http://192.168.4.1
Content-Type: text/html

<!DOCTYPE html>
<html>
<head> <title>Poletni tabor inovativnih tehnologij 2017</title> 
<style>table, th, td { border: 1px solid black; } th, td {padding: 5px; padding-left:15px; padding-right:15px; }</style></head>

    <body> <h1>Geigerjev &#353;tevec</h1><hr>
<table>
	<tr>
	<td>Trenutni CPM</td>
	<td><font size=+3>%s</font></td>
	</tr>
	<tr>
	<td>Sevanje</td>
	<td><font size=+3>%s uSv/h</font></td>
	</tr>
</table>
<br>
	CPM intervala zadnjih 30 s: %s
<br><br>
	%s
    </body>
</html>
"""


CONV_FACTOR=0.044444

count=0
rom_count=0
event_occured=0
last_time=ticks_ms()
tim=Timer(-1)
tim_cpm=Timer(-1)
tim_save=Timer(-1)
tim_uart=Timer(-1)
cpm=0
sv=0.0
file_status=0
uart=None
report_mode=0
lcd=None

def long_to_bytes(a):
	"""Converts 2 bytes integer to encoded string"""
	return("%c%c" % ((a>>8)&0xFF, a&0xFF))

def bytes_to_long(b):
	"""Converts 2 bytes binary to 2 bytes integer"""
	return(b[0]*256+b[1])

def save_file(t):
	"""Saves current rom_count value to file if there is disk space"""
	global file_status, rom_count, report_mode
	if(report_mode==1):  # do not do data logging during normal operation
		rom_count=0
		return
###	print("Saving")
	f=open('data.bin','a')
	if(f.tell()>10000):
		f.close()
		file_status=1 #full
		rom_count=0
		return
	else:
		file_status=0 #not full
		f.write(long_to_bytes(rom_count))
		f.close()
		rom_count=0


def send_data():
	"""Reads the file and sends it to screen"""
	f=open('data.bin','ab')
	length=f.tell()
	f.close()
	f=open('data.bin','rb')
	print(str(int(length/2)))
	for i in range(0, length/2):
		dat=f.read(2)
		print(str(bytes_to_long(dat)))

def delete_file():
	os.remove('data.bin')

def callback(p):
	"""This callback function is called each time the beginning of the pulse is detected on pin 5 -- interrupt call"""
	global count, rom_count, cpm, event_occured, sv, last_time
#	print("Interrupt!")
	count+=1
	rom_count+=1
	event_occured=1
#	now=ticks_ms()
#	delta=now-last_time
#	cpm=count*6000/delta
#	sv=cpm*CONV_FACTOR


def refresh_screen(t):
	"""This function is called every now and then, when screen needs refreshing"""
	global cpm, sv, lcd
	lcd.move_to(0,0)
	lcd.putstr("cpm: {:4d}\nrad:{:6.2f} uSv/h".format(int(cpm),sv))
###	print("Refresh "+str(cpm)+" cpm or "+str(sv)+" uS/h.")

def refresh_cpm(t):
	global cpm, sv, count, last_time
	now=ticks_ms()
	delta=now-last_time
	cpm=count*60000/delta
	sv=cpm*CONV_FACTOR
	count=0
#	sv=0.0
#	cpm=0
	last_time=now


def init_serial():
	"""Initialize serial port"""
	global uart
	uart=UART(0,115200)
	uart.init(115200,bits=8, parity=None, stop=1)

#use print instead
#def send_uart(message):
#	global uart
#	uart.write(message)

def receive_uart():
	global uart
	return uart.read()


def init_sta():
	sta_if=network.WLAN(network.STA_IF)
	sta_if.connect('jeglic', 'ciklama1')
	print(sta_if.ifconfig())


def uart_handler(t):
	global uart,count, report_mode, event_occured
	if(report_mode):
		if event_occured:
			print("1")
			event_occured=0
		else:
			print("0")
	a=receive_uart()
	"""read commands from serial port"
	"n -- go to normal mode, sending 0 or 1 every 10 ms"
	"l -- go to log mode"
	"r -- read (send) data from log file to the UART"
	"d -- delete file"
	"^C -- break program to REPL"
	"""
	if(a is not None):
		if(a[0]==110): #n
			report_mode=1
			###print("going to report")
		elif(a[0]==108): #l
			report_mode=0
		elif(a[0]==114 and report_mode==0): #r
			send_data()		
		elif(a[0]==100):
			delete_file() #d


def initialize():
	""" Initialize LCD screen, interrupts, WiFi and timers """
	global count, last_time, tim, tip_cpm, tim_save, tim_uart, uart, lcd
	#SERIAL
	init_serial()
	#NETWORK
	ap_if=network.WLAN(network.AP_IF)
	try:
		f=open('SSID','r')
		ssid=f.readline()
		f.close()
	except:
		ssid='Geiger-config'

	if(ssid==''):
		ssid='Geiger-empty'

	try:
		f=open('CHANNEL','r')
		channel=f.readline()
		f.close()
	except:
		channel=1
	if(channel==''):
		channel=2
	ap_if.config(essid=ssid.strip(), password='12345678', channel=int(channel))
	###print(ap_if.ifconfig())
	#LCD screen
	lcd = GpioLcd(rs_pin=Pin(4), enable_pin=Pin(0), d4_pin=Pin(12), d5_pin=Pin(13), d6_pin=Pin(14), d7_pin=Pin(15), num_lines=2, num_columns=16)
	lcd.putstr("Geiger FE '17\nW:%s" % ssid)
	sleep(3)
	lcd.clear()
	
	#IRQ and TIMERS
	p5=Pin(5,Pin.IN)
	p5.irq(handler=callback, trigger=Pin.IRQ_RISING, hard=True)
	last_time=ticks_ms()
	tim.init(period=1000, mode=Timer.PERIODIC, callback=refresh_screen)
	tim_cpm.init(period=2000, mode=Timer.PERIODIC, callback=refresh_cpm)
	tim_save.init(period=30000, mode=Timer.PERIODIC, callback=save_file)
	tim_uart.init(period=10, mode=Timer.PERIODIC, callback=uart_handler)

def main_loop():
	global report_mode, count, rom_count,cv,cpm

	addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
	s = socket.socket()
	s.bind(addr)
#	s.setblocking(False)
	s.listen(1)

	while True:
		try:
			cl, addr = s.accept()
			###print('client connected from', addr)
			cl_file = cl.makefile('rwb', 0)
			while True:
				line = cl_file.readline()
				###print(line)
				if not line or line == b'\r\n':
					break
			if(report_mode==1):
				rpt="Merilnik deluje v re&#158;imu sprotnega po&#353;iljanja podatkov"
			else:
				rpt="Merilnik deluje v re&#158;imu shranjevanja podatkov v pomnilnik."
			response = html % (str(int(cpm)), str(sv), str(rom_count), rpt)
			cl.send(response)
			cl.close()
		except:
			pass

#Experimental stuff#
#class ControlL():
#	def __repr__(self):
#		global count
#		return count
#
#l=ControlL()
initialize()
main_loop()

