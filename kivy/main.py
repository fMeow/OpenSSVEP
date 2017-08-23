from __future__ import print_function,unicode_literals,with_statement,division

# kivy related
import matplotlib
matplotlib.use('module://kivy.garden.matplotlib.backend_kivy')
from matplotlib import pyplot as plt
#import matplotlib.animation as animation
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.properties import StringProperty,ListProperty

import serial,struct,logging,serial.tools.list_ports
from serial import SerialException
import numpy as np
from scipy import signal

from functools import partial

# Kivy Material Design
from kivymd.theming import ThemeManager

__author__ = 'Guoli Lv'
__email__ = 'guoli-lv@hotmail.com'

class SerialPortSelection(BoxLayout):

    """ Select Serial Port on GUI """

    def __init__(self,**kwargs):
        super(SerialPortSelection,self).__init__(**kwargs)
        # kv file is load after rendering. So in __init__ it's impossible to access widget by ids for no widget has been renderred. Then we can use Clock.schedule_once(..., 0) to schedule the call to a function relying on ids.
        Clock.schedule_once(self.scanPorts,0)
        Clock.schedule_once(self.popupHintOnConnectionFailedConfig,0)


    def popupHintOnConnectionFailedConfig(self,dt=0):
        # Connection Failed popup hint configuration
        self.popup = Popup(title='Connection Failed',id='popup')
        App.get_running_app().root.add_widget(self.popup)
        App.get_running_app().root.remove_widget(self.popup)

    def changeState(self,state):
        if state == 'down':
            con = App.get_running_app().connect(self.ids['uart'].text)
            # When connection failed
            if con is False:
                self.ids['connect'].state = 'normal'
                # Popup hint and rescan serial devices
                self.popup.open()
                Clock.schedule_once(self.popup.dismiss ,1)
                self.scanPorts()
        else:
            data = App.get_running_app().disconnect()

    def scanPorts(self,dt=0):
        # scan ports
        self.ports = serial.tools.list_ports.comports()

        # Clear device lists
        self.ids['uart'].values = []

        self.ids['uart'].sync_height = True

        # Put ports found on selector
        if len(self.ports) == 0:
            self.ids['uart'].text = 'None'
        else:
            for port in self.ports:
                # The first one should be put on Spinner.text else spinner will show None
                if port is self.ports[-1]:
                    self.ids['uart'].text = port.device

                self.ids['uart'].values.append(port.device)


class FFT(BoxLayout):
    """ Real Time frequency-domain Plotting """

    length = 128 # FFT length
    fs = 125 # FFT Sampling rate
    ts = 1.0/fs # Sampling interval
    fftLen = 1024
    plotScale = 1 # After FFT there are much points as fftLen/2 to plot. Considerable to reduce the points.

    # Temporary data for storing points which is used to plot FFT
    data = []

    def __init__(self,**kwargs):
        super(FFT,self).__init__(**kwargs)

        # Configure real time fft figure with matplotlib
        self.fig, self.ax = plt.subplots()
        #plt.ion() #Never turn this on. Or enjoy a almost frozen Application.

        # Settings
        self.ax.set_xlabel('Frequency(Hz)')
        self.ax.set_ylabel('Amplitude(uV)')
        self.ax.set_title('FFT')

        # x-axis, ts = 1/fs
        self.f = np.fft.fftfreq(self.fftLen,self.ts)

        fPos = self.f[self.f>=0]
        fPlot = [fPos[i]  for i in range(len(fPos)) if np.mod(i,self.plotScale) == 0 ]
        self.plotLen = len(fPlot)

        # Plot x data once. Then we only need to update y data
        self.ax.set_xlim([np.min(fPlot),np.max(fPlot)*1.1])
        self.FFTplot, = self.ax.plot(fPlot,np.zeros_like(fPlot))

        self.add_widget(self.fig.canvas)

