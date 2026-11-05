"""
Unit tests for PII masking module.
"""

from backend.services.ocr_masking import mask_pii


def test_email_masking():
    text = "Booking atas nama John Doe email john.doe@example.com untuk villa di Canggu."
    masked, counts = mask_pii(text)
    assert "[EMAIL_DISAMARKAN]" in masked
    assert "john.doe@example.com" not in masked
    assert counts["email"] == 1


def test_phone_masking():
    text = "Kontak darurat hotel: +6281234567890 atau 081987654321."
    masked, counts = mask_pii(text)
    assert "[TELEPON_DISAMARKAN]" in masked
    assert "081234567890" not in masked
    assert counts["phone"] >= 1


def test_booking_code_masking():
    text = "E-ticket penerbangan Garuda Indonesia Kode Booking: ABC123X tiba di Denpasar."
    masked, counts = mask_pii(text)
    assert "[KODE_BOOKING_DISAMARKAN]" in masked
    assert "ABC123X" not in masked
    assert counts["booking_code"] == 1


def test_booking_code_masking_with_intervening_word():
    text = "Kode booking saya BK12345 untuk penerbangan besok."
    masked, counts = mask_pii(text)
    assert "[KODE_BOOKING_DISAMARKAN]" in masked
    assert "BK12345" not in masked
    assert counts["booking_code"] == 1


def test_passport_masking_with_nomor_paspor():
    text = "Nomor paspor saya A1234567 dan visa saya masih berlaku."
    masked, counts = mask_pii(text)
    assert "[PASPOR_DISAMARKAN]" in masked
    assert "A1234567" not in masked
    assert counts["passport"] == 1


def test_clean_text_no_masking():
    text = "Rencana liburan ke Pura Besakih dan Danau Beratan bersama keluarga."
    masked, counts = mask_pii(text)
    assert masked == text
    assert sum(counts.values()) == 0
