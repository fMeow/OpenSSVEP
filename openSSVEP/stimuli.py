from __future__ import print_function,unicode_literals,with_statement,division

# kivy related
import matplotlib
import threading
matplotlib.use('module://kivy.garden.matplotlib.backend_kivy')
from matplotlib import pyplot as plt
from kivy.garden.graph import MeshLinePlot
#import matplotlib.animation as animation
from kivy.app import App
from kivy.config import Config
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.clock import Clock, CyClockBaseFree
from kivy.properties import StringProperty,ListProperty
from kivy.uix.screenmanager import ScreenManager, Screen

import serial,struct,logging,serial.tools.list_ports
from serial import SerialException
import numpy as np
from scipy import signal

from functools import partial


from colorama import Fore, Back, Style, init
import logging
import time
import os
from ipdb import set_trace

# Kivy Material Design
from kivymd.theming import ThemeManager

from BCIEncode import sequence
__author__ = 'Guoli Lv'
__email__ = 'guoli-lv@hotmail.com'

class Test(Screen):
    """Test Layout"""
    # Settings
    theme_cls = ThemeManager()
    frame = 0

    def __init__(self, interval, **kwargs):
        """ Initializing serial and plot
        :returns: TODO
        """
        super(Test,self).__init__(**kwargs)
        ''' BLINKING
        '''
        self.lasttime = time.time()
        self.Clock = CyClockBaseFree()

        self.f = open('blinkState','w+')
        self.schedule = list()
        Clock.schedule_interval(self.loop, interval)
        #  Clock.schedule_interval(partial(self.blinking,1),1/(2*15))
        #  Clock.schedule_interval(partial(self.blinking,2),1/(2*15))
        #  Clock.schedule_interval(partial(self.blinking,3),1/(2*15))

    def loop(self,dt):

        for schedule in self.schedule:
            schedule.cancel()
            del schedule

        self.schedule = list()

        try:
            self.count += 1
        except AttributeError:
            self.count = 0

        if self.count == 0:

            for i in range(12):
                widgetID = 'button%d' % i
                self.ids[widgetID].state = 'normal'
                #  self.ids[widgetID].text = '0'
        else:
            for i in range(12):
                seq = sequence[i]
                index = self.count - 1
                widgetID = 'button%d' % i
                hz = seq[index]
                self.schedule.append(Clock.schedule_interval(partial(self.blinking,i),1/(2*hz)))
                #  self.ids[widgetID].text = str(hz)

        Clock.schedule_once(self.write_state, 1)

        if os.path.isfile('code'):
            with open('code','r+') as f:
                index = int(f.read())
                f.close()
                os.remove('code')

            if index < 10:
                self.ids['inputText'].text += str(index)
            elif index == 10:
                self.ids['inputText'].text = ''
            elif index == 11:
                self.ids['inputText'].text = self.ids['inputText'].text[:-1]

    def blinking(self,idx,dt):
        #  if idx ==0:
            #  t = time.time()
            #  delta = (t-self.lasttime) * 1000
            #  logging.info("Time between(ms):%d"%delta)
            #  self.lasttime = t

        widgetID = 'button%d' % idx
        if self.ids[widgetID].state == 'normal':
            self.ids[widgetID].state = 'down'
            #  self.ids[widgetID].trigger_action(0.1)
        elif self.ids[widgetID].state == 'down':
            self.ids[widgetID].state = 'normal'
            #  self.ids[widgetID].trigger_action(0.1)

    def write_state(self,dt):
        self.f.seek(0)
        self.f.write(str(self.count))
        #  print(self.count)
        self.f.flush()
        if self.count == 3:
            self.count = -1


class StimuliApp(App):
    # Settings
    kv_directory = 'ui_template'

    def __init__(self,**kwargs):
        init(autoreset=True)
        super(StimuliApp,self).__init__(**kwargs)

    def build(self):
        root = ScreenManager()
        root.add_widget(Test(name='bci', interval = 3))
        return root

if __name__ == '__main__':
    #  logging.basicConfig(level=logging.INFO,
                #  format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                #  datefmt='%H:%M:%S')
    #  BlinkApp().run()
    Config.set('graphics','vsync','1')
    try:
        StimuliApp().run()
    except KeyboardInterrupt:
        pass
