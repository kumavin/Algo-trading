from signals import generate_buy_signals, generate_sell_signals
from risk_manager import RiskManager
from paper_trader import PaperTrader

def run_daily_simulation(price_dfs, ranked, regime):
    trader = PaperTrader()
    risk = RiskManager()
    dates = price_dfs[next(iter(price_dfs))]["Date"]

    for i in range(60, len(dates)):
        prices_today = {s:df["Close"].iloc[i] for s,df in price_dfs.items()}
        prices_hist = {s:df["Close"].iloc[:i+1].values for s,df in price_dfs.items()}

        for s in generate_sell_signals(prices_hist, trader.positions):
            trader.sell(s, prices_today[s], dates.iloc[i])

        for s in generate_buy_signals(prices_hist, ranked, regime):
            if s in trader.positions: continue
            q = risk.position_size(trader.cash, prices_today[s])
            trader.buy(s, prices_today[s], q, dates.iloc[i])

        trader.history.append({
            "Date": dates.iloc[i],
            "Value": trader.value(prices_today)
        })
    return trader
