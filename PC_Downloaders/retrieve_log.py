import serial
import time

ser = serial.Serial('/dev/ttyUSB0',115200)
f = open('filename.txt','w')

ser.write('l')
time.sleep(0.5)
ser.write('r')
n=int(ser.readline().decode('utf-8'))
f.write(str(n))
f.write('\n')
for i in range(0,n):
	line=ser.readline().decode('utf-8')
	print(line.strip())
	f.write(line)
f.close()

