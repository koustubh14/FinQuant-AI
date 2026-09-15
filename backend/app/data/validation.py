from datetime import datetime, timezone

import numpy as np
import pandas as pd
from app.core.exceptions import AnalysisError
from pydantic import BaseModel


class QualityReport(BaseModel):
    rows: int
    start: str
    end: str
    stale_days: int
    possible_missing_weekdays: int
    warnings: list[str]
    handling: str = "No price filling, sorting, deduplication or repair. A trailing all-null OHLC/adjusted-close row with zero volume may be excluded and is explicitly reported. Other invalid data is rejected."


def validate_history(
    frame: pd.DataFrame, minimum: int = 160, now: datetime | None = None
) -> tuple[pd.DataFrame, QualityReport]:
    required = {"Open", "High", "Low", "Close", "Adj Close", "Volume"}
    if frame.empty:
        raise AnalysisError("No price history returned. Check the ticker or provider availability.")
    if not required.issubset(frame.columns) or frame.columns.duplicated().any():
        raise AnalysisError("Provider history has missing or duplicate OHLCV columns.")
    if not isinstance(frame.index, pd.DatetimeIndex) or frame.index.hasnans:
        raise AnalysisError("History must have valid session timestamps.")
    result = frame.copy()
    original_dates = result.index.tz_localize(None).normalize()
    today = (now or datetime.now(timezone.utc)).date()
    if original_dates.duplicated().any() or not original_dates.is_monotonic_increasing:
        raise AnalysisError(
            "Duplicate or non-monotonic session dates; no automatic repair performed."
        )
    if original_dates[-1].date() > today:
        raise AnalysisError("Price history contains future session dates.")
    exclusions = []
    price_columns = ["Open", "High", "Low", "Close", "Adj Close"]
    if result.iloc[-1][price_columns].isna().all() and result.iloc[-1]["Volume"] == 0:
        exclusions.append(
            f"Excluded trailing empty provider placeholder dated {result.index[-1].date()}: all prices null and volume zero; no price imputation."
        )
        result = result.iloc[:-1].copy()
        if result.empty:
            raise AnalysisError(
                "No observed prices after excluding the trailing empty placeholder."
            )
    dates = result.index.tz_localize(None).normalize()  # Preserve local exchange session dates.
    result.index = dates
    try:
        numeric = result[list(required)].astype(float)
    except (TypeError, ValueError) as exc:
        raise AnalysisError("OHLCV contains nonnumeric values.") from exc
    if not np.isfinite(numeric.to_numpy()).all():
        raise AnalysisError("OHLCV contains null or non-finite values; no filling performed.")
    prices = numeric.drop(columns="Volume")
    if (prices <= 0).any().any() or (numeric.Volume < 0).any():
        raise AnalysisError("Prices must be positive and volume nonnegative.")
    if (
        (numeric.High < numeric[["Open", "Close", "Low"]].max(axis=1))
        | (numeric.Low > numeric[["Open", "Close"]].min(axis=1))
    ).any():
        raise AnalysisError("OHLC high/low bounds are inconsistent.")
    if len(result) < minimum:
        raise AnalysisError(
            f"Insufficient history: {len(result)} rows; at least {minimum} required."
        )
    stale = (today - dates[-1].date()).days
    if stale < 0:
        raise AnalysisError("Price history contains future session dates.")
    gaps = len(pd.bdate_range(dates[0], dates[-1]).difference(dates))
    warnings = exclusions
    if stale > 7:
        warnings.append(f"Latest session is {stale} calendar days old; data may be stale.")
    if gaps:
        warnings.append(
            f"{gaps} absent weekdays may be holidays or missing sessions; no exchange calendar applied."
        )
    extra = set(frame.columns) - required
    if extra:
        warnings.append("Additional provider columns retained: " + ", ".join(sorted(extra)))
    if (numeric.Volume == 0).any():
        warnings.append("Zero-volume sessions present; may indicate illiquidity or index data.")
    # numeric currently has original timezone index: assign values by position.
    result[list(required)] = numeric.to_numpy()
    return result, QualityReport(
        rows=len(result),
        start=dates[0].date().isoformat(),
        end=dates[-1].date().isoformat(),
        stale_days=stale,
        possible_missing_weekdays=gaps,
        warnings=warnings,
    )
