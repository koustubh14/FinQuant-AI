import json
from datetime import datetime, timezone

import httpx
import pytest
from app.ai.analyst import interpret
from app.core.config import Settings
from app.core.exceptions import AnalysisError
from app.data.market_data import MarketBundle
from app.main import app, provider, store
from app.services.storage import AnalysisStore
from fastapi.testclient import TestClient


@pytest.fixture
def client(history, tmp_path):
    class FakeProvider:
        def search(self, query):
            return []

        def fetch(self, symbol, period, optional=True):
            if symbol == "BAD":
                raise AnalysisError("Provider unavailable.", "provider_unavailable", 503)
            if symbol == "EMPTY":
                return MarketBundle(history.iloc[:0], {}, [], "", [])
            return MarketBundle(history.copy(), {}, [], datetime.now(timezone.utc).isoformat(), [])

    app.dependency_overrides[provider] = FakeProvider
    app.dependency_overrides[store] = lambda: AnalysisStore(tmp_path / "test.sqlite3")
    with TestClient(app, raise_server_exceptions=False) as connection:
        yield connection
    app.dependency_overrides.clear()


@pytest.mark.parametrize("symbol", ["AAPL", "RELIANCE.NS"])
def test_api_pipeline_and_roundtrip(client, symbol):
    response = client.post("/api/analyze", json={"symbol": symbol})
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["company"]["symbol"] == symbol
    assert result["interpretation"]["status"] == "disabled"
    assert len(result["forecast"]["predictions"]) == 30
    assert result["recommendation"]["action"] in ["BUY", "HOLD", "SELL"]
    assert result["company"]["market_cap"] is None
    json.dumps(result, allow_nan=False)
    assert client.get("/api/analysis/" + result["analysis_id"]).json() == result


def test_api_errors(client):
    assert client.get("/api/health").status_code == 200
    assert client.get("/openapi.json").status_code == 200
    for body in [
        {"symbol": ""},
        {"symbol": "AAPL", "forecast_horizon": 0},
        {"symbol": "AAPL", "period": "forever"},
        {"symbol": "../bad"},
        {"symbol": "EMPTY"},
        {"symbol": "AAPL", "extra": 1},
    ]:
        assert client.post("/api/analyze", json=body).status_code == 422
    assert client.post("/api/analyze", json={"symbol": "BAD"}).status_code == 503
    assert client.get("/api/analysis/00000000-0000-0000-0000-000000000000").status_code == 404


def test_ai_missing_key_and_network_failure(monkeypatch):
    assert interpret({}, Settings(gemini_api_key=""), True).status == "unconfigured"

    def fail(*args, **kwargs):
        raise httpx.ConnectError("private internal detail")

    monkeypatch.setattr(httpx, "post", fail)
    result = interpret({}, Settings(gemini_api_key="test-placeholder"), True)
    assert result.status == "unavailable"
    assert "private" not in result.text


def test_llm_cannot_replace_recommendation(client, monkeypatch):
    from app.schemas.analysis import Interpretation

    monkeypatch.setattr(
        "app.services.analysis.interpret",
        lambda *args: Interpretation(status="generated", text="BUY with invented 99% confidence"),
    )
    result = client.post("/api/analyze", json={"symbol": "AAPL", "include_ai": True}).json()
    assert result["recommendation"]["action"] == "HOLD"  # stale fixture forces Python HOLD
    assert result["interpretation"]["text"].startswith("BUY")
    # Narrative is unverified display text, never parsed into the numerical schema.


def test_persistence_failure_preserves_result(client):
    class FailingStore:
        def save(self, result):
            raise OSError("private disk path")

    app.dependency_overrides[store] = FailingStore
    response = client.post("/api/analyze", json={"symbol": "AAPL"})
    assert response.status_code == 200
    assert any("Persistence unavailable" in w for w in response.json()["warnings"])
    assert "private disk" not in response.text


def test_unexpected_provider_error_is_sanitized(client):
    class BrokenProvider:
        def search(self, query):
            return []

        def fetch(self, *args, **kwargs):
            raise RuntimeError("private credential text")

    app.dependency_overrides[provider] = BrokenProvider
    response = client.post("/api/analyze", json={"symbol": "AAPL"})
    assert response.status_code == 500
    assert "private credential" not in response.text


@pytest.mark.parametrize("mode", ["missing", "success", "invalid_key", "network_failure"])
def test_ai_modes_preserve_complete_quantitative_analysis(client, monkeypatch, mode):
    monkeypatch.setattr(
        "app.main.settings.gemini_api_key", "" if mode == "missing" else "unit-test-placeholder"
    )

    def mock_post(url, **kwargs):
        assert kwargs["timeout"] == 20
        assert "systemInstruction" in kwargs["json"]
        assert "unit-test-placeholder" not in url
        if mode == "network_failure":
            raise httpx.ConnectError("private error detail")
        return httpx.Response(
            403 if mode == "invalid_key" else 200,
            request=httpx.Request("POST", url),
            json={
                "candidates": [{"content": {"parts": [{"text": "Research interpretation only."}]}}]
            },
        )

    monkeypatch.setattr(httpx, "post", mock_post)
    response = client.post("/api/analyze", json={"symbol": "AAPL", "include_ai": True})
    assert response.status_code == 200
    result = response.json()
    assert all(result[key] for key in ["returns", "risk", "forecast", "recommendation"])
    expected = {
        "missing": "unconfigured",
        "success": "generated",
        "invalid_key": "unavailable",
        "network_failure": "unavailable",
    }
    assert result["interpretation"]["status"] == expected[mode]
    assert "private error" not in response.text


def test_invalid_benchmark_is_optional_and_warning_is_persisted(client, history):
    class BenchmarkFailure:
        def search(self, query):
            return []

        def fetch(self, symbol, period, optional=True):
            frame = history.copy()
            if symbol.startswith("^"):
                frame.iloc[30, 3] = float("nan")
            return MarketBundle(frame, {}, [], datetime.now(timezone.utc).isoformat(), [])

    app.dependency_overrides[provider] = BenchmarkFailure
    result = client.post("/api/analyze", json={"symbol": "RELIANCE.NS"}).json()
    assert result["benchmark"] is None
    assert result["recommendation"]["signals"][-1]["score"] is None
    assert any("benchmark data failed quality validation" in w for w in result["warnings"])
    saved = client.get("/api/analysis/" + result["analysis_id"]).json()
    assert saved["warnings"] == result["warnings"]
