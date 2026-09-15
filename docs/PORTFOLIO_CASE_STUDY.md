# FinQuant AI — Portfolio case study

FinQuant AI is a local equity research application that connects market-data validation, financial analytics and forecast evaluation to an inspectable dashboard. It was developed with AI assistance. This case study describes the implemented design and observed results, rather than inventing a personal origin story or claiming trading performance.

## Problem and motivation

A stock dashboard can look convincing while hiding fragile data, ambiguous formulas or an unfair model comparison. The project addresses those problems by making assumptions and evidence visible alongside the output. The design motivation was to produce a research artifact whose results can be inspected, saved and reproduced.

## System design and implementation

React and TypeScript present the dashboard. FastAPI exposes five application routes backed by Pydantic schemas. Python modules separately handle Yahoo Finance data, validation, returns, statistics, risk, benchmarking, forecasts and recommendations. SQLite stores each successful analysis with its parameters, adjusted-price history, package versions and data hash. A replay script recalculates the main analytical outputs offline.

The quantitative engine uses adjusted closes for returns and keeps raw quoted prices separate. It computes geometric annualized return, sample volatility, rolling metrics, drawdown, Sharpe, Sortino, historical VaR, Expected Shortfall, distribution diagnostics and aligned benchmark statistics. Definitions and denominator edge cases are explicit. These metrics describe a historical sample; they do not demonstrate a profitable strategy.

## Forecast evaluation and leakage prevention

Three candidates are evaluated: last-price naive, trailing 20-price mean, and regularized regression using five lagged log returns. Full-horizon, non-overlapping chronological folds split into earlier validation and later holdout folds. Validation RMSE selects the model before holdout scoring. Each forecast fits only observations available at its origin; feature scaling is fitted on training data only. A regression test modifies holdout prices and checks that model selection and predictions made before those observations are unchanged.

In the latest AAPL run, naive won validation with RMSE 12.580 versus Ridge's 14.730. On the separate holdout, Ridge's RMSE was 16.643 versus naive's 17.411. The application correctly retained naive as the selected model. This is useful evidence of the evaluation procedure, not evidence that naive always wins or Ridge generalizes better.

## Deterministic decisions and optional AI

The recommendation engine combines trend, momentum, risk, forecast and available benchmark votes. Its agreement score reports how many votes support the action; it is not a calibrated probability. Python produces BUY/HOLD/SELL. Gemini can add clearly separated explanatory text but cannot replace structured metrics or the action. Mocked provider and AI failures verify that optional services do not destroy a valid core analysis.

## Results and a meaningful failure

The final local checks passed 59 backend tests, three frontend display tests and the TypeScript/Vite production build. The real application was inspected on desktop and at 390-pixel mobile width, with charts and data-quality warnings captured in screenshots.

The current AAPL request succeeded and its saved result replayed. An earlier Reliance request also produced a valid saved result after excluding one final all-null, zero-volume placeholder with an explicit warning. In the latest request, that same missing date had a later valid observation after it. The app therefore rejected the interior gap. It did not silently fill prices to force a successful demo. The earlier result remains available and replayable, clearly labeled by its fetch time. Invalid NIFTY data likewise causes benchmark omission while otherwise valid stock analysis survives.

## Limitations and lessons

The current evidence covers two example equities and a modest test suite, not a broad investment validation. Forecast intervals are not calibrated; recommendation rules have no trading-cost backtest. Weekday forecast dates are not exchange calendars. Provider reliability and data licensing require review. The project is published to a private GitHub repository with both initial CI jobs passing. Docker runtime and real authenticated Gemini generation remain unverified.

The project illustrates three practical lessons: validation failures can be correct outcomes, baseline models deserve honest comparison, and separating deterministic calculations from AI text improves reproducibility. The next substantial improvement is broader walk-forward evaluation across market regimes and assets, accompanied by exchange-aware data handling and uncertainty calibration.
