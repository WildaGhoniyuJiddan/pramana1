"""
Integration tests for FastAPI endpoints.
"""

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_healthcheck_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["total_regulations_indexed"] >= 6


def test_get_corpus_endpoint():
    response = client.get("/api/v1/corpus")
    assert response.status_code == 200
    data = response.json()
    assert "metadata" in data
    assert "tiers" in data
    assert len(data["regulations"]) >= 6


def test_trip_brief_endpoint():
    payload = {
        "itinerary_text": "Liburan ke Pura Besakih dan belanja di Ubud",
        "start_date": "2026-05-10",
        "end_date": "2026-05-15",
        "traveler_origin": "international"
    }
    response = client.post("/api/v1/trip-brief", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert len(data["briefing_items"]) > 0
    assert "ics_content" in data
    assert "whatsapp_text" in data


def test_context_note_endpoint():
    payload = {
        "post_content": "Viral video bule memanjat pohon suci pura di Tabanan tanpa busana"
    }
    response = client.post("/api/v1/context-note", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "TERVERIFIKASI"
    assert len(data["citations"]) > 0
    assert "copyable_comment" in data
