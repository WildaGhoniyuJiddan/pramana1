"""
Deterministic Balinese Calendar and Holiday Conflict Service for Pramana.
Handles official Nyepi dates, Catur Brata Penyepian rules, and Pawukon cycle celebrations.
"""

from datetime import datetime, date, time, timedelta, timezone
from typing import Optional, List, Dict, Any
import hashlib

BALI_TZ = timezone(timedelta(hours=8))
CALENDAR_COVERAGE = "2025-2028"

# Official Nyepi dates from SKB 3 Menteri and PHDI/MDA Bali.
# Each entry covers the full 24-hour window, not only the calendar date.
NYEPI_CALENDAR: Dict[int, Dict[str, Any]] = {
    2025: {
        "date": "2025-03-29",
        "saka_year": 1947,
        "start_time": "2025-03-29T06:00:00+08:00",
        "end_time": "2025-03-30T06:00:00+08:00",
        "ogoh_ogoh_date": "2025-03-28",  # Pengerupukan
        "ngembak_geni": "2025-03-30",
    },
    2026: {
        "date": "2026-03-19",
        "saka_year": 1948,
        "start_time": "2026-03-19T06:00:00+08:00",
        "end_time": "2026-03-20T06:00:00+08:00",
        "ogoh_ogoh_date": "2026-03-18",  # Pengerupukan
        "ngembak_geni": "2026-03-20",
    },
    2027: {
        "date": "2027-03-08",
        "saka_year": 1949,
        "start_time": "2027-03-08T06:00:00+08:00",
        "end_time": "2027-03-09T06:00:00+08:00",
        "ogoh_ogoh_date": "2027-03-07",
        "ngembak_geni": "2027-03-09",
    },
    2028: {
        "date": "2028-03-26",
        "saka_year": 1950,
        "start_time": "2028-03-26T06:00:00+08:00",
        "end_time": "2028-03-27T06:00:00+08:00",
        "ogoh_ogoh_date": "2028-03-25",
        "ngembak_geni": "2028-03-27",
    },
}

# Major Pawukon festivals (210-day cycle). Galungan and Kuningan are 10 days apart.
PAWUKON_FESTIVALS = [
    # 2026
    {"name": "Hari Raya Galungan", "date": "2026-06-17", "type": "cultural_ceremony", "notes": "Perayaan kemenangan Dharma melawan Adharma. Penjor terpasang di sepanjang jalan."},
    {"name": "Hari Raya Kuningan", "date": "2026-06-27", "type": "cultural_ceremony", "notes": "Persembahyangan bersama leluhur sampai pukul 12.00 siang."},
    # 2027 (first cycle)
    {"name": "Hari Raya Galungan", "date": "2027-01-13", "type": "cultural_ceremony", "notes": "Siklus pertama 2027. Penjor terpasang di sepanjang jalan desa."},
    {"name": "Hari Raya Kuningan", "date": "2027-01-23", "type": "cultural_ceremony", "notes": "Siklus pertama 2027."},
    # 2027 (second cycle)
    {"name": "Hari Raya Galungan", "date": "2027-08-11", "type": "cultural_ceremony", "notes": "Siklus kedua 2027."},
    {"name": "Hari Raya Kuningan", "date": "2027-08-21", "type": "cultural_ceremony", "notes": "Siklus kedua 2027."},
    # 2028 (first cycle)
    {"name": "Hari Raya Galungan", "date": "2028-03-08", "type": "cultural_ceremony", "notes": "Siklus pertama 2028."},
    {"name": "Hari Raya Kuningan", "date": "2028-03-18", "type": "cultural_ceremony", "notes": "Siklus pertama 2028."},
    # 2028 (second cycle)
    {"name": "Hari Raya Galungan", "date": "2028-10-04", "type": "cultural_ceremony", "notes": "Siklus kedua 2028."},
    {"name": "Hari Raya Kuningan", "date": "2028-10-14", "type": "cultural_ceremony", "notes": "Siklus kedua 2028."},
]

