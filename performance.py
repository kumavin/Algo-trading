import numpy as np
import pandas as pd

def compute_cagr(equity_series, dates):
    """
    equity_series: pandas Series of portfolio values
    dates: pandas Series of datetime
    """
    start_value = equity_series.iloc[0]
    end_value = equity_series.iloc[-1]

    days = (dates.iloc[-1] - dates.iloc[0]).days
    years = days / 365.25

    if years <= 0:
        return 0.0

    cagr = (end_value / start_value) ** (1 / years) - 1
    return cagr


def compute_sharpe(equity_series, rf=0.0):
    """
    rf: risk-free rate (annual), default 0 for simplicity
    """
    returns = equity_series.pct_change().dropna()

    if returns.std() == 0:
        return 0.0

    sharpe = ((returns.mean() * 252) - rf) / (returns.std() * np.sqrt(252))
    return sharpe