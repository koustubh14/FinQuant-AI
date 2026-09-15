# Forecasting and evaluation

Implementation: `backend/app/forecasting/`. Evidence:
`backend/tests/test_forecast.py` and `docs/results/live_verification.json`.

## Fixed candidates

1. **Naive:** repeat the last adjusted close at every requested step.
2. **Moving average:** repeat the trailing 20-price mean.
3. **Ridge:** five previous log returns predict the next log return. StandardScaler
   and Ridge(alpha=10) are fitted as a pipeline on training observations only.
   Predictions recurse through the requested horizon; predicted returns, never
   future realized returns, supply future lag features. Prices compound with exp(return).

No hyperparameter search or random split is performed. The fixed lag count,
alpha and baseline window are design choices, not optimized research findings.
The [scikit-learn guidance](https://scikit-learn.org/dev/common_pitfalls.html)
explains why fitting transformations only on training subsets matters.

## Time ordering

For L prices and horizon H, the evaluator uses
K=min(12, floor((L-120)/H)) non-overlapping full-horizon folds. At least four folds
are required. The API additionally requires max(160,120+4H) prices.
The first training block contains L-KH prices.

At each origin o, fit only on prices[:o] and predict prices[o:o+H].
The first floor(K/2) folds form **validation**. Select the candidate with the
lowest pooled validation RMSE before scoring any holdout fold. Exact ties follow
the declared order: naive, moving average, Ridge. The remaining folds form
**holdout**. Model identity and hyperparameters stay fixed.

This is walk-forward holdout evaluation: earlier holdout observations can enter
a later fold's training history **after they have become observable**. They cannot
change model identity, hyperparameters or earlier forecasts. It is not a single
frozen fit spanning the entire holdout. The final future forecast refits the
selected model on all observed history, after evaluation.

The output's `selection_training_end` denotes the initial training block's end.
`validation_end` is the end of data used to choose the model.
`training_end` denotes the full-history refit cutoff.

## Metrics and interpretation

MAE = mean(abs(predicted-actual)); RMSE = sqrt(mean((predicted-actual)^2)).
Both are adjusted-price units and are not comparable across currencies or
price scales without normalization. MAPE is a fraction and is omitted when any
actual value is ≤1e-12. Directional accuracy compares each horizon step with its
fold's origin price. Flat forecasts are their own direction; the naive forecast
therefore usually scores zero. This is not a conventional binary up/down classifier.

Errors are pooled over all forecasted steps of their phase. Within-fold errors
are dependent because horizons share an origin. No significance test or calibrated
prediction interval is claimed. Forecast dates are weekday estimates, not exchange
trading dates.

## Actual AAPL example

Run fetched at 2026-09-15T04:48:44.343961+00:00; horizon 30 observed sessions.
Validation starts 2025-04-08; holdout 2025-12-24 to 2026-09-14.

| Model | Validation RMSE | Holdout MAE | Holdout RMSE |
| --- | ---: | ---: | ---: |
| naive | 12.580 | 14.190 | 17.411 |
| moving_average | 16.302 | 15.175 | 18.917 |
| ridge_lags | 14.730 | 13.505 | 16.643 |

Naive won validation and remains selected. Ridge's later holdout RMSE is lower.
Reselecting Ridge after inspecting holdout would contaminate the evaluation.
All three model scores remain visible in the UI and saved JSON. Neither this
example nor the earlier snapshot establishes a persistent edge.

## Leakage regression and limitations

The existing regression multiplies all holdout prices by 1.5. Selection and all
validation-fold outputs remain identical, as do predictions at the first
holdout origin. Later folds may legitimately change after observing changed data.

This proves that boundary in the implemented pipeline, not absence of every
possible research bias. Current adjusted-history downloads are not point-in-time;
provider revisions, corporate actions, universe selection, regime changes and
the small number of folds limit conclusions. No trading strategy, transaction-cost
simulation, execution assumption or buy-and-hold outperformance is established.
