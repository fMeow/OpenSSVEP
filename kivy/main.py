from __future__ import print_function,unicode_literals,with_statement,division
import numpy as np
from kivy.app import App
import serial,struct,logging

__author__ = 'Guoli Lv'
__email__ = 'guoli-lv@hotmail.com'

class BCIApp(App):
    """BCI App"""
    kv_directory = 'ui_template'
    rawRemained = '' # raw Data from serial, this should contain the data unused last time

    def __init__(self):
        """ Initializing serial and plot
        :returns: TODO
        """
        super(BCIApp,self).__init__()
        try:
            # serial part
            ser = serial.Serial(port = '/dev/ttyUSB0',baudrate = 38400, bytesize=8,parity='N',stopbits=1)
            # TODO serial should be opened after face recognition finished
            ser.open()
        except Exception as e:
            logging.exception("Device/Port not found.")

    def __rawData2Voltage(self, rawData,gainCoefficient=12):
        """ convert rawData to exact voltage

        :rawData: a list of rawData
        :returns: converted voltage tupple in mV

        """
        raw = np.array(rawData)
        # 2.42 is the referrence voltage of BCI device, 24 is the sampling resolution
        dataVol = 2.42 / 2**24 / gainCoefficient * raw
        dataVol = dataVol * 1000 # convert uints to mV
        return tuple(dataVol)


    def __dataHex2int(self, dataHex):
        """ Convert hex data of 4 bytes containing EEG data to int

        :dataHex: string of length 4
        :returns: int
        """
        # 'i' means signed integer, '<' means little-endian
        data = struct.unpack('<i', dataHex)[0]
        return data

    def readFromSerial(self,ser,protocol='EasyBCISingleChannel'):
        """TODO: Docstring for readFromSerial.
        :protocol:protocol type. Should be 'EasyBCISingleChannel'.
        :ser: Serial Object
        :returns: a list of raw data from BCI
        """
        rawData = ser.read_all() # read cureent all available data
        raw = self.rawRemained + rawData
        data= []

        # Manipulate raw data with given protocol
        if protocol is 'EasyBCISingleChannel':
            start = b'\xaa'
            middle = b'\xa1'
            lastIndex = 0
            # find possible index by search raw data for which is the same with bytes indicating start
            possibleIndex = [i for i in range(len(raw)) if raw[i] == start ]
            # To validate possibleIndex, we should check whether the byte indicating middle comflies.
            for index in possibleIndex :
                middleIndex = index + 6
                try:
                    raw[middleIndex]
                except Exception as e:
                    continue
                if raw[middleIndex] == middle:
                    # middle byte does comply, so extract the pack
                    rawDataPack = raw[index:index+12]
                    # TODO given check code is smaller than protocol
                    checkCode = sum([ord(data) for data in rawDataPack[0:-1]])%256
                    if ord(rawDataPack[-1]) == checkCode:
                        # All validation steps passed
                        # convert hex to int
                        dataHex = rawDataPack[2:6] # first data
                        data.append(self.__dataHex2int(dataHex))

                        dataHex = rawDataPack[7:11] # second dats
                        data.append(self.__dataHex2int(dataHex))
                        lastIndex = index + 12
            # Update remaining raw data
            self.rawRemained = raw[lastIndex:]
            return self.__rawData2Voltage(data)

        else:
            raise Exception('protocol should be EasyBCISingleChannel')

    def on_start(self):
        """ Event when started.
        :returns: TODO
        """
        pass


if __name__ == '__main__':
    BCIApp().run()
