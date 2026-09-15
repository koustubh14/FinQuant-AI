# Project scorecard

Subjective engineering assessment as of 2026-09-15, on a 0–10 scale. These scores assess this local research/portfolio implementation, not readiness to manage money. They are not externally audited and do not average into a certification.

| Area | Score | Evidence and constraint |
| --- | ---: | --- |
| Quantitative correctness | 8 | Explicit formulas, finite guards and known-value tests; independent external numerical review still useful |
| Statistical depth | 6 | Distribution moments, normality and autocorrelation diagnostics; no regime or robust dependence modeling |
| Risk analytics | 7 | Sharpe/Sortino, drawdown, VaR and tail mean; no liquidity, portfolio or stress framework |
| Forecast evaluation | 8 | Three baselines/candidates, chronological selection, separate holdout; small asset sample and no calibrated interval |
| Leakage prevention | 8 | Training-only scaling and holdout perturbation tests; provider-adjusted historical data is not point-in-time |
| Software architecture | 8 | Clear typed data/analytics/service/UI separation; deliberately small local design |
| Backend engineering | 7 | Validation, bounded concurrency, cache, retries and persistence; no auth/retention/load-test evidence |
| Frontend quality | 8 | Clear evidence sections, charts and real desktop/mobile checks; no comprehensive accessibility/user study |
| Testing | 7 | 59 backend and 3 frontend tests plus browser checks; limited automated UI coverage and no production load testing |
| Documentation | 9 | Formula, evaluation, evidence, provenance and interview documents; human technical editorial review still needed |
| Reproducibility | 7 | Locks, hashes and offline saved-run replay; raw benchmark history absent and external data mutable |
| Portfolio value | 8 | Demonstrable cross-stack quantitative project with honest failures; no deployed showcase or strategy success evidence |
| Interview defensibility | 8 | Traceable methods and candid model results; depends on the author's understanding of AI-assisted code |

## Three weakest remaining areas

1. **Investment and statistical validation:** only limited real examples, no broad regimes/universe evaluation, calibrated uncertainty or transaction-cost strategy backtest. More output metrics would not substitute for this evidence.
2. **Data reliability and reproducibility:** public data can be incomplete/revised, current Reliance is rejected, exchange sessions are approximated, and benchmark history is not retained for complete replay.
3. **Operational verification:** hosted CI now passes, but Docker runtime and real Gemini generation remain unverified; authentication, retention, monitoring and load testing are absent. These prevent production-readiness claims.
