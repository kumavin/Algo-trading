import streamlit as st
from datetime import datetime
import pandas as pd
import os
import time
import random
import requests

from universe import UNIVERSE
from signals import buy_signal, rank_stocks
from paper_trader import PaperTrader
from live_prices import get_live_prices, get_price_history
from rebalance import weekly_rebalance
from state_manager import save_state, load_state
from market_regime import detect_market_regime
from equity_logger import log_equity
from drawdown import compute_drawdown
from performance import compute_cagr, compute_sharpe

from index_prices import get_all_indices
from advanced_filters import momentum_score, trend_slope, pullback_quality
from breakout_retest import is_breakout_retest_bounce

from trade_logger import log_trade, load_trades
from trade_analytics import compute_trade_stats

from streamlit_autorefresh import st_autorefresh


# ==========================================================
# CONFIG
# ==========================================================
REBALANCE_DAY = 2     # Wednesday

REFRESH_MIN_SEC = 120
REFRESH_MAX_SEC = 180

if "refresh_interval_sec" not in st.session_state:
    st.session_state.refresh_interval_sec = random.randint(
        REFRESH_MIN_SEC, REFRESH_MAX_SEC
    )

st.set_page_config(layout="wide")
st.title("📊 Auto Buy & Live PnL — Trading Cockpit")


# ==========================================================
# PERSISTED TRADER
# ==========================================================
if "trader" not in st.session_state:
    st.session_state.trader = PaperTrader()
    load_state(st.session_state.trader)

trader = st.session_state.trader


# ==========================================================
# STATE LOGS
# ==========================================================
if "price_cache" not in st.session_state:
    st.session_state.price_cache = {}

if "missing_price_log" not in st.session_state:
    st.session_state.missing_price_log = []


def log_missing(symbol, source):
    st.session_state.missing_price_log.append({
        "symbol": symbol,
        "source": source,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })


# ==========================================================
# CACHING HELPERS
# ==========================================================
@st.cache_data(ttl=120)
def cache_prices(symbols):
    return build_resilient_prices(symbols)


@st.cache_data(ttl=900)
def cache_market_regime():
    return detect_market_regime()


@st.cache_data(ttl=300)
def cache_indices():
    return get_all_indices()


@st.cache_data
def cache_trade_stats():
    trades = load_trades()
    return compute_trade_stats(trades)


@st.cache_data
def load_equity_curve():
    if os.path.exists("equity_curve.json"):
        df = pd.read_json("equity_curve.json")
        df["time"] = pd.to_datetime(df["time"])
        return df
    return None


# ==========================================================
# NSE FALLBACK
# ==========================================================
def get_nse_price(symbol):
    try:
        url = f"https://www.nseindia.com/api/quote-equity?symbol={symbol}"
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://www.nseindia.com"
        }
        r = requests.get(url, headers=headers, timeout=6)
        data = r.json()
        return float(data["priceInfo"]["lastPrice"])
    except Exception:
        return None


# ==========================================================
# RESILIENT PRICE ENGINE
# ==========================================================
def build_resilient_prices(symbols):

    final_prices = {}
    cache = st.session_state.price_cache
    now = time.time()

    yf_prices = get_live_prices(symbols)

    for s in symbols:

        if s in yf_prices and yf_prices[s] is not None:
            final_prices[s] = yf_prices[s]
            cache[s] = {"price": yf_prices[s], "time": now, "source": "YF"}
            continue

        nse_price = get_nse_price(s)

        if nse_price:
            final_prices[s] = nse_price
            cache[s] = {"price": nse_price, "time": now, "source": "NSE"}
            log_missing(s, "YF → NSE fallback")
            continue

        if s in cache:
            final_prices[s] = cache[s]["price"]
            log_missing(s, "CACHE used")
            continue

        final_prices[s] = None
        log_missing(s, "NO price available")

    return final_prices


