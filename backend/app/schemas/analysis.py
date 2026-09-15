from typing import Literal

from app.analytics.benchmarks import BenchmarkResult
from app.analytics.returns import ReturnMetrics
from app.analytics.statistics import StatisticsResult
from app.data.validation import QualityReport
from app.forecasting.validation import ForecastResult
from app.recommendation.engine import Recommendation
from app.risk.metrics import RiskMetrics
from pydantic import BaseModel, ConfigDict, Field, field_validator


class AnalyzeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)
    symbol: str = Field(min_length=1, max_length=80)
    period: Literal["1y", "2y", "5y"] = "2y"
    forecast_horizon: int = Field(default=30, ge=1, le=60)
    annual_risk_free: float = Field(default=0, ge=0, le=0.3)
    benchmark: str | None = Field(default=None, max_length=25)
    include_ai: bool = False

    @field_validator("symbol")
    @classmethod
    def strip_symbol(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("A company name or ticker is required.")
        return value.strip()


class Company(BaseModel):
    symbol: str
    name: str
    exchange: str | None = None
    currency: str | None = None
    sector: str | None = None
    industry: str | None = None
    market_cap: float | None = None
    trailing_pe: float | None = None
    forward_pe: float | None = None
    price_to_book: float | None = None
    revenue_growth: float | None = None
    return_on_equity: float | None = None
    latest_close: float
    adjusted_close: float
    daily_change: float


class PricePoint(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    adjusted_close: float
    volume: float
    daily_return: float | None
    log_return: float | None
    cumulative_return: float
    moving_average: float | None
    rolling_return: float | None
    rolling_volatility: float | None
    drawdown: float


class NewsItem(BaseModel):
    headline: str
    source: str | None = None
    date: str | None = None
    url: str | None = None
    summary: str | None = None


class Interpretation(BaseModel):
    status: Literal["disabled", "unconfigured", "unavailable", "generated"]
    text: str
    model: str | None = None


class Provenance(BaseModel):
    source: str = "Yahoo Finance via yfinance"
    fetched_at: str
    cached: bool
    input_sha256: str
    versions: dict[str, str]
    duration_seconds: float
    assumptions: list[str]


class AnalysisResult(BaseModel):
    analysis_id: str
    generated_at: str
    parameters: AnalyzeRequest
    company: Company
    quality: QualityReport
    returns: ReturnMetrics
    risk: RiskMetrics
    statistics: StatisticsResult
    benchmark: BenchmarkResult | None
    forecast: ForecastResult
    recommendation: Recommendation
    history: list[PricePoint]
    news: list[NewsItem]
    interpretation: Interpretation
    provenance: Provenance
    warnings: list[str]
