"""
PII Masking Service for Pramana Strict-RAG.

Strips five categories of sensitive personal information before text is
processed or forwarded to an LLM:
1. Email addresses
2. Phone numbers
3. Booking references / PNR / e-ticket codes
4. Payment card numbers
5. Passport numbers

This is a best-effort deterministic filter, not a complete DLP system.
"""

import re
from typing import Dict, Any, Tuple


EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b')
PHONE_PATTERN = re.compile(r'(?:\+?62|08|0)[0-9\s\-]{8,14}[0-9]')
BOOKING_CODE_PATTERN = re.compile(
    r'\b(?:Booking|Kode\s*Booking|PNR|E-ticket|Ticket|Kode\s*Pemesanan)'
    r'[^\n]{0,25}?\b(?=[A-Z0-9]*\d)([A-Z0-9]{5,8})\b',
    re.IGNORECASE,
)
CARD_PATTERN = re.compile(r'\b(?:\d{4}[-\s]?){3}\d{4}\b')
PASSPORT_PATTERN = re.compile(
    r'\b(?:Passport|Paspor|No\.?\s*Paspor|Nomor\s*Paspor)'
    r'[^\n]{0,25}?\b([A-Z0-9]{7,10})\b',
    re.IGNORECASE,
)


def mask_pii(text: str) -> Tuple[str, Dict[str, int]]:
    """
    Mask personally identifiable information from text.
    Returns (masked_text, count_of_redactions).
    """
    if not text:
        return "", {}

    counts = {
        "email": 0,
        "phone": 0,
        "booking_code": 0,
        "card": 0,
        "passport": 0
    }

    # Mask emails
    def email_repl(match):
        counts["email"] += 1
        return "[EMAIL_DISAMARKAN]"
    masked = EMAIL_PATTERN.sub(email_repl, text)

    # Mask booking reference codes
    def booking_repl(match):
        counts["booking_code"] += 1
        return f"{match.group(0).split(match.group(1))[0]}[KODE_BOOKING_DISAMARKAN]"
    masked = BOOKING_CODE_PATTERN.sub(booking_repl, masked)

    # Mask passport
    def passport_repl(match):
        counts["passport"] += 1
        return f"{match.group(0).split(match.group(1))[0]}[PASPOR_DISAMARKAN]"
    masked = PASSPORT_PATTERN.sub(passport_repl, masked)

    # Mask credit/debit card numbers
    def card_repl(match):
        counts["card"] += 1
        return "[NOMOR_KARTU_DISAMARKAN]"
    masked = CARD_PATTERN.sub(card_repl, masked)

    # Mask phone numbers
    def phone_repl(match):
        counts["phone"] += 1
        return "[TELEPON_DISAMARKAN]"
    masked = PHONE_PATTERN.sub(phone_repl, masked)

    return masked, counts