# ==========================================================
# LOAD PRICE HISTORY ONCE (NOT PER REFRESH)
# ==========================================================
if "price_history" not in st.session_state:
    st.session_state.price_history = {
        s: get_price_history(s)
        for s in UNIVERSE
        if len(get_price_history(s)) >= 180
    }

price_history = st.session_state.price_history


# ==========================================================
# LIGHTWEIGHT BACKGROUND REFRESH (PRICES ONLY)
# ==========================================================
now = time.time()
last_update = st.session_state.get("last_update_time", 0)
interval = st.session_state.refresh_interval_sec

should_refresh = (now - last_update) > interval

if should_refresh:

    prices = cache_prices(list(UNIVERSE))

    st.session_state["prices_bg"] = prices
    st.session_state["last_update_time"] = now

    st.session_state.refresh_interval_sec = random.randint(
        REFRESH_MIN_SEC, REFRESH_MAX_SEC
    )
    interval = st.session_state.refresh_interval_sec

else:
    prices = st.session_state.get("prices_bg", {})


# ==========================================================
# UI AUTORERUN
# ==========================================================
st_autorefresh(
    interval=st.session_state.refresh_interval_sec * 1000,
    key="ui_refresh_sync"
)


# ==========================================================
# REFRESH BADGE
# ==========================================================
t = st.session_state.get("last_update_time", now)
age = int(now - t)

st.markdown(
    f"""
    <div style="
        padding:6px 10px;
        border:1px solid #334155;
        border-radius:10px;
        display:inline-block;
        font-size:12px;">
        🔄 Last refreshed <b>{age}s</b> ago
        &nbsp;&nbsp;|&nbsp;&nbsp;
        ⏱️ Next refresh <b>{interval//60}m {interval%60}s</b>
    </div>
    """,
    unsafe_allow_html=True
)


# ==========================================================
# MARKET REGIME (CACHED)
# ==========================================================
regime = cache_market_regime()

if regime == "BULL":
    MAX_POSITIONS = 15
    TRAIL_PCT = 0.05
    st.success("📈 BULL MARKET — Full Allocation Mode")

elif regime == "NEUTRAL":
    MAX_POSITIONS = 8
    TRAIL_PCT = 0.04
    st.warning("🟡 NEUTRAL — Reduced Exposure")

elif regime == "BEAR":
    MAX_POSITIONS = 5
    TRAIL_PCT = 0.03
    st.error("📉 BEAR — Capital Protection Mode")

else:
    MAX_POSITIONS = 6
    TRAIL_PCT = 0.04
    st.info("⚪ UNKNOWN — Conservative Mode")


# ==========================================================
# INDEX SNAPSHOT (CACHED)
# ==========================================================
st.subheader("📊 Market Index Snapshot")

indices = cache_indices()
cols = st.columns(4)

for i, (name, data) in enumerate(indices.items()):
    with cols[i % 4]:
        if not data:
            st.metric(name, "N/A")
            continue

        icon = "🔻" if data["pct"] < 0 else "🟢"

        st.metric(
            label=name,
            value=round(data["price"], 2),
            delta=f"{icon} {round(data['pct'],2)}% ({data['source']})"
        )


# ==========================================================
# SIDEBAR STATUS
# ==========================================================
st.sidebar.subheader("📊 Data Status")
st.sidebar.metric("Stocks with history", len(price_history))
st.sidebar.metric("Prices available", sum(1 for p in prices.values() if p))

with st.sidebar.expander("Missing price symbols"):
    missing = [s for s in UNIVERSE if s not in prices or prices[s] is None]
    st.write(missing if missing else "All resolved 👍")

st.sidebar.subheader("⏳ Refresh Timing")
st.sidebar.write("Last refresh:", datetime.fromtimestamp(t))
st.sidebar.write("Cycle (sec):", interval)


# ==========================================================
# SCREENING + RANKING (RUN ON DEMAND)
# ==========================================================
st.subheader("🏆 Swing Candidates")

