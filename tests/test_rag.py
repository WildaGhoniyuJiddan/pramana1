"""
Unit tests for Strict-RAG Engine (Mode 1 & Mode 2).

These tests force the deterministic local fallback by removing GEMINI_API_KEY,
so results never depend on network access or a developer's local secrets.
"""

import pytest

from backend.services.rag_engine import StrictRAGEngine


@pytest.fixture
def engine(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    return StrictRAGEngine()


def test_mode1_trip_brief_with_nyepi(engine):
    itinerary = (
        "Kunjungan ke Pura Uluwatu dan sewa motor di Seminyak "
        "kode booking BK12345."
    )
    result = engine.analyze_trip_itinerary(
        itinerary_text=itinerary,
        start_date="2026-03-18",
        end_date="2026-03-21",
        traveler_origin="international",
    )

    assert result["status"] == "SUCCESS"
    assert result["guard_status"] == "TERVERIFIKASI"
    assert result["ai_synthesis_status"] == "deterministic"
    assert "[KODE_BOOKING_DISAMARKAN]" in result["masked_itinerary"]
    assert result["pii_redacted_count"] >= 1
    assert result["calendar_conflicts"]["has_nyepi"] is True
    assert len(result["briefing_items"]) > 0
    assert "BEGIN:VCALENDAR" in result["ics_content"]
    assert "*PRAMANA: Bali Trip Brief" in result["whatsapp_text"]
    assert result["verification_scope"] == "corpus"
    assert result["confidence"] in {"SEDANG", "RENDAH"}
    assert result["confidence"] != "TINGGI"
    assert result["disclaimer"]


def test_mode1_international_adds_levy(engine):
    result = engine.analyze_trip_itinerary(
        itinerary_text="Liburan ke Pura Besakih dan belanja di Ubud",
        start_date="2026-05-10",
        end_date="2026-05-15",
        traveler_origin="international",
    )
    ids = [item["id"] for item in result["briefing_items"]]
    assert "PERDA_BALI_06_2023_LEVY" in ids

    levy = next(
        item for item in result["briefing_items"]
        if item["id"] == "PERDA_BALI_06_2023_LEVY"
    )
    assert levy["text_status"] == "verbatim"
    assert levy["document_id"] == "perda-bali-2-2025"
    assert "Pasal 4A" in levy["full_text"]
    assert "Pasal 16A" in levy["full_text"]


def test_mode1_domestic_does_not_add_levy(engine):
    result = engine.analyze_trip_itinerary(
        itinerary_text="Liburan ke Pura Besakih dan belanja di Ubud",
        start_date="2026-05-10",
        end_date="2026-05-15",
        traveler_origin="domestic",
    )
    ids = [item["id"] for item in result["briefing_items"]]
    assert "PERDA_BALI_06_2023_LEVY" not in ids


def test_mode1_abstains_for_unrelated_itinerary(engine):
    result = engine.analyze_trip_itinerary(
        itinerary_text="Kucing oranye tertidur di atas laptop di kafe Jakarta.",
        start_date="2026-05-10",
        end_date="2026-05-12",
        traveler_origin="international",
    )

    assert result["status"] == "TIDAK_DITEMUKAN"
    assert result["guard_status"] == "TIDAK_DITEMUKAN"
    assert result["confidence"] == "TIDAK_DITEMUKAN"
    assert result["briefing_items"] == []
    # Calendar export must still work even when retrieval abstains.
    assert "BEGIN:VCALENDAR" in result["ics_content"]
    assert "TIDAK_DITEMUKAN" in result["ics_content"]


def test_mode2_viral_post_verified(engine):
    post = (
        "Bule memanjat pohon suci di Tabanan tanpa pakaian "
        "dan berteriak kasar."
    )
    result = engine.analyze_viral_post(post)

    assert result["status"] == "TERVERIFIKASI"
    assert result["guard_status"] == "TERVERIFIKASI"
    assert result["ai_synthesis_status"] == "deterministic"
    assert result["confidence"] in {"SEDANG", "RENDAH"}
    assert result["confidence"] != "TINGGI"
    assert result["verification_scope"] == "corpus"
    assert len(result["citations"]) > 0
    assert any(
        citation["reg_id"] == "SE_GUB_04_2023_DONT"
        for citation in result["citations"]
    )

    for citation in result["citations"]:
        assert citation["verified_layer1"] is True
        assert citation["verification_scope"] == "corpus"
        assert len(citation["quote_sha256"]) == 64
        assert citation["source_url"].startswith("https://")
        assert citation["is_verbatim"] is True
        assert citation["document_id"]
        assert citation["text_status"] == "verbatim"

    assert result["disclaimer"]


def test_mode2_cites_non_verbatim_compilation_honestly(engine):
    result = engine.analyze_viral_post(
        "Aturan Catur Brata Penyepian dan patroli Pecalang saat Nyepi"
    )
    assert result["status"] == "TERVERIFIKASI"
    nyepi = next(
        citation
        for citation in result["citations"]
        if citation["reg_id"] == "KETENTUAN_HARI_RAYA_NYEPI"
    )
    assert nyepi["is_verbatim"] is False
    assert nyepi["text_status"] == "compilation"
    assert nyepi["document_id"] == "seruan-bersama-nyepi-2026"


def test_mode2_viral_post_abstain_out_of_domain(engine):
    result = engine.analyze_viral_post(
        "Kucing oranye tertidur di atas laptop di kafe Jakarta."
    )

    assert result["status"] == "TIDAK_DITEMUKAN"
    assert result["guard_status"] == "TIDAK_DITEMUKAN"
    assert result["confidence"] == "TIDAK_DITEMUKAN"
    assert result["citations"] == []
    assert result["disclaimer"]


def test_mode2_masks_email(engine):
    result = engine.analyze_viral_post(
        "Bule memanjat pohon suci, laporkan ke alex@travel.com"
    )
    assert "alex@travel.com" not in result["masked_post"]
    assert "[EMAIL_DISAMARKAN]" in result["masked_post"]
    assert result["pii_redacted_count"] >= 1
