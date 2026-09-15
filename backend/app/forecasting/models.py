import numpy as np
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

MODELS = {
    "naive": "Last observed adjusted close at every horizon step",
    "moving_average": "Trailing 20 adjusted closes, constant forecast",
    "ridge_lags": "Ridge(alpha=10) on five lagged log returns; train-only scaling; recursive multi-step forecast",
}


def predict(name: str, prices: np.ndarray, horizon: int) -> np.ndarray:
    prices = np.asarray(prices, dtype=float)
    if len(prices) < 30 or horizon < 1 or not np.isfinite(prices).all() or (prices <= 0).any():
        raise ValueError("Forecast needs 30 positive prices and a positive horizon.")
    if name == "naive":
        return np.repeat(prices[-1], horizon)
    if name == "moving_average":
        return np.repeat(prices[-20:].mean(), horizon)
    if name != "ridge_lags":
        raise ValueError("Unknown forecasting model.")
    returns = np.diff(np.log(prices))
    lags = 5
    features = np.array([returns[t - lags : t] for t in range(lags, len(returns))])
    target = returns[lags:]
    model = make_pipeline(StandardScaler(), Ridge(alpha=10.0))
    model.fit(features, target)
    recent = list(returns[-lags:])
    output = []
    value = prices[-1]
    for _ in range(horizon):
        r = float(model.predict(np.array(recent[-lags:]).reshape(1, -1))[0])
        value *= np.exp(r)
        recent.append(r)
        output.append(value)
    result = np.asarray(output)
    if not np.isfinite(result).all() or (result <= 0).any():
        raise ValueError("Model produced invalid prices.")
    return result
