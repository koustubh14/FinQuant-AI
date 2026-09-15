from pydantic import BaseModel


class Signal(BaseModel):
    name: str
    score: int | None
    weight: float
    evidence: str


class Recommendation(BaseModel):
    action: str
    score: float
    signal_agreement: float
    signals: list[Signal]
    positive_factors: list[str]
    negative_factors: list[str]
    risk_factors: list[str]
    explanation: str
    confidence_definition: str = "Fraction of available directional votes agreeing with the final action (HOLD=neutral). Not a probability."


def threshold(value: float, band: float) -> int:
    return 1 if value > band else -1 if value < -band else 0


def recommend(
    prices,
    volatility: float,
    max_drawdown: float,
    forecast_return: float,
    relative_return: float | None = None,
    stale: bool = False,
) -> Recommendation:
    trend = float(prices.iloc[-1] / prices.iloc[-60:].mean() - 1)
    momentum = float(prices.iloc[-1] / prices.iloc[-21] - 1)
    signals = [
        Signal(
            name="trend",
            score=threshold(trend, 0.02),
            weight=1,
            evidence=f"Adjusted close versus 60-session mean: {trend:.2%}; neutral band ±2%.",
        ),
        Signal(
            name="momentum",
            score=threshold(momentum, 0.03),
            weight=1,
            evidence=f"20-session adjusted return: {momentum:.2%}; neutral band ±3%.",
        ),
        Signal(
            name="risk",
            score=-1 if volatility >= 0.4 or max_drawdown <= -0.3 else 0,
            weight=1,
            evidence=f"Volatility {volatility:.2%}, drawdown {max_drawdown:.2%}; negative at ≥40% volatility or ≤-30% drawdown.",
        ),
        Signal(
            name="forecast",
            score=threshold(forecast_return, 0.03),
            weight=1,
            evidence=f"Selected forecast endpoint return: {forecast_return:.2%}; neutral band ±3%.",
        ),
        Signal(
            name="benchmark",
            score=None if relative_return is None else threshold(relative_return, 0.05),
            weight=1,
            evidence="Benchmark unavailable."
            if relative_return is None
            else f"Relative period return: {relative_return:.2%}; neutral band ±5%.",
        ),
    ]
    available = [s for s in signals if s.score is not None]
    score = sum(s.score * s.weight for s in available) / sum(s.weight for s in available)
    action = "BUY" if score >= 0.4 else "SELL" if score <= -0.4 else "HOLD"
    if stale:
        action = "HOLD"
    target_vote = {"BUY": 1, "SELL": -1, "HOLD": 0}[action]
    agreement = sum(s.score == target_vote for s in available) / len(available)
    risk_factors = [
        "Heuristic rule, not a backtested trading strategy; no transaction costs or suitability assessment."
    ]
    if stale:
        risk_factors.append("Data older than seven calendar days: recommendation forced to HOLD.")
    if signals[2].score == -1:
        risk_factors.append(signals[2].evidence)
    return Recommendation(
        action=action,
        score=score,
        signal_agreement=agreement,
        signals=signals,
        positive_factors=[s.evidence for s in signals if s.score == 1],
        negative_factors=[s.evidence for s in signals if s.score == -1],
        risk_factors=risk_factors,
        explanation="Equal-weight available votes (-1/0/+1); BUY at score ≥0.4, SELL at ≤-0.4, otherwise HOLD. "
        "Thresholds are explicit design choices, not optimized or statistically established. "
        "Valuation and news are context only; no unsupported valuation/sentiment score.",
    )
