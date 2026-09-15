"""Recompute numerical outputs from a downloaded result, without network or LLM."""

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from app.analytics import returns, statistics
from app.forecasting.validation import evaluate
from app.recommendation.engine import recommend
from app.risk import metrics


def replay(path: Path) -> dict:
    result = json.loads(path.read_text(encoding="utf-8"))
    history = result["history"]
    digest = hashlib.sha256(
        json.dumps(history, sort_keys=True, allow_nan=False).encode()
    ).hexdigest()
    if digest != result["provenance"]["input_sha256"]:
        raise ValueError("Input fingerprint does not match the stored snapshot.")
    prices = pd.Series(
        [row["adjusted_close"] for row in history],
        index=pd.to_datetime([row["date"] for row in history]),
    )
    ret = returns.summarize(prices).model_dump()
    risk = metrics.summarize(prices, result["parameters"]["annual_risk_free"]).model_dump()
    stats = statistics.describe(returns.simple_returns(prices)).model_dump()
    forecast = evaluate(prices, result["parameters"]["forecast_horizon"]).model_dump()

    def check(actual, expected):
        if isinstance(actual, dict):
            for key in actual:
                check(actual[key], expected[key])
        elif isinstance(actual, list):
            if len(actual) != len(expected):
                raise AssertionError("Length mismatch")
            for a, b in zip(actual, expected):
                check(a, b)
        elif isinstance(actual, (float, int)) and not isinstance(actual, bool):
            np.testing.assert_allclose(actual, expected, rtol=1e-9, atol=1e-10)
        elif actual != expected:
            raise AssertionError(f"Mismatch: {actual!r} != {expected!r}")

    check(ret, result["returns"])
    check(risk, result["risk"])
    check(stats, result["statistics"])
    check(forecast, result["forecast"])
    recommendation = recommend(
        prices,
        ret["annualized_volatility"],
        risk["maximum_drawdown"],
        forecast["predictions"][-1]["value"] / float(prices.iloc[-1]) - 1,
        result["benchmark"]["relative_return"] if result["benchmark"] else None,
        result["quality"]["stale_days"] > 7,
    ).model_dump()
    check(recommendation, result["recommendation"])
    return {
        "symbol": result["company"]["symbol"],
        "input_sha256": digest,
        "recomputed": ["returns", "risk", "statistics", "forecast", "recommendation"],
        "benchmark_note": "Recommendation reuses saved relative-return context; benchmark covariance not replayed.",
        "status": "matched",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("snapshot", type=Path)
    print(json.dumps(replay(parser.parse_args().snapshot), indent=2))
