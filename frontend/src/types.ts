export interface Metrics { mae: number; rmse: number; mape: number | null; directional_accuracy: number }
export interface HistoryPoint {
  date: string; open: number; high: number; low: number; close: number; adjusted_close: number; volume: number;
  daily_return: number | null; log_return: number | null; cumulative_return: number;
  moving_average: number | null; rolling_return: number | null; rolling_volatility: number | null; drawdown: number;
}
export interface Analysis {
  snapshot_saved: boolean;
  analysis_id: string; generated_at: string;
  parameters: {symbol: string; period: string; forecast_horizon: number; annual_risk_free: number};
  company: {symbol: string; name: string; exchange: string | null; currency: string | null; sector: string | null;
    industry: string | null; market_cap: number | null; trailing_pe: number | null; forward_pe: number | null;
    price_to_book: number | null; revenue_growth: number | null; return_on_equity: number | null;
    latest_close: number; adjusted_close: number; daily_change: number};
  quality: {rows: number; start: string; end: string; stale_days: number; possible_missing_weekdays: number; warnings: string[]; handling: string};
  returns: {total_return: number; annualized_return: number; annualized_volatility: number; observations: number};
  risk: {downside_deviation: number; maximum_drawdown: number; sharpe: number | null; sortino: number | null;
    historical_var_95: number; expected_shortfall_95: number; normal_var_95: number; level: string; assumptions: string[]};
  statistics: {mean: number; median: number; variance: number; standard_deviation: number; skewness: number | null;
    excess_kurtosis: number | null; autocorrelation_lag1: number | null;
    normality: {name: string; statistic: number | null; p_value: number | null; interpretation: string}; histogram: {return: number; count: number}[]};
  benchmark: null | {symbol: string; beta: number | null; correlation: number | null; relative_return: number;
    methodology: string; series: {date: string; asset: number; benchmark: number}[]};
  forecast: {selected_model: string; baseline_model: string; horizon: number; training_start: string; training_end: string;
    validation_start: string; validation_end: string; holdout_start: string; holdout_end: string;
    methodology: string; limitations: string[]; selected_beats_naive_holdout: boolean;
    models: Record<string, {validation: Metrics; holdout: Metrics}>; predictions: {step: number; date: string; value: number}[]};
  recommendation: {action: string; score: number; signal_agreement: number;
    signals: {name: string; score: number | null; weight: number; evidence: string}[];
    positive_factors: string[]; negative_factors: string[]; risk_factors: string[]; explanation: string; confidence_definition: string};
  history: HistoryPoint[]; news: {headline: string; source: string | null; date: string | null; url: string | null; summary: string | null}[];
  interpretation: {status: string; text: string; model: string | null};
  provenance: {source: string; fetched_at: string; cached: boolean; input_sha256: string; duration_seconds: number; versions: Record<string, string>; assumptions: string[]};
  warnings: string[];
}
