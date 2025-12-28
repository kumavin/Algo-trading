import json
import os
from datetime import datetime

EQUITY_FILE = "equity_curve.json"

def log_equity(value):
    data = []

    if os.path.exists(EQUITY_FILE):
        with open(EQUITY_FILE, "r") as f:
            data = json.load(f)

    data.append({
        "time": datetime.now().isoformat(),
        "value": value
    })

    with open(EQUITY_FILE, "w") as f:
        json.dump(data, f, indent=2)