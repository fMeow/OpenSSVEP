from __future__ import print_function,unicode_literals,with_statement,division

# kivy related
import matplotlib
import threading
matplotlib.use('module://kivy.garden.matplotlib.backend_kivy')
from matplotlib import pyplot as plt
from kivy.garden.graph import MeshLinePlot
#import matplotlib.animation as animation
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.properties import StringProperty,ListProperty
from kivy.uix.screenmanager import ScreenManager, Screen

import serial,struct,logging,serial.tools.list_ports
from serial import SerialException
import numpy as np
from scipy import signal

from functools import partial

from colorama import Fore, Back, Style, init
import logging
from ipdb import set_trace

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
        App.get_running_app().root.current_screen.add_widget(self.popup)
        App.get_running_app().root.current_screen.remove_widget(self.popup)

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
    fftLen = length
    plotScale = 1 # (integer) After FFT there are much points as fftLen/2 to plot. Considerable to reduce the points.
    autoScale = True
    xscale = fs/4
    xcenter = fs/2

    def __init__(self,**kwargs):
        super(FFT,self).__init__(**kwargs)

        # Configure real time fft figure with matplotlib
        self.fig, self.ax = plt.subplots()
        #plt.ion() #Never turn this on. Or enjoy a almost frozen Application.

        # Settings
        self.ax.xaxis.set_label_coords(0.9, -0.01)
        self.ax.yaxis.set_label_coords(-0.00, 1.05)
        self.ax.set_xlabel('Freq(Hz)')
        self.ax.set_ylabel('Amplitude(uV)',rotation=0)
        self.ax.set_title('FFT')

        # x-axis, ts = 1/fs
        self.f = np.fft.fftfreq(self.fftLen,self.ts)

        fPos = self.f[self.f>=0]
        fPlot = [fPos[i]  for i in range(len(fPos)) if np.mod(i,self.plotScale) == 0 ]
        self.plotLen = len(fPlot)

        # Set X padding
        padding = (np.max(fPlot) - np.min(fPlot)) * 0.01
        self.ax.set_xlim([np.min(fPlot)-padding,np.max(fPlot)+padding])
        self.FFTplot, = self.ax.plot(fPlot,np.zeros_like(fPlot))
        #  self.fig.canvas.mpl_connect('scroll_event', self.figure_scroll)

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

    def figure_scroll(self,event):
        print('scroll event from mpl ', event.x, event.y, event.step, event.button)

    def clear(self, dt=0):
        self.FFTplot.set_ydata(np.zeros(self.plotLen).tolist())
        self.ax.set_ylim([-1,1])
        plt.draw_all()

    def set_fft_length(self, FixedFFTLen=False):
        self.length = int(self.ids['fftLen'].text)
        if not FixedFFTLen:
            self.fftLen = self.length
            self.f = np.fft.fftfreq(self.fftLen,self.ts)

            fPos = self.f[self.f>=0]
            fPlot = [fPos[i]  for i in range(len(fPos)) if np.mod(i,self.plotScale) == 0 ]
            self.plotLen = len(fPlot)
            self.FFTplot.set_data(fPlot,np.zeros_like(fPlot))

    def set_scale(self):
        self.scale = self.ids['scale'].text
        if self.ids['scale'].text == 'Auto':
            self.autoScale = True
        else:
            self.autoScale = False
            if self.scale == '10μV':
                self.ax.set_ylim([0,10])
            elif self.scale == '100μV':
                self.ax.set_ylim([0,100])
            elif self.scale == '1mV':
                self.ax.set_ylim([0,1000])
            elif self.scale == '10mV':
                self.ax.set_ylim([0,10000])
            elif self.scale == '100mV':
                self.ax.set_ylim([0,1e5])
            elif self.scale == '1000mV':
                self.ax.set_ylim([0,1e6])

    def set_horizontal_width(self):
        self.xcenter = self.ids['horizon'].value
        self.ax.set_xlim([self.xcenter - self.xscale , self.xcenter + self.xscale])

    def set_xscale(self):
        self.xscale = self.fs/4 / self.ids['xscale'].value
        xmin = self.xscale
        xmax =  self.fs/2 - self.xscale
        self.ids['horizon'].range = (xmin,xmax)
        if self.xcenter - self.xscale < 0:
            self.ids['horizon'].value = xmin
        elif self.xcenter + self.xscale > self.fs/2:
            self.ids['horizon'].value = xmax
        self.ax.set_xlim([self.xcenter - self.xscale , self.xcenter + self.xscale])

    def refresh(self):
        data = App.get_running_app().data
        if len(data) < self.length:
            return False
        #  logging.info("Refreshing. Length of data:%d"%(len(data)))
        # Clear
        #self.ax.cla()

        # Get data
        y = data[-self.length:]
        Y = np.fft.fft(y,self.fftLen)
        YampPos = np.abs(Y[self.f>=0]/self.fftLen)
        YampPos[1:-1] = YampPos[1:-1] * 2
        YPlot = [YampPos[i]  for i in range(len(YampPos)) if np.mod(i,self.plotScale)==0 ]

        self.FFTplot.set_ydata(YPlot)

        if self.autoScale:
            # Set y padding
            padding = (np.max(YPlot) - np.min(YPlot)) * 0.1
            # TODO To improve figure ylimits stability
            if padding > 0.1:
                self.ax.set_ylim([np.min(YPlot)-padding,np.max(YPlot)+padding])
        plt.draw_all()
        #self.ax.plot(fPlot,YPlot)