if st.button("Run Screening / Ranking"):

    qualified = {}

    for s, hist in price_history.items():

        if not buy_signal(hist): continue
        if momentum_score(hist) < 0: continue
        if trend_slope(hist) <= 0: continue
        if pullback_quality(hist) < 0.8: continue
        if not is_breakout_retest_bounce(hist): continue

        qualified[s] = hist

    ranked = rank_stocks(qualified)
    st.session_state.ranked = ranked

ranked = st.session_state.get("ranked", [])


# ==========================================================
# WEEKLY REBALANCE — MANUAL TRIGGER
# ==========================================================
today = datetime.today().weekday()

st.subheader("🔁 Weekly Rebalance")

if today == REBALANCE_DAY and st.button("Run Weekly Rebalance"):

    weekly_rebalance(trader, price_history, prices)
    save_state(trader)
    st.success("Rebalance executed")

else:
    st.info("Runs Wednesday — click when ready")


# ==========================================================
# ⚡ TRADING CONSOLE
# ==========================================================
st.markdown("## ⚡ Trading Console")


# ==========================================================
# BUY CONSOLE
# ==========================================================
if ranked:

    st.dataframe(
        [{"Rank": i+1, "Stock": s} for i, s in enumerate(ranked[:MAX_POSITIONS])]
    )

    buy_col1, buy_col2 = st.columns(2)

    # AUTO BUY
    with buy_col1:
        st.markdown("##### 🚀 Auto Buy — Top Ranked")

        if st.button("Buy Top Ranked"):
            for s in ranked[:MAX_POSITIONS]:

                if s in trader.positions:
                    continue

                price = prices.get(s)
                if not price:
                    continue

                qty = max(int(trader.cash // (MAX_POSITIONS * price)), 1)

                trader.buy(s, price, qty)
                log_trade("BUY", s, qty, price, 0)

            save_state(trader)
            st.success("Auto-buy executed")

    # MANUAL BUY
    with buy_col2:

        selectable = ranked[:MAX_POSITIONS * 2]
        selected = st.multiselect("Choose stocks", selectable)

        if st.button("Buy Selected") and selected:

            for s in selected:

                if s in trader.positions:
                    continue

                price = prices.get(s)
                if not price:
                    continue

                qty = max(int(trader.cash // (MAX_POSITIONS * price)), 1)

                trader.buy(s, price, qty)
                log_trade("BUY", s, qty, price, 0)

            save_state(trader)
            st.success("Selected stocks bought")

else:
    st.info("Run screening to see candidates")


# ==========================================================
# OPEN POSITIONS — LIVE PNL
# ==========================================================
st.subheader("📈 Open Positions — Live PnL")

rows = []
total_pnl = 0

for s, pos in trader.positions.items():

    live = prices.get(s) or pos["entry"]

    if live > pos["high"]:
        pos["high"] = live

    pnl = (live - pos["entry"]) * pos["qty"]
    total_pnl += pnl

    rows.append({
        "Stock": s,
        "Entry ₹": round(pos["entry"], 2),
        "High ₹": round(pos["high"], 2),
        "Trail ₹": round(pos["high"] * (1 - TRAIL_PCT), 2),
        "Live ₹": round(live, 2),
        "Qty": pos["qty"],
        "PnL ₹": round(pnl, 2)
    })


def pnl_color(val):
    if val > 0:
        return "background-color: rgba(0,255,120,.18)"
    if val < 0:
        return "background-color: rgba(255,60,60,.20)"
    return ""


if rows:

    df = pd.DataFrame(rows)

    st.dataframe(
        df.style.map(pnl_color, subset=["PnL ₹"]),
        use_container_width=True
    )

    st.metric("Total Live PnL ₹", round(total_pnl, 2))

else:
    st.info("No open positions")


# ==========================================================
# EXIT CONSOLE
# ==========================================================
st.subheader("🟠 Exit Console")

open_stocks = list(trader.positions.keys())

if open_stocks:

    col_a, col_b = st.columns(2)

    to_close = st.multiselect("Select positions to exit", open_stocks)

    with col_a:
        if st.button("❌ Exit Selected") and to_close:

            for s in to_close:
                pos = trader.positions[s]

                exit_price = prices.get(s, pos["entry"])
                qty = pos["qty"]
                pnl = (exit_price - pos["entry"]) * qty

                trader.sell(s, exit_price)
                log_trade("SELL", s, qty, exit_price, pnl)

            save_state(trader)
            st.success("Selected positions exited")

    with col_b:
        if st.button("🔥 Exit ALL Positions"):

            for s, pos in list(trader.positions.items()):

                exit_price = prices.get(s, pos["entry"])
                qty = pos["qty"]
                pnl = (exit_price - pos["entry"]) * qty

                trader.sell(s, exit_price)
                log_trade("SELL", s, qty, exit_price, pnl)

            save_state(trader)
            st.error("All positions exited")

else:
    st.info("No open positions")


# ==========================================================
# ANALYTICS TABS
# ==========================================================
tabs = st.tabs([
    "💰 Portfolio",
    "📒 Trades",
    "⚠️ Risk",
    "📈 Equity"
])


# ---------------- PORTFOLIO TAB ----------------
with tabs[0]:

    st.subheader("💰 Portfolio Summary")

    portfolio_value = trader.value(prices)

    st.metric("Portfolio Value ₹", round(portfolio_value, 2))
    st.metric("Available Cash ₹", round(trader.cash, 2))

    log_equity(portfolio_value)


# ---------------- TRADES TAB ----------------
with tabs[1]:

    st.subheader("📒 Trade Analytics")

    if st.button("Refresh Trade Analytics"):

        stats, closed = cache_trade_stats()

        if stats:

            col1, col2, col3 = st.columns(3)

            col1.metric("Total Trades", stats["Trades"])
            col2.metric("Win Rate %", round(stats["Win Rate %"], 2))
            col3.metric("Profit Factor", round(stats["Profit Factor"], 2))

            col1.metric("Avg Win ₹", round(stats["Avg Win ₹"], 2))
            col2.metric("Avg Loss ₹", round(stats["Avg Loss ₹"], 2))
            col3.metric("Total Profit ₹", round(stats["Total Profit ₹"], 2))

            st.dataframe(closed.tail(25))

        else:
            st.info("No closed trades yet")


# ---------------- RISK TAB ----------------
with tabs[2]:

    st.subheader("⚠️ Drawdown Analytics")

    df_dd = load_equity_curve()

    if df_dd is not None:

        drawdown = compute_drawdown(df_dd["value"])

        col1, col2 = st.columns(2)
        col1.metric("Max Drawdown (%)", round(drawdown.min()*100, 2))
        col2.metric("Current Drawdown (%)", round(drawdown.iloc[-1]*100, 2))

        st.line_chart(
            pd.DataFrame({"Drawdown": drawdown.values}, index=df_dd["time"])
        )

    else:
        st.info("Curve unavailable yet")


# ---------------- EQUITY TAB ----------------
with tabs[3]:

    st.subheader("📈 Equity Curve")

    df_perf = load_equity_curve()

    if df_perf is not None:

        st.line_chart(df_perf.set_index("time")["value"])

        cagr = compute_cagr(df_perf["value"], df_perf["time"]) * 100
        sharpe = compute_sharpe(df_perf["value"])

        col1, col2 = st.columns(2)
        col1.metric("CAGR (%)", round(cagr, 2))
        col2.metric("Sharpe Ratio", round(sharpe, 2))

    else:
        st.info("Equity curve will appear after first log")


# ==========================================================
# DEBUG
# ==========================================================
st.sidebar.subheader("⚠️ Missing Price Log")

if st.session_state.missing_price_log:
    st.sidebar.write(pd.DataFrame(st.session_state.missing_price_log).tail(20))
else:
    st.sidebar.write("All prices resolved successfully")

st.sidebar.subheader("📦 Persisted State")
st.sidebar.write(trader.positions)
st.sidebar.write("Cash:", trader.cash)