# Quantitative methodology

These are the implemented conventions, not claims of predictive skill. Code is in
`backend/app/analytics/`, `backend/app/risk/metrics.py` and
`backend/tests/test_quant.py`. Decimal fractions become percentages only in the UI.

## Inputs and notation

Let P[0] ... P[n] be n+1 positive, finite, chronological adjusted closes.
r[t] = P[t]/P[t-1] - 1; l[t] = log(P[t]/P[t-1]).
N is the number of return observations and A=252 observed sessions per year.
The user supplies annual risk-free rate Rf (default zero); daily target
d=(1+Rf)^(1/252)-1. The same target is used for downside deviation and Sortino.
This is a constant scenario assumption, not a downloaded historical yield curve.

Raw OHLCV remains available separately. The latest raw daily close and its
raw day-to-day change are displayed as a market snapshot; they can differ from
corporate-action-adjusted performance. The current daily bar may be incomplete.
Adjusted history may be revised and is not point-in-time data.

## Returns and rolling measures

| Metric | Formula | Annualization / edge handling |
| --- | --- | --- |
| Simple return | P[t]/P[t-1]-1 | None; first observation unavailable |
| Log return | ln(P[t]/P[t-1]) | None; positive prices required |
| Cumulative return | P[t]/P[0]-1 | None; starts at zero |
| Annualized return | (P[n]/P[0])^(252/n)-1 | Geometric, n intervals, not n+1 prices |
| Annualized volatility | sample_sd(r) × sqrt(252) | ddof=1; at least two returns |
| Moving average | mean of last 20 prices | First 19 entries unavailable |
| Rolling return | P[t]/P[t-20]-1 | Twenty observed intervals |
| Rolling volatility | sample_sd(last 20 returns) × sqrt(252) | No partial-window estimate |

Missing weekdays may be holidays or true gaps. There is no exchange calendar.
If true missing sessions remain, successive observed returns can span several
sessions; fixed-252 scaling then becomes an approximation. No prices are filled.

## Risk measures

| Metric | Formula | Assumptions and edge cases |
| --- | --- | --- |
| Downside deviation | sqrt(mean(min(r-d,0)^2)) × sqrt(252) | Denominator uses **all** observations, not only negative returns |
| Sharpe | (mean(r)-d)/sample_sd(r) × sqrt(252) | Null when daily sd ≤1e-12; arithmetic excess numerator |
| Sortino | (mean(r)-d) × 252 / annual downside deviation | Null when downside deviation ≤1e-12 |
| Drawdown series | P[t]/max(P[0:t])-1 | Zero at peaks, negative below peaks |
| Maximum drawdown | min(drawdown series) | Period-specific; peak before analysis start is unknown |
| Historical VaR 95% | max(0, linear_quantile(-r,0.95)) | One-session loss fraction; not an annual measure |
| Empirical ES 95% | max(0, mean(losses ≥ raw VaR quantile)) | Includes threshold ties; conditional empirical tail mean |
| Gaussian VaR 95% | max(0, -mean(r)+normal_ppf(.95) × sample_sd(r)) | Gaussian comparator only; no asserted normality |
| Risk label | Low <20%, Moderate 20–<40%, High ≥40% annual volatility | Explicit heuristic cutoffs, not suitability ratings |

The ES estimator is a conditional sample-tail mean. With small samples or atoms at
the quantile, it is not identical to a fractional-weight worst-5%-mass estimator.
Both VaR and ES are floored at zero when the estimated tail contains only gains.

Square-root scaling assumes stable variance and negligible serial dependence.
Sharpe/Sortino describe realized history, not guaranteed future performance.
The geometric annual return card is deliberately **not** the Sharpe numerator.
VaR does not bound the worst loss; ES remains sensitive to rare observations and
cannot anticipate tail events absent from the sample. Liquidity, gaps and
transaction costs are not modeled.

## Statistics

Daily sample mean, median, variance (ddof=1), standard deviation, bias-corrected
skewness and Fisher excess kurtosis are calculated. Quantiles use NumPy's linear
interpolation. A 24-bin histogram describes the observed sample; it is not a
fitted density. Lag-one Pearson autocorrelation is null if either lagged window
has near-zero variance.

Shapiro–Wilk challenges Gaussian tail assumptions. At least eight returns are
required by this module; constant histories and samples above 5,000 skip the test.
The deterministic interpretation uses a 5% significance threshold. A large
p-value does not prove normality; an iid p-value is only a diagnostic for potentially
dependent market returns. This bound follows the [SciPy documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.shapiro.html).
ADF was not added because no implemented model requires a unit-root decision.

## Benchmarks

Join validated asset and benchmark **prices** on common local session dates,
then compute returns. This gives both series the same return endpoints even if
their calendars differ. At least 30 common prices are required.

Beta = sample_cov(asset returns, benchmark returns)/sample_var(benchmark returns).
Correlation uses Pearson's coefficient. Beta is null when benchmark variance
≤1e-16; correlation is also null for near-constant asset returns.
Relative return is asset cumulative return minus benchmark cumulative return
over the aligned period: a percentage-point difference, not a ratio.

Defaults are ^GSPC for unqualified US symbols and ^NSEI for .NS/.BO listings.
Other listings require an explicit appropriate benchmark. No FX conversion is
performed. Price indices omit dividend reinvestment while adjusted stocks reflect
distributions, so relative performance is not Jensen's alpha. Alpha is not reported.
Invalid, stale or insufficient benchmark data disables this section and signal.

## Validation evidence

Known-value tests check [100,110,99] returns, sample volatility, nonzero Sharpe and
Sortino, a -25% drawdown, a 75% loss quantile of 0.0175 and tail mean of 0.04,
beta=2, mismatched calendars and undefined ratios. Separate tests reject null,
nonpositive, infinite and insufficient input. The API rejects non-finite JSON.

The conventional excess-return/volatility definition is consistent with
[CFA Institute's Sharpe summary](https://rpc.cfainstitute.org/research/cfa-digest/2010/02/refining-the-sharpe-ratio-digest-summary).
The choices above fully specify this implementation; no external endorsement is implied.
