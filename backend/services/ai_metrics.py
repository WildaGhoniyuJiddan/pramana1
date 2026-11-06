"""Small in-process telemetry for AI calls.

No prompts, PII, or model responses are stored. Only counters, latency, and a
short error category are kept for operational transparency.
"""

import statistics
import threading
from typing import Any, Dict, List

from backend.services.ai_config import (
    GEMINI_MODEL,
    ai_enabled,
    get_ai_mode,
)

_lock = threading.Lock()
_calls = 0
_success = 0
_failures = 0
_guard_rejections = 0
_fallbacks = 0
_requests = 0
_verified_grounded = 0
_needs_clarification = 0
_out_of_scope = 0
_latencies: List[int] = []
_last_error = ""


def record_call() -> None:
    global _calls
    with _lock:
        _calls += 1


def record_success(latency_ms: int) -> None:
    global _success
    with _lock:
        _success += 1
        _latencies.append(max(0, int(latency_ms)))
        if len(_latencies) > 200:
            del _latencies[:-200]


def record_failure(error: str) -> None:
    global _failures, _last_error
    with _lock:
        _failures += 1
        _last_error = (error or "unknown")[:200]


def record_guard_rejection() -> None:
    global _guard_rejections
    with _lock:
        _guard_rejections += 1


def record_fallback() -> None:
    global _fallbacks
    with _lock:
        _fallbacks += 1


def record_resolution(mode: str) -> None:
    global _requests, _verified_grounded, _needs_clarification, _out_of_scope
    with _lock:
        _requests += 1
        if mode == "VERIFIED_GROUNDED":
            _verified_grounded += 1
        elif mode == "NEEDS_CLARIFICATION":
            _needs_clarification += 1
        else:
            _out_of_scope += 1


def snapshot() -> Dict[str, Any]:
    with _lock:
        average = int(statistics.mean(_latencies)) if _latencies else 0
        p95 = 0
        if _latencies:
            ordered = sorted(_latencies)
            index = min(len(ordered) - 1, int(round(0.95 * (len(ordered) - 1))))
            p95 = ordered[index]
        return {
            "mode": get_ai_mode(),
            "enabled": ai_enabled(),
            "model": GEMINI_MODEL,
            "model_name": GEMINI_MODEL,
            "calls": _calls,
            "success": _success,
            "failures": _failures,
            "guard_rejections": _guard_rejections,
            "guard_rejections_count": _guard_rejections,
            "fallbacks": _fallbacks,
            "total_requests": _requests,
            "verified_grounded_count": _verified_grounded,
            "needs_clarification_count": _needs_clarification,
            "out_of_scope_count": _out_of_scope,
            "avg_latency_ms": average,
            "p95_latency_ms": p95,
            "last_error": _last_error,
        }
