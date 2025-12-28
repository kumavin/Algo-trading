import json
import os
from datetime import datetime

LOG_FILE = "trade_log.json"


def load_trades():
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE, "r") as f:
        return json.load(f)


def save_trades(trades):
    with open(LOG_FILE, "w") as f:
        json.dump(trades, f, indent=2, default=str)


def log_trade(action, stock, qty, price, pnl=None):
    trades = load_trades()

    trades.append({
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            # ISO not required for now — readable format preferred
        "action": action,
        "stock": stock,
        "qty": qty,
        "price": price,
        "pnl": pnl
    })

    save_trades(trades)