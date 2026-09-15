import numpy as np
import pandas as pd
import pytest
from app.analytics import benchmarks, returns, statistics
from app.risk.metrics import downside_deviation, historical_tail, maximum_drawdown, sharpe, sortino


def test_returns_known_values():
    p = pd.Series([100.0, 110.0, 99.0])
    np.testing.assert_allclose(returns.simple_returns(p), [0.1, -0.1])
    np.testing.assert_allclose(returns.log_returns(p), np.log([1.1, 0.9]))
    np.testing.assert_allclose(returns.cumulative_returns(p), [0, 0.1, -0.01])
    assert returns.annualized_return(p, sessions=2) == pytest.approx(-0.01)
    assert returns.annualized_volatility(pd.Series([0.1, -0.1]), sessions=2) == pytest.approx(0.2)


def test_risk_known_values():
    r = pd.Series([0.02, -0.01, 0.03, -0.04])
    assert downside_deviation(r) == pytest.approx(np.sqrt(0.0017 / 4 * 252))
    assert sharpe(r) == pytest.approx(0.0, abs=1e-12)
    assert sortino(r) == pytest.approx(0.0, abs=1e-12)
    var, es = historical_tail(r, 0.75)
    assert var == pytest.approx(0.0175)
    assert es == pytest.approx(0.04)
    assert maximum_drawdown(pd.Series([100.0, 120.0, 90.0, 108.0])) == pytest.approx(-0.25)


def test_ratios_nonzero_and_no_downside():
    r = pd.Series([0.01, -0.01, 0.02])
    mean = 0.02 / 3
    sample_sd = np.sqrt(((0.01 - mean) ** 2 + (-0.01 - mean) ** 2 + (0.02 - mean) ** 2) / 2)
    assert sharpe(r) == pytest.approx(mean / sample_sd * np.sqrt(252))
    assert sortino(r) == pytest.approx(mean * 252 / np.sqrt(0.0001 / 3 * 252))
    assert sharpe(pd.Series([0.01] * 10)) is None
    assert sortino(pd.Series([0.01] * 10)) is None
    assert historical_tail(pd.Series([0.01] * 10)) == (0, 0)


def test_beta_known_two():
    idx = pd.bdate_range("2024-01-01", periods=80)
    rb = 0.01 * np.sin(np.arange(79))
    b = pd.Series(np.r_[100, 100 * np.cumprod(1 + rb)], index=idx)
    a = pd.Series(np.r_[100, 100 * np.cumprod(1 + 2 * rb)], index=idx)
    result = benchmarks.compare(a, b, "TEST")
    assert result.beta == pytest.approx(2)
    assert result.correlation == pytest.approx(1)


def test_benchmark_mismatched_sessions(history):
    prices = history["Adj Close"]
    result = benchmarks.compare(prices, prices.drop(prices.index[30]), "TEST")
    assert result.beta == pytest.approx(1)
    assert result.relative_return == pytest.approx(0)


def test_constant_stats_and_rolling():
    result = statistics.describe(pd.Series([0.0] * 50))
    assert result.normality.p_value is None
    assert result.skewness is None
    roll = returns.rolling(pd.Series([100.0] * 50))
    assert roll.rolling_volatility.iloc[-1] == 0
    assert pd.isna(roll.moving_average.iloc[0])


@pytest.mark.parametrize("p", [[0, 1, 2], [1, np.nan, 3], [1, 2], [1, np.inf, 3]])
def test_invalid_prices(p):
    with pytest.raises(ValueError):
        returns.simple_returns(pd.Series(p))


def test_autocorrelation_with_constant_lag_window():
    result = statistics.describe(pd.Series([0.0] * 49 + [0.1]))
    assert result.autocorrelation_lag1 is None
