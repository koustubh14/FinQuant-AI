# Reference project analysis

Inspected 2026-09-14. The earlier application was read as source only, never
imported or executed; imports create caches and require Gemini credentials.
The reference directory remains read-only throughout this work.

## Useful ideas and retained concepts

- `tools.py` retrieves Yahoo Finance OHLCV, fundamentals and structured news via
  yfinance. Retain that provider, with bounded requests and isolated optional data.
- `ticker_resolver.py` preserves exchange-qualified symbols and resolves common
  Indian names deterministically. Retain explicit resolution without LLM guessing.
- `analysis_engine.py` finalizes Python recommendation values before the narrative
  call. Retain this ownership boundary and structured evidence.
- `models.py` uses Pydantic and positive-finite validation. Retain typed contracts.
- `api.py` exposes health and analysis routes; the React/Vite/Recharts interface
  groups history, forecast, risk and narrative. Retain these product concepts.

## Rewrite independently

The old forecast combines a 180-observation linear price slope (65%) with 30/90
moving-average momentum (35%). It floors outputs and assigns a heuristic confidence
starting at 0.72. There is no historical out-of-sample evaluation in this module.
Replace with naive and moving-average baselines plus a regularized lag-return
model. Select on an earlier validation period and report a separate final holdout.

The old decision is BUY above 10% predicted upside and SELL below -10%. Preserve
determinism, but expose all new signal definitions, weights and thresholds.
Signal agreement must not be described as a success probability.

The old resolver removes spaces (so arbitrary company names can become nonexistent
symbols). Add a modest explicit alias registry and provider search that rejects
ambiguous name matches instead of silently choosing a different listing.

## Abandon and avoid carrying over

- CrewAI for a single narrative request, legacy Gemini SDK experiments and duplicate
  Streamlit/CLI frontends: unnecessary for the new API/dashboard architecture.
- Eager LLM initialization in `agents.py`; it makes an optional key mandatory.
- Overall failure after the Gemini stage fails despite available quantitative data.
- Unadjusted historical closes for total-return-oriented analysis without disclosure.
- Silent removal of invalid prices in forecasting and undocumented output floors.
- Per-symbol output overwrites, arbitrary confidence, artificial sleeps, broad raw
  exception messages in API responses, unpinned dependencies and runtime path hacks.
- Unrelated PDFs, notebook outputs, local caches and credentials.

## Architecture lessons

Keep numerical functions independent of providers, API, persistence and AI. Fetch
history first; absent metadata/news must not block it. Keep raw daily close separate
from adjusted analytics prices. Validate before calculation. Store immutable run
IDs and input snapshots. An LLM narrative can be absent or wrong without changing
the structured result. The reference SDK scripts are connectivity experiments,
not numerical or leakage tests. Source inspection alone does not prove runtime
correctness, provider availability or profitable recommendations.
