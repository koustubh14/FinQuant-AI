# Project summary

FinQuant AI is a local equity research dashboard, with a Python/FastAPI analytical backend and React/TypeScript interface. Implemented components include market-data validation, returns and statistics, risk and benchmarks, three forecast candidates, deterministic recommendations, optional Gemini narrative, and SQLite saved analyses. Development was AI-assisted; personal implementation claims should follow human code review and understanding.

Methods include adjusted-price simple/log returns, geometric annualization, sample volatility, Sharpe, Sortino, drawdown, historical VaR/Expected Shortfall, distribution diagnostics and date-aligned beta. Forecasts compare naive, trailing mean and Ridge. Earlier chronological folds select the model; separate later expanding folds evaluate the fixed selection. Training-only scaling and a holdout perturbation regression test protect earlier predictions from future information.

Python aggregates explicit trend, momentum, risk, forecast and optional benchmark votes into BUY/HOLD/SELL. Agreement describes votes, not success probability. Gemini only explains numerical evidence and cannot overwrite it; numerical results survive optional narrative/benchmark failures.

Local verification passed 59 backend tests, three frontend display tests, a production build, and desktop/mobile browser checks. Current AAPL succeeds. Earlier valid Reliance data remains saved and replayable; the current feed is correctly rejected for an interior missing row. No live authenticated Gemini generation, Docker runtime or remote CI run was verified. Forecast uncertainty, broad investment validation, exchange calendars, licensed data and production controls remain limitations.
