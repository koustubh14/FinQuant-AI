import pandas as pd
from app.analytics.returns import valid_prices
from pydantic import BaseModel


class BenchmarkResult(BaseModel):
    symbol: str
    observations: int
    beta: float | None
    correlation: float | None
    asset_return: float
    benchmark_return: float
    relative_return: float
    series: list[dict]
    methodology: str


def compare(asset: pd.Series, benchmark: pd.Series, symbol: str) -> BenchmarkResult:
    valid_prices(asset)
    valid_prices(benchmark)
    # Calculate returns only after price alignment: both spans have identical endpoints.
    aligned = pd.concat([asset.rename("asset"), benchmark.rename("benchmark")], axis=1).dropna()
    if len(aligned) < 30:
        raise ValueError("At least 30 common sessions needed for benchmark comparison.")
    returns = aligned.pct_change(fill_method=None).iloc[1:]
    variance = returns.benchmark.var(ddof=1)
    beta = float(returns.asset.cov(returns.benchmark) / variance) if variance > 1e-16 else None
    corr = (
        float(returns.asset.corr(returns.benchmark))
        if variance > 1e-16 and returns.asset.var() > 1e-16
        else None
    )
    normalized = aligned / aligned.iloc[0] - 1
    a, b = normalized.iloc[-1]
    return BenchmarkResult(
        symbol=symbol,
        observations=len(returns),
        beta=beta,
        correlation=corr,
        asset_return=float(a),
        benchmark_return=float(b),
        relative_return=float(a - b),
        series=[
            {
                "date": d.date().isoformat(),
                "asset": float(row.asset),
                "benchmark": float(row.benchmark),
            }
            for d, row in normalized.iterrows()
        ],
        methodology="Aligned session endpoints before returns; beta=cov(asset,benchmark)/var(benchmark). "
        "Relative return is percentage-point difference. Default benchmarks are price indices, "
        "whereas adjusted equity prices reflect distributions; comparison is not pure alpha.",
    )
