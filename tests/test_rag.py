"""
Unit tests for Strict-RAG Engine (Mode 1 & Mode 2).
"""

from backend.services.rag_engine import StrictRAGEngine


def test_mode1_trip_brief_with_nyepi():
    engine = StrictRAGEngine()
    itinerary = "Kunjungan ke Pura Uluwatu dan sewa motor di Seminyak kode booking BK12345."
    result = engine.analyze_trip_itinerary(
        itinerary_text=itinerary,
        start_date="2026-03-18",
        end_date="2026-03-21",
        traveler_origin="international"
    )

    assert result["status"] == "SUCCESS"
    assert "[KODE_BOOKING_DISAMARKAN]" in result["masked_itinerary"]
    assert result["calendar_conflicts"]["has_nyepi"] is True
    assert len(result["briefing_items"]) > 0
    assert "BEGIN:VCALENDAR" in result["ics_content"]
    assert "*PRAMANA: Bali Trip Brief" in result["whatsapp_text"]


def test_mode2_viral_post_verified():
    engine = StrictRAGEngine()
    post = "Bule memanjat pohon suci di Tabanan tanpa pakaian dan berteriak kasar."
    result = engine.analyze_viral_post(post)

    assert result["status"] == "TERVERIFIKASI"
    assert result["confidence"] == "TINGGI"
    assert len(result["citations"]) > 0
    assert any("SE_GUB_04_2023_DONT" == c["reg_id"] for c in result["citations"])


def test_mode2_viral_post_abstain_out_of_domain():
    engine = StrictRAGEngine()
    # Post about something completely unregulated in Bali legal corpus
    post = "Kucing oranye tertidur di atas laptop di kafe Jakarta."
    result = engine.analyze_viral_post(post)

    assert result["status"] == "TIDAK_DITEMUKAN"
    assert result["confidence"] == "TIDAK_DITEMUKAN"
    assert len(result["citations"]) == 0
