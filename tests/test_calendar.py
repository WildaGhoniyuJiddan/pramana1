"""
Unit tests for Pramana Balinese Calendar and Holiday Conflict Engine.
"""

import pytest

from backend.services.calendar_service import (
    CALENDAR_COVERAGE,
    CATUR_BRATA_RULES,
    NYEPI_CALENDAR,
    check_holiday_conflicts,
    generate_ics_calendar,
    parse_date,
)


def test_nyepi_calendar_constants():
    assert CALENDAR_COVERAGE == "2025-2028"
    assert NYEPI_CALENDAR[2026]["date"] == "2026-03-19"
    assert NYEPI_CALENDAR[2026]["saka_year"] == 1948
    assert NYEPI_CALENDAR[2026]["start_time"] == "2026-03-19T06:00:00+08:00"
    assert NYEPI_CALENDAR[2026]["end_time"] == "2026-03-20T06:00:00+08:00"
    assert len(CATUR_BRATA_RULES) == 4


def test_conflict_detection_during_nyepi_2026_full_window():
    # 18-21 March 2026 fully contains the 19 Mar 06:00 -> 20 Mar 06:00 window.
    conflict = check_holiday_conflicts("2026-03-18", "2026-03-21")
    assert conflict["has_conflict"] is True
    assert conflict["has_nyepi"] is True
    assert conflict["data_available"] is True
    assert conflict["nyepi_summary"] is not None
    assert conflict["nyepi_summary"]["severity"] == "CRITICAL"
    assert conflict["nyepi_summary"]["overlap_type"] == "FULL_24H"

    # Must contain both Pengerupukan and Nyepi.
    event_names = [e["name"] for e in conflict["events"]]
    assert any("Nyepi" in name for name in event_names)
    assert any("Pengerupukan" in name for name in event_names)


def test_nyepi_partial_window_on_departure_morning():
    # 20 March is after the calendar date but still inside the 24-hour closure
    # window that ends at 06:00 WITA on 20 March.
    result = check_holiday_conflicts("2026-03-20", "2026-03-21")
    assert result["has_nyepi"] is True
    assert result["nyepi_summary"]["overlap_type"] == "PARTIAL"
    assert "06.00 WITA" in result["nyepi_summary"]["overlap_note"]


def test_no_conflict_safe_dates():
    result = check_holiday_conflicts("2026-06-01", "2026-06-07")
    assert result["has_conflict"] is False
    assert result["has_nyepi"] is False
    assert result["events"] == []
    assert result["data_available"] is True


def test_galungan_and_kuningan_2026_dates():
    galungan = check_holiday_conflicts("2026-06-17", "2026-06-17")
    assert galungan["has_nyepi"] is False
    assert any("Galungan" in e["name"] for e in galungan["events"])

    kuningan = check_holiday_conflicts("2026-06-27", "2026-06-27")
    assert kuningan["has_nyepi"] is False
    assert any("Kuningan" in e["name"] for e in kuningan["events"])

    # Old, incorrect April dates must not emit a festival.
    april = check_holiday_conflicts("2026-04-14", "2026-04-16")
    assert april["events"] == []


def test_coverage_warning_outside_known_years():
    result = check_holiday_conflicts("2030-01-01", "2030-01-02")
    assert result["data_available"] is False
    assert result["has_nyepi"] is False
    assert result["coverage_warning"] is not None
    assert "2030" in result["coverage_warning"]


def test_invalid_calendar_input_is_reported_not_raised():
    result = check_holiday_conflicts("2026-13-01", "2026-13-02")
    assert result["input_error"] is not None
    assert result["has_nyepi"] is False

    assert parse_date("2026-02-30") is None
    assert parse_date("19-03-2026") is None
    assert parse_date("2026-03-19") is not None


def test_ics_export_generation():
    ics_str = generate_ics_calendar(
        title="Trip to Ubud & Kuta",
        description="Aturan Wisatawan: Hormati kawasan suci Pura, siapkan QRIS/Rupiah.",
        start_date_str="2026-04-10",
        end_date_str="2026-04-15",
        location="Ubud, Bali",
    )

    assert "BEGIN:VCALENDAR" in ics_str
    assert "END:VCALENDAR" in ics_str
    assert "DTSTART;VALUE=DATE:20260410" in ics_str
    assert "DTEND;VALUE=DATE:20260416" in ics_str  # +1 day for inclusive end
    assert "UID:pramana-" in ics_str
    assert "BEGIN:VALARM" in ics_str
    assert ics_str.endswith("\r\n")


def test_ics_escapes_text_and_folds_long_lines():
    description = "Line1\nLine2, with; separators " + ("panjang " * 30)
    ics_str = generate_ics_calendar(
        title="Trip, Ubud; Test",
        description=description,
        start_date_str="2026-04-10",
        end_date_str="2026-04-15",
    )

    assert "SUMMARY:Trip\\, Ubud\\; Test" in ics_str
    assert "Line1\\nLine2\\, with\\; separators" in ics_str

    # Every physical line must be within the RFC 5545 75-octet limit.
    for line in ics_str.split("\r\n"):
        assert len(line.encode("utf-8")) <= 75


@pytest.mark.parametrize(
    "start_date,end_date",
    [
        ("2026-02-30", "2026-03-02"),
        ("2026-03-10", "2026-03-01"),
        ("19-03-2026", "2026-03-21"),
        ("", "2026-03-21"),
    ],
)
def test_ics_rejects_invalid_dates(start_date, end_date):
    with pytest.raises(ValueError):
        generate_ics_calendar(
            title="Invalid trip",
            description="Invalid dates",
            start_date_str=start_date,
            end_date_str=end_date,
        )