class RealTimePlotting(BoxLayout):

    fs = 125
    scale = 'Auto'
    #  band = np.array([49,51])
    """Real Time time-domain Plotting """

    def __init__(self,**kwargs):
        super(RealTimePlotting ,self).__init__(**kwargs)

        self.length = self.fs * 4
        # Configure real time fft figure with matplotlib
        self.fig, self.ax = plt.subplots()
        #plt.ion() #Never turn this on. Or enjoy a almost frozen Application.

        # Settings
        self.ax.set_xlabel('Time(seconds)')
        self.ax.xaxis.set_label_coords(0.8, -0.01)
        self.ax.yaxis.set_label_coords(-0.00, 1.05)
        self.ax.set_ylabel('Amplitude(uV)',rotation=0)
        self.ax.get_xaxis().set_visible(True)
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

    def clear(self,dt=0):
        self.RealTimePlot.set_ydata(np.zeros(self.length).tolist())
        self.ax.set_ylim([-1,1])
        plt.draw_all()

    def refresh(self):
        # TODO Now real time plotting and FFT cannot be showed on the same time
        y = App.get_running_app().data[-self.length:]

        #  b,a = signal.butter(4,2 * np.pi * self.band/self.fs,'bandstop')
        #  y_filtered = signal.lfilter(b,a,y)
        self.RealTimePlot.set_ydata(y)
        if self.scale == 'Auto':
            padding = (np.max(y) - np.min(y)) * 0.1
            # TODO To improve figure ylimits stability
            if padding > 0.1:
                self.ax.set_ylim([np.min(y)-padding,np.max(y)+padding])

        plt.draw_all()

    def set_filter(self):
        pass

    def set_notch(self):
        if self.ids['notch'].text == '50Hz':
            pass
        elif self.ids['notch'].text == '60Hz':
            pass

    def set_length(self):
        if self.ids['length'].text == '0.5s':
            self.length = int(self.fs * 0.5)
        elif self.ids['length'].text == '1s':
            self.length = self.fs * 1
        elif self.ids['length'].text == '2s':
            self.length = self.fs * 2
        elif self.ids['length'].text == '3s':
            self.length = self.fs * 3
        elif self.ids['length'].text == '4s':
            self.length = self.fs * 4

        x = np.arange(0,self.length)/self.fs
        y = App.get_running_app().data[-self.length:]
        self.ax.set_xlim([np.min(x),np.max(x)])
        self.RealTimePlot.set_data(x,y)
        plt.draw_all()


class Test(Screen):
    """Test Layout"""
    # Settings
    theme_cls = ThemeManager()

    def __init__(self, **kwargs):
        """ Initializing serial and plot
        :returns: TODO
        """
        super(Test,self).__init__(**kwargs)
        ''' BLINKING
        '''
        #  for i in range(12):
            #  Clock.schedule_interval(partial(self.blinking,i),1/(0+12))

    def blinking(self,idx,dt):
        widgetID = 'button%d' % idx
        if self.ids[widgetID].state == 'normal':
            self.ids[widgetID].state = 'down'
            self.ids[widgetID].trigger_action(0.01)
        if self.ids[widgetID].state == 'down':
            self.ids[widgetID].state = 'normal'
            self.ids[widgetID].trigger_action(0.01)

