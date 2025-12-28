import numpy as np

def allocate_capital(cash, buy_list, price_history):
    """
    - Use 70% capital
    - Volatility adjusted allocation
    """
    if not buy_list:
        return {}

    deployable = cash * 0.7

    vols = {}
    for s in buy_list:
        prices = price_history[s]
        returns = np.diff(np.log(prices))
        vols[s] = np.std(returns)

    inv_vol_sum = sum(1 / v for v in vols.values() if v > 0)

    allocation = {}
    for s in buy_list:
        weight = (1 / vols[s]) / inv_vol_sum
        allocation[s] = deployable * weight

    return allocation