CATUR_BRATA_RULES = [
    {
        "rule": "Amati Geni",
        "translation": "Tidak menyalakan api atau cahaya",
        "instruction": "Lampu penerangan kamar harus redup, gorden ditutup rapat agar tidak ada cahaya bocor ke luar, dilarang menyalakan api rokok atau lilin di luar ruangan."
    },
    {
        "rule": "Amati Karya",
        "translation": "Tidak bekerja / beraktivitas fisik",
        "instruction": "Semua kantor, toko, restoran, dan layanan wisata tutup total selama 24 jam (pukul 06.00 s/d 06.00 WITA)."
    },
    {
        "rule": "Amati Lelungan",
        "translation": "Tidak bepergian keluar",
        "instruction": "Dilarang keras keluar dari pekarangan penginapan/hotel atau berjalan di jalan raya/pantai. Patroli dijaga ketat oleh Pecalang."
    },
    {
        "rule": "Amati Lelanguan",
        "translation": "Tidak mengadakan hiburan atau kebisingan",
        "instruction": "Dilarang menyetel musik keras, berteriak, atau mengadakan pesta. Tetap tenang dan hormati keheningan."
    }
]


def parse_date(date_str: str) -> Optional[date]:
    """Parse a strict YYYY-MM-DD date or return None on invalid input."""
    if not date_str or not isinstance(date_str, str):
        return None
    value = date_str.strip()
    if len(value) != 10:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value).astimezone(BALI_TZ)


