import matplotlib.pyplot as plt
from walk_forward import run_walk_forward
from load_prices import load_price_data

def main():
    print("📥 Loading historical price data...")
    price_dfs = load_price_data()

    print(f"✅ Loaded {len(price_dfs)} symbols")

    # ---- WALK-FORWARD PARAMETERS ----
    TRAIN_YEARS = 1      # start small (safe)
    TEST_MONTHS = 3
    REBALANCE_DAY = 2    # Wednesday
    TRAIL_PCT = 0.05

    print(
        f"🚶 Running walk-forward test | "
        f"Train={TRAIN_YEARS}y, Test={TEST_MONTHS}m"
    )

    try:
        df = run_walk_forward(
            price_dfs,
            train_years=TRAIN_YEARS,
            test_months=TEST_MONTHS,
            rebalance_day=REBALANCE_DAY,
            trail_pct=TRAIL_PCT
        )
    except Exception as e:
        print("❌ Walk-forward failed:")
        print(e)
        return

    # ---- RESULTS ----
    final_value = df["Value"].iloc[-1]
    max_dd = df["Drawdown"].min() * 100

    print("\n📊 WALK-FORWARD RESULTS")
    print("----------------------")
    print(f"Final Portfolio Value : {round(final_value, 2)}")
    print(f"Max Drawdown (%)      : {round(max_dd, 2)}")

    # ---- EQUITY CURVE ----
    plt.figure(figsize=(12, 5))
    plt.plot(df["Date"], df["Value"])
    plt.title("Walk-Forward Equity Curve")
    plt.xlabel("Date")
    plt.ylabel("Portfolio Value")
    plt.grid(True)
    plt.show()

    # ---- DRAWDOWN ----
    plt.figure(figsize=(12, 3))
    plt.plot(df["Date"], df["Drawdown"])
    plt.title("Walk-Forward Drawdown")
    plt.xlabel("Date")
    plt.ylabel("Drawdown")
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    main()