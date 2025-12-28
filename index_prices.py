import requests
import yfinance as yf


NSE_HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.nseindia.com"
}

# NSE index names must match API
INDEX_MAP = {
    "NIFTY 50": "NIFTY 50",
    "BANKNIFTY": "NIFTY BANK",
    "MIDCAP 100": "NIFTY MIDCAP 100",
    "FINNIFTY": "NIFTY FIN SERVICE",
    "NIFTY IT": "NIFTY IT",
    "NIFTY AUTO": "NIFTY AUTO",

    # Sensex handled separately (BSE)
    "SENSEX": "^BSESN",
}


def fetch_nse_index(name):
    """Fetch live index price from NSE"""
    try:
        url = f"https://www.nseindia.com/api/equity-stockIndices?index={name}"
        r = requests.get(url, headers=NSE_HEADERS, timeout=8)
        data = r.json()

        rec = data["data"][0]

        return {
            "price": float(rec["lastPrice"]),
            "change": float(rec["change"]),
            "pct": float(rec["pChange"]),
            "source": "NSE"
        }

    except Exception:
        return None


def fetch_sensex_yahoo(symbol):
    """Fallback for Sensex via Yahoo"""
    try:
        data = yf.Ticker(symbol).history(period="1d", interval="5m")
        price = float(data["Close"].iloc[-1])

        return {
            "price": price,
            "change": 0,
            "pct": 0,
            "source": "Yahoo"
        }

    except Exception:
        return None


def get_all_indices():
    results = {}

    for label, api_name in INDEX_MAP.items():

        # Sensex via Yahoo
        if label == "SENSEX":
            results[label] = fetch_sensex_yahoo(api_name)
            continue

        # NSE index fetch
        results[label] = fetch_nse_index(api_name)

    return results