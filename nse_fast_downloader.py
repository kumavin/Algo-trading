import pandas as pd
import requests, zipfile, io, os
from datetime import datetime, timedelta

BASE_URL = "https://archives.nseindia.com/content/historical/EQUITIES"

def _bhavcopy_path(date):
    return f"data/bhavcopy/{date.strftime('%Y-%m-%d')}.csv"

def download_bhavcopy_once(date):
    os.makedirs("data/bhavcopy", exist_ok=True)
    path = _bhavcopy_path(date)

    if os.path.exists(path):
        return path

    url = (
        f"{BASE_URL}/{date.year}/"
        f"{date.strftime('%b').upper()}/"
        f"cm{date.strftime('%d%b%Y').upper()}bhav.csv.zip"
    )

    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        z = zipfile.ZipFile(io.BytesIO(r.content))
        df = pd.read_csv(z.open(z.namelist()[0]))
        df.to_csv(path, index=False)
        return path
    except:
        return None

def build_price_history_fast(symbols, years=2):
    os.makedirs("data/prices", exist_ok=True)

    price_map = {s: [] for s in symbols}
    days = years * 365

    for i in range(days):
        date = datetime.today() - timedelta(days=i)
        path = download_bhavcopy_once(date)
        if not path:
            continue

        df = pd.read_csv(path)

        for s in symbols:
            row = df[df["SYMBOL"] == s]
            if not row.empty:
                close = float(row["CLOSE"].iloc[0])
                price_map[s].append((date.date(), close))

    for s, rows in price_map.items():
        if rows:
            rows.reverse()
            pd.DataFrame(rows, columns=["Date","Close"]) \
              .to_csv(f"data/prices/{s}.csv", index=False)

    return price_map