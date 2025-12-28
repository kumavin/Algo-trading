import numpy as np
from hmmlearn.hmm import GaussianHMM

def detect_regime(returns, vol):
    X = np.column_stack([returns[-len(vol):], vol])
    model = GaussianHMM(n_components=3, n_iter=200)
    model.fit(X)

    probs = model.predict_proba(X)[-1]
    order = np.argsort(model.means_[:,0])

    mapping = {
        order[0]: "BEAR",
        order[1]: "NEUTRAL",
        order[2]: "BULL"
    }

    return mapping[np.argmax(probs)], {
        mapping[i]: probs[i] for i in mapping
    }