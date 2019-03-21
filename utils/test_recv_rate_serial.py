"""
This script test the receiving rate via serial device.
"""

import serial
import time
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--baudrate', type=int, help='baudrate',
                        dest='baudrate', default=115200)
    parser.add_argument('--port', type=int, help='serial device port, for example: COM1, /dev/TTYusb0',
                        dest='port')
    args = parser.parse_args()

    ser = serial.Serial(port=args.port, baudrate=args.baudrate,
                        bytesize=8, parity='N', stopbits=1, write_timeout=0)
    try:
        while True:
            loop = True
            start = time.time()
            count = 0
            while loop:
                end = time.time()
                if int(end-start) > 1:
                    loop = False
                count += len(ser.read_all())
            print("Bytes per second:%d" % (count/(end-start)))
    except KeyboardInterrupt:
        ser.close()
