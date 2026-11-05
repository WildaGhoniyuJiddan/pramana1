"""
Pramana AI Strict-RAG Backend API.
Entrypoint for Bali DigiFest 2026 AI Web Innovation Challenge.
"""

import logging
import os
import threading
import time
from typing import Dict, List

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.models.schemas import (
    TripBriefRequest,
    TripBriefResponse,
    ContextNoteRequest,
    ContextNoteResponse,
    CorpusResponse,
)
from backend.services.calendar_service import CALENDAR_COVERAGE
from backend.services.rag_engine import StrictRAGEngine
from backend.services.corpus_loader import CorpusManager

logger = logging.getLogger("pramana")

APP_VERSION = "1.2.0"
RATE_LIMIT_PATHS = {"/api/v1/trip-brief", "/api/v1/context-note"}
RATE_LIMIT_WINDOW_SECONDS = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))
RATE_LIMIT_MAX_REQUESTS = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "60"))
MAX_REQUEST_BODY_BYTES = int(os.getenv("MAX_REQUEST_BODY_BYTES", "65536"))
TRUST_PROXY_HEADERS = os.getenv("TRUST_PROXY_HEADERS", "false").strip().lower() in {
    "1", "true", "yes", "on",
}

_rate_lock = threading.Lock()
_rate_buckets: Dict[str, List[float]] = {}


def _allowed_origins() -> List[str]:
    raw = os.getenv(
        "CORS_ALLOW_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    )
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


def _client_key(request: Request) -> str:
    # Only trust proxy headers when the deployment explicitly enables it.
    # Otherwise a client can spoof X-Forwarded-For to bypass the rate limit.
    if TRUST_PROXY_HEADERS:
        forwarded = request.headers.get("x-forwarded-for", "")
        if forwarded:
            return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _allow_request(client_key: str) -> bool:
    """Small in-memory sliding-window limiter for the two expensive endpoints."""
    now = time.monotonic()
    with _rate_lock:
        bucket = [
            timestamp
            for timestamp in _rate_buckets.get(client_key, [])
            if now - timestamp < RATE_LIMIT_WINDOW_SECONDS
        ]
        if len(bucket) >= RATE_LIMIT_MAX_REQUESTS:
            _rate_buckets[client_key] = bucket
            return False

        bucket.append(now)
        _rate_buckets[client_key] = bucket

        # Prevent unbounded growth from many distinct client keys.
        if len(_rate_buckets) > 10000:
            stale_keys = [
                key for key, timestamps in _rate_buckets.items()
                if not timestamps or now - timestamps[-1] >= RATE_LIMIT_WINDOW_SECONDS
            ]
            for key in stale_keys:
                _rate_buckets.pop(key, None)

        return True


app = FastAPI(
    title="Pramana Strict-RAG API",
    version=APP_VERSION,
    description=(
        "Deterministic legal retrieval and abstention-first compliance "
        "assistance for Bali tourism. Output is educational, not legal advice."
    ),
)

# CORS is environment-driven. Wildcard origins are not combined with
# credentials, which browsers reject anyway.
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins(),
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
    max_age=600,
)

rag_engine = StrictRAGEngine()
corpus_manager = CorpusManager.get_instance()


@app.middleware("http")
async def security_and_rate_limit(request: Request, call_next):
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            if int(content_length) > MAX_REQUEST_BODY_BYTES:
                return JSONResponse(
                    status_code=413,
                    content={"detail": "Ukuran permintaan melebihi batas."},
                )
        except ValueError:
            return JSONResponse(
                status_code=400,
                content={"detail": "Header Content-Length tidak valid."},
            )

    if request.method == "POST" and request.url.path in RATE_LIMIT_PATHS:
        if not _allow_request(_client_key(request)):
            return JSONResponse(
                status_code=429,
                content={
                    "detail": (
                        "Terlalu banyak permintaan. Silakan coba lagi dalam "
                        "satu menit."
                    )
                },
                headers={"Retry-After": str(RATE_LIMIT_WINDOW_SECONDS)},
            )

    response = await call_next(request)

    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = (
        "geolocation=(), microphone=(), camera=()"
    )

    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store"
        response.headers["Content-Security-Policy"] = (
            "default-src 'none'; frame-ancestors 'none'"
        )

    return response


@app.get("/api/v1/health")
def healthcheck():
    stats = corpus_manager.get_stats()
    return {
        "status": "healthy",
        "service": "pramana-strict-rag",
        "version": APP_VERSION,
        "total_regulations_indexed": stats["total_regulations_indexed"],
        "total_documents_registered": stats["total_documents_registered"],
        "total_manifest_documents": stats["total_manifest_documents"],
        "corpus_version": corpus_manager.metadata.get("version"),
        "corpus_last_verified_date": corpus_manager.metadata.get(
            "last_verified_date"
        ),
        "calendar_coverage": CALENDAR_COVERAGE,
        "verification_scope": "corpus",
    }


@app.get("/api/v1/corpus", response_model=CorpusResponse)
def get_corpus():
    """Return registered regulations and legal tier metadata for UI transparency."""
    return {
        "metadata": corpus_manager.metadata,
        "tiers": corpus_manager.tiers,
        "regulations": corpus_manager.get_all(),
        "documents": corpus_manager.get_documents(),
    }


@app.post("/api/v1/trip-brief", response_model=TripBriefResponse)
def generate_trip_brief(req: TripBriefRequest):
    """
    Mode 1: Generate an itinerary-based compliance briefing.
    Detects Nyepi conflicts, retrieves relevant corpus articles, and formats
    WhatsApp / ICS outputs. Abstains when retrieval is not grounded.
    """
    try:
        return rag_engine.analyze_trip_itinerary(
            itinerary_text=req.itinerary_text,
            start_date=req.start_date,
            end_date=req.end_date,
            traveler_origin=req.traveler_origin,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception:
        logger.exception("trip-brief processing failed")
        raise HTTPException(
            status_code=500,
            detail=(
                "Terjadi kesalahan internal saat memproses trip brief. "
                "Silakan coba lagi."
            ),
        )


@app.post("/api/v1/context-note", response_model=ContextNoteResponse)
def generate_context_note(req: ContextNoteRequest):
    """
    Mode 2: Generate a neutral, verifiable Context Note for viral content.
    Identifies legal grounds, emotional framing, and returns corpus citations.
    """
    try:
        return rag_engine.analyze_viral_post(post_content=req.post_content)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception:
        logger.exception("context-note processing failed")
        raise HTTPException(
            status_code=500,
            detail=(
                "Terjadi kesalahan internal saat memproses catatan konteks. "
                "Silakan coba lagi."
            ),
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
