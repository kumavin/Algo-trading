import numpy as np

def sma(prices, window):
    if len(prices) < window:
        return None
    return np.mean(prices[-window:])

def volatility(prices, window=20):
    returns = np.diff(np.log(prices))
    if len(returns) < window:
        return None
    return np.std(returns[-window:])

def atr(high, low, close, window=14):
    trs = []
    for i in range(1, len(close)):
        tr = max(
            high[i] - low[i],
            abs(high[i] - close[i-1]),
            abs(low[i] - close[i-1])
        )
        trs.append(tr)

    if len(trs) < window:
            return None

    return np.mean(trs[-window:])