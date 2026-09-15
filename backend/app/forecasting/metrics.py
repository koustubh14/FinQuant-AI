import numpy as np
from pydantic import BaseModel


class ForecastMetrics(BaseModel):
    mae: float
    rmse: float
    mape: float | None
    directional_accuracy: float


def score(actual, predicted, origins) -> ForecastMetrics:
    a, p, o = (np.asarray(x, dtype=float) for x in (actual, predicted, origins))
    if a.size == 0 or a.shape != p.shape or a.shape != o.shape:
        raise ValueError("Nonempty matching arrays required.")
    if not all(np.isfinite(x).all() for x in (a, p, o)):
        raise ValueError("Forecast metrics require finite values.")
    errors = p - a
    return ForecastMetrics(
        mae=float(np.abs(errors).mean()),
        rmse=float(np.sqrt((errors**2).mean())),
        mape=float(np.mean(np.abs(errors / a))) if (a > 1e-12).all() else None,
        directional_accuracy=float(np.mean(np.sign(p - o) == np.sign(a - o))),
    )
