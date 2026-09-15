# Technical interview guide

Answers refer to this implementation. Review the linked code and methods before presenting them as personal expertise; development was AI-assisted.

1. **Why use adjusted prices for returns?** Adjusted closes reflect provider corporate-action adjustments, reducing mechanical split/dividend distortions. Provider adjustment quality still matters. Raw OHLC is retained for quoted-price display; this is not an audited total-return database.

2. **Simple versus log returns?** Simple return is P(t)/P(t−1)−1; log return is log(P(t)/P(t−1)). Simple returns compound multiplicatively; log returns add across time. Ridge predicts log returns and compounds them with exp.

3. **How is volatility annualized?** Sample standard deviation of daily simple returns, ddof=1, times sqrt(252). This assumes a conventional trading year and square-root scaling; autocorrelation and volatility clustering limit that approximation.

4. **Sharpe versus Sortino?** Sharpe divides mean daily excess return by daily sample volatility and multiplies by sqrt(252). Sortino uses annualized arithmetic excess return over downside deviation, where downside squared deviations are averaged across all observations. Near-zero denominators return null, not infinity.

5. **What is maximum drawdown?** The most negative P(t)/running_peak(t)−1. The app reports a negative fraction and the complete drawdown path. It is sample-dependent and does not forecast the next loss.

6. **How does historical VaR work?** Form daily losses as −simple_return and calculate the 95th percentile with linear interpolation. The loss measure is floored at zero for presentation. It is a one-day historical estimate, not a worst-case guarantee.

7. **Why is CVaR useful?** It describes tail-loss severity beyond a threshold, while VaR alone gives that threshold. This implementation averages losses greater than or equal to the raw 95% quantile, including all ties. It is a conditional-tail-mean estimator, not fractional weighting of exactly the worst 5% at discrete mass points.

8. **What are VaR's limitations?** Historical observations can miss new regimes, tail samples are small, and the result depends on horizon and estimator. Neither the historical estimate nor the Gaussian comparator models liquidity, transaction costs or future extreme events reliably.

9. **What does beta measure?** Covariance of aligned stock and benchmark daily returns divided by benchmark variance. It measures sample linear sensitivity to that chosen benchmark. It is not causation or a standalone risk score; near-zero benchmark variance produces null.

10. **How does benchmark alignment work?** Validate both price histories, intersect dates, then calculate returns on that shared price grid so each paired return spans identical dates. Require at least 30 common prices. A sparse grid may create multi-day intervals; this limitation is disclosed. USD stock/S&P and INR stock/NIFTY comparisons are local-currency, not FX-neutral alpha.

11. **How is missing data handled?** No interpolation or forward fill. Only one final all-null OHLC/adjusted-close row with zero volume may be removed, with a dated warning. Duplicate, unordered or future timestamps are checked first. Partial rows and interior missing prices fail validation. Absent weekdays are disclosed without assuming every weekday is an exchange session.

12. **Why chronological validation?** The forecast problem asks what could have been predicted from information available at a particular time. Earlier folds choose the model; later folds evaluate it under that information ordering.

13. **Why not a random train/test split?** Random splitting can put future market information into training and break the deployment sequence. Lag construction and preprocessing also need to respect each origin, not just the final dataset split.

14. **What is leakage here?** Any use of unavailable future observations in features, scaling, selection, hyperparameter choice or earlier forecasts. The code fits the scaler inside each training pipeline and locks candidate identity before holdout scoring.

15. **How is leakage tested?** The regression test perturbs holdout prices and asserts unchanged model selection and forecasts made before those prices were known. It does not require later expanding-window predictions to ignore observations that have become available by their origin.

16. **Why did naive win validation?** It had the lowest pooled validation RMSE on this particular sample. More complex models can add estimation error; this run alone does not establish why the market behaved as it did or which model will win next.

17. **Why could Ridge win later?** Holdout observations differ from validation. In current AAPL evidence Ridge has lower holdout RMSE even though naive won validation. Sample variation and changing dynamics are possible explanations, not proven causal findings.

18. **Why not re-select on holdout?** Doing so would turn the reported holdout into another selection set and make the advertised independent evaluation misleading. A redesigned selection process would need fresh untouched evaluation data.

19. **How does recommendation confidence work?** It is signal agreement: the fraction of included votes matching the final action. The action is based on the average signed vote, with BUY at ≥0.4 and SELL at ≤−0.4; otherwise HOLD. Stale data over seven days forces HOLD. Agreement is not probability or backtested accuracy.

20. **Why does Gemini not make the recommendation?** Reproducible Python rules own structured outputs. Gemini receives computed evidence to explain it in a separate text field. This prevents narrative variability from changing the stored analytical decision.

21. **What happens when Gemini fails?** A missing key yields an unconfigured status; rejected credentials/network errors yield an unavailable message. Metrics, forecast and recommendation remain. Mocked success/failure paths were tested; real authenticated generation has not been verified.

22. **What is needed before professional investment use?** Licensed and exchange-aware data, robust corporate-action audits, wider temporal evaluation, transaction-cost and execution modeling, uncertainty calibration, independent quantitative review, authentication, operational monitoring and tested deployment. There is no evidence of profitability here.

23. **How is the annual return calculated?** (P_last/P_first)^(252/n)−1, with n return intervals, not price rows. It is a geometric trading-period annualization, whereas Sharpe's numerator uses an arithmetic daily excess-return mean.

24. **What do statistical diagnostics prove?** Skewness, Fisher excess kurtosis, histogram, lag-one correlation and Shapiro provide sample diagnostics. A normality-test p-value is not the probability prices or returns are normal; time dependence complicates its usual iid interpretation.

25. **What is reproducible in a saved run?** The stored adjusted history and hash support offline recalculation of returns, risk, statistics, forecasts and recommendation. Benchmark covariance is not fully replayed because raw benchmark prices are not saved; replay uses the saved relative-return input for the recommendation. News and AI text are saved observations, not deterministic fresh generations.

26. **Why no forecast confidence interval?** The project has not calibrated predictive coverage. Showing an invented band would imply unsupported certainty. Future dates are weekday placeholders rather than verified exchange sessions.

27. **What happens if persistence fails?** The API returns the computed analysis with an explicit save warning. It does not promise that the ID can then be retrieved. SQLite is appropriate for this local prototype but has no retention, authentication or production concurrency guarantees.

28. **What does the test count demonstrate?** 59 backend tests cover known-value calculations, data-quality boundaries, chronological evaluation, API behavior and optional-service isolation; three frontend tests cover display utilities. Browser checks add real UI evidence. Counts are not coverage percentages or proof of all edge cases.

See [quantitative](QUANTITATIVE_METHODOLOGY.md), [forecast](FORECASTING_METHODOLOGY.md), [recommendation](RECOMMENDATION_METHODOLOGY.md), and [verification](FINAL_VERIFICATION_REPORT.md) details.
