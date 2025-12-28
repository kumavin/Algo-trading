import pandas as pd


def compute_trade_stats(trades):

    if not trades:
        return None, None

    df = pd.DataFrame(trades)

    closed = df[df["pnl"].notnull()]

    if closed.empty:
        return None, None

    wins = closed[closed["pnl"] > 0]
    losses = closed[closed["pnl"] < 0]

    stats = {
        "Trades": len(closed),
        "Win Rate %": len(wins) / len(closed) * 100 if len(closed) else 0,
        "Avg Win ₹": wins["pnl"].mean() if len(wins) else 0,
        "Avg Loss ₹": losses["pnl"].mean() if len(losses) else 0,
        "Best Trade ₹": closed["pnl"].max(),
        "Worst Trade ₹": closed["pnl"].min(),
        "Total Profit ₹": closed["pnl"].sum(),
        "Profit Factor": abs(wins["pnl"].sum() / losses["pnl"].sum())
                            if len(losses) else 0
    }

    return stats, closed