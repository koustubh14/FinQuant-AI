import pandas as pd
from app.analytics.returns import valid_prices
from app.forecasting.metrics import ForecastMetrics, score
from app.forecasting.models import MODELS, predict
from pydantic import BaseModel


class ModelEvaluation(BaseModel):
    validation: ForecastMetrics
    holdout: ForecastMetrics


class ForecastResult(BaseModel):
    selected_model: str
    baseline_model: str = "naive"
    horizon: int
    training_start: str
    training_end: str
    validation_start: str
    validation_end: str
    holdout_start: str
    holdout_end: str
    selection_training_end: str
    models: dict[str, ModelEvaluation]
    folds: list[dict]
    predictions: list[dict]
    selected_beats_naive_holdout: bool
    methodology: str
    limitations: list[str]


def evaluate(prices: pd.Series, horizon: int = 30) -> ForecastResult:
    values = valid_prices(prices).to_numpy()
    if not 1 <= horizon <= 60:
        raise ValueError("Horizon must be 1–60 sessions.")
    # Keep runtime bounded and evaluate at most twelve non-overlapping origins.
    count = min(12, (len(values) - 120) // horizon)
    if count < 4:
        raise ValueError(
            f"Need at least {120 + 4 * horizon} prices for four {horizon}-session folds."
        )
    start = len(values) - count * horizon
    split = count // 2
    dates = prices.index.strftime("%Y-%m-%d")
    folds = []
    buffers = {
        name: {phase: {"a": [], "p": [], "o": []} for phase in ("validation", "holdout")}
        for name in MODELS
    }
    selected = None
    for i, origin in enumerate(range(start, len(values) - horizon + 1, horizon)):
        if i == split:
            # Selection is finalized before any holdout targets are scored.
            selected = min(
                MODELS,
                key=lambda name: (
                    score(
                        **{
                            "actual": buffers[name]["validation"]["a"],
                            "predicted": buffers[name]["validation"]["p"],
                            "origins": buffers[name]["validation"]["o"],
                        }
                    ).rmse
                ),
            )
        phase = "validation" if i < split else "holdout"
        actual = values[origin : origin + horizon]
        predictions = {}
        for name in MODELS:
            forecast = predict(name, values[:origin], horizon)
            buf = buffers[name][phase]
            buf["a"].extend(actual.tolist())
            buf["p"].extend(forecast.tolist())
            buf["o"].extend([float(values[origin - 1])] * horizon)
            predictions[name] = forecast.tolist()
        folds.append(
            {
                "phase": phase,
                "train_end": dates[origin - 1],
                "test_start": dates[origin],
                "test_end": dates[origin + horizon - 1],
                "origin_price": float(values[origin - 1]),
                "actual": actual.tolist(),
                "predictions": predictions,
            }
        )
    evaluations = {
        name: ModelEvaluation(
            **{phase: score(buf["a"], buf["p"], buf["o"]) for phase, buf in phases.items()}
        )
        for name, phases in buffers.items()
    }
    final = predict(selected, values, horizon)
    future_dates = pd.bdate_range(prices.index[-1] + pd.offsets.BDay(), periods=horizon)
    return ForecastResult(
        selected_model=selected,
        horizon=horizon,
        training_start=dates[0],
        training_end=dates[-1],
        selection_training_end=folds[0]["train_end"],
        validation_start=folds[0]["test_start"],
        validation_end=folds[split - 1]["test_end"],
        holdout_start=folds[split]["test_start"],
        holdout_end=folds[-1]["test_end"],
        models=evaluations,
        folds=folds,
        predictions=[
            {"step": i + 1, "date": d.date().isoformat(), "value": float(v)}
            for i, (d, v) in enumerate(zip(future_dates, final))
        ],
        selected_beats_naive_holdout=evaluations[selected].holdout.rmse
        < evaluations["naive"].holdout.rmse,
        methodology="Expanding-window, non-overlapping full-horizon folds. First half selects lowest pooled "
        "validation RMSE; model identity locked before remaining holdout folds. Refit at each "
        "origin using only observed prices; final forecast refits all history. Fixed hyperparameters.",
        limitations=[
            "Forecast units are adjusted prices, not a guaranteed future traded quote.",
            "No prediction interval: coverage has not been calibrated. Error scores are not intervals.",
            "Future dates are weekday estimates, not exchange-calendar sessions.",
            "Small holdout sample; overlapping horizons within each fold are dependent.",
            "Directional accuracy compares each step with its origin; flat naive forecasts usually score zero.",
            "Adjusted historical data may be revised by the provider; this is not point-in-time trading research.",
        ],
    )
