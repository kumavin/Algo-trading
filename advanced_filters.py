import numpy as np
from sklearn.linear_model import LinearRegression


def momentum_score(prices):
    """6m + 3m + 1m momentum blend"""

    if len(prices) < 180:
        return -999

    p = prices

    r1 = p[-21] / p[-63] - 1      # 1–3 month
    r3 = p[-63] / p[-126] - 1     # 3–6 month
    r6 = p[-126] / p[-180] - 1    # 6m

    return (r1 + r3 + r6) / 3


def trend_slope(prices, window=60):
    """Measures smooth trend persistence"""

    if len(prices) < window:
        return -999

    y = np.log(prices[-window:])
    x = np.arange(len(y)).reshape(-1, 1)

    model = LinearRegression().fit(x, y)

    return model.coef_[0]   # slope


def pullback_quality(prices, window=30):
    """Prefer shallow pullbacks (trend continuation bias)"""

    if len(prices) < window:
        return -999

    p = np.array(prices[-window:])

    returns = np.diff(np.log(p))

    downside = np.std(returns[returns < 0])
    upside = np.std(returns[returns > 0])

    if downside == 0:
        return 1

    return upside / downside