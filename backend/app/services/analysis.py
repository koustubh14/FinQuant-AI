import hashlib
import importlib.metadata
import json
import math
import time
from datetime import datetime, timezone
from typing import Protocol
from uuid import uuid4

import numpy as np
from app import __version__
from app.ai.analyst import interpret
from app.analytics import benchmarks, returns, statistics
from app.core.config import Settings
from app.core.exceptions import AnalysisError
from app.data.market_data import MarketBundle
from app.data.ticker import default_benchmark, resolve
from app.data.validation import validate_history
from app.forecasting.validation import evaluate
from app.recommendation.engine import recommend
from app.risk import metrics as risk_metrics
from app.schemas.analysis import AnalysisResult, AnalyzeRequest, Company, PricePoint, Provenance


class MarketProvider(Protocol):
    def search(self, query: str) -> list[dict]: ...
    def fetch(self, symbol: str, period: str, optional: bool = True) -> MarketBundle: ...


def number(value) -> float | None:
    try:
        result = float(value)
        return result if math.isfinite(result) else None
    except (TypeError, ValueError):
        return None


def analyze(request: AnalyzeRequest, provider: MarketProvider, config: Settings) -> AnalysisResult:
    started = time.perf_counter()
    symbol = resolve(request.symbol, provider.search)
    bundle = provider.fetch(symbol, request.period)
    minimum = max(160, 120 + 4 * request.forecast_horizon)
    frame, quality = validate_history(bundle.history, minimum=minimum)
    prices = frame["Adj Close"]
    stats = statistics.describe(returns.simple_returns(prices))
    ret = returns.summarize(prices)
    risk = risk_metrics.summarize(prices, request.annual_risk_free)
    forecast = evaluate(prices, request.forecast_horizon)
    warnings = list(bundle.warnings) + quality.warnings
    benchmark = None
    benchmark_symbol = (
        resolve(request.benchmark) if request.benchmark else default_benchmark(symbol)
    )
    if benchmark_symbol:
        try:
            other = provider.fetch(benchmark_symbol, request.period, optional=False)
            other_frame, other_quality = validate_history(other.history, minimum=30)
            if other_quality.stale_days > 7:
                raise ValueError("Stale benchmark")
            benchmark = benchmarks.compare(prices, other_frame["Adj Close"], benchmark_symbol)
        except AnalysisError as exc:
            if exc.code == "invalid_data":
                warnings.append(
                    "Benchmark analysis unavailable because benchmark data failed quality validation. Relative signals omitted."
                )
            else:
                warnings.append("Benchmark provider unavailable; relative signals omitted.")
        except ValueError:
            warnings.append(
                "Benchmark analysis unavailable because dates, freshness or aligned history failed validation. Relative signals omitted."
            )
    else:
        warnings.append(
            "No default benchmark for this listing; supply one explicitly if appropriate."
        )
    recommendation = recommend(
        prices,
        ret.annualized_volatility,
        risk.maximum_drawdown,
        forecast.predictions[-1]["value"] / float(prices.iloc[-1]) - 1,
        benchmark.relative_return if benchmark else None,
        quality.stale_days > 7,
    )
    metadata = bundle.metadata
    company = Company(
        symbol=symbol,
        name=metadata.get("longName") or metadata.get("shortName") or symbol,
        exchange=metadata.get("exchange"),
        currency=metadata.get("currency"),
        sector=metadata.get("sector"),
        industry=metadata.get("industry"),
        market_cap=number(metadata.get("marketCap")),
        trailing_pe=number(metadata.get("trailingPE")),
        forward_pe=number(metadata.get("forwardPE")),
        price_to_book=number(metadata.get("priceToBook")),
        revenue_growth=number(metadata.get("revenueGrowth")),
        return_on_equity=number(metadata.get("returnOnEquity")),
        latest_close=float(frame.Close.iloc[-1]),
        adjusted_close=float(prices.iloc[-1]),
        daily_change=float(frame.Close.iloc[-1] / frame.Close.iloc[-2] - 1),
    )
    rolling = returns.rolling(prices)
    simple = prices.pct_change(fill_method=None)
    logs = np.log(prices).diff()
    history = [
        PricePoint(
            date=d.date().isoformat(),
            open=float(row.Open),
            high=float(row.High),
            low=float(row.Low),
            close=float(row.Close),
            adjusted_close=float(row["Adj Close"]),
            volume=float(row.Volume),
            daily_return=number(simple.loc[d]),
            log_return=number(logs.loc[d]),
            cumulative_return=float(prices.loc[d] / prices.iloc[0] - 1),
            **{k: number(v) for k, v in rolling.loc[d].items()},
        )
        for d, row in frame.iterrows()
    ]
    digest = hashlib.sha256(
        json.dumps([p.model_dump() for p in history], sort_keys=True, allow_nan=False).encode()
    ).hexdigest()
    ai_payload = {
        "company": company.model_dump(),
        "returns": ret.model_dump(),
        "risk": risk.model_dump(),
        "statistics": stats.model_dump(exclude={"histogram"}),
        "forecast": forecast.model_dump(exclude={"folds", "predictions"}),
        "recommendation": recommendation.model_dump(),
        "news": bundle.news,
    }
    narrative = interpret(ai_payload, config, request.include_ai)
    return AnalysisResult(
        analysis_id=str(uuid4()),
        generated_at=datetime.now(timezone.utc).isoformat(),
        parameters=request,
        company=company,
        quality=quality,
        returns=ret,
        risk=risk,
        statistics=stats,
        benchmark=benchmark,
        forecast=forecast,
        recommendation=recommendation,
        history=history,
        news=bundle.news,
        interpretation=narrative,
        warnings=warnings,
        provenance=Provenance(
            fetched_at=bundle.fetched_at,
            cached=bundle.cached,
            input_sha256=digest,
            versions={
                "finquant": __version__,
                **{
                    p: importlib.metadata.version(p)
                    for p in ["numpy", "pandas", "scipy", "scikit-learn", "yfinance"]
                },
            },
            duration_seconds=round(time.perf_counter() - started, 4),
            assumptions=[
                "Raw OHLCV displayed; adjusted close used for returns, risk and model outputs.",
                "Provider-adjusted history is not point-in-time; corporate-action revisions can change results.",
                "No exchange calendar or currency conversion. Latest daily bar may still be in progress.",
                "Financial ratios are provider snapshots, not audited valuation estimates.",
                "The optional AI narrative is unverified interpretation; structured Python output is authoritative.",
            ],
        ),
    )
