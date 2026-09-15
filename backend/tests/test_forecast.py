import numpy as np
import pytest
from app.forecasting.metrics import score
from app.forecasting.models import predict
from app.forecasting.validation import evaluate
from app.recommendation.engine import recommend


def test_forecast_errors_known():
    metrics = score([100, 110], [102, 106], [99, 109])
    assert metrics.mae == 3
    assert metrics.rmse == pytest.approx(np.sqrt(10))
    assert metrics.mape == pytest.approx((0.02 + 4 / 110) / 2)
    assert metrics.directional_accuracy == 0.5
    assert score([0], [1], [0]).mape is None
    with pytest.raises(ValueError):
        score([], [], [])
    with pytest.raises(ValueError):
        score([1], [np.nan], [1])


def test_baselines():
    p = np.arange(100.0, 140.0)
    np.testing.assert_allclose(predict("naive", p, 4), [139] * 4)
    np.testing.assert_allclose(predict("moving_average", p, 4), [129.5] * 4)
    np.testing.assert_allclose(predict("ridge_lags", np.ones(100) * 42, 5), [42] * 5)


def test_temporal_separation_and_selection_no_future(history):
    prices = history["Adj Close"]
    first = evaluate(prices, 30)
    changed = prices.copy()
    changed.loc[first.holdout_start :] *= 1.5
    second = evaluate(changed, 30)
    assert first.selected_model == second.selected_model
    for a, b in zip(first.folds, second.folds):
        assert a["train_end"] < a["test_start"] <= a["test_end"]
        if a["phase"] == "validation":
            assert a == b
    # At the first holdout origin, none of the changed observations is yet available.
    k = next(i for i, f in enumerate(first.folds) if f["phase"] == "holdout")
    assert first.folds[k]["predictions"] == second.folds[k]["predictions"]
    assert len(first.predictions) == 30


def test_short_horizon_requirement(history):
    with pytest.raises(ValueError, match="Need at least"):
        evaluate(history["Adj Close"].iloc[:200], 60)


def test_recommendation_and_stale_override(history):
    import pandas as pd

    rising = pd.Series(np.linspace(100.0, 160.0, 100))
    result = recommend(rising, 0.15, -0.1, 0.1, 0.2)
    assert result.action == "BUY"
    assert result.signal_agreement == 0.8
    assert recommend(rising, 0.15, -0.1, 0.1, 0.2, stale=True).action == "HOLD"
    falling = pd.Series(np.linspace(160.0, 80.0, 100))
    assert recommend(falling, 0.5, -0.5, -0.1, -0.2).action == "SELL"
    flat = pd.Series(np.ones(100) * 100)
    neutral = recommend(flat, 0.1, 0, 0)
    assert neutral.action == "HOLD"
    assert neutral.signal_agreement == 1
    assert neutral.signals[-1].score is None
