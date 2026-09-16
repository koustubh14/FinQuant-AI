import json
import logging
import threading
import time
from functools import lru_cache
from uuid import UUID

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app import __version__
from app.core.config import settings
from app.core.exceptions import AnalysisError
from app.data.market_data import YahooProvider
from app.forecasting.models import MODELS
from app.schemas.analysis import AnalysisResult, AnalyzeRequest
from app.services.analysis import analyze
from app.services.storage import AnalysisStore

logger = logging.getLogger("finquant")
logging.basicConfig(level=logging.INFO, format="%(message)s")
app = FastAPI(
    title="FinQuant AI",
    version=__version__,
    description="Quantitative research with optional AI interpretation.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)
capacity = threading.BoundedSemaphore(4)


@lru_cache
def provider():
    return YahooProvider()


@lru_cache
def store():
    if not settings.persistence_enabled:
        return None
    return AnalysisStore(settings.data_dir / "analyses.sqlite3")


@app.middleware("http")
async def request_log(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    logger.info(
        json.dumps(
            {
                "event": "http_request",
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "seconds": round(time.perf_counter() - start, 4),
            }
        )
    )
    return response


@app.exception_handler(AnalysisError)
async def analysis_error(request: Request, exc: AnalysisError):
    return JSONResponse(
        status_code=exc.status, content={"error": {"code": exc.code, "message": str(exc)}}
    )


@app.exception_handler(Exception)
async def unexpected_error(request: Request, exc: Exception):
    logger.error(json.dumps({"event": "unexpected_error", "type": type(exc).__name__}))
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "internal_error",
                "message": "Analysis failed unexpectedly. Check server logs; no partial result was saved.",
            }
        },
    )


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "service": "FinQuant AI",
        "version": __version__,
        "ai_configured": bool(settings.gemini_api_key),
        "persistence_enabled": settings.persistence_enabled,
    }


@app.get("/api/models")
def models():
    return MODELS


@app.get("/api/methodology")
def methodology():
    return {
        "annualization": 252,
        "price_basis": "Adjusted close; raw OHLCV retained separately",
        "risk": "Daily 95% historical loss VaR and tail-mean ES; sample volatility; geometric annual return",
        "forecast": "Full-horizon expanding folds; earlier validation selects; separate holdout reports",
        "recommendation": "Equal-weight deterministic votes; score ≥0.4 BUY, ≤-0.4 SELL, otherwise HOLD",
        "confidence": "Signal agreement, not a probability",
        "ai": "Optional narrative; cannot modify numeric fields",
    }


@app.post("/api/analyze", response_model=AnalysisResult)
def run_analysis(request: AnalyzeRequest, market=Depends(provider), database=Depends(store)):
    if not capacity.acquire(blocking=False):
        raise AnalysisError("Analysis capacity reached. Retry shortly.", "busy", 429)
    try:
        result = analyze(request, market, settings)
        json.dumps(result.model_dump(mode="json"), allow_nan=False)
        if database is None:
            result.warnings.append(
                "Saved analyses are disabled on this deployment. Download the run JSON to keep it; "
                "reloading this page will not restore the result."
            )
        else:
            try:
                result.snapshot_saved = True
                database.save(result)
            except Exception:
                result.snapshot_saved = False
                result.warnings.append(
                    "Persistence unavailable. Download this result now; retrieval by ID is unavailable."
                )
        return result
    except (ValueError, ArithmeticError) as exc:
        raise AnalysisError(
            "Numerical analysis is undefined for this history. Review the data quality and requested horizon.",
            "numerical_error",
        ) from exc
    finally:
        capacity.release()


@app.get("/api/analysis/{analysis_id}", response_model=AnalysisResult)
def saved_analysis(analysis_id: UUID, database=Depends(store)):
    if database is None:
        raise AnalysisError(
            "Saved analyses are disabled on this deployment. Run a new analysis or use your downloaded JSON.",
            "persistence_disabled",
            503,
        )
    result = database.get(str(analysis_id))
    if result is None:
        raise AnalysisError("Analysis ID not found.", "not_found", 404)
    return result
