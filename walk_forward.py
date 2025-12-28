import pandas as pd
from paper_trader import PaperTrader
from rebalance import weekly_rebalance
from drawdown import compute_drawdown

def run_walk_forward(
    price_dfs,
    train_years=2,
    test_months=6,
    rebalance_day=2,
    trail_pct=0.05
):
    """
    Walk-forward backtest using rolling windows
    """

    all_dates = price_dfs[next(iter(price_dfs))]["Date"]

    train_days = int(train_years * 252)
    test_days = int(test_months * 21)

    min_required = train_days + test_days
    if len(all_dates) < min_required:
        raise ValueError(
            f"Not enough data for walk-forward. "
            f"Required ≈ {min_required} rows, found {len(all_dates)}"
        )

    results = []
    start = train_days

    while start + test_days < len(all_dates):
        trader = PaperTrader()

        test_end = start + test_days

        for i in range(start, test_end):
            date = all_dates.iloc[i]
            weekday = date.weekday()

            prices_today = {
                s: df["Close"].iloc[i]
                for s, df in price_dfs.items()
            }

            price_history = {
                s: df["Close"].iloc[:i].values
                for s, df in price_dfs.items()
            }

            # Weekly rebalance
            if weekday == rebalance_day:
                weekly_rebalance(trader, price_history, prices_today)

            # Trailing stop
            to_exit = []
            for stock, pos in trader.positions.items():
                if stock not in prices_today:
                    continue

                live = prices_today[stock]
                pos["high"] = max(pos.get("high", pos["entry"]), live)
                trail_price = pos["high"] * (1 - trail_pct)

                if live <= trail_price:
                    to_exit.append(stock)

            for stock in to_exit:
                trader.sell(stock, prices_today[stock])

            results.append({
                "Date": date,
                "Value": trader.value(prices_today)
            })

        start += test_days  # walk forward

    df = pd.DataFrame(results)

    if df.empty:
        raise ValueError("Walk-forward produced no results (empty dataframe)")

    df["Drawdown"] = compute_drawdown(df["Value"])
    return df