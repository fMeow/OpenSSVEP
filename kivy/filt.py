from scipy import signal
fmin = 49
fmax = 51
fs = 250
b,a = signal.butter(4,[fmin /(fs/2),fmax /(fs/2)],'bandstop')
xbuf= [0 for i in range(len(b)-1)]
ybuf= [0 for i in range(len(a)-1)]

def filt(new,b,a,xbuf,ybuf):
    xbuf += [new]
    y = sum(b * xbuf[::-1]) - sum(a[1:] * ybuf[::-1])
    xbuf.pop(0)
    ybuf += [y]
    ybuf.pop(0)
    return y

