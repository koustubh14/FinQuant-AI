import numpy as np
import pandas as pd
import pytest
from app.core.exceptions import AnalysisError
from app.data.ticker import default_benchmark, resolve
from app.data.validation import validate_history


@pytest.mark.parametrize(
    "query,expected",
    [
        ("Apple", "AAPL"),
        ("Reliance", "RELIANCE.NS"),
        ("HDFC Bank", "HDFCBANK.NS"),
        ("msft", "MSFT"),
        ("INFY.NS", "INFY.NS"),
    ],
)
def test_resolution(query, expected):
    assert resolve(query) == expected


@pytest.mark.parametrize("query", ["", " ", "../secrets", "<script>"])
def test_invalid_query(query):
    with pytest.raises(AnalysisError):
        resolve(query)


def test_ambiguity():
    with pytest.raises(AnalysisError, match="Ambiguous"):
        resolve(
            "Example Company",
            lambda _: [{"symbol": s, "quoteType": "EQUITY"} for s in ["EX", "EX.NS"]],
        )
    assert default_benchmark("RELIANCE.NS") == "^NSEI"
    assert default_benchmark("AAPL") == "^GSPC"
    assert default_benchmark("VOD.L") is None


def test_quality_and_timezone(history):
    history.index = history.index.tz_localize("Asia/Kolkata")
    result, quality = validate_history(history)
    assert result.index[0].date() == history.index[0].date()
    assert np.isfinite(result.to_numpy()).all()
    assert quality.stale_days > 7
    assert quality.rows == 520


@pytest.mark.parametrize(
    "kind",
    [
        "empty",
        "short",
        "column",
        "duplicate",
        "reverse",
        "nan",
        "zero",
        "negative",
        "infinite",
        "bounds",
        "nat",
        "volume",
    ],
)
def test_malformed_history(history, kind):
    if kind == "empty":
        history = history.iloc[:0]
    if kind == "short":
        history = history.iloc[:10]
    if kind == "column":
        history = history.drop(columns="Close")
    if kind == "duplicate":
        history = pd.concat([history, history.iloc[-1:]])
    if kind == "reverse":
        history = history.iloc[::-1]
    if kind == "nan":
        history.iloc[4, 3] = np.nan
    if kind == "zero":
        history.iloc[4, 3] = 0
    if kind == "negative":
        history.iloc[4, 3] = -1
    if kind == "infinite":
        history.iloc[4, 3] = np.inf
    if kind == "bounds":
        history.iloc[4, 1] = 0.01
    if kind == "nat":
        history.index = pd.DatetimeIndex([pd.NaT] + list(history.index[1:]))
    if kind == "volume":
        history.iloc[4, 5] = -1
    with pytest.raises(AnalysisError):
        validate_history(history)


def test_missing_weekday_is_reported_not_filled(history):
    result, report = validate_history(history.drop(history.index[5]))
    assert len(result) == 519
    assert report.possible_missing_weekdays == 1


def test_empty_trailing_placeholder_is_explicitly_excluded(history):
    history.iloc[-1, :5] = np.nan
    history.iloc[-1, 5] = 0
    result, report = validate_history(history)
    assert len(result) == 519
    assert any("Excluded trailing empty" in warning for warning in report.warnings)
    history.iloc[30, :5] = np.nan
    history.iloc[30, 5] = 0
    with pytest.raises(AnalysisError):
        validate_history(history)


@pytest.mark.parametrize("kind", ["partial", "duplicate", "future", "multiple"])
def test_placeholder_exclusion_does_not_mask_other_errors(history, kind):
    history.iloc[-1, :5] = np.nan
    history.iloc[-1, 5] = 0
    if kind == "partial":
        history.iloc[-1, 3] = 100
    elif kind == "duplicate":
        history.index = pd.DatetimeIndex([*history.index[:-1], history.index[-2]])
    elif kind == "future":
        history.index = pd.DatetimeIndex([*history.index[:-1], pd.Timestamp("2099-01-01")])
    elif kind == "multiple":
        history.iloc[-2, :5] = np.nan
        history.iloc[-2, 5] = 0
    with pytest.raises(AnalysisError):
        validate_history(history)
