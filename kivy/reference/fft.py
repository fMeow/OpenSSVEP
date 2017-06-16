
import numpy as np
import matplotlib.pyplot as plt
def fft(x,fig=0):
    plt.figure(fig)
    fs = 600
    ts = 1.0/fs
    L = 512
    # Perform 512 point FFT to improve resolution
    Y = np.fft.fft(x,L)
    # and select the left half of the symmetry spectrum
    #Yamp = np.abs(Y/L)

    # x-axis, ts = 1/fs
    f = np.fft.fftfreq(L,ts)

    fHalf = f[f>=0]
    YampHalf = np.abs(Y[f>=0]/L)
    #fHalf = f[:]
    #YampHalf = Yamp[:]

    YampHalf[1:-1] = YampHalf[1:-1] * 2
    #YampHalf[1:-2] = YampHalf[1:-2] * 2

    plt.plot(fHalf,YampHalf)

