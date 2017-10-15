from pandas import Series
from scipy import signal
import numpy as np
from matplotlib import pyplot as plt

def plot_fft(data, start, target, fftLen=1024, duration=512, fs=250,filt=[4,45]):
    end = int((start) * fs+ duration)
    start = int(start * fs)

    if filt is not None:
        w0 = 50/(fs/2)
        b,a = signal.iirnotch(w0,1)
        data = signal.filtfilt(b, a, data)
        b,a = signal.butter(8, (filt[0]/(fs/2),filt[1]/(fs/2)), 'band')
        data = signal.filtfilt(b, a, data)

    y = data[start:end] * signal.blackman(end-start,sym=0)
    Y = np.fft.rfft(y,fftLen)
    freq = np.fft.rfftfreq(fftLen,1/250)
    YampPos = np.abs(Y/fs)
    plt.clf()
    plt.xlim([0,60])
    p1 = plt.subplot(211)
    p1.plot(freq, YampPos)
    m = max(YampPos)
    p1.set_xlim([0,62.5])
    p1.axvspan(target-1,target+1,color='r',alpha=0.3)
    p1.axvspan(2*target-2,2*target+2,color='r',alpha=0.3)
    p1.axvspan(3*target-3,3*target+3,color='r',alpha=0.3)

    p2 = plt.subplot(212)
    p2.plot(data)

def animate(data, target, fftLen=1024, duration=512, fs=250,filt=[4,45],gap=0.1):
    plt.ion()
    l = len(data)
    s = l/250 - 30
    for start in np.arange(int(s), int( (l-fftLen)/fs),0.5):
        plot_fft(data, start, target, fftLen, duration, fs, filt)
        plt.pause(gap)

