# Final verification report

Verification date: **2026-09-15**. Final live script started **04:48:39 UTC** (10:18:39 IST); final UI/documentation checks followed that morning. This report describes local evidence, not deployment certification.

## Environment and checks

| Check | Observed result |
| --- | --- |
| Workspace | Existing FinQuant AI repository; reference project remained read-only |
| Python | 3.14.0, project .venv; declared 3.12–3.14 range, only 3.14 tested |
| Node | v24.18.0 |
| uv | 0.11.8 |
| Backend | **59 passed, 2 warnings in 7.02 s** |
| Frontend | **3 display tests passed** |
| Production build | TypeScript and Vite passed; build 13.53 s |
| Ruff | Check passed; final formatting covers 29 Python files |
| Credential scan | No known credential-pattern findings in active source/docs/manifests; targeted credential-reference review also performed |
| Docker Compose syntax | `docker compose config --quiet` passed |
| Docker engine | Unavailable: missing Docker Desktop Linux engine named pipe |
| Remote CI / deployment | Not executed; no Git remote configured |

The continuation baseline was **50 passing backend tests**, rather than the user's earlier count of 45: the existing suite already contained additional provider/edge-case coverage. Nine meaningful regression cases were added: four trailing-placeholder timestamp/partial-row safeguards, four API-level AI isolation cases and one invalid-benchmark persistence case. No tests were removed or weakened. An initial sandbox execution produced 42 passes and eight setup errors because the sandbox identity could not access an Admin-owned pytest temporary directory. Running in the authorized Admin context resolved those setup errors; they were not numerical failures.

Remaining warnings come from Starlette TestClient's deprecated httpx use and AnyIO's BlockingPortal alias. No TypeScript/build errors occurred. These observations are not coverage percentages or a clean dependency vulnerability audit.

## Live API and saved-run results

Source: [current live JSON](results/live_verification.json), [earlier live JSON](results/initial_live_verification.json).

| Request | Result |
| --- | --- |
| GET /api/health | 200, service healthy, ai_configured=false |
| GET /api/models | 200 |
| GET /api/methodology | 200 |
| GET /openapi.json | 200 |
| POST /api/analyze — AAPL | 200; complete analytics and persisted snapshot |
| GET /api/analysis/{id} — AAPL | 200; saved result round-tripped |
| POST /api/analyze — RELIANCE.NS, latest | **422 invalid_data**, interior null prices |
| Invalid ticker syntax / empty input / invalid horizon body | 422 in each case |
| Provider network failure | Mocked retry/failure behavior verified in backend tests |

**Current AAPL:** fetched 2026-09-15 04:48:44.343961 UTC, 500 prices from 2024-09-16 through 2026-09-14. Annualized return 24.88%, volatility 28.97%, maximum drawdown −33.36%, Sharpe 0.911, Sortino 1.356, 95% historical VaR 2.663%, Expected Shortfall 4.242%. S&P benchmark beta 1.111. Deterministic action BUY; selected model naive. Its snapshot ID is `04a8d99e-3d14-4a1b-9296-3b3b294aead0`.

Naive validation RMSE is 12.580 versus Ridge 14.730; holdout RMSE is 17.411 versus Ridge 16.643. Selection correctly remains naive. These are adjusted-price errors, not profitability or recommendation accuracy.

**Earlier successful Reliance:** fetched 2026-09-14 18:48:08.474909 UTC, 498 prices through 2026-09-11. One final all-null OHLC/adjusted-close, zero-volume 2026-09-14 placeholder was excluded and disclosed. Annualized return −7.25%, volatility 20.76%, maximum drawdown −23.87%; selected naive, action SELL. Invalid NIFTY data caused benchmark omission with a warning, while stock analytics and persistence succeeded. Snapshot ID `dcd63e78-cf0f-4e68-81da-4820e993638b`.

**Why the latest Reliance run fails:** direct inspection of the latest provider history found the empty 2026-09-14 row followed by a populated 2026-09-15 row (close 1256.300049). The empty row is now interior. Excluding it would violate the requested data-quality rule. It is correctly rejected, and the earlier saved result is retained. This is a real current limitation, not a claimed successful refresh.

Both successful full snapshots were replayed offline again. Hashes and recalculated return, risk, statistics, forecast and recommendation values matched. Benchmark covariance is not independently replayed because full benchmark history is not saved; recommendation replay reuses the recorded relative-return input. Full snapshots and SQLite remain under ignored local data; a fresh clone must fetch new data to create its own saved runs.

