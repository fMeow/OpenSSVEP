import serial
import time

ser = serial.Serial(port = '/dev/cu.wchusbserial14340',baudrate = 115200, bytesize=8,parity='N',stopbits=1, write_timeout=0)
while True:
    loop = True
    start = time.time()
    count = 0
    while loop:
        end=time.time()
        if int(end-start)>1:
            loop = False
        count += len(ser.read_all())
    print("Bytes per second:%d"%(count/(end-start)))
ser.close()

