# Resume evidence

## Safe claims

These describe the verified implementation, not a claim of unaided personal authorship. This project was developed with AI assistance. Use first-person wording only after reviewing and understanding the code and being able to explain the decisions.

| Claim | Evidence |
| --- | --- |
| Python financial analytics with explicit edge cases | [Quantitative methods](QUANTITATIVE_METHODOLOGY.md), backend/tests/test_quant.py |
| Three forecast candidates with chronological selection and separate holdout | [Forecast methods](FORECASTING_METHODOLOGY.md), backend/tests/test_forecast.py |
| FastAPI, typed schemas, SQLite snapshots, React/TypeScript UI | [Evidence matrix](../EVIDENCE.md) |
| 59 backend tests and 3 frontend display tests passing locally | [Final verification](FINAL_VERIFICATION_REPORT.md) |
| Real US and Indian equity analyses and strict provider validation | Current AAPL and earlier valid RELIANCE.NS snapshots; the latest Reliance request is rejected for interior missing prices |
| Optional Gemini explanation isolated from deterministic calculations | Mocked success, missing key, rejected key and network-failure tests; no live Gemini success verified |
| Hosted CI checks passed | .github/workflows/ci.yml and docs/results/github_verification.json; both initial GitHub Actions jobs succeeded |

## Unsafe / unsupported claims

Do not claim production-grade or institutional-grade infrastructure, a profitable trading strategy, market-beating forecasts, high forecasting accuracy, real-time trading, calibrated recommendation probabilities, live Gemini integration success, Docker runtime verification, application deployment, or a personal performance improvement without evidence. A BUY/SELL label is a heuristic output, not proof of investment value. Passing tests and hosted CI does not establish model profitability or eliminate bugs.

## Exactly three resume bullets

- Developed a Python/FastAPI and React/TypeScript equity research application with return, statistical, risk and benchmark analytics, five API routes, and reproducible SQLite analysis snapshots.
- Implemented three forecasting candidates with chronological validation, a separate expanding holdout, and leakage regression tests; preserved validation-based selection when another model performed better on holdout.
- Verified the application with 59 backend tests, three frontend display tests, a production build, and desktop/mobile browser checks; isolated optional AI and benchmark failures from quantitative results.

## GitHub repository description

Equity research dashboard with Python risk analytics, chronological forecast evaluation, deterministic signals, saved analyses, and optional Gemini explanations.

## Portfolio description

FinQuant AI combines a typed Python analytical engine with a responsive research dashboard. It emphasizes inspectable formulas, strict financial-data validation, honest model comparisons, and a clear boundary between numerical results and optional AI narrative. Its evidence includes automated tests, real market-data runs and saved-run replay rather than profitability claims.

## LinkedIn project copy

Built FinQuant AI as an equity-research engineering project using Python, FastAPI, React and TypeScript, with AI-assisted development. The project evaluates three forecast candidates chronologically, reports separate holdout errors, and calculates risk from validated adjusted-price history. One useful result: the naive baseline won AAPL validation while Ridge later had lower holdout RMSE; the selected model stayed unchanged. Verification includes 59 backend tests, three frontend tests and real desktop/mobile screenshots. This is a research prototype, with provider limitations and unverified deployment/runtime items documented openly.

## 30-second interview pitch

FinQuant AI is an equity research dashboard I developed with AI assistance. Python validates market data, calculates returns and risk, and compares three forecast models using chronological validation and a separate holdout. Recommendations follow explicit rules; Gemini only explains the results. I verified 59 backend tests and the responsive UI. The strongest lesson was preserving honest evaluation: the naive model stayed selected even when Ridge later performed better on holdout.

## Two-minute technical pitch

The design problem was to make equity analysis inspectable: each number should have a formula, each forecast should have an honest evaluation, and an AI service failure should not erase useful results. I used FastAPI and Pydantic for the backend, pure Python analytical modules, SQLite for immutable saved runs, and React/TypeScript for the dashboard. Development was AI-assisted, so I would distinguish the implemented system from claims of independent authorship.

The input layer validates timestamps, positive prices, OHLC relationships, history length and missing values. Adjusted closes drive analytics; raw prices are shown separately. A single final empty provider row may be excluded with a dated warning. Interior missing prices are rejected. That distinction matters: an earlier Reliance analysis succeeded with a trailing-placeholder warning, while a later request correctly failed after the missing row became interior.

Risk includes sample annualized volatility, Sharpe, Sortino, drawdown, historical VaR and conditional tail loss. Forecasting compares a last-price baseline, a trailing mean and Ridge on five lagged log returns. Earlier full-horizon folds select the model; later folds evaluate that fixed choice. Scaling is fitted only on each training window, and a regression test changes holdout observations to confirm selection and earlier predictions stay unchanged.

Recommendations aggregate documented signals. Their agreement score is not a success probability. Gemini receives the computed evidence only for narrative explanation. Tests cover missing credentials, mocked success and external failures. The application passes 59 backend tests, three frontend tests and a production build, with desktop and mobile verification. Before professional use, I would prioritize broader temporal testing, licensed exchange-aware data, calibrated uncertainty and operational security.
