import numpy as np
import pandas as pd
from pydantic import BaseModel
from scipy.stats import kurtosis, shapiro, skew


class Diagnostic(BaseModel):
    name: str
    statistic: float | None
    p_value: float | None
    interpretation: str


class StatisticsResult(BaseModel):
    mean: float
    median: float
    variance: float
    standard_deviation: float
    skewness: float | None
    excess_kurtosis: float | None
    quantiles: dict[str, float]
    autocorrelation_lag1: float | None
    normality: Diagnostic
    histogram: list[dict[str, float | int]]


def describe(returns: pd.Series) -> StatisticsResult:
    values = np.asarray(returns, dtype=float)
    if len(values) < 8 or not np.isfinite(values).all():
        raise ValueError("At least eight finite returns required for diagnostics.")
    constant = np.std(values) < 1e-12
    if constant or len(values) > 5000:
        diagnostic = Diagnostic(
            name="Shapiro-Wilk",
            statistic=None,
            p_value=None,
            interpretation="Not run: constant returns or sample exceeds 5000.",
        )
    else:
        stat, p = shapiro(values)
        diagnostic = Diagnostic(
            name="Shapiro-Wilk",
            statistic=float(stat),
            p_value=float(p),
            interpretation=(
                "Reject normality at 5%."
                if p < 0.05
                else "Do not reject normality at 5%; this does not prove normality."
            )
            + " Tail-risk diagnostic; p-value assumes independent observations, which market returns may violate.",
        )
    counts, edges = np.histogram(values, bins=24)
    return StatisticsResult(
        mean=float(values.mean()),
        median=float(np.median(values)),
        variance=float(values.var(ddof=1)),
        standard_deviation=float(values.std(ddof=1)),
        skewness=None if constant else float(skew(values, bias=False)),
        excess_kurtosis=None if constant else float(kurtosis(values, fisher=True, bias=False)),
        quantiles={
            str(q): float(np.quantile(values, q)) for q in [0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99]
        },
        autocorrelation_lag1=None
        if np.std(values[:-1]) < 1e-12 or np.std(values[1:]) < 1e-12
        else float(pd.Series(values).autocorr(1)),
        normality=diagnostic,
        histogram=[
            {"return": float((edges[i] + edges[i + 1]) / 2), "count": int(n)}
            for i, n in enumerate(counts)
        ],
    )
