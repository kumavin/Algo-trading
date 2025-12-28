# import numpy as np
# from live_prices import get_price_history

# NIFTY_SYMBOL = "^NSEI"   # NIFTY 50 index


# def detect_market_regime():
#     """
#     Returns: "BULL" or "BEAR"
#     """
#     prices = get_price_history(NIFTY_SYMBOL, days=300)

#     if len(prices) < 200:
#         return "UNKNOWN"

#     sma50 = np.mean(prices[-50:])
#     sma200 = np.mean(prices[-200:])

#     return "BULL" if sma50 > sma200 else "BEAR"

import numpy as np
from live_prices import get_price_history

NIFTY_SYMBOL = "^NSEI"   # ✅ Correct Yahoo Finance symbol


def detect_market_regime():
    """
    Market regime using NIFTY 50 trend
    """
    prices = get_price_history(NIFTY_SYMBOL, days=300)

    if len(prices) < 200:
        return "UNKNOWN"

    sma50 = np.mean(prices[-50:])
    sma200 = np.mean(prices[-200:])

    return "BULL" if sma50 > sma200 else "BEAR"