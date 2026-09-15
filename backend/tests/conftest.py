import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def history():
    """Deterministic synthetic test fixture; never presented as observed market data."""
    rng = np.random.default_rng(2026)
    prices = 100 * np.exp(np.cumsum(rng.normal(0.0003, 0.012, 520)))
    return pd.DataFrame(
        {
            "Open": prices,
            "High": prices * 1.01,
            "Low": prices * 0.99,
            "Close": prices,
            "Adj Close": prices,
            "Volume": 1000.0,
        },
        index=pd.bdate_range("2023-01-02", periods=len(prices)),
    )
