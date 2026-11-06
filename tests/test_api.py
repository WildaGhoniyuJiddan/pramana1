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
    for path in ["/", "/health", "/api/v1/health"]:
        response = client.get(path)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        head_res = client.head(path)
        assert head_res.status_code == 200
    assert data["version"] == "1.4.0"
    assert data["total_regulations_indexed"] == 42
    assert data["total_documents_registered"] == 29
    assert data["total_manifest_documents"] == 21
    assert data["total_smart_gate_zones"] == 3
    assert data["smart_gate_version"] == "1.0.0"
    assert data["corpus_version"] == "1.3.0"
    assert data["ai_mode"] == "optional"
    assert data["ai_enabled"] is False
    assert data["ai_model"] == main_module.GEMINI_MODEL
    assert data["calendar_coverage"] == "2025-2028"
    assert data["verification_scope"] == "corpus"


def test_ai_status_endpoint():
    response = client.get("/api/v1/ai/status")
    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "optional"
    assert data["enabled"] is False
    assert data["model"] == main_module.GEMINI_MODEL
    assert "calls" in data
    assert "guard_rejections" in data
    assert "last_error" in data
    assert data["hybrid_retrieval_available"] is False
    assert data["embedding_vectors_loaded"] in {0, 40, 42}
    assert data["ai_mode"] == "optional"
    assert data["model_name"] == main_module.GEMINI_MODEL
    assert data["model_chain"][0] == main_module.GEMINI_MODEL
    assert data["api_key_configured"] is False
    assert data["active_chunks_count"] in {40, 42}
    assert data["registry_docs_count"] == 4
    assert data["epistemic_routing_enabled"] is True
    assert "total_requests" in data
    assert "verified_grounded_count" in data
    assert "needs_clarification_count" in data
    assert "out_of_scope_count" in data
    assert "guard_rejections_count" in data


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
    assert len(data["regulations"]) == 42
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
    assert "public_base_url" in data
    assert {zone["id"] for zone in data["zones"]} == {
        "bandara-ngurah-rai",
        "pura-besakih",
        "pantai-melasti",
    }
    for zone in data["zones"]:
        assert zone["name"]["id"]
        assert zone["name"]["en"]


def test_zone_endpoints_expose_configured_public_base_url(monkeypatch):
    monkeypatch.setattr(
        main_module, "PUBLIC_BASE_URL", "https://pramana.example.com"
    )
    zones = client.get("/api/v1/zones").json()
    assert zones["public_base_url"] == "https://pramana.example.com"
    card = client.get("/api/v1/totem/bandara-ngurah-rai").json()
    assert card["public_base_url"] == "https://pramana.example.com"


def test_totem_card_endpoint():
    response = client.get("/api/v1/totem/bandara-ngurah-rai?lang=en")
    assert response.status_code == 200
    data = response.json()

    assert data["zone"]["id"] == "bandara-ngurah-rai"
    assert data["zone"]["name"] == "I Gusti Ngurah Rai Airport"
    assert data["language"] == "en"
    assert "public_base_url" in data
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
    assert data["resolution_mode"] == "VERIFIED_GROUNDED"
    assert data["epistemic_tier"] == 1
    assert "user_guidance" in data
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
    assert data["resolution_mode"] == "VERIFIED_GROUNDED"
    assert data["epistemic_tier"] == 1
    assert len(data["citations"]) > 0
    assert "copyable_comment" in data
    assert "user_guidance" in data
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
    assert data["resolution_mode"] == "OUT_OF_SCOPE_GUIDANCE"
    assert data["epistemic_tier"] == 3
    assert data["citations"] == []
    assert data["ai_synthesis_status"] == "deterministic"
    assert data["ai_claims"] == []
    assert data["neutral_summary_en"]
    assert len(data["user_guidance"]["suggested_query_rewrites"]) == 3


