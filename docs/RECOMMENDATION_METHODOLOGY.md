# Deterministic recommendation methodology

Implementation: `backend/app/recommendation/engine.py`.
Tests: `backend/tests/test_forecast.py`, `backend/tests/test_api.py`.

Python produces the action before the optional Gemini call. No narrative text is
parsed into the recommendation schema.

## Signals

Each available signal receives equal weight 1 and vote -1, 0 or +1.

| Signal | Input | Rule |
| --- | --- | --- |
| Trend | Latest adjusted close / mean of last 60 adjusted closes -1 | +1 above +2%; -1 below -2%; otherwise 0 |
| Momentum | Latest adjusted close / adjusted close 20 intervals earlier -1 | +1 above +3%; -1 below -3%; otherwise 0 |
| Risk | Annual volatility and maximum drawdown | -1 if volatility ≥40% or drawdown ≤-30%; otherwise 0 |
| Forecast | Selected future endpoint / latest adjusted close -1 | +1 above +3%; -1 below -3%; otherwise 0 |
| Benchmark | Aligned period asset return minus benchmark return | +1 above +5 percentage points; -1 below -5; otherwise 0 |

Directional boundary equality is neutral. The risk vote does not issue a positive
vote for low volatility. Missing benchmark data has no vote and no denominator
weight; it is not silently treated as zero. News and financial ratios are context
only: no unsupported sentiment or valuation scores are invented.

Score = weighted vote sum / available weight sum.
BUY at score ≥0.4; SELL at score ≤-0.4; otherwise HOLD.
If the last observed session is older than seven calendar days, force HOLD and
explain the override. Its composite score remains visible as underlying evidence.

## Agreement, not probability

`signal_agreement` is the fraction of available votes matching the final action:
+1 for BUY, -1 for SELL and 0 for HOLD. If all signals are neutral, HOLD can have
100% agreement. A forced stale-data HOLD may have low agreement. Neither value
measures the probability of making money or recommendation correctness.

Trend, momentum and forecast can be correlated, so votes are not independent
evidence. Equal weights and cutoffs are transparent heuristics, not financially
optimal, calibrated or backtested parameters. Data-period choices can change
the label. A model with weak forecast performance still contributes according
to the documented rule; holdout scores never trigger retrospective model selection.

## AI boundary and limitations

Gemini receives immutable structured evidence and instructions to explain it.
The code can guarantee that narrative cannot overwrite Python fields; it cannot
guarantee every generated sentence is factually correct. The UI explicitly labels
the narrative as unverified interpretation. Tests deliberately return a contrary
BUY narrative while Python's stale-data HOLD remains unchanged.

This is a research signal summary, not a portfolio allocation, personalized
recommendation, price target guarantee or trading system. Suitability, costs,
liquidity, taxation and position sizing are outside scope.
