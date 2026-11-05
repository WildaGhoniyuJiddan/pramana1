"""
Integration tests for FastAPI endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from starlette.requests import Request

from backend import main as main_module
from backend.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def _disable_gemini(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)


def test_healthcheck_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "1.2.0"
    assert data["total_regulations_indexed"] == 10
    assert data["total_documents_registered"] == 22
    assert data["total_manifest_documents"] == 21
    assert data["corpus_version"] == "1.2.0"
    assert data["calendar_coverage"] == "2025-2028"
    assert data["verification_scope"] == "corpus"


def test_security_headers_present():
    response = client.get("/api/v1/health")
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "no-referrer"
    assert response.headers["cache-control"] == "no-store"


def test_get_corpus_endpoint():
    response = client.get("/api/v1/corpus")
    assert response.status_code == 200
    data = response.json()
    assert "metadata" in data
    assert "tiers" in data
    assert data["metadata"]["version"] == "1.2.0"
    assert len(data["regulations"]) == 10
    assert len(data["documents"]) == 22

    documents_by_id = {doc["id"]: doc for doc in data["documents"]}
    for regulation in data["regulations"]:
        assert regulation["document_id"] in documents_by_id
        document = documents_by_id[regulation["document_id"]]
        assert regulation["id"] in document["regulation_ids"]
        assert document["retrieval_eligible"] is True

    tourism_law = documents_by_id["uu-18-2025"]
    assert tourism_law["text_status"] == "belum-diambil"
    assert tourism_law["retrieval_eligible"] is False


def test_trip_brief_endpoint():
    payload = {
        "itinerary_text": "Liburan ke Pura Besakih dan belanja di Ubud",
        "start_date": "2026-05-10",
        "end_date": "2026-05-15",
        "traveler_origin": "international",
    }
    response = client.post("/api/v1/trip-brief", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "SUCCESS"
    assert data["guard_status"] == "TERVERIFIKASI"
    assert len(data["briefing_items"]) > 0
    assert "ics_content" in data
    assert data["ics_content"].startswith("BEGIN:VCALENDAR")
    assert "ics_calendar" not in data
    assert "whatsapp_text" in data
    assert data["verification_scope"] == "corpus"
    assert data["confidence"] in {"SEDANG", "RENDAH"}
    assert data["disclaimer"]
    for item in data["briefing_items"]:
        assert item["document_id"]
        assert item["text_status"] in {"verbatim", "compilation"}
        assert item["source_type"]


def test_context_note_endpoint():
    payload = {
        "post_content": (
            "Viral video bule memanjat pohon suci pura di Tabanan tanpa busana"
        )
    }
    response = client.post("/api/v1/context-note", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "TERVERIFIKASI"
    assert len(data["citations"]) > 0
    assert "copyable_comment" in data
    assert data["verification_scope"] == "corpus"
    assert data["confidence"] in {"SEDANG", "RENDAH"}
    assert data["disclaimer"]
    for citation in data["citations"]:
        assert citation["verified_layer1"] is True
        assert len(citation["quote_sha256"]) == 64
        assert citation["document_id"]
        assert citation["text_status"] in {"verbatim", "compilation"}


def test_context_note_abstain_endpoint():
    response = client.post(
        "/api/v1/context-note",
        json={"post_content": "Kucing oranye tertidur di atas laptop."},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "TIDAK_DITEMUKAN"
    assert data["citations"] == []


@pytest.mark.parametrize(
    "payload",
    [
        {"itinerary_text": "Liburan", "start_date": "2026-02-30"},
        {"itinerary_text": "Liburan", "start_date": "2026-13-01"},
        {"itinerary_text": "Liburan", "start_date": "2026-03-10", "end_date": "2026-03-01"},
        {"itinerary_text": "   ", "start_date": "2026-03-10"},
        {"itinerary_text": "Liburan", "start_date": "2026-03-10", "traveler_origin": "mars"},
    ],
)
def test_trip_brief_validation_errors(payload):
    response = client.post("/api/v1/trip-brief", json=payload)
    assert response.status_code == 422


def test_context_note_rejects_blank_text():
    response = client.post("/api/v1/context-note", json={"post_content": "   "})
    assert response.status_code == 422


def test_oversized_request_is_rejected_before_parsing():
    response = client.post(
        "/api/v1/trip-brief",
        content=b"x" * (main_module.MAX_REQUEST_BODY_BYTES + 1024),
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 413


def test_rate_limiter_blocks_after_limit(monkeypatch):
    monkeypatch.setattr(main_module, "RATE_LIMIT_MAX_REQUESTS", 2)
    monkeypatch.setattr(main_module, "RATE_LIMIT_WINDOW_SECONDS", 60)

    key = "test-rate-limit-key"
    assert main_module._allow_request(key) is True
    assert main_module._allow_request(key) is True
    assert main_module._allow_request(key) is False


def _request_with_forwarded_header() -> Request:
    return Request(
        {
            "type": "http",
            "method": "POST",
            "path": "/api/v1/trip-brief",
            "headers": [(b"x-forwarded-for", b"198.51.100.7, 10.0.0.1")],
            "client": ("203.0.113.5", 12345),
        }
    )


def test_client_key_ignores_forwarded_header_by_default(monkeypatch):
    monkeypatch.setattr(main_module, "TRUST_PROXY_HEADERS", False)
    assert main_module._client_key(_request_with_forwarded_header()) == "203.0.113.5"


def test_client_key_uses_forwarded_header_when_trusted(monkeypatch):
    monkeypatch.setattr(main_module, "TRUST_PROXY_HEADERS", True)
    assert main_module._client_key(_request_with_forwarded_header()) == "198.51.100.7"
