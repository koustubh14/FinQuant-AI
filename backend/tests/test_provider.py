from unittest.mock import MagicMock

import pytest
from app.core.exceptions import AnalysisError
from app.data.market_data import YahooProvider


def test_provider_cache_isolation_and_optional_failures(history, monkeypatch, tmp_path):
    monkeypatch.setattr("app.data.market_data.settings.data_dir", tmp_path)
    stock = MagicMock()
    stock.history.return_value = history
    stock.get_info.side_effect = RuntimeError("optional metadata failed")
    stock.get_news.side_effect = RuntimeError("optional news failed")
    monkeypatch.setattr("app.data.market_data.yf.Ticker", lambda *args, **kwargs: stock)
    market = YahooProvider()
    first = market.fetch("TEST", "2y")
    assert len(first.warnings) == 2
    first.history.iloc[0, 0] = 0
    second = market.fetch("TEST", "2y")
    assert second.cached
    assert second.history.iloc[0, 0] > 0
    assert stock.history.call_count == 1


def test_provider_retries_bounded_and_does_not_cache_failure(monkeypatch, tmp_path):
    monkeypatch.setattr("app.data.market_data.settings.data_dir", tmp_path)
    monkeypatch.setattr("app.data.market_data.time.sleep", lambda _: None)
    stock = MagicMock()
    stock.history.side_effect = TimeoutError("internal service detail")
    monkeypatch.setattr("app.data.market_data.yf.Ticker", lambda *args, **kwargs: stock)
    market = YahooProvider()
    with pytest.raises(AnalysisError, match="Market provider"):
        market.fetch("TEST", "2y")
    assert stock.history.call_count == 2
    assert not market._cache
