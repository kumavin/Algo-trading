import numpy as np


def recent_breakout(prices, lookback=40):
    """
    Stock must have broken recent resistance
    """

    if len(prices) < lookback + 10:
        return False

    p = np.array(prices)

    range_high = p[-lookback:-10].max()
    recent_high = p[-10:].max()

    return recent_high > range_high


def retest_support_hold(prices, tolerance=0.02):
    """
    Pullback must NOT break below breakout level
    """

    p = np.array(prices)

    breakout_level = p[-20:-5].max()
    pullback_low = p[-5:].min()

    return pullback_low >= breakout_level * (1 - tolerance)


def bounce_confirmation(prices):
    """
    Bounce & bullish close
    """
    return prices[-1] > prices[-2]


def is_breakout_retest_bounce(prices):
    """
    Final combined condition
    """

    if not recent_breakout(prices):
        return False

    if not retest_support_hold(prices):
        return False

    if not bounce_confirmation(prices):
        return False

    return True