class Blink(Screen):
    # Settings
    theme_cls = ThemeManager()

    def __init__(self, **kwargs):
        """ Initializing serial and plot
        :returns: TODO
        """
        super(Blink,self).__init__(**kwargs)
        ''' BLINKING
        '''
        for i in range(12):
            Clock.schedule_interval(partial(self.blinking,i),1/(0+12))

    def blinking(self,idx,dt):
        widgetID = 'button%d' % idx
        if self.ids[widgetID].state == 'normal':
            self.ids[widgetID].state = 'down'
            self.ids[widgetID].trigger_action(0.01)
        if self.ids[widgetID].state == 'down':
            self.ids[widgetID].state = 'normal'
            self.ids[widgetID].trigger_action(0.01)

    def set_freq(self):
        """
        set screen blinking frequency

        """
        freq = self.ids['freq'].value
        self.ids['freqLabel'].text = "%dHz" % self.ids['freq'].value
        for i in range(12):
            Clock.unschedule(partial(self.blinking,i))
            Clock.schedule_interval(partial(self.blinking,i),1/(freq*2))

    def toggleBlink(self):
        pass

class BlinkApp(App):
    kv_directory = 'ui_template'

    def __init__(self,**kwargs):
        """ Initializing serial
        :returns: TODO
        """
        super(BlinkApp,self).__init__(**kwargs)
    def build(self):
        root = ScreenManager()
        root.add_widget(Blink(name='bci'))
        return root