#    def start(self):
#        Clock.unschedule(self.refresh)
#        Clock.schedule_interval(self.refresh,1/self.fps)
#
#    def stop(self):
#        Clock.unschedule(self.refresh)
#        self.FFTplot.set_ydata(np.zeros(self.fftLen))
#        self.ax.set_ylim([-1,1])
#        plt.draw()

    def clear(self):
        self.FFTplot.set_ydata(np.zeros(self.plotLen).tolist())
        self.ax.set_ylim([-1,1])
        plt.draw_all()

    def refresh(self):
        self.data.extend(App.get_running_app().data)
        if len(self.data) < self.length:
            return False
        #logging.info("Refreshing. Length of data:%d"%(len(self.data)))
        # Clear
        #self.ax.cla()

        # Get data
        y = self.data[0:self.length+1]

        # Perform 512 point FFT to improve resolution
        Y = np.fft.fft(y,self.fftLen)

        # deal with amplitude scale and choose the positive half
        #Yamp = np.abs(Y/self.fftLen)
        #YampHalf = Yamp[f>=0]
        YampPos = np.abs(Y[self.f>=0]/self.fftLen)
        YampPos[1:-1] = YampPos[1:-1] * 2

        YPlot = [YampPos[i]  for i in range(len(YampPos)) if np.mod(i,self.plotScale)==0 ]

        self.FFTplot.set_ydata(YPlot)
        padding = (np.max(YPlot) - np.min(YPlot)) * 0.1
        # TODO To improve figure ylimits stability
        if padding > 1:
            self.ax.set_ylim([np.min(YPlot)-padding,np.max(YPlot)+padding])
        plt.draw_all()
        #self.ax.plot(fPlot,YPlot)
        # Update stored data from BCI device
        self.data = self.data[self.length:]

class RealTimePlotting(BoxLayout):

    fs = 125
    length = 125 * 10
    """Real Time time-domain Plotting """

    def __init__(self,**kwargs):
        super(RealTimePlotting ,self).__init__(**kwargs)

        # Configure real time fft figure with matplotlib
        self.fig, self.ax = plt.subplots()
        #plt.ion() #Never turn this on. Or enjoy a almost frozen Application.

        # Settings
        #self.ax.set_xlabel('Time(seconds)')
        self.ax.set_ylabel('Amplitude(uV)')
        self.ax.get_xaxis().set_visible(False)
        #self.ax.set_title('Real Time Plotting')

        # Plot x data once. Then we only need to update y data
        x = np.arange(0,self.length)/self.fs
        self.ax.set_xlim([np.min(x),np.max(x)])
        self.RealTimePlot, = self.ax.plot([],[])
        self.RealTimePlot.set_xdata(x)
        self.RealTimePlot.set_ydata(np.zeros_like(x).tolist())

        self.add_widget(self.fig.canvas)

#    def start(self):
#        Clock.unschedule(self.refresh)
#        Clock.schedule_interval(self.refresh,1/self.fps)

#    def stop(self):
#        Clock.unschedule(self.refresh)
#        self.RealTimePlot.set_ydata(np.zeros(self.length))
#        self.ax.set_ylim([-1,1])
#        plt.draw()

    def clear(self):
        self.RealTimePlot.set_ydata(np.zeros(self.length).tolist())
        self.ax.set_ylim([-1,1])
        plt.draw_all()

    def refresh(self):
        # TODO Now real time plotting and FFT cannot be showed on the same time
        data = App.get_running_app().data

        if data is None:
            data=[]
            logging.info("Nothong from serial. Please check UART connection.")
        y = self.RealTimePlot.get_ydata()

        newLen = len(y) + len(data)
        dump = newLen - self.length
        if dump > 0:
            y = y[dump:]
        y.extend(data)

        self.RealTimePlot.set_ydata(y)
        padding = (np.max(y) - np.min(y)) * 0.1
        # TODO To improve figure ylimits stability
        if padding > 20:
            self.ax.set_ylim([np.min(y)-padding,np.max(y)+padding])
        plt.draw_all()

class Test(BoxLayout):
    """Test Layout"""
    # Settings
    theme_cls = ThemeManager()

    def __init__(self, **kwargs):
        """ Initializing serial and plot
        :returns: TODO
        """
        super(Test,self).__init__(**kwargs)
        for i in range(12):
            Clock.schedule_interval(partial(self.blinking,i),1/(i+10))

    def blinking(self,idx,dt):
        widgetID = 'button%d' % idx
        if self.ids[widgetID].state == 'normal':
            self.ids[widgetID].state = 'down'
            self.ids[widgetID].trigger_action(0.01)
        if self.ids[widgetID].state == 'down':
            self.ids[widgetID].state = 'normal'
            self.ids[widgetID].trigger_action(0.01)


