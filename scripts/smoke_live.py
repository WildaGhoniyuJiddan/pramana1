#!/usr/bin/env python3
"""
scripts/smoke_live.py - End-to-end smoke verification for Pramana deployment.
Validates live or local frontend & backend URLs:
- GET & HEAD health checks
- CORS preflight headers
- Trip Brief, Context Note, Smart Gate zones, and Corpus API endpoints
- Latency and JSON content verification
"""

import argparse
import json
import os
import sys
import time
import urllib.parse
import urllib.request
import urllib.error

DEFAULT_FRONTEND_URL = os.getenv("FRONTEND_URL", "https://pramana1.vercel.app").rstrip("/")
DEFAULT_BACKEND_URL = os.getenv("BACKEND_URL", "https://pramana1.onrender.com").rstrip("/")


def request(url: str, method: str = "GET", headers: dict = None, data: dict = None, timeout: float = 15.0):
    headers = headers or {}
    body = None
    if data is not None:
        body = json.dumps(data).encode("utf-8")
        headers.setdefault("Content-Type", "application/json")

    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    start_time = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            latency = (time.monotonic() - start_time) * 1000
            resp_bytes = response.read()
            content_type = response.headers.get("Content-Type", "")
            return {
                "status": response.status,
                "latency_ms": latency,
                "headers": dict(response.headers),
                "body_bytes": resp_bytes,
                "content_type": content_type,
            }
    except urllib.error.HTTPError as exc:
        latency = (time.monotonic() - start_time) * 1000
        resp_bytes = exc.read()
        return {
            "status": exc.code,
            "latency_ms": latency,
            "headers": dict(exc.headers),
            "body_bytes": resp_bytes,
            "content_type": exc.headers.get("Content-Type", ""),
            "error": str(exc),
        }
    except Exception as exc:
        latency = (time.monotonic() - start_time) * 1000
        return {
            "status": 0,
            "latency_ms": latency,
            "headers": {},
            "body_bytes": b"",
            "content_type": "",
            "error": str(exc),
        }