class BCIApp(App):
    # Settings
    kv_directory = 'ui_template'
    fps = 10
    storedLen = 1024
    data = ListProperty()
    # Buffer
    rawRemained = b'' # raw Data from serial, this should contain the data unused last time
    ser = None
    tmp = list()


    def __init__(self,**kwargs):
        """ Initializing serial
        :returns: TODO
        """
        init(autoreset=True)
        self.data = np.zeros(self.storedLen).tolist()
        super(BCIApp,self).__init__(**kwargs)


    def build(self):
        root = ScreenManager()
        root.add_widget(Test(name='bci'))
        return root

    def _read_thread(self,dt):
        t = threading.Thread(target=self._read)
        t.start()

        l = len(self.tmp)
        if l > 0:
            tmp = self.data[l:]
            tmp.extend(list(self.tmp))
            self.data = tmp
            #  logging.info("len:%d"%len(self.tmp))
        #  logging.info("len:%d"%len(self.data))

    def _read(self,dt=0):
        # data is a Listproperty, so on_data() will be called whenever data has been changed. on_data() will be called right after the following line.
        if self.ser.inWaiting() > 0:
            self.tmp = self.__readFromSerial()
            #  logging.info(len(self.data))

    def on_data(self,instance,data):
        self.root.current_screen.ids['RealTimePlotting'].refresh()
        self.root.current_screen.ids['FFT'].refresh()

    #  def __send_command(self,command):
            #  import time
            #  self.ser.write(command)
            #  time.sleep(1)
            #  #  state = self.ser.read_all()
            #  #  if b'START' not in command and b'OK' not in state:
                #  #  print(str(command) + " Error")
                #  #  print(state)

    #  def __configure_easybci(self):
            #  self.__send_command(b"RDM+STOP")
            #  self.__send_command(b"RDM+FILTER=OFF")
            #  self.__send_command(b"RDM+LOFF=OFF")
            #  self.__send_command(b"RDM+MODE=R1CH")
            #  self.__send_command(b"RDM+START")

    #  def __configure_easybci_thread(self):
        #  t = threading.Thread(target=self.__configure_easybci)
        #  t.start()

    def connect(self,port='/dev/ttyUSB0',baudrate=115200):
        try:
            # serial part
            # TODO serial should be opened after face recognition finished
            self.ser = serial.Serial(port = port,baudrate = baudrate, bytesize=8,parity='N',stopbits=1, write_timeout=0)
            self.data = np.zeros(self.storedLen).tolist()
            #  self.__configure_easybci_thread()

            # enable real time time-domain or/and frequency-domain plotting
            Clock.schedule_interval(self._read_thread,1/self.fps)
            #self.root.ids['RealTimePlotting'].start()
            #self.root.ids['FFT'].start()

            return True
        except SerialException:
            # Failed
            return False

    def disconnect(self):
        try:
            # Stop event
            Clock.unschedule(self._read_thread)

            # Close connection
            self.ser.close()

            # Clear Figures
            Clock.schedule_once(self.root.current_screen.ids['RealTimePlotting'].clear,1)
            Clock.schedule_once(self.root.current_screen.ids['FFT'].clear,1)
            #  self.root.current_screen.ids['RealTimePlotting'].clear()
            #  self.root.current_screen.ids['FFT'].clear()
        except AttributeError:
            # self.ser is None. We have not connect to any available serial device
            pass

    def __rawData2Voltage(self, rawData,protocol,gainCoefficient=12):
        """ convert rawData to exact voltage

        :rawData: a list of rawData
        :returns: converted voltage tupple in uV

        """
        raw = np.array(rawData)
        raw = raw[raw!=None]
        if protocol == 'EasyBCISingleChannel':
            #  2.42 is the referrence voltage of BCI device, 23 is the sampling resolution
            dataVol = 2.42 / 2**23 / gainCoefficient * raw
        elif protocol == 'BCISingleChannel':
            dataVol = 4.033 / 2**23 / gainCoefficient * raw /2**8
        dataVol = dataVol * 1e6 # convert uints to uV
        return tuple(dataVol)

    def __dataHex2int(self, dataHex):
        """ Convert hex data of 4 bytes containing EEG data to int

        :dataHex: string of length 4
        :returns: int
        """
        # 'i' means signed integer, '<' means little-endian
        try:
            data = struct.unpack('<i', dataHex)[0]
            return data
        except Exception:
            pass

    def __readFromSerial(self,protocol='BCISingleChannel'):
        """TODO: Docstring for readFromSerial.
        :protocol:protocol type. Should be 'EasyBCISingleChannel' or 'BCISingleChannel'.
        :ser: Serial Object
        :returns: a list of raw data from BCI
        """

        # Check Serial device and assign self.ser
        if self.ser is None:
            logging.error("Serial device not set.")
            return None

        ser = self.ser

        # Read cureent all available data
        try:
            rawData = ser.read_all()
        except OSError:
            # serial device unplugged
            # Stop event
            Clock.unschedule(self._read_thread)

            # Clear Figures
            self.root.current_screen.ids['RealTimePlotting'].clear()
            self.root.current_screen.ids['FFT'].clear()

        # Get data remaining in the last run
        rawRemained = self.rawRemained
        raw = rawRemained + rawData

        dataList= []

        # Manipulate raw data with given protocol
        if protocol == 'EasyBCISingleChannel' or protocol == 'BCISingleChannel':
            start = b'\xaa'
            middle = b'\xa1'
            lastIndex = 0
            # find possible index by search raw data for which is the same with bytes indicating start
            possibleIndex = [i for i in range(len(raw)) if raw[i:i+1] == start ]
            rawLen = len(raw)
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
                        rawDataPack[11]
                    except IndexError:
                        break

                    try:
                        # Python 2
                        checkCode = sum([ord(data) for data in rawDataPack[0:-1]])%256
                    except Exception:
                        # Python 3
                        checkCode = sum([data for data in rawDataPack[0:-1]])%256
                    if ord(rawDataPack[11:]) == checkCode:
                        # All validation steps passed
                        # convert hex to int
                        dataHex = rawDataPack[2:6] # first data
                        dataList.append(self.__dataHex2int(dataHex))

                        dataHex = rawDataPack[7:11] # second data
                        dataList.append(self.__dataHex2int(dataHex))
                        lastIndex = index + 12

                        # 接触检测
                        connectState = (rawDataPack[1] & 0xC0) >> 6
                    else:
                        # if index + 12 <= rawLen:
                        logging.warning('CheckCode: %s Fail with CheckCode %s%s%s' %(rawDataPack.hex(), Fore.RED, hex(checkCode)[2:], Style.RESET_ALL ) )
            # Update remaining raw data
            self.rawRemained = raw[lastIndex:]
            return self.__rawData2Voltage(dataList, protocol = protocol)

        else:
            # Exclude the last and incomplete data
            raise Exception('protocol should be EasyBCISingleChannel')

if __name__ == '__main__':
    #  logging.basicConfig(level=logging.INFO,
                #  format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                #  datefmt='%H:%M:%S')
    #  BlinkApp().run()
    try:
        BCIApp().run()
    except KeyboardInterrupt:
        if BCIApp.ser is not None:
            BCIApp.ser.close()