def check_holiday_conflicts(start_date_str: str, end_date_str: Optional[str] = None) -> Dict[str, Any]:
    """
    Check if a trip window conflicts with Nyepi or other major Balinese ceremonies.

    The trip is treated as a full-day window: [start 00:00, end+1 00:00) WITA.
    Nyepi is treated as [date 06:00, next date 06:00) WITA. This means a trip that
    only touches the morning after Nyepi is still flagged for the remaining
    closure window until 06:00.
    """
    start_d = parse_date(start_date_str)
    if not start_d:
        return {
            "has_conflict": False,
            "has_nyepi": False,
            "events": [],
            "nyepi_summary": None,
            "data_available": False,
            "calendar_coverage": CALENDAR_COVERAGE,
            "checked_years": [],
            "input_error": "Tanggal mulai tidak valid. Gunakan format YYYY-MM-DD.",
            "coverage_warning": None,
        }

    end_d = parse_date(end_date_str) if end_date_str else start_d
    if not end_d:
        return {
            "has_conflict": False,
            "has_nyepi": False,
            "events": [],
            "nyepi_summary": None,
            "data_available": False,
            "calendar_coverage": CALENDAR_COVERAGE,
            "checked_years": [],
            "input_error": "Tanggal akhir tidak valid. Gunakan format YYYY-MM-DD.",
            "coverage_warning": None,
        }
    if end_d < start_d:
        end_d = start_d

    trip_start = datetime.combine(start_d, time.min, tzinfo=BALI_TZ)
    trip_end = datetime.combine(end_d + timedelta(days=1), time.min, tzinfo=BALI_TZ)

    conflicts: List[Dict[str, Any]] = []
    has_nyepi = False
    nyepi_alert_data = None

    checked_years = list(range(start_d.year, end_d.year + 1))
    missing_years = [year for year in checked_years if year not in NYEPI_CALENDAR]

    for year in checked_years:
        info = NYEPI_CALENDAR.get(year)
        if not info:
            continue

        nyepi_start = _parse_datetime(info["start_time"])
        nyepi_end = _parse_datetime(info["end_time"])
        overlap_start = max(trip_start, nyepi_start)
        overlap_end = min(trip_end, nyepi_end)

        if overlap_start < overlap_end:
            has_nyepi = True
            is_full_24h = trip_start <= nyepi_start and trip_end >= nyepi_end
            overlap_type = "FULL_24H" if is_full_24h else "PARTIAL"
            overlap_note = (
                "Rentang perjalanan mencakup seluruh jendela Nyepi 24 jam."
                if is_full_24h
                else "Rentang perjalanan bersinggungan dengan sebagian jendela Nyepi. Bandara dan layanan publik tetap tutup sampai pukul 06.00 WITA pada hari berikutnya."
            )

            details = {
                "event_name": f"Hari Suci Nyepi (Tahun Baru Saka {info['saka_year']})",
                "date": info["date"],
                "saka_year": info["saka_year"],
                "severity": "CRITICAL",
                "window_start": info["start_time"],
                "window_end": info["end_time"],
                "overlap_start": overlap_start.isoformat(),
                "overlap_end": overlap_end.isoformat(),
                "overlap_type": overlap_type,
                "overlap_note": overlap_note,
                "restrictions": CATUR_BRATA_RULES,
                "service_disruptions": [
                    "Bandara Internasional I Gusti Ngurah Rai tutup total selama 24 jam (pukul 06.00 WITA s/d 06.00 WITA keesokan harinya).",
                    "Pelabuhan penyeberangan (Gilimanuk, Padangbai, Sanur) tutup total.",
                    "Data internet seluler dan siaran TV/IPTV dimatikan serentak oleh Kemenkominfo/Operator.",
                    "Layanan ATM dan minimarket tutup; siapkan uang tunai dan perbekalan H-1.",
                    "Hanya layanan medis darurat dan rumah sakit yang beroperasi terbatas dengan pengawalan Pecalang."
                ],
                "recommendations": [
                    "Pastikan jadwal penerbangan kedatangan/keberangkatan Anda tidak berada pada tanggal ini.",
                    "Beli makanan, obat-obatan, dan kebutuhan pribadi pada H-1 (saat Pengerupukan).",
                    "Simpan panduan ini secara offline sebelum koneksi seluler dinonaktifkan."
                ]
            }

            conflicts.append({
                "name": f"Hari Suci Nyepi (Saka {info['saka_year']})",
                "date": info["date"],
                "severity": "CRITICAL",
                "details": details,
            })

            if nyepi_alert_data is None:
                nyepi_alert_data = details

        # Pengerupukan starts on the evening before Nyepi.
        ogoh_d = parse_date(info["ogoh_ogoh_date"])
        if ogoh_d and start_d <= ogoh_d <= end_d:
            conflicts.append({
                "name": "Malam Pengerupukan (Pawai Ogoh-Ogoh)",
                "date": info["ogoh_ogoh_date"],
                "severity": "WARNING",
                "details": {
                    "event_name": "Malam Pengerupukan (Pawai Ogoh-ogoh)",
                    "date": info["ogoh_ogoh_date"],
                    "severity": "WARNING",
                    "restrictions": [],
                    "service_disruptions": [
                        "Penutupan jalan raya utama di seluruh Bali mulai pukul 16.00 WITA untuk pawai Ogoh-ogoh.",
                        "Kemacetan ekstrem di pusat-pusat kota/desa (Denpasar, Kuta, Ubud)."
                    ],
                    "recommendations": [
                        "Kembalilah ke hotel/akomodasi Anda sebelum pukul 15.00 WITA untuk menghindari terjebak penutupan jalan."
                    ]
                }
            })

    # Check Pawukon festivals.
    for fest in PAWUKON_FESTIVALS:
        f_date = parse_date(fest["date"])
        if f_date and start_d <= f_date <= end_d:
            conflicts.append({
                "name": fest["name"],
                "date": fest["date"],
                "severity": "INFO",
                "details": {
                    "event_name": fest["name"],
                    "date": fest["date"],
                    "severity": "INFO",
                    "restrictions": [],
                    "service_disruptions": [
                        "Aktivitas persembahyangan massal di pura desa; kenakan pakaian adat sopan bila berkunjung dekat area upacara."
                    ],
                    "recommendations": [
                        fest["notes"]
                    ]
                }
            })

    coverage_warning = None
    if missing_years:
        years_text = ", ".join(str(year) for year in missing_years)
        coverage_warning = (
            f"Data Nyepi untuk tahun {years_text} belum tersedia di kalender deterministik ini. "
            "Tanggal yang tidak terdeteksi bukan berarti bebas dari penutupan; verifikasi jadwal resmi sebelum berangkat."
        )

    return {
        "has_conflict": len(conflicts) > 0,
        "has_nyepi": has_nyepi,
        "events": conflicts,
        "nyepi_summary": nyepi_alert_data,
        "data_available": len(missing_years) == 0,
        "calendar_coverage": CALENDAR_COVERAGE,
        "checked_years": checked_years,
        "coverage_warning": coverage_warning,
    }