def run_smoke(backend_url: str, frontend_url: str, check_ai_enabled: bool = False):
    print(f"=== PRAMANA LIVE SMOKE VERIFICATION ===")
    print(f"Backend URL:  {backend_url}")
    print(f"Frontend URL: {frontend_url}")
    print("-" * 50)

    failures = []

    # 1. Healthcheck GET & HEAD
    print("[1/6] Checking health endpoints (GET and HEAD)...")
    for method in ["HEAD", "GET"]:
        res = request(f"{backend_url}/api/v1/health", method=method)
        if res["status"] != 200:
            msg = f"{method} /api/v1/health failed with status {res['status']}: {res.get('error')}"
            failures.append(msg)
            print(f"  [FAIL] {msg}")
        else:
            print(f"  [OK] {method} /api/v1/health OK ({res['latency_ms']:.1f}ms)")
            if method == "GET":
                try:
                    data = json.loads(res["body_bytes"].decode("utf-8"))
                    if check_ai_enabled and not data.get("ai_enabled"):
                        failures.append("ai_enabled is False in production healthcheck")
                        print("  [FAIL] ai_enabled is False in healthcheck response!")
                    else:
                        print(f"    ai_mode: {data.get('ai_mode')}, ai_enabled: {data.get('ai_enabled')}")
                except Exception as e:
                    failures.append(f"Invalid JSON from health: {e}")
                    print(f"  [FAIL] Invalid JSON: {e}")

    # 2. CORS Preflight
    print("\n[2/6] Checking CORS Preflight from frontend origin...")
    cors_headers = {
        "Origin": frontend_url,
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "Content-Type",
    }
    res = request(f"{backend_url}/api/v1/trip-brief", method="OPTIONS", headers=cors_headers)
    allow_origin = res["headers"].get("access-control-allow-origin", res["headers"].get("Access-Control-Allow-Origin", ""))
    if allow_origin not in [frontend_url, "*"]:
        msg = f"CORS preflight failed: Allow-Origin is '{allow_origin}', expected '{frontend_url}'"
        failures.append(msg)
        print(f"  [FAIL] {msg}")
    else:
        print(f"  [OK] CORS Preflight OK: Allow-Origin: {allow_origin} ({res['latency_ms']:.1f}ms)")

    # 3. Trip Brief (Mode 1)
    print("\n[3/6] Testing Mode 1: Trip Brief (Bilingual test)...")
    trip_payload_en = {
        "itinerary_text": "Visiting Besakih Temple and hiking Mount Batur in late March",
        "start_date": "2026-03-24",
        "end_date": "2026-03-26",
        "traveler_origin": "international",
        "lang": "en"
    }
    res = request(f"{backend_url}/api/v1/trip-brief", method="POST", data=trip_payload_en, timeout=25.0)
    if res["status"] != 200:
        msg = f"Trip Brief failed with status {res['status']}: {res.get('error')}"
        failures.append(msg)
        print(f"  [FAIL] {msg}")
    else:
        try:
            data = json.loads(res["body_bytes"].decode("utf-8"))
            items = data.get("briefing_items", [])
            print(f"  [OK] Trip Brief OK ({res['latency_ms']:.1f}ms) - {len(items)} items, Nyepi flag: {data.get('nyepi_conflict')}")
            # Parity check
            if items:
                assert "display_text" in items[0], "display_text missing from BriefingItem"
                assert "text_original" in items[0], "text_original missing from BriefingItem"
                print(f"    display_title: {items[0].get('display_title')[:45]}...")
        except Exception as e:
            failures.append(f"Trip Brief response validation error: {e}")
            print(f"  [FAIL] Validation error: {e}")

    # 4. Context Note (Mode 2)
    print("\n[4/6] Testing Mode 2: Context Note...")
    note_payload = {
        "post_content": "Foreign tourist detained for posing unclothed near sacred banyan tree in Tabanan.",
        "lang": "en"
    }
    res = request(f"{backend_url}/api/v1/context-note", method="POST", data=note_payload, timeout=25.0)
    if res["status"] != 200:
        msg = f"Context Note failed with status {res['status']}: {res.get('error')}"
        failures.append(msg)
        print(f"  [FAIL] {msg}")
    else:
        try:
            data = json.loads(res["body_bytes"].decode("utf-8"))
            citations = data.get("citations", [])
            print(f"  [OK] Context Note OK ({res['latency_ms']:.1f}ms) - {len(citations)} citations")
        except Exception as e:
            failures.append(f"Context Note validation error: {e}")
            print(f"  [FAIL] Validation error: {e}")

    # 5. Smart Gate Zones (Mode 3)
    print("\n[5/6] Testing Smart Gate 3 zones...")
    zones = ["pura-besakih", "pantai-melasti", "bandara-ngurah-rai"]
    for z in zones:
        res = request(f"{backend_url}/api/v1/totem/{z}?lang=en")
        if res["status"] != 200:
            msg = f"Totem zone '{z}' failed with status {res['status']}: {res.get('error')}"
            failures.append(msg)
            print(f"  [FAIL] {msg}")
        else:
            try:
                data = json.loads(res["body_bytes"].decode("utf-8"))
                cit_count = len(data.get("citations", []))
                print(f"  [OK] Zone '{z}' OK ({res['latency_ms']:.1f}ms) - {cit_count} citations")
            except Exception as e:
                failures.append(f"Zone '{z}' JSON error: {e}")
                print(f"  [FAIL] JSON error: {e}")

    # 6. Corpus Explorer
    print("\n[6/6] Testing Corpus endpoint...")
    res = request(f"{backend_url}/api/v1/corpus")
    if res["status"] != 200:
        msg = f"Corpus endpoint failed with status {res['status']}: {res.get('error')}"
        failures.append(msg)
        print(f"  [FAIL] {msg}")
    else:
        try:
            data = json.loads(res["body_bytes"].decode("utf-8"))
            reg_count = len(data.get("regulations", []))
            doc_count = len(data.get("documents", []))
            print(f"  [OK] Corpus OK ({res['latency_ms']:.1f}ms) - {reg_count} regulations, {doc_count} documents")
        except Exception as e:
            failures.append(f"Corpus JSON error: {e}")
            print(f"  [FAIL] JSON error: {e}")

    print("-" * 50)
    if failures:
        print(f"FAILED with {len(failures)} error(s):")
        for f in failures:
            print(f" - {f}")
        return False
    else:
        print("ALL SMOKE TESTS PASSED!")
        return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pramana Live Smoke Tests")
    parser.add_argument("--backend", default=DEFAULT_BACKEND_URL, help="Backend API base URL")
    parser.add_argument("--frontend", default=DEFAULT_FRONTEND_URL, help="Frontend origin URL for CORS")
    parser.add_argument("--check-ai-enabled", action="store_true", help="Fail if ai_enabled is False")
    args = parser.parse_args()

    success = run_smoke(args.backend, args.frontend, args.check_ai_enabled)
    sys.exit(0 if success else 1)
