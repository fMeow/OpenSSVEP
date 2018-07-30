from pandas import Series
from scipy import signal
import numpy as np
from ipdb import set_trace
from matplotlib import pyplot as plt

def plot_fft(data, start, target=None, fftLen=1024, window=512, fs=250,filt=[4,45],tolerance=1):
    end = int((start) * fs+ window)
    start = int(start * fs)

    # Filter
    if filt is not None:
        w0 = 50/(fs/2)
        b,a = signal.iirnotch(w0,10)
        data = signal.filtfilt(b, a, data)
        b,a = signal.butter(10, (filt[0]/(fs/2),filt[1]/(fs/2)), 'band')
        data = signal.filtfilt(b, a, data)

    # Power Spectrum
    y = data[start:end] # * signal.blackman(end-start,sym=0)
    Y = np.fft.rfft(y,fftLen)
    freq = np.fft.rfftfreq(fftLen,1/fs)
    Yabs = np.abs(Y/fs)

    #  mask = (freq>target-tolerance) * (freq<target+tolerance)
    #  argmax = signal.argrelmax(Yabs[mask])
    #  fmax1 = freq[mask][argmax]
    #  #  print('Start at %ds, local maximum at', fmax1)
    #  mask = (freq>2*(target-tolerance)) * (freq<3*(target+tolerance))
    #  argmax = np.argmax(Yabs[mask])
    #  fmax2 = freq[mask][argmax]
    #  #  print('Start at %ds, local maximum at', fmax2,"Diff: %f",fmax2-2*fmax1)

    # Plot
    plt.xlim([0,60])
    p1 = plt.subplot(311)
    p1.cla()
    p1.plot(freq, Yabs)
    p1.set_xlim([0,62.5])
    p1.set_title('Start Time:%f Duration: %f'%(start/fs,window/fs))

    if target:
        # Vertical line to indicate stimuli frequency
        p1.axvspan(target-tolerance,target+tolerance,color='r',alpha=0.3)
        p1.axvspan(2*(target-tolerance),2*(target+tolerance),color='r',alpha=0.3)
        p1.axvspan(3*(target-tolerance), 3*(target+tolerance),color='r',alpha=0.3)

    p2 = plt.subplot(312)
    p2.cla()
    p2.plot(data)

    return freq,Yabs, Series( Yabs,index=freq)

def computeSNR(y,data):
    maximum = y.max()
    fmax = y.argmax()
    #  argmax = len(data.index[data.index<fmax])
    #  argrelmin = signal.argrelmin(data.values)[0]
    #  # 寻找左右两个极小值点
    #  argrelminR = argrelmin[argrelmin > argmax][0]
    #  argrelminL = argrelmin[argrelmin < argmax][-1]
    #  relminL =  data.index[argrelminL]
    #  relminR =  data.index[argrelminR]
    #  m = (data[relminR] + data[relminL])/2
    m = data.mean()
    return maximum/m


def classify(freq,Yabs,filt,tolerance):
    '''
        取可疑极大值点左右两个极小值点，求出两个极小值点的均值作为这附近功率谱的基准。
    '''
    N=5
    Yabs = np.convolve(Yabs, np.ones((N,))/N, mode='same')
    y = Series(Yabs ,index = freq)
    if filt:
        yFilt= y[filt[0]:filt[1]]
    else:
        yFilt = y
    maximum = yFilt.max()
    mean = yFilt.mean()
    threshold = 4
    if computeSNR(y, y) > threshold and maximum < 15:
        # Threshold
        maxF = y.argmax()
        #  print("Max freq at %f" % maxF)

        # Inspect half frequency of max frequency with a tolerance
        halfMaxF = maxF/2
        halfY = y[halfMaxF-tolerance:halfMaxF+tolerance]
        halfSNR = computeSNR(halfY,y)

        doubleMaxF = maxF*2
        doubleY = y[doubleMaxF-2*tolerance:doubleMaxF+2*tolerance]
        doubleSNR = computeSNR(doubleY,y)

        if halfSNR <= threshold:
            if doubleSNR > threshold/2:
                print('Stimuli at %f' % yFilt.argmax())
            else:
                print('SNR on double frequency too low')
            #  print('Max freq at %f' % yFilt.argmax())
        else:
            print('Stimuli at %f' % halfY.argmax())
    else:
        print('SNR too low')
    return y


def animate(data, target=None, fftLen=1024, window=512, fs=250,filt=[4,45],gap=0.1,duration=30,tolerance=1, avg = 4,interval=0.5, claTol = 1):
    plt.ion()
    l = len(data)
    s = l/fs - duration
    freq = np.fft.rfftfreq(fftLen,1/fs)
    powerSpectrumAvg = np.zeros_like(freq)

    pSAvg = np.zeros_like(freq)
    c = 0

    plt.show()

    try:
        count = 0
        for start in np.arange(int(s), int( (l-window)/fs),interval):
            _, powerSpectrum, _ = plot_fft(data, start, target, fftLen, window, fs, filt,tolerance)
            pSAvg+= powerSpectrum
            c += 1

            if count < avg:
                powerSpectrumAvg += powerSpectrum
                count += 1
            else:

                #  classify(freq,powerSpectrumAvg/count,filt = filt,tolerance=tolerance)
                classifyNaive(freq,powerSpectrumAvg/count, tolerance = claTol)
                p3 = plt.subplot(313)
                p3.cla()
                p3.set_xlim([0,62.5])
                p3.plot(freq,powerSpectrumAvg/count)

                count = 1
                powerSpectrumAvg = powerSpectrum
            plt.pause(gap)
        pSAvg /= c
        p3 = plt.subplot(313)
        p3.cla()
        p3.plot(freq, pSAvg)
        p3.set_xlim([0,62.5])
    except KeyboardInterrupt:
        print('Stoped')
    return freq, powerSpectrumAvg, Series(powerSpectrumAvg,index=freq)

def sumHz(data, tolerance=0.5):
    out = dict()
    for i in range(1, int(data.index.max())):
        out[i] = data[i-tolerance : i+tolerance].mean()
    return Series(out)

def classifyNaive(freq, powerSpectrum, tolerance=0.5, plot=False):
    d = Series(powerSpectrum,index=freq)
    naive = sumHz(d, tolerance)
    maximum = naive.argmax()
    if plot:
        naive.plot(kind='bar')

    noise = (naive.sum() - naive.max()) / (len(naive) - 1)
    snr = naive.max()/noise
    print("Max:%d SNR:%f"%(naive.argmax(), snr))
    return naive, maximum

