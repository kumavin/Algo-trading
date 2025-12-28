import pandas as pd
import os

def load_price_data(folder="data/prices"):
    """
    Loads historical price CSVs into a dictionary
    CSV format required: Date,Close
    """
    price_dfs = {}

    if not os.path.exists(folder):
        raise FileNotFoundError(f"Price folder not found: {folder}")

    for file in os.listdir(folder):
        if file.endswith(".csv"):
            symbol = file.replace(".csv", "")
            df = pd.read_csv(
                os.path.join(folder, file),
                parse_dates=["Date"]
            )

            if "Close" not in df.columns:
                continue

            price_dfs[symbol] = df

    if not price_dfs:
        raise ValueError("No valid price files loaded")

    return price_dfs