import pandas as pd

def compute_drawdown(equity_series):
    """
    equity_series: pandas Series of portfolio values
    returns: drawdown series
    """
    peak = equity_series.cummax()
    drawdown = (equity_series - peak) / peak
    return drawdown