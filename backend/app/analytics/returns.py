import numpy as np
import pandas as pd
from pydantic import BaseModel


def valid_prices(prices: pd.Series) -> pd.Series:
    values = prices.astype(float)
    if len(values) < 3 or not np.isfinite(values).all() or (values <= 0).any():
        raise ValueError("At least three finite positive prices required.")
    return values


def simple_returns(prices: pd.Series) -> pd.Series:
    return valid_prices(prices).pct_change(fill_method=None).iloc[1:]


def log_returns(prices: pd.Series) -> pd.Series:
    return np.log(valid_prices(prices)).diff().iloc[1:]


def cumulative_returns(prices: pd.Series) -> pd.Series:
    values = valid_prices(prices)
    return values / values.iloc[0] - 1


def annualized_return(prices: pd.Series, sessions: int = 252) -> float:
    values = valid_prices(prices)
    return float(np.expm1(np.log(values.iloc[-1] / values.iloc[0]) * sessions / (len(values) - 1)))


def annualized_volatility(returns: pd.Series, sessions: int = 252) -> float:
    if len(returns) < 2 or not np.isfinite(returns).all():
        raise ValueError("At least two finite returns required.")
    return float(returns.std(ddof=1) * np.sqrt(sessions))


class ReturnMetrics(BaseModel):
    total_return: float
    annualized_return: float
    annualized_volatility: float
    observations: int


def summarize(prices: pd.Series) -> ReturnMetrics:
    returns = simple_returns(prices)
    return ReturnMetrics(
        total_return=float(cumulative_returns(prices).iloc[-1]),
        annualized_return=annualized_return(prices),
        annualized_volatility=annualized_volatility(returns),
        observations=len(returns),
    )


def rolling(prices: pd.Series, window: int = 20) -> pd.DataFrame:
    values = valid_prices(prices)
    returns = values.pct_change(fill_method=None)
    return pd.DataFrame(
        {
            "moving_average": values.rolling(window).mean(),
            "rolling_return": values.pct_change(window, fill_method=None),
            "rolling_volatility": returns.rolling(window).std(ddof=1) * np.sqrt(252),
            "drawdown": values / values.cummax() - 1,
        }
    )
