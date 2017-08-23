import serial

ser = serial.Serial('/dev/ttyUSB0',115200)
f = open('filename.txt','w')

ser.write('n')
while 1:
	line=ser.readline().decode('utf-8')
	print(line.strip())
	f.write(line)

#never comes to here
f.close()

