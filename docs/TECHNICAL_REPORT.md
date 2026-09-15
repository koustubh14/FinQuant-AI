# FinQuant AI — Technical Report

## Abstract

FinQuant AI is a local equity-research application that makes numerical methods,
forecast evaluation and decision rules inspectable. It combines adjusted market
history with descriptive statistics, risk measures, chronological model comparison
and optional Gemini interpretation. The project demonstrates implementation and
evaluation, not profitable investment advice.

## 1. Problem

A stock dashboard can conceal arbitrary confidence scores and unevaluated forecasts
behind fluent prose. This application exposes the calculation inputs, limitations,
baseline comparisons and provenance. The earlier system informed the design;
its source remained read-only.

## 2. Architecture

React/TypeScript calls a FastAPI service. A provider boundary retrieves data; pure
analytics and forecasting modules calculate results. Python rules produce the
recommendation. A separate optional HTTP call generates interpretation.
SQLite stores typed results. [Diagrams](ARCHITECTURE_DIAGRAMS.md).

## 3. Data Sources

Yahoo Finance through yfinance supplies OHLCV, adjusted close, optional company
metadata and news. Qualified tickers are preserved; explicit aliases cover common
names, with provider search for multiword names. Ambiguous names require a ticker.
The source is unaudited, may impose usage constraints and is not a point-in-time
research database. Provider news relevance is not guaranteed.

## 4. Data Validation

Required OHLCV columns, finite positive prices, nonnegative volume, OHLC bounds,
chronological unique local session dates and minimum history are checked.
Only a single trailing all-null OHLC/adjusted row with zero volume can be excluded,
with a warning. Partial and interior gaps are rejected. Full timestamps are checked
before exclusion, preventing duplicate/future placeholders from hiding errors.

No forward fill or automatic price repair occurs. Weekday gaps are warnings because
no exchange calendar distinguishes holidays from missing sessions.
The data-quality report is persisted and displayed.

## 5. Return Analytics

Simple/log returns, cumulative performance, geometric annual return and rolling
20-session measures use adjusted prices. Sample volatility scales by sqrt(252).
The raw daily price header stays separate. Detailed notation and edge handling
are in [quantitative methodology](QUANTITATIVE_METHODOLOGY.md).

## 6. Statistical Analysis

Moments, quantiles, histogram and lag-one autocorrelation describe observed returns.
Shapiro–Wilk challenges normal-tail assumptions, with sample-size and dependence
caveats. Constant series return unavailable skewness/kurtosis or diagnostic outputs.
ADF is intentionally absent because the selected modeling workflow does not use it.

## 7. Risk Analytics

Sharpe uses arithmetic excess return and sample volatility. Sortino uses a daily
target derived from the annual risk-free scenario and downside squared deviations
over all observations. Zero denominators return null.
Drawdown is negative loss from the observed running peak. Historical VaR and
empirical tail-mean ES use positive one-session loss fractions and a 95% threshold.
Gaussian VaR is a comparator, not a validated tail model.

## 8. Benchmark Analysis

Validated prices are aligned before returns, avoiding comparisons over mismatched
endpoints. Beta, correlation and cumulative-return differences require sufficient
common sessions. Invalid benchmark data results in a warning and omitted vote.
Price indices versus adjusted equities and absent FX conversion limit interpretation;
no alpha is reported.

## 9. Forecasting

The candidates are last-price naive, trailing-20 mean and Ridge(alpha=10) on five
lagged log returns. The scaler is fitted with training data inside each model fit.
Ridge forecasts recursively in log-return space, then compounds prices.
[Forecasting methodology](FORECASTING_METHODOLOGY.md) defines all boundaries.

## 10. Validation and Leakage Prevention

Up to twelve non-overlapping full-horizon folds retain at least 120 initial prices.
The earlier half chooses minimum validation RMSE. The remaining folds report
walk-forward holdout errors under a locked model identity and fixed hyperparameters.
Earlier holdout data can train later folds only after it becomes observable.
Final forecasts refit the selected model on all available observations.

A perturbation regression confirms that changing holdout prices leaves selection,
validation results and predictions preceding those observations unchanged.
This does not establish absence of every source of research bias.

