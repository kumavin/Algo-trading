import numpy as np

def momentum(prices):
    if len(prices) < 60:
        return 0
    return prices[-1] / prices[-60] - 1


def sharpe_ratio(returns, rf=0.06):
    if len(returns) < 20 or np.std(returns) == 0:
        return 0
    return (np.mean(returns)*252 - rf) / (np.std(returns)*np.sqrt(252))


def composite_score(prices):
    r = np.diff(np.log(prices))
    return 0.6 * momentum(prices) + 0.4 * sharpe_ratio(r)