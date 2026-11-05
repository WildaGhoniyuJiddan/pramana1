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
    monkeypatch.setenv("AI_MODE", "optional")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)


def test_healthcheck_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "1.4.0"
    assert data["total_regulations_indexed"] == 40
    assert data["total_documents_registered"] == 29
    assert data["total_manifest_documents"] == 21
    assert data["total_smart_gate_zones"] == 3
    assert data["smart_gate_version"] == "1.0.0"
    assert data["corpus_version"] == "1.3.0"
    assert data["ai_mode"] == "optional"
    assert data["ai_enabled"] is False
    assert data["ai_model"] == "gemini-3.1-flash-lite"
    assert data["calendar_coverage"] == "2025-2028"
    assert data["verification_scope"] == "corpus"


def test_ai_status_endpoint():
    response = client.get("/api/v1/ai/status")
    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "optional"
    assert data["enabled"] is False
    assert data["model"] == "gemini-3.1-flash-lite"
    assert "calls" in data
    assert "guard_rejections" in data
    assert "last_error" in data
    assert data["hybrid_retrieval_available"] is False
    assert data["embedding_vectors_loaded"] == 40


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
    assert data["metadata"]["version"] == "1.3.0"
    assert len(data["regulations"]) == 40
    assert len(data["documents"]) == 29

    documents_by_id = {doc["id"]: doc for doc in data["documents"]}
    for regulation in data["regulations"]:
        assert regulation["document_id"] in documents_by_id
        document = documents_by_id[regulation["document_id"]]
        assert regulation["id"] in document["regulation_ids"]
        assert document["retrieval_eligible"] is True

    tourism_law = documents_by_id["uu-18-2025"]
    assert tourism_law["text_status"] == "verbatim-ocr-dibersihkan"
    assert tourism_law["retrieval_eligible"] is True
    assert len(tourism_law["regulation_ids"]) == 7


def test_zone_list_endpoint():
    response = client.get("/api/v1/zones")
    assert response.status_code == 200
    data = response.json()
    assert data["metadata"]["version"] == "1.0.0"
    assert len(data["zones"]) == 3
    assert {zone["id"] for zone in data["zones"]} == {
        "bandara-ngurah-rai",
        "pura-besakih",
        "pantai-melasti",
    }
    for zone in data["zones"]:
        assert zone["name"]["id"]
        assert zone["name"]["en"]


def test_totem_card_endpoint():
    response = client.get("/api/v1/totem/bandara-ngurah-rai?lang=en")
    assert response.status_code == 200
    data = response.json()

    assert data["zone"]["id"] == "bandara-ngurah-rai"
    assert data["zone"]["name"] == "I Gusti Ngurah Rai Airport"
    assert data["language"] == "en"
    assert len(data["citations"]) == 3
    assert data["historical_citations"] == []
    assert data["tts_text"]
    for citation in data["citations"]:
        assert citation["verified_layer1"] is True
        assert citation["text_status"] == "verbatim"


def test_totem_card_keeps_historical_references_separate():
    response = client.get("/api/v1/totem/pura-besakih?lang=id")
    assert response.status_code == 200
    data = response.json()

    assert len(data["citations"]) == 2
    assert len(data["historical_citations"]) == 2
    assert all(
        citation["status"] == "Disempurnakan"
        for citation in data["historical_citations"]
    )


def test_totem_unknown_zone_returns_404():
    response = client.get("/api/v1/totem/gerbang-tidak-ada")
    assert response.status_code == 404


def test_totem_invalid_language_returns_422():
    response = client.get("/api/v1/totem/bandara-ngurah-rai?lang=fr")
    assert response.status_code == 422


def test_totem_brief_endpoint_uses_deterministic_fallback():
    response = client.post(
        "/api/v1/totem/bandara-ngurah-rai/brief",
        json={"lang": "en"},
    )
    assert response.status_code == 200
    data = response.json()

    assert data["zone_id"] == "bandara-ngurah-rai"
    assert data["language"] == "en"
    assert data["ai_synthesis_status"] == "deterministic"
    assert data["guard_status"] == "FALLBACK_DETERMINISTIK"
    assert data["brief"]
    assert data["brief_id"]
    assert data["brief_en"]
    assert data["claims"] == []
    assert data["rejected_claims"] == 0
    assert len(data["citation_ids"]) == 3


def test_totem_brief_is_rate_limited(monkeypatch):
    monkeypatch.setattr(main_module, "RATE_LIMIT_MAX_REQUESTS", 1)
    monkeypatch.setattr(main_module, "RATE_LIMIT_WINDOW_SECONDS", 60)
    main_module._rate_buckets.clear()

    first = client.post(
        "/api/v1/totem/bandara-ngurah-rai/brief",
        json={"lang": "id"},
    )
    second = client.post(
        "/api/v1/totem/bandara-ngurah-rai/brief",
        json={"lang": "id"},
    )

    assert first.status_code == 200
    assert second.status_code == 429
    main_module._rate_buckets.clear()


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
    assert data["ai_synthesis_status"] == "deterministic"
    assert data["ai_guard_status"] == "FALLBACK_DETERMINISTIK"
    assert data["ai_claims"] == []
    assert data["ai_synthesis_en"]
    for item in data["briefing_items"]:
        assert item["document_id"]
        assert item["text_status"] in {
            "verbatim", "verbatim-ocr-dibersihkan", "compilation",
        }
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
    assert data["ai_synthesis_status"] == "deterministic"
    assert data["ai_guard_status"] == "FALLBACK_DETERMINISTIK"
    assert data["ai_claims"] == []
    assert data["neutral_summary_en"]
    for citation in data["citations"]:
        assert citation["verified_layer1"] is True
        assert len(citation["quote_sha256"]) == 64
        assert citation["document_id"]
        assert citation["text_status"] in {
            "verbatim", "verbatim-ocr-dibersihkan", "compilation",
        }


def test_context_note_abstain_endpoint():
    response = client.post(
        "/api/v1/context-note",
        json={"post_content": "Kucing oranye tertidur di atas laptop."},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "TIDAK_DITEMUKAN"
    assert data["citations"] == []
    assert data["ai_synthesis_status"] == "abstain"
    assert data["ai_claims"] == []
    assert data["neutral_summary_en"]


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
