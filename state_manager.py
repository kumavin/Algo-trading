import json
import os

STATE_FILE = "state.json"

def save_state(trader):
    data = {
        "cash": trader.cash,
        "positions": trader.positions
    }
    with open(STATE_FILE, "w") as f:
        json.dump(data, f)


def load_state(trader):
    if not os.path.exists(STATE_FILE):
        return

    with open(STATE_FILE, "r") as f:
        data = json.load(f)

    trader.cash = data.get("cash", trader.cash)
    trader.positions = data.get("positions", trader.positions)