"""Run explicit live integration checks; writes measured evidence, never fixture data."""

import json
from datetime import datetime, timezone
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]


def main():
    evidence = {"executed_at": datetime.now(timezone.utc).isoformat(), "runs": []}
    with httpx.Client(base_url="http://127.0.0.1:8000", timeout=180) as client:
        evidence["health"] = client.get("/api/health").json()
        evidence["endpoint_statuses"] = {
            path: client.get(path).status_code
            for path in ["/api/models", "/api/methodology", "/openapi.json"]
        }
        for symbol in ["AAPL", "RELIANCE.NS"]:
            response = client.post("/api/analyze", json={"symbol": symbol, "include_ai": True})
            if response.status_code != 200:
                entry = {"symbol": symbol, "status": response.status_code, "error": response.json()}
            else:
                result = response.json()
                directory = ROOT / "data" / "examples"
                directory.mkdir(parents=True, exist_ok=True)
                (directory / f"{symbol}.json").write_text(
                    json.dumps(result, indent=2, allow_nan=False), encoding="utf-8"
                )
                entry = {
                    "symbol": symbol,
                    "status": 200,
                    "analysis_id": result["analysis_id"],
                    "company": result["company"],
                    "quality": result["quality"],
                    "returns": result["returns"],
                    "risk": result["risk"],
                    "models": result["forecast"]["models"],
                    "selected_model": result["forecast"]["selected_model"],
                    "selected_beats_naive_holdout": result["forecast"][
                        "selected_beats_naive_holdout"
                    ],
                    "validation_start": result["forecast"]["validation_start"],
                    "holdout_start": result["forecast"]["holdout_start"],
                    "holdout_end": result["forecast"]["holdout_end"],
                    "recommendation": result["recommendation"]["action"],
                    "ai_status": result["interpretation"]["status"],
                    "ai_message": result["interpretation"]["text"],
                    "warnings": result["warnings"],
                    "benchmark": None
                    if result["benchmark"] is None
                    else {
                        key: value for key, value in result["benchmark"].items() if key != "series"
                    },
                    "news_items": len(result["news"]),
                    "provenance": result["provenance"],
                    "roundtrip": client.get("/api/analysis/" + result["analysis_id"]).status_code
                    == 200,
                }
            evidence["runs"].append(entry)
            print(json.dumps(entry, allow_nan=False), flush=True)
        evidence["invalid_ticker_status"] = client.post(
            "/api/analyze", json={"symbol": "../bad"}
        ).status_code
        evidence["empty_input_status"] = client.post(
            "/api/analyze", json={"symbol": ""}
        ).status_code
        evidence["bad_body_status"] = client.post(
            "/api/analyze", json={"symbol": "AAPL", "forecast_horizon": 0}
        ).status_code
    directory = ROOT / "docs" / "results"
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "live_verification.json").write_text(
        json.dumps(evidence, indent=2, allow_nan=False), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