class BCIApp(App):
    # Settings
    kv_directory = 'ui_template'
    fps = 30
    data = ListProperty([])
    # Buffer
    rawRemained = b'' # raw Data from serial, this should contain the data unused last time
    ser = None


    def __init__(self,**kwargs):
        """ Initializing serial
        :returns: TODO
        """
        super(BCIApp,self).__init__(**kwargs)

    def _read(self,dt):
        # data is a Listproperty, so on_data() will be called whenever data has been changed. on_data() will be called right after the following line.
        self.data = self.__readFromSerial()

    def on_data(self,instance,data):
        self.root.ids['RealTimePlotting'].refresh()
        self.root.ids['FFT'].refresh()

    def connect(self,port='/dev/ttyUSB0'):
        try:
            # serial part
            # TODO serial should be opened after face recognition finished
            self.ser = serial.Serial(port = port,baudrate = 38400, bytesize=8,parity='N',stopbits=1)
            # enable real time time-domain or/and frequency-domain plotting
            Clock.schedule_interval(self._read,1/self.fps)
            #self.root.ids['RealTimePlotting'].start()
            #self.root.ids['FFT'].start()

            return True
        except SerialException:
            # Failed
            return False

    def disconnect(self):
        try:
            # Stop event
            Clock.unschedule(self._read)

            # Close connection
            self.ser.close()

            # Clear Figures
            self.root.ids['RealTimePlotting'].clear()
            self.root.ids['FFT'].clear()
        except AttributeError:
            # self.ser is None. We have not connect to any available serial device
            pass


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
        dataVol = dataVol * 1e6 # convert uints to uV
        return tuple(dataVol)

    def __dataHex2int(self, dataHex):
        """ Convert hex data of 4 bytes containing EEG data to int

        :dataHex: string of length 4
        :returns: int
        """
        # 'i' means signed integer, '<' means little-endian
        data = struct.unpack('<i', dataHex)[0]
        return data

    def __readFromSerial(self,protocol='EasyBCISingleChannel'):
        """TODO: Docstring for readFromSerial.
        :protocol:protocol type. Should be 'EasyBCISingleChannel'.
        :ser: Serial Object
        :returns: a list of raw data from BCI
        """

        # Check Serial device and assign self.ser
        if self.ser is None:
            logging.error("Serial device not set.")
            return None

        ser = self.ser

        # Read cureent all available data
        rawData = ser.read_all()

        # Get data remaining in the last run
        rawRemained = self.rawRemained
        raw = rawRemained + rawData

        dataList= []

        # Manipulate raw data with given protocol
        if protocol == 'EasyBCISingleChannel':
            start = b'\xaa'
            middle = b'\xa1'
            lastIndex = 0
            # find possible index by search raw data for which is the same with bytes indicating start
            possibleIndex = [i for i in range(len(raw)) if raw[i:i+1] == start ]
            # To validate possibleIndex, we should check whether the byte indicating middle comflies.
            for index in possibleIndex :
                middleIndex = index + 6
                try:
                    raw[middleIndex]
                except Exception as e:
                    continue
                if raw[middleIndex:middleIndex+1] == middle:
                    # middle byte does comply, so extract the pack
                    rawDataPack = raw[index:index+12]
                    try:
                        # Python 2
                        checkCode = sum([ord(data) for data in rawDataPack[0:-1]])%256
                    except Exception:
                        # Python 3
                        checkCode = sum([data for data in rawDataPack[0:-1]])%256
                    if ord(rawDataPack[-1::]) == checkCode:
                        # All validation steps passed
                        # convert hex to int
                        dataHex = rawDataPack[2:6] # first data
                        dataList.append(self.__dataHex2int(dataHex))

                        dataHex = rawDataPack[7:11] # second data
                        dataList.append(self.__dataHex2int(dataHex))
                        lastIndex = index + 12
            # Update remaining raw data
            self.rawRemained = raw[lastIndex:]
            return self.__rawData2Voltage(dataList)

        else:
            raise Exception('protocol should be EasyBCISingleChannel')

if __name__ == '__main__':
    BCIApp().run()
