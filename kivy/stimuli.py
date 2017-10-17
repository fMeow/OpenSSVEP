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
from ipdb import set_trace

# Kivy Material Design
from kivymd.theming import ThemeManager

__author__ = 'Guoli Lv'
__email__ = 'guoli-lv@hotmail.com'

class Test(Screen):
    """Test Layout"""
    # Settings
    theme_cls = ThemeManager()
    ## f1 f2 f3 依准确度排列
    f1 = 8
    f2 = 12
    f3 = 10
    sequence = [
            #  [8],
            #  [8],
            #  [8],
            #  [8],
            #  [8],
            #  [8],
            #  [8],
            #  [8],
            #  [8],
            #  [8],
            #  [8],
            #  [8],
            #  [12,  8,  10,],
            #  [12,  8,  10,],
            #  [12,  8,  10,],
            #  [12,  8,  10,],
            #  [12,  8,  10,],
            #  [12,  8,  10,],
            #  [12,  8,  10,],
            #  [12,  8,  10,],
            #  [12,  8,  10,],
            #  [12,  8,  10,],
            #  [12,  8,  10,],
            #  [12,  8,  10,],


            ##################################3
            [f1, f1, f2,],

            [f1, f1, f3],
            [f1, f2, ],
            [f1, f3, ],

            [f2, f2, ],
            [f2, f3, ],
            [f3, f2, ],

            [f3, f3, ],
            [f2, f1,  f1,],
            [f2, f1,  f2,],

            [f1,f1,f1],
            [f1,f2],

            ]

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
        self.blinkState = True
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

        if self.blinkState:
            try:
                self.count += 1
            except AttributeError:
                self.count = 0

            for i in range(12):
                seq = self.sequence[i]
                index = self.count % (len(seq))
                widgetID = 'button%d' % i
                hz = seq[index]
                self.schedule.append(Clock.schedule_interval(partial(self.blinking,i),1/(2*hz)))
                #  self.ids[widgetID].text = str(hz)
        else:
            for i in range(12):
                widgetID = 'button%d' % i
                self.ids[widgetID].state = 'normal'
                #  self.ids[widgetID].text = '0'
        Clock.schedule_once(self.write_state, 1)
        self.blinkState = not self.blinkState

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
        if not self.blinkState:
            self.f.write('1')
            self.f.flush()
        else:
            self.f.write('0')
            self.f.flush()

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