def test_context_note_subjective_input_returns_active_triage():
    response = client.post(
        "/api/v1/context-note",
        json={
            "post_content": (
                "direndahkan, disepelekan, dianggap tidak memiliki uang"
            )
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "PERLU_KLARIFIKASI"
    assert data["resolution_mode"] == "NEEDS_CLARIFICATION"
    assert data["epistemic_tier"] == 2
    assert data["citations"] == []
    assert data["ai_claims"] == []
    guidance = data["user_guidance"]
    assert guidance["missing_context_diagnosis"]
    assert len(guidance["what_user_should_do_next"]) >= 3
    assert len(guidance["suggested_query_rewrites"]) == 3
    assert guidance["relevant_authority_or_channel"]


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


def test_cors_preflight_accepts_vercel_origin():
    response = client.options(
        "/api/v1/trip-brief",
        headers={
            "Origin": "https://pramana1.vercel.app",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") in {
        "https://pramana1.vercel.app",
        "*",
    }


def test_two_different_ips_have_independent_quotas(monkeypatch):
    monkeypatch.setattr(main_module, "RATE_LIMIT_MAX_REQUESTS", 1)
    monkeypatch.setattr(main_module, "RATE_LIMIT_WINDOW_SECONDS", 60)

    ip1 = "192.0.2.1"
    ip2 = "192.0.2.2"

    assert main_module._allow_request(ip1) is True
    assert main_module._allow_request(ip1) is False  # ip1 exhausted

    # ip2 is unaffected
    assert main_module._allow_request(ip2) is True
    assert main_module._allow_request(ip2) is False


def test_client_key_prefers_session_id_header():
    req = Request(
        {
            "type": "http",
            "method": "POST",
            "path": "/api/v1/trip-brief",
            "headers": [
                (b"x-session-id", b"session-abc-123"),
                (b"x-forwarded-for", b"198.51.100.7"),
            ],
            "client": ("203.0.113.5", 12345),
        }
    )
    assert main_module._client_key(req) == "session:session-abc-123"



def test_rate_limit_trusted_proxy_headers(monkeypatch):
    """B4: Two different X-Forwarded-For IPs have independent rate limit buckets."""
    from backend import main as main_module
    monkeypatch.setattr(main_module, "TRUST_PROXY_HEADERS", True)

    req_body = {
        "itinerary_text": "Kunjungan ke Pura Besakih dan sewa motor di Ubud.",
        "start_date": "2026-06-10",
        "end_date": "2026-06-15",
        "traveler_origin": "international"
    }

    # IP 1 calls endpoint
    resp1 = client.post("/api/v1/trip-brief", json=req_body, headers={"X-Forwarded-For": "203.0.113.10"})
    assert resp1.status_code == 200

    # IP 2 calls endpoint with different IP
    resp2 = client.post("/api/v1/trip-brief", json=req_body, headers={"X-Forwarded-For": "198.51.100.25"})
    assert resp2.status_code == 200

    # IP 1 and IP 2 generate different client keys
    from fastapi import Request
    class DummyRequest:
        def __init__(self, headers, host="127.0.0.1"):
            self.headers = headers
            self.client = type("Client", (), {"host": host})()

    r1 = DummyRequest({"x-forwarded-for": "203.0.113.10"})
    r2 = DummyRequest({"x-forwarded-for": "198.51.100.25"})
    assert main_module._client_key(r1) == "203.0.113.10"
    assert main_module._client_key(r2) == "198.51.100.25"

def test_trip_brief_bilingual_fields():
    # Test English request
    res_en = client.post(
        "/api/v1/trip-brief",
        json={
            "itinerary_text": "Visiting Uluwatu temple and renting a scooter",
            "start_date": "2026-06-01",
            "end_date": "2026-06-05",
            "traveler_origin": "international",
            "lang": "en",
        },
    )
    assert res_en.status_code == 200
    data_en = res_en.json()
    assert data_en["briefing_items"]
    first_en = data_en["briefing_items"][0]
    assert first_en.get("display_text")
    assert first_en.get("display_title")
    assert first_en.get("text_original")
    assert first_en.get("display_penalties")
    assert "Date: 2026-06-01" in data_en["whatsapp_text"]
    assert "Verification status:" in data_en["ics_content"]

    # Test Indonesian request
    res_id = client.post(
        "/api/v1/trip-brief",
        json={
            "itinerary_text": "Mengunjungi pura uluwatu dan sewa motor",
            "start_date": "2026-06-01",
            "end_date": "2026-06-05",
            "traveler_origin": "international",
            "lang": "id",
        },
    )
    assert res_id.status_code == 200
    data_id = res_id.json()
    first_id = data_id["briefing_items"][0]
    assert first_id.get("display_text") == first_id.get("text_original")
    assert "Tanggal: 2026-06-01" in data_id["whatsapp_text"]
    assert "Status verifikasi:" in data_id["ics_content"]


def test_context_note_bilingual_fields():
    # Test English request
    res_en = client.post(
        "/api/v1/context-note",
        json={
            "post_content": "Foreign tourist arrested for climbing a sacred banyan tree at temple in Bali",
            "lang": "en",
        },
    )
    assert res_en.status_code == 200
    data_en = res_en.json()
    if data_en.get("citations"):
        first_cite = data_en["citations"][0]
        assert first_cite.get("display_text")
        assert first_cite.get("display_title")
        assert first_cite.get("text_original")
        assert first_cite.get("display_penalties")
        assert "Context Note (Pramana):" in data_en["copyable_comment"]

    # Test Indonesian request
    res_id = client.post(
        "/api/v1/context-note",
        json={
            "post_content": "Bule naik pohon keramat pura bali ditangkap",
            "lang": "id",
        },
    )
    assert res_id.status_code == 200
    data_id = res_id.json()
    if data_id.get("citations"):
        first_cite = data_id["citations"][0]
        assert first_cite.get("display_text") == first_cite.get("text_original")
        assert "Catatan Konteks (Pramana):" in data_id["copyable_comment"]


def test_totem_bilingual_citations():
    # Test EN
    res_en = client.get("/api/v1/totem/pura-besakih?lang=en")
    assert res_en.status_code == 200
    data_en = res_en.json()
    for cite in data_en["citations"]:
        assert cite.get("display_text")
        assert cite.get("display_title")
        assert cite.get("text_original")

    # Test ID
    res_id = client.get("/api/v1/totem/pura-besakih?lang=id")
    assert res_id.status_code == 200
    data_id = res_id.json()
    for cite in data_id["citations"]:
        assert cite.get("display_text") == cite.get("text_original")

