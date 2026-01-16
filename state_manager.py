import json
import os

STATE_FILE = "state.json"

def save_state(trader):
    state = {
        "cash": trader.cash,
        "positions": trader.positions  # MUST save empty {}
    }
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def load_state(trader):
    if not os.path.exists(STATE_FILE):
        return

    with open(STATE_FILE) as f:
        state = json.load(f)

    trader.cash = state.get("cash", trader.cash)
    trader.positions = state.get("positions", {})  # MUST REPLACE, not update
