# Technical change record

## Completion and regression review (2026-09-15)

- Preserved the current architecture, financial formulas and validation-selected
  model identity. The reference project remained read-only.
- Anchored `.gitignore` runtime `data/` exclusion to `/data/`; the original rule
  also excluded required `backend/app/data` source. Fixed the credential scanner's
  root-data exclusion for the same reason. Ruff now checks all 29 Python files.
- Validate original timestamps before the single trailing-empty-row exception.
  Added four tests for partial, duplicate, future and repeated null placeholders.
- Added four API-level AI isolation tests (missing key, mocked successful but
  contrary narrative, rejected credentials and network failure), and a persisted
  invalid-benchmark test. The existing 50-test suite now has 59 passing tests.
- Made the benchmark-quality failure warning explicit. It remains optional and
  contributes no vote when unavailable.
- Recorded current real AAPL success and current Reliance rejection after its
  missing date became interior. Preserved the earlier valid Reliance result and
  replayed both successful snapshots; no missing prices were filled.
- Completed documentation, evidence and seven real viewport screenshots. Replaced
  obsolete empty-workspace audit/plan text with current findings and completion status.
- Reviewed Git ownership and source inclusion without adding a wildcard global
  safe-directory setting. Docker runtime and authenticated Gemini calls remain
  explicitly unverified.
- At the user's subsequent request, created the private koustubh14/FinQuant-AI
  repository and pushed the reviewed implementation. Both first hosted GitHub
  Actions jobs passed on f6bca02; recorded their evidence and updated the reports.

## Independent implementation (2026-09-14/15)

No reference project files were modified or imported. See REFERENCE_PROJECT_ANALYSIS.md
for the source inspection and ARCHITECTURE_PLAN.md for decisions made before coding.

- New pure analytical functions replace the old unvalidated trend blend. Naive,
  trailing mean and train-scaled Ridge are evaluated with separate selection and
  holdout folds. This is an independent design, not a claim the old logic was ported unchanged.
- Recommendations use documented equal-weight signals. The LLM cannot assign any
  structured recommendation field. AI failure leaves the numerical result intact.
- Raw OHLC and adjusted analytical prices remain separate. Ratios use explicit
  annualization and return null when denominators are zero.
- A live Reliance request revealed a final all-null, zero-volume provider row.
  Only that trailing placeholder is excluded, with its date/reason in the quality
  report. Partial and interior missing observations remain rejected. No price is filled.
- NIFTY had interior all-null rows in the live check. Benchmark metrics were omitted
  with a warning; validation was not weakened to manufacture a comparison.
- A browser test found offscreen chart tooltip transforms causing mobile overflow.
  Chart containers now contain that overflow; 390px layout was rechecked.
- Saved-run loading restores period, horizon and risk-free parameters in the form.
  API documentation uses relative proxy routes for development and Docker.