## AI and optional failure handling

No live Gemini key was available. AAPL's real response reports AI unconfigured and still contains the complete quantitative result. API tests exercise mocked successful narrative with contrary action text, missing key, HTTP 403 for rejected credentials and network failure. Structured metrics/forecast/risk/recommendation survive all optional AI failure cases and are not overwritten by narrative. **Real authenticated Gemini success is unverified.**

An invalid benchmark test confirms the readable quality-validation warning, omission of the benchmark vote, and saved snapshot retrieval. The warning now distinguishes invalid benchmark data from an unavailable provider. No stock prices were filled, and no selection or financial formula was changed to improve example results.

## Browser and screenshots

The actual local FastAPI and Vite application was inspected at 1440×1000 and 390×844. AAPL rendered seven chart surfaces; the saved Reliance analysis rendered six because its benchmark was unavailable. Company, returns, risk, statistical diagnostics, forecast table, recommendation votes, news, AI status and methodology were present. Document width did not exceed viewport width; mobile navigation/table scrolling stays inside its container. No invalid NaN/Infinity/undefined display or runtime console errors were observed during successful-page checks.

Current Reliance failure and invalid-symbol submission show a readable alert, leave the earlier analysis visible with an explicit previous-run message, re-enable the action button and clear the loading state. Expected failed HTTP requests are distinct from JavaScript runtime errors.

Seven real viewport images are linked in [the screenshot guide](SCREENSHOT_GUIDE.md). Overview, forecast and mobile captures were visually inspected after capture, and provenance explicitly distinguishes latest AAPL from earlier Reliance. Images are not edited or synthesized.

## Git, ignores, secrets and CI

The repository's actual metadata path is the workspace `.git`. Its owner is `LAPTOP-L6DL3FC7\Admin`; normal tool commands may run as `CodexSandboxOffline`, while authorized runtime commands use Admin. The earlier newly created empty Git metadata was inspected for commits, tracked files and remotes before being preserved under ignored `.cache/initial-git-sandbox` and initialized under Admin. No wildcard/global safe-directory exemption was added.

`git status --short`, `git branch --show-current` and `git log --all --oneline` run successfully. The branch is **main**, with **no commits and no remote**. A plain `git log -1` says there are no commits, which is the expected unborn-branch state, not an ownership error. Project files are currently untracked; no initial commit or push is claimed.

The ignore pattern `data/` was corrected to `/data/`: the former accidentally excluded required `backend/app/data` source. Runtime data, local env, virtualenvs, dependencies, caches, build output, databases, IDE files and logs are ignored. Provider/validation source and documentation screenshots are includable. The credential scan received the same root-data scope fix. No secrets were found in reviewed first-party files; credential references use settings/environment variables or test fixtures. `.env.example` contains no live key. No committed history exists to scan; there is no claim that a small regex scanner detects every possible credential.

GitHub Actions configuration runs backend tests, Ruff checks/formatting, credential scan, frontend tests and production build. Only the equivalent local checks are verified. **No hosted workflow run has occurred.**

## Docker and remaining limitations

**Configuration prepared; runtime not verified in the current environment.** Docker CLI and Compose configuration exist, but the engine remained unavailable. No image-build/container-health result is claimed.

Other unverified or incomplete areas: live authenticated Gemini output; fresh valid Reliance analysis after provider correction; hosted CI/deployment; Linux container operation; broader asset/regime evaluation; calibrated predictive intervals; recommendation backtesting including transaction costs; exchange calendars and current-session finalization; point-in-time fundamentals and corporate-action history; licensed data review; authentication, retention, load tests and operational monitoring. Provider-success but invalid data can remain in cache until expiry. This is a local research prototype.

Human review should prioritize numerical conventions and thresholds, data usage rights, AI narrative behavior with a real key, and ownership/understanding of AI-assisted code before public portfolio claims. Start Docker and run the documented container check when available; configure a Git remote and inspect the first CI run before claiming those capabilities as executed.

## Change scope

The current source tree remains the source of truth. This continuation repaired specific validation/ignore/failure-message issues, added nine tests and completed evidence/documentation without redesigning the application. Against the 67-file SHA-256 continuation inventory: **24 files created, 13 modified, none deleted; 37 files changed and 91 first-party files now present**. This scope excludes local runtime data, dependencies, build output, Git and caches; documentation screenshots are included. The data adapter/ticker changes include Ruff formatting/import cleanup after the source-ignore correction.
