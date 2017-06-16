from __future__ import print_function,unicode_literals,with_statement,division

# kivy related
import matplotlib
matplotlib.use('module://kivy.garden.matplotlib.backend_kivy')
from matplotlib import pyplot as plt
import matplotlib.animation as animation
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.properties import StringProperty,ListProperty

import serial,struct,logging
import numpy as np

from kivymd.theming import ThemeManager

__author__ = 'Guoli Lv'
__email__ = 'guoli-lv@hotmail.com'


class FFT(BoxLayout):
    """Docstring for FFT. """
    fps = 30

    length = 80 # FFT length
    fs = 125 # FFT Sampling rate
    ts = 1.0/fs # Sampling interval
    fftLen = 1024
    plotScale = 1 # After FFT there are much points as fftLen/2 to plot. Considerable to reduce the points.

    def __init__(self,**kwargs):
        super(FFT,self).__init__(**kwargs)
        # Configure real time fft figure with matplotlib
        self.fig, self.ax = plt.subplots()
        #plt.ion()

        #self.fig.subplots_adjust(bottom=0.2,left=0.3)
        self.ax.set_xlabel('Frequency(Hz)')
        self.ax.set_ylabel('Amplitude(mV)')
        self.ax.set_xlim([0,40])
        self.ax.set_ylim([0,1000])
        self.ax.set_title('FFT')

        self.add_widget(self.fig.canvas)
        Clock.schedule_interval(self.refresh,1/self.fps)

    def refresh(self,dt):
        App.get_running_app().data.extend(App.get_running_app().readFromSerial())
        if len(App.get_running_app().data) >= self.length:
            logging.info("Refreshing. Length of data:%d"%(len(App.get_running_app().data)))
            # Clear
            self.ax.cla()

            # Get data
            x = App.get_running_app().data[0:self.length+1]

            # Perform 512 point FFT to improve resolution
            Y = np.fft.fft(x,self.fftLen)

            # x-axis, ts = 1/fs
            f = np.fft.fftfreq(self.fftLen,self.ts)

            # deal with amplitude scale and choose the positive half
            #Yamp = np.abs(Y/self.fftLen)
            #YampHalf = Yamp[f>=0]
            fPos = f[f>=0]
            YampPos = np.abs(Y[f>=0]/self.fftLen)
            YampPos[1:-1] = YampPos[1:-1] * 2

            fPlot = [fPos[i]  for i in range(len(fPos)) if np.mod(i,self.plotScale) == 0 ]
            YPlot = [YampPos[i]  for i in range(len(YampPos)) if np.mod(i,self.plotScale)==0 ]

            self.ax.plot(fPlot,YPlot)
            # Update stored data from BCI device
            App.get_running_app().data = App.get_running_app().data[self.length:]

class Test(BoxLayout):
    """Test Layout"""
    # Settings
    theme_cls = ThemeManager()

    def __init__(self, **kwargs):
        """ Initializing serial and plot
        :returns: TODO
        """
        super(Test,self).__init__(**kwargs)


    def on_start(self):
        """ Event when started.
        :returns: TODO
        """
        pass

class BCIApp(App):
    # Settings
    kv_directory = 'ui_template'
    data = ListProperty([])
    # Buffer
    rawRemained = StringProperty(str('')) # raw Data from serial, this should contain the data unused last time


    def __init__(self, **kwargs):
        """ Initializing serial
        :returns: TODO
        """
        super(BCIApp,self).__init__(**kwargs)
        try:
            # serial part
            # TODO allow users to choose serial device
            # TODO serial should be opened after face recognition finished
            self.ser = serial.Serial(port = '/dev/ttyUSB1',baudrate = 38400, bytesize=8,parity='N',stopbits=1)
        except Exception as e:
            self.ser = None

    def build(self):
        return Test()

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

    def readFromSerial(self,ser=None,protocol='EasyBCISingleChannel'):
        """TODO: Docstring for readFromSerial.
        :protocol:protocol type. Should be 'EasyBCISingleChannel'.
        :ser: Serial Object
        :returns: a list of raw data from BCI
        """

        # Check Serial device and assign self.ser
        if self.ser is None:
            logging.error("Serial device not set.")
            return None

        if ser is None:
            ser = self.ser
        # Read cureent all available data
        rawData = ser.read_all()

        # Get data remaining in the last run
        rawRemained = App.get_running_app().rawRemained
        raw = rawRemained + rawData

        dataList= []

        # Manipulate raw data with given protocol
        if protocol == 'EasyBCISingleChannel':
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
                        dataList.append(self.__dataHex2int(dataHex))

                        dataHex = rawDataPack[7:11] # second dats
                        dataList.append(self.__dataHex2int(dataHex))
                        lastIndex = index + 12
            # Update remaining raw data
            App.get_running_app().rawRemained = raw[lastIndex:]
            return self.__rawData2Voltage(dataList)

        else:
            raise Exception('protocol should be EasyBCISingleChannel')

if __name__ == '__main__':
    BCIApp().run()
