"""
Deterministic Balinese Calendar and Holiday Conflict Service for Pramana.
Handles official Nyepi dates, Catur Brata Penyepian rules, and Pawukon cycle celebrations.
"""

from datetime import datetime, date, timedelta, timezone
from typing import Optional, List, Dict, Any


# Official Nyepi dates from SKB 3 Menteri and PHDI Bali
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

# Major Pawukon Festivals (210-day cycle)
PAWUKON_FESTIVALS = [
    # 2026 Dates
    {"name": "Hari Raya Galungan", "date": "2026-04-15", "type": "cultural_ceremony", "notes": "Perayaan kemenangan Dharma melawan Adharma. Penjor terpasang di sepanjang jalan."},
    {"name": "Hari Raya Kuningan", "date": "2026-04-25", "type": "cultural_ceremony", "notes": "Persembahyangan bersama leluhur sampai pukul 12.00 siang."},
    {"name": "Hari Raya Galungan", "date": "2026-11-11", "type": "cultural_ceremony", "notes": "Siklus kedua 2026. Penjor terpasang di sepanjang jalan desa."},
    {"name": "Hari Raya Kuningan", "date": "2026-11-21", "type": "cultural_ceremony", "notes": "Siklus kedua 2026."},
    # 2027 Dates
    {"name": "Hari Raya Galungan", "date": "2027-06-09", "type": "cultural_ceremony", "notes": "Penjor terpasang di sepanjang jalan."},
    {"name": "Hari Raya Kuningan", "date": "2027-06-19", "type": "cultural_ceremony", "notes": "Puncak perayaan Kuningan."},
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
    """Parse string YYYY-MM-DD or return None on invalid format."""
    if not date_str:
        return None
    try:
        # Handles YYYY-MM-DD
        return datetime.strptime(date_str[:10], "%Y-%m-%d").date()
    except Exception:
        return None


def check_holiday_conflicts(start_date_str: str, end_date_str: Optional[str] = None) -> Dict[str, Any]:
    """
    Check if a trip window conflicts with Nyepi or other major Balinese ceremonies.
    Returns structured alerts and mitigation recommendations.
    """
    start_d = parse_date(start_date_str)
    if not start_d:
        return {"has_conflict": False, "events": []}

    end_d = parse_date(end_date_str) if end_date_str else start_d
    if end_d < start_d:
        end_d = start_d

    conflicts = []
    has_nyepi = False
    nyepi_alert_data = None

    # Check Nyepi
    curr = start_d
    while curr <= end_d:
        year = curr.year
        if year in NYEPI_CALENDAR:
            info = NYEPI_CALENDAR[year]
            nyepi_d = parse_date(info["date"])
            ogoh_d = parse_date(info["ogoh_ogoh_date"])

            # Check exact Nyepi day
            if curr == nyepi_d:
                has_nyepi = True
                nyepi_alert_data = {
                    "event_name": f"Hari Suci Nyepi (Tahun Baru Saka {info['saka_year']})",
                    "date": info["date"],
                    "severity": "CRITICAL",
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
                        "Unduh brief ini secara offline (PWA) sebelum koneksi seluler dinonaktifkan."
                    ]
                }
                conflicts.append({
                    "name": f"Hari Suci Nyepi (Saka {info['saka_year']})",
                    "date": info["date"],
                    "severity": "CRITICAL",
                    "details": nyepi_alert_data
                })

            # Check Pengerupukan (Eve of Nyepi)
            elif curr == ogoh_d:
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

        curr += timedelta(days=1)

    # Check Pawukon festivals
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

    return {
        "has_conflict": len(conflicts) > 0,
        "has_nyepi": has_nyepi,
        "events": conflicts,
        "nyepi_summary": nyepi_alert_data
    }


def generate_ics_calendar(
    title: str,
    description: str,
    start_date_str: str,
    end_date_str: str,
    location: str = "Bali, Indonesia"
) -> str:
    """Generate RFC 5545 compliant iCalendar string for exporting travel briefings."""
    start_clean = start_date_str.replace("-", "")[:8]
    # End date in iCal for all-day is exclusive, so add 1 day if single day
    end_d = parse_date(end_date_str) or parse_date(start_date_str)
    if end_d:
        end_clean = (end_d + timedelta(days=1)).strftime("%Y%m%d")
    else:
        end_clean = start_clean

    dtstamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    uid = f"pramana-{start_clean}-{abs(hash(title)) % 100000}@pramana.balidigifest.id"

    # Escape text for ICS format
    desc_escaped = description.replace("\n", "\\n").replace(",", "\\,").replace(";", "\\;")

    ics_content = (
        "BEGIN:VCALENDAR\r\n"
        "VERSION:2.0\r\n"
        "PRODID:-//Pramana Bali DigiFest//Strict RAG Travel Brief//ID\r\n"
        "CALSCALE:GREGORIAN\r\n"
        "METHOD:PUBLISH\r\n"
        "BEGIN:VEVENT\r\n"
        f"UID:{uid}\r\n"
        f"DTSTAMP:{dtstamp}\r\n"
        f"DTSTART;VALUE=DATE:{start_clean}\r\n"
        f"DTEND;VALUE=DATE:{end_clean}\r\n"
        f"SUMMARY:{title}\r\n"
        f"DESCRIPTION:{desc_escaped}\r\n"
        f"LOCATION:{location}\r\n"
        "STATUS:CONFIRMED\r\n"
        "BEGIN:VALARM\r\n"
        "TRIGGER:-P1D\r\n"
        "ACTION:DISPLAY\r\n"
        f"DESCRIPTION:Pengingat Aturan Wisata Pramana Bali: {title}\r\n"
        "END:VALARM\r\n"
        "END:VEVENT\r\n"
        "END:VCALENDAR\r\n"
    )
    return ics_content