def _escape_ics_text(value: str) -> str:
    """Escape a text value per RFC 5545 section 3.3.11."""
    if value is None:
        return ""
    return (
        str(value)
        .replace("\\", "\\\\")
        .replace("\r\n", "\\n")
        .replace("\n", "\\n")
        .replace("\r", "\\n")
        .replace(",", "\\,")
        .replace(";", "\\;")
    )


def _fold_ics_line(line: str, limit: int = 75) -> str:
    """
    Fold a content line at 75 UTF-8 octets per RFC 5545 section 3.1.
    Continuation lines start with a single space and carry at most 74 octets.
    """
    if len(line.encode("utf-8")) <= limit:
        return line

    chunks: List[str] = []
    current: List[str] = []
    current_bytes = 0
    max_bytes = limit

    for char in line:
        char_bytes = len(char.encode("utf-8"))
        if current and current_bytes + char_bytes > max_bytes:
            chunks.append("".join(current))
            current = [char]
            current_bytes = char_bytes
            max_bytes = limit - 1
        else:
            current.append(char)
            current_bytes += char_bytes

    if current:
        chunks.append("".join(current))

    return "\r\n ".join(chunks)


def generate_ics_calendar(
    title: str,
    description: str,
    start_date_str: str,
    end_date_str: str,
    location: str = "Bali, Indonesia"
) -> str:
    """
    Generate an RFC 5545 iCalendar string for a travel briefing.

    Raises ValueError if either date is missing/invalid or the end date is
    earlier than the start date. All-day DTEND is exclusive, so the end date is
    incremented by one day.
    """
    start_d = parse_date(start_date_str)
    if not start_d:
        raise ValueError("start_date_str harus berupa tanggal valid berformat YYYY-MM-DD")

    end_d = parse_date(end_date_str) if end_date_str else start_d
    if not end_d:
        raise ValueError("end_date_str harus berupa tanggal valid berformat YYYY-MM-DD")
    if end_d < start_d:
        raise ValueError("end_date_str tidak boleh lebih awal dari start_date_str")

    start_clean = start_d.strftime("%Y%m%d")
    end_clean = (end_d + timedelta(days=1)).strftime("%Y%m%d")

    dtstamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    uid_source = f"{title}|{start_clean}|{end_clean}".encode("utf-8")
    uid_hash = hashlib.sha256(uid_source).hexdigest()[:20]
    uid = f"pramana-{uid_hash}@pramana.local"

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Pramana Bali DigiFest//Strict RAG Travel Brief//ID",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "BEGIN:VEVENT",
        f"UID:{uid}",
        f"DTSTAMP:{dtstamp}",
        f"DTSTART;VALUE=DATE:{start_clean}",
        f"DTEND;VALUE=DATE:{end_clean}",
        f"SUMMARY:{_escape_ics_text(title)}",
        f"DESCRIPTION:{_escape_ics_text(description)}",
        f"LOCATION:{_escape_ics_text(location)}",
        "STATUS:CONFIRMED",
        "BEGIN:VALARM",
        "TRIGGER:-P1D",
        "ACTION:DISPLAY",
        f"DESCRIPTION:{_escape_ics_text(f'Pengingat Aturan Wisata Pramana Bali: {title}')}",
        "END:VALARM",
        "END:VEVENT",
        "END:VCALENDAR",
    ]

    return "\r\n".join(_fold_ics_line(line) for line in lines) + "\r\n"
