import matplotlib
matplotlib.use('module://kivy.garden.matplotlib.backend_kivy')
from matplotlib.figure import Figure
from numpy import arange, sin, pi
from kivy.app import App

import numpy as np
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvas,\
                                                NavigationToolbar2Kivy
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from matplotlib.transforms import Bbox
from kivy.uix.button import Button
from kivy.graphics import Color, Line, Rectangle

import matplotlib.pyplot as plt


class MatplotlibTest(App):
    title = 'Matplotlib Test'
    def __init__(self, **kwargs):
        super(MatplotlibTest,self).__init__(**kwargs)
        N = 5
        menMeans = (20, 35, 30, 35, 27)
        menStd = (2, 3, 4, 1, 2)

        ind = np.arange(N)  # the x locations for the groups
        width = 0.35       # the width of the bars

        self.fig, self.ax = plt.subplots()
        rects1 = self.ax.bar(ind, menMeans, width, color='r', yerr=menStd)
        self.canvas = self.fig.canvas

    def build(self):
        fl = BoxLayout(orientation="vertical")
        #a.bind(on_press=callback)
        fl.add_widget(self.canvas)
        #fl.add_widget(a)
        return fl

if __name__ == '__main__':
    MatplotlibTest().run()
