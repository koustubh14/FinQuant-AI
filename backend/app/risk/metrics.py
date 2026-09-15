import numpy as np
import pandas as pd
from app.analytics.returns import simple_returns, valid_prices
from pydantic import BaseModel
from scipy.stats import norm


def _returns(values: pd.Series) -> np.ndarray:
    result = np.asarray(values, dtype=float)
    if len(result) < 2 or not np.isfinite(result).all() or (result <= -1).any():
        raise ValueError("At least two finite simple returns greater than -1 required.")
    return result


def downside_deviation(returns: pd.Series, annual_target: float = 0) -> float:
    if annual_target <= -1:
        raise ValueError("Annual target must exceed -1.")
    daily = (1 + annual_target) ** (1 / 252) - 1
    excess = _returns(returns) - daily
    return float(np.sqrt(np.mean(np.minimum(excess, 0) ** 2)) * np.sqrt(252))


def sharpe(returns: pd.Series, annual_risk_free: float = 0) -> float | None:
    if annual_risk_free <= -1:
        raise ValueError("Risk-free rate must exceed -1.")
    values = _returns(returns)
    daily = (1 + annual_risk_free) ** (1 / 252) - 1
    volatility = np.std(values, ddof=1)
    return (
        float((values.mean() - daily) / volatility * np.sqrt(252)) if volatility > 1e-12 else None
    )


def sortino(returns: pd.Series, annual_target: float = 0) -> float | None:
    values = _returns(returns)
    downside = downside_deviation(returns, annual_target)
    daily = (1 + annual_target) ** (1 / 252) - 1
    return float((values.mean() - daily) * 252 / downside) if downside > 1e-12 else None


def maximum_drawdown(prices: pd.Series) -> float:
    values = valid_prices(prices)
    return float((values / values.cummax() - 1).min())


def historical_tail(returns: pd.Series, confidence: float = 0.95) -> tuple[float, float]:
    """Linear empirical loss quantile; ES averages all losses at/above it (ties included)."""
    if not 0 < confidence < 1:
        raise ValueError("Confidence must be strictly between zero and one.")
    losses = -_returns(returns)
    var = float(np.quantile(losses, confidence, method="linear"))
    es = float(losses[losses >= var].mean())
    return max(0.0, var), max(0.0, es)


def parametric_var(returns: pd.Series, confidence: float = 0.95) -> float:
    if not 0 < confidence < 1:
        raise ValueError("Confidence must be strictly between zero and one.")
    values = _returns(returns)
    return max(0.0, float(-values.mean() + norm.ppf(confidence) * values.std(ddof=1)))


class RiskMetrics(BaseModel):
    downside_deviation: float
    maximum_drawdown: float
    sharpe: float | None
    sortino: float | None
    historical_var_95: float
    expected_shortfall_95: float
    normal_var_95: float
    annual_risk_free: float
    level: str
    assumptions: list[str]


def summarize(prices: pd.Series, annual_risk_free: float = 0) -> RiskMetrics:
    returns = simple_returns(prices)
    var, es = historical_tail(returns)
    vol = returns.std(ddof=1) * np.sqrt(252)
    return RiskMetrics(
        downside_deviation=downside_deviation(returns, annual_risk_free),
        maximum_drawdown=maximum_drawdown(prices),
        sharpe=sharpe(returns, annual_risk_free),
        sortino=sortino(returns, annual_risk_free),
        historical_var_95=var,
        expected_shortfall_95=es,
        normal_var_95=parametric_var(returns),
        annual_risk_free=annual_risk_free,
        level="High" if vol >= 0.4 else "Moderate" if vol >= 0.2 else "Low",
        assumptions=[
            "252 sessions/year; sample standard deviation; risk-free rate is user supplied (default zero).",
            "Daily VaR/ES are positive loss fractions floored at zero; linear quantile and tail ties included.",
            "Normal VaR is a comparison under a Gaussian assumption, not a validated tail model.",
            "Risk labels use annual volatility cutoffs 20%/40%, not suitability or loss probabilities.",
            "Square-root time scaling ignores serial dependence; ratios are descriptive, not guarantees.",
        ],
    )
