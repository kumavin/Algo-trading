# import yfinance as yf

# def get_live_prices(symbols):
#     prices = {}

#     for s in symbols:
#         try:
#             data = yf.Ticker(s + ".NS").history(period="2d")
#             if not data.empty:
#                 prices[s] = float(data["Close"].iloc[-1])
#         except:
#             continue

#     return prices


# def get_price_history(symbol, days=180):
#     try:
#         ticker = symbol + ".NS"
#         data = yf.Ticker(ticker).history(period=f"{days}d")
#         if data.empty:
#             return []
#         return data["Close"].values
#     except:
#         return []

import yfinance as yf

def get_live_prices(symbols):
    prices = {}

    for s in symbols:
        try:
            ticker = s if s.startswith("^") else s + ".NS"
            data = yf.Ticker(ticker).history(period="2d")
            if not data.empty:
                prices[s] = float(data["Close"].iloc[-1])
        except:
            continue

    return prices


def get_price_history(symbol, days=300):
    """
    Handles both stocks and index symbols
    """
    try:
        ticker = symbol if symbol.startswith("^") else symbol + ".NS"
        data = yf.Ticker(ticker).history(period=f"{days}d")

        if data.empty:
            return []

        return data["Close"].values
    except:
        return []