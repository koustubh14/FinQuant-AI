import copy
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timezone

import pandas as pd
import yfinance as yf
from app.core.config import settings
from app.core.exceptions import AnalysisError
from curl_cffi import requests


@dataclass
class MarketBundle:
    history: pd.DataFrame
    metadata: dict
    news: list[dict]
    fetched_at: str
    warnings: list[str]
    cached: bool = False


class YahooProvider:
    """Bounded in-process cache. Failure entries are never cached."""

    def __init__(self, ttl: int = 900):
        self.ttl = ttl
        self._cache: dict[tuple, tuple[float, MarketBundle]] = {}
        self._lock = threading.Lock()
        settings.data_dir.mkdir(parents=True, exist_ok=True)
        yf.set_tz_cache_location(str(settings.data_dir / "yfinance"))

    @staticmethod
    def _session():
        return requests.Session(impersonate="chrome", timeout=10)

    def search(self, query: str) -> list[dict]:
        try:
            with self._session() as session:
                return yf.Search(
                    query, max_results=6, news_count=0, session=session, timeout=10
                ).quotes
        except Exception as exc:
            raise AnalysisError(
                "Ticker search is unavailable. Enter an exact exchange ticker.",
                "provider_unavailable",
                503,
            ) from exc

    def fetch(self, symbol: str, period: str, optional: bool = True) -> MarketBundle:
        key = (symbol, period, optional)
        with self._lock:
            found = self._cache.get(key)
            if found and time.monotonic() - found[0] < self.ttl:
                bundle = copy.deepcopy(found[1])
                bundle.cached = True
                return bundle
        warnings = []
        with self._session() as session:
            stock = yf.Ticker(symbol, session=session)
            history = None
            for attempt in range(2):
                try:
                    history = stock.history(
                        period=period,
                        auto_adjust=False,
                        actions=False,
                        repair=False,
                        keepna=True,
                        timeout=10,
                        raise_errors=True,
                    )
                    break
                except Exception as exc:
                    if attempt:
                        raise AnalysisError(
                            "Market provider unavailable or ticker has no history. "
                            "Check the listing and retry later.",
                            "provider_unavailable",
                            503,
                        ) from exc
                    time.sleep(0.3)
            if history is None or history.empty:
                raise AnalysisError(
                    "No market history for this ticker. Check the exchange suffix.",
                    "no_history",
                    404,
                )
            metadata, news = {}, []
            if optional:
                try:
                    metadata = stock.get_info() or {}
                except Exception:
                    warnings.append("Optional company metadata unavailable.")
                try:
                    for item in stock.get_news(count=6) or []:
                        content = item.get("content", item)
                        url = (content.get("canonicalUrl") or {}).get("url")
                        if content.get("title"):
                            news.append(
                                {
                                    "headline": content["title"],
                                    "source": (content.get("provider") or {}).get("displayName"),
                                    "date": content.get("pubDate"),
                                    "url": url if url and url.startswith("https://") else None,
                                    "summary": content.get("summary") or None,
                                }
                            )
                except Exception:
                    warnings.append("Optional news unavailable.")
        bundle = MarketBundle(
            history, metadata, news, datetime.now(timezone.utc).isoformat(), warnings
        )
        with self._lock:
            if len(self._cache) >= 32:
                self._cache.pop(next(iter(self._cache)))
            self._cache[key] = (time.monotonic(), copy.deepcopy(bundle))
        return bundle