## 11. Recommendation Engine

Five transparent votes describe trend, momentum, risk, forecast and available
benchmark-relative performance. Equal-weight score cutoffs are ±0.4.
Stale data forces HOLD. Agreement is the fraction of available votes matching the
action, not a success probability. No threshold optimization, strategy backtest
or recommendation-accuracy estimate is claimed.
[Recommendation methodology](RECOMMENDATION_METHODOLOGY.md).

## 12. AI Interpretation

A single 20-second-bounded Gemini request receives structured evidence, no tools,
and instructions not to introduce numbers or change the action.
The result is stored separately as unverified plain text. A contrary narrative
cannot overwrite Python fields. Mocked success, invalid-key HTTP and network failure
are tested; no live valid key was available for authenticated generation.

## 13. API and Persistence

Five routes expose health, analysis, model definitions, methodology and UUID-based
snapshot retrieval. OpenAPI is generated from request/response models.
SQLite stores the complete processed history, results, parameters, hash and package
versions. Offline replay verifies the fingerprint and numerical outputs.
Recommendation replay reuses saved benchmark relative return; benchmark covariance
is not independently replayed. Storage has no retention policy or schema migration
framework. Failed writes return the result with an explicit download warning.

## 14. Frontend

The restrained research dashboard groups price/volume, risk, statistics, forecast
evaluation, decision factors, metadata/news, AI text and methodology. It provides
JSON download and saved-run URLs. Real browser checks covered desktop and 390px
mobile layouts, chart rendering, invalid-input recovery and missing-AI-key text.

## 15. Testing

59 backend pytest cases and three frontend Vitest cases passed; TypeScript/Vite
build and Ruff checks passed. Tests cover numerical answers, malformed data, temporal
boundaries, providers, optional failures and persistence. Synthetic fixtures are
clearly test-only. No percentage coverage claim is made. Python emits two upstream
test-client deprecation warnings.

## 16. Example Results

| Recorded run | Data end | Annual return | Annual volatility | Max drawdown | Selected model |
| --- | --- | ---: | ---: | ---: | --- |
| AAPL, 2026-09-15 UTC | 2026-09-14 | 24.88% | 28.97% | -33.36% | naive |
| RELIANCE.NS, 2026-09-14 UTC (saved earlier run) | 2026-09-11 | -7.25% | 20.76% | -23.87% | naive |

Sources: [current live evidence](results/live_verification.json) and
[earlier evidence](results/initial_live_verification.json).
The newest Reliance live request fails with HTTP 422: September 14 remains null
while September 15 has values, so the gap is interior. Its earlier valid snapshot
is retained, replayable and shown as historical evidence.

AAPL comparison, adjusted-price error units:

| Model | Validation RMSE | Holdout MAE | Holdout RMSE |
| --- | ---: | ---: | ---: |
| naive | 12.580 | 14.190 | 17.411 |
| moving_average | 16.302 | 15.175 | 18.917 |
| ridge_lags | 14.730 | 13.505 | 16.643 |

Naive is selected on validation. Ridge's better holdout score does not change the
selection. The run is an evaluation example, not statistical evidence of superiority.

## 17. Failure Handling

Provider failures produce sanitized errors; empty/malformed requests return 422.
Missing metadata/news do not block calculation. Invalid benchmark data disables
comparison; AI failures leave risk, forecasts and recommendations intact.
Non-finite JSON is rejected before persistence. A four-request semaphore bounds
simultaneous analyses per process.

## 18. Limitations

No production authentication, risk governance, transaction-cost model, strategy
backtest, point-in-time data, exchange-calendar validation, calibrated uncertainty
or historical risk-free curve is implemented. Price updates during a session can
change results. The 15-minute per-process cache may retain an invalid provider
snapshot until expiry. Optional prose can hallucinate. No hosted CI execution,
Docker runtime, production deployment or live authenticated Gemini success was
verified.

## 19. Future Work

The highest-value next research improvement is an exchange-calendar-aware,
point-in-time data validation layer with an independently validated fallback source.
Then evaluate a predeclared strategy with transaction costs and an untouched
evaluation period; separately calibrate and test forecast interval coverage.
For service deployment, add authentication, retention, observability and load tests.
