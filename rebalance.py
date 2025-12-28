from signals import buy_signal, rank_stocks
from market_regime import detect_market_regime
from indicators_plus import sma, volatility


def bear_market_filter(prices):
    sma200 = sma(prices, 200)
    if sma200 is None:
        return False

    # must be above 200-day trend
    if prices[-1] < sma200:
        return False

    vol = volatility(prices, 20)
    if vol is None:
        return False

    # reject high-volatility names
    return vol < 0.035


def compute_position_size(cash, price, prices, risk_pct=0.02):
    """
    Volatility-based position sizing
    Equalizes risk contribution across stocks
    """

    vol = volatility(prices)

    if vol is None or vol == 0:
        return 0

    # risk budget
    capital_risk = cash * risk_pct

    # inverse volatility weighting
    position_value = capital_risk / vol

    qty = int(position_value // price)

    return max(qty, 0)


def weekly_rebalance(trader, price_history, prices):
    """
    Weekly rebalance logic:

    ✔ Always sell losers / non-qualified names
    ✔ Rank strongest stocks
    ✔ Select top N based on regime
    ✔ Buy using volatility-based position sizing
    ✔ Bear mode = safety filter only
    """

    regime = detect_market_regime()

    # -------- regime-adaptive constraints --------
    if regime == "BULL":
        max_positions = 15

    elif regime == "NEUTRAL":
        max_positions = 8

    elif regime == "BEAR":
        max_positions = 5

    else:
        max_positions = 6

    # -------- generate BUY universe --------
    qualified = {}

    for s, p in price_history.items():

        # must pass normal strategy signal
        if not buy_signal(p):
            continue

        # extra safety filter in BEAR markets
        if regime == "BEAR":
            if not bear_market_filter(p):
                continue

        qualified[s] = p

    ranked = rank_stocks(qualified)
    top = ranked[:max_positions]

    # -------- SELL positions that dropped out --------
    to_sell = [s for s in trader.positions if s not in top]

    for stock in to_sell:
        if stock in prices:
            trader.sell(stock, prices[stock])

    # -------- BUY & SIZE positions --------
    if not top:
        return

    for stock in top:

        # skip if already holding
        if stock in trader.positions:
            continue

        if stock not in prices:
            continue

        price = prices[stock]

        qty = compute_position_size(
            trader.cash,
            price,
            price_history[stock]
        )

        if qty > 0:
            trader.buy(stock, price, qty)