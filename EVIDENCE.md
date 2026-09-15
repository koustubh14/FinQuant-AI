# FinQuant AI evidence manifest

This table links actual implementation to verification. Test counts refer to
2026-09-15. Tests are not a coverage percentage or proof of profitable decisions.
[Final verification report](docs/FINAL_VERIFICATION_REPORT.md) records limits.

| Capability | Implementation | Evidence File(s) | Verification |
| --- | --- | --- | --- |
| Financial returns | Simple/log/cumulative, geometric annualization, rolling measures | [returns.py](backend/app/analytics/returns.py), [tests](backend/tests/test_quant.py) | Known prices and independent expected returns |
| Applied statistics | Moments, quantiles, histogram, normality diagnostic, lag correlation | [statistics.py](backend/app/analytics/statistics.py), [methods](docs/QUANTITATIVE_METHODOLOGY.md) | Constant-series and undefined-lag tests; live AAPL output |
| Risk analytics | Sample volatility, downside deviation, Sharpe and Sortino | [metrics.py](backend/app/risk/metrics.py), [tests](backend/tests/test_quant.py) | Known-value and zero-denominator checks |
| Historical VaR / ES | Linear loss quantile and explicit conditional tail mean | [metrics.py](backend/app/risk/metrics.py) | 0.0175 VaR / 0.04 ES known example at 75% |
| Drawdown analysis | Running-peak underwater series and worst drawdown | [metrics.py](backend/app/risk/metrics.py) | Independent -25% example |
| Benchmark analysis | Price alignment before returns, beta/correlation/relative return | [benchmarks.py](backend/app/analytics/benchmarks.py) | Beta=2, differing-session tests; real AAPL/^GSPC |
| Time-series forecasting | Naive, 20-price mean, five-log-return Ridge | [models.py](backend/app/forecasting/models.py) | Baseline values, constant-price Ridge and live evaluation |
| Chronological validation | Expanding full-horizon folds and separate holdout | [validation.py](backend/app/forecasting/validation.py) | Fold boundary assertions |
| Leakage prevention | Training-only scaling; selection before holdout scoring | [test_forecast.py](backend/tests/test_forecast.py) | Holdout perturbation cannot alter selection or prior predictions |
| Evaluation / model selection | MAE/RMSE/MAPE/direction and validation RMSE selection | [metrics.py](backend/app/forecasting/metrics.py), [results](docs/results/live_verification.json) | Known errors; naive stays selected despite lower Ridge holdout error |
| Deterministic decisions | Visible votes, cutoffs, stale HOLD and agreement definition | [engine.py](backend/app/recommendation/engine.py) | BUY/SELL/HOLD, unavailable benchmark and stale-data tests |
| Python / modular design | Pure numerical modules behind a provider protocol | [analysis.py](backend/app/services/analysis.py) | Modules exercised without network providers |
| FastAPI / API design | Five public routes and generated OpenAPI | [main.py](backend/app/main.py), [test_api.py](backend/tests/test_api.py) | Health, methods/models, analysis, retrieval and invalid requests |
| Pydantic contracts | Typed request and nested response schemas | [schemas](backend/app/schemas/analysis.py) | Body validation and snapshot roundtrip |
| Financial data validation | OHLC bounds, finite prices, timestamps, history length | [validation.py](backend/app/data/validation.py), [tests](backend/tests/test_data.py) | Null/interior/partial/duplicate/future/empty tests |
| Provider engineering | Bounded request retry, TTL cache, optional metadata/news | [market_data.py](backend/app/data/market_data.py), [tests](backend/tests/test_provider.py) | Cache isolation and bounded failure tests |
| React / TypeScript | Structured dashboard with chart components and typed API client | [App](frontend/src/App.tsx), [Dashboard](frontend/src/components/Dashboard.tsx) | TypeScript production build passes |
| Financial visualization | Seven AAPL charts and forecast comparison table | [Charts](frontend/src/components/Charts.tsx), [screenshots](docs/screenshots/aapl-dashboard.png) | Real browser rendering, no error overlay |
| Responsive UI | Mobile layout with contained chart tooltips | [styles](frontend/src/styles.css), [mobile capture](docs/screenshots/mobile-dashboard.png) | 390px layout has no page overflow |
| Testing | pytest numerical/API tests; Vitest display tests | [backend tests](backend/tests), [frontend tests](frontend/src/utils.test.ts) | 59 backend + 3 frontend cases pass |
| Optional LLM integration | One bounded Gemini REST call; numerical fields never parsed from prose | [analyst.py](backend/app/ai/analyst.py), [tests](backend/tests/test_api.py) | Mock success/403/network tests and real missing-key behavior; authenticated live generation unverified |
| Failure handling | Sanitized errors; optional benchmark/AI/save failure isolation | [main.py](backend/app/main.py), [test_api.py](backend/tests/test_api.py) | Pipeline survives optional failures; malformed market history rejected |
| Persistence / reproducibility | SQLite run JSON, UUID, input hash, versions and numerical replay | [storage.py](backend/app/services/storage.py), [replay](scripts/replay.py) | Real saved runs retrieved and recomputed offline |
| CI configuration | Backend checks and frontend tests/build workflow | [ci.yml](.github/workflows/ci.yml) | Equivalent local checks pass; hosted CI has not run |

Dockerfiles exist but **runtime verification is not claimed**, so Docker operation
is not listed as a verified capability. No live authenticated Gemini success,
professional investment validation, trading profitability or production-readiness
claim is supported.
