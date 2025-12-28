import numpy as np
def cagr(v): return (v[-1]/v[0])**(252/len(v))-1
def sharpe(r): return np.mean(r)/np.std(r)*np.sqrt(252)
def max_dd(v):
    peak=v[0]; dd=0
    for x in v:
        peak=max(peak,x)
        dd=max(dd,(peak-x)/peak)
    return dd