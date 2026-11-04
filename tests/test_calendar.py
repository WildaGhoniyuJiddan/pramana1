"""
Unit tests for Pramana Balinese Calendar and Holiday Conflict Engine.
"""

import pytest
from backend.services.calendar_service import (
    check_holiday_conflicts,
    generate_ics_calendar,
    NYEPI_CALENDAR,
    CATUR_BRATA_RULES
)


def test_nyepi_calendar_constants():
    assert 2026 in NYEPI_CALENDAR
    assert NYEPI_CALENDAR[2026]["date"] == "2026-03-19"
    assert NYEPI_CALENDAR[2026]["saka_year"] == 1948
    assert len(CATUR_BRATA_RULES) == 4


def test_conflict_detection_during_nyepi_2026():
    # Tourist itinerary overlapping with Nyepi 2026 (18-21 March 2026)
    conflict = check_holiday_conflicts("2026-03-18", "2026-03-21")
    assert conflict["has_conflict"] is True
    assert conflict["has_nyepi"] is True
    assert conflict["nyepi_summary"] is not None
    assert conflict["nyepi_summary"]["severity"] == "CRITICAL"

    # Must contain both Pengerupukan and Nyepi
    event_names = [e["name"] for e in conflict["events"]]
    assert any("Nyepi" in name for name in event_names)
    assert any("Pengerupukan" in name for name in event_names)


def test_no_conflict_safe_dates():
    # Trip outside any religious holidays (e.g., June 2026)
    result = check_holiday_conflicts("2026-06-01", "2026-06-07")
    assert result["has_conflict"] is False
    assert result["has_nyepi"] is False
    assert len(result["events"]) == 0


def test_galungan_2026_detection():
    # Galungan in April 2026
    result = check_holiday_conflicts("2026-04-14", "2026-04-16")
    assert result["has_conflict"] is True
    assert result["has_nyepi"] is False
    assert any("Galungan" in e["name"] for e in result["events"])


def test_ics_export_generation():
    ics_str = generate_ics_calendar(
        title="Trip to Ubud & Kuta",
        description="Aturan Wisatawan: Hormati kawasan suci Pura, siapkan QRIS/Rupiah.",
        start_date_str="2026-04-10",
        end_date_str="2026-04-15",
        location="Ubud, Bali"
    )

    assert "BEGIN:VCALENDAR" in ics_str
    assert "END:VCALENDAR" in ics_str
    assert "DTSTART;VALUE=DATE:20260410" in ics_str
    assert "DTEND;VALUE=DATE:20260416" in ics_str  # +1 day for inclusive end date
    assert "SUMMARY:Trip to Ubud & Kuta" in ics_str
    assert "BEGIN:VALARM" in ics_str
