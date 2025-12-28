import numpy as np
from factors import composite_score

def buy_signal(prices):
    if len(prices) < 50:
        return False

    sma20 = np.mean(prices[-20:])
    sma50 = np.mean(prices[-50:])
    return sma20 > sma50


def rank_stocks(price_history):
    scores = {}

    for stock, prices in price_history.items():
        if len(prices) < 60:
            continue

        score = composite_score(prices)
        scores[stock] = score

    return sorted(scores, key=scores.get, reverse=True)

def bear_market_filter(symbol, prices):
    sma200 = sma(prices, 200)
    if sma200 is None:
        return False

    # must be above 200-day trend
    if prices[-1] < sma200:
        return False

    vol = volatility(prices, 20)
    if vol is None:
        return False

    # reject high volatility junk stocks
    return vol < 0.035