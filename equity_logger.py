import json
import os
from datetime import datetime

FILE = "equity_curve.json"


def log_equity(value):

    data = []

    # load existing equity log safely
    if os.path.exists(FILE):

        try:
            with open(FILE, "r") as f:
                content = f.read().strip()
                if content:
                    data = json.loads(content)
        except Exception:
            # corrupted or partially written file
            data = []

    # append new record
    data.append({
        "time": datetime.now().isoformat(),
        "value": float(value)
    })

    # write file safely
    with open(FILE, "w") as f:
        json.dump(data, f, indent=2)
