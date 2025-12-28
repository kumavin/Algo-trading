import numpy as np

def log_returns(prices):
    return np.diff(np.log(prices))

def rolling_volatility(returns, window=20):
    if len(returns) < window:
        return np.array([])
    return np.sqrt(
        np.convolve(returns**2, np.ones(window)/window, mode="valid")
    )

import numpy as np

def sma(prices, window):
    if len(prices) < window:
        return None
    return np.mean(prices[-window:])


def rsi(prices, period=14):
    if len(prices) < period + 1:
        return None

    deltas = np.diff(prices)
    gains = deltas[deltas > 0].sum() / period
    losses = -deltas[deltas < 0].sum() / period

    if losses == 0:
        return 100

    rs = gains / losses
    return 100 - (100 / (1 + rs))