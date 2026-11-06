"""Tests for the single-pass grounded AI pipeline and evidence spans."""

import pytest

from backend.services.ai_pipeline import GroundedAIPipeline
from backend.services.corpus_loader import CorpusManager
from backend.services.evidence_spans import build_span_index, split_evidence_spans


@pytest.fixture
def citations():
    corpus = CorpusManager.get_instance()
    reg = corpus.get_by_id("PERDA_BALI_06_2023_LEVY")
    return [{
        "reg_id": reg["id"],
        "official_doc_title": reg["doc_title"],
        "pasal": reg["pasal"],
        "quoted_text": reg["text"],
        "text_status": reg["text_status"],
    }]


def _pipeline(parsed):
    return GroundedAIPipeline(
        lambda *args, **kwargs: (
            parsed,
            "mock-gemini",
            {"latency_ms": 1, "model": "mock"},
        )
    )


def test_evidence_spans_are_substrings_of_chunk():
    corpus = CorpusManager.get_instance()
    reg = corpus.get_by_id("UU_18_2025_PASAL_25")
    spans = split_evidence_spans(reg["text"])
    assert spans
    normalized = " ".join(reg["text"].split())
    for span in spans:
        assert span in normalized


def test_pipeline_accepts_valid_span_claim(citations, monkeypatch):
    monkeypatch.setenv("AI_MODE", "optional")
    span_index = build_span_index(citations)
    span_id = next(iter(span_index))

    parsed = {
        "abstain": False,
        "summary_id": "Wisatawan asing wajib membayar pungutan Rp150.000.",
        "summary_en": "Foreign tourists must pay the IDR 150,000 levy.",
        "claims": [{
            "claim_text_id": "Wisatawan asing wajib membayar pungutan Rp150.000.",
            "claim_text_en": "Foreign tourists must pay the IDR 150,000 levy.",
            "citation_id": "PERDA_BALI_06_2023_LEVY",
            "span_ids": [span_id],
        }],
    }

    result = _pipeline(parsed).answer(
        citations=citations,
        system_prompt="test",
        user_prompt="test",
        fallback_summary="fallback",
    )

    assert result["ai_synthesis_status"] == "llm"
    assert result["guard_status"] == "LLM_GROUNDED"
    assert len(result["claims"]) == 1
    assert result["claims"][0]["verified"] is True


def test_pipeline_drops_claim_with_invalid_span(citations, monkeypatch):
    monkeypatch.setenv("AI_MODE", "optional")
    parsed = {
        "abstain": False,
        "summary_id": "Wisatawan asing wajib membayar pungutan Rp150.000.",
        "summary_en": "Foreign tourists must pay the IDR 150,000 levy.",
        "claims": [{
            "claim_text_id": "Wisatawan asing wajib membayar pungutan Rp150.000.",
            "claim_text_en": "Foreign tourists must pay the IDR 150,000 levy.",
            "citation_id": "PERDA_BALI_06_2023_LEVY",
            "span_ids": ["PERDA_BALI_06_2023_LEVY#s999"],
        }],
    }

    result = _pipeline(parsed).answer(
        citations=citations,
        system_prompt="test",
        user_prompt="test",
        fallback_summary="fallback",
    )

    assert result["ai_synthesis_status"] == "deterministic"
    assert result["guard_status"] == "FALLBACK_GUARD"
    assert result["claims"] == []


def test_pipeline_rejects_hallucinated_article(citations, monkeypatch):
    monkeypatch.setenv("AI_MODE", "optional")
    span_index = build_span_index(citations)
    span_id = next(iter(span_index))

    parsed = {
        "abstain": False,
        "summary_id": "Pasal 999 mewajibkan denda Rp999.000.000.",
        "summary_en": "Pasal 999 requires a Rp999.000.000 fine.",
        "claims": [{
            "claim_text_id": "Pasal 999 mewajibkan denda Rp999.000.000.",
            "claim_text_en": "Pasal 999 requires a Rp999.000.000 fine.",
            "citation_id": "PERDA_BALI_06_2023_LEVY",
            "span_ids": [span_id],
        }],
    }

    result = _pipeline(parsed).answer(
        citations=citations,
        system_prompt="test",
        user_prompt="test",
        fallback_summary="fallback",
    )

    assert result["ai_synthesis_status"] == "deterministic"
    assert result["guard_status"] == "FALLBACK_GUARD"
    assert "Pasal 999" not in (result["summary_id"] or "")


def test_pipeline_rejects_unsupported_foreign_currency(citations, monkeypatch):
    monkeypatch.setenv("AI_MODE", "optional")
    span_index = build_span_index(citations)
    span_id = next(iter(span_index))

    parsed = {
        "abstain": False,
        "summary_id": "Turis wajib membayar 1000 dolar.",
        "summary_en": "Tourists must pay 1000 dolar.",
        "claims": [{
            "claim_text_id": "Turis wajib membayar 1000 dolar.",
            "claim_text_en": "Tourists must pay 1000 dolar.",
            "citation_id": "PERDA_BALI_06_2023_LEVY",
            "span_ids": [span_id],
        }],
    }

    result = _pipeline(parsed).answer(
        citations=citations,
        system_prompt="test",
        user_prompt="test",
        fallback_summary="fallback",
    )

    assert result["ai_synthesis_status"] == "deterministic"
    assert result["guard_status"] == "FALLBACK_GUARD"
    assert "1000 dolar" not in (result["summary_id"] or "")


def test_pipeline_supports_abstain(citations, monkeypatch):
    monkeypatch.setenv("AI_MODE", "required")
    parsed = {
        "abstain": True,
        "summary_id": "",
        "summary_en": "",
        "claims": [],
    }

    result = _pipeline(parsed).answer(
        citations=citations,
        system_prompt="test",
        user_prompt="test",
        fallback_summary="fallback",
    )

    assert result["ai_synthesis_status"] == "abstain"
    assert result["guard_status"] == "AI_ABSTAIN"
    assert result["claims"] == []


def test_pipeline_tier2_hard_locks_citations_and_sanitizes(citations, monkeypatch):
    monkeypatch.setenv("AI_MODE", "required")
    span_index = build_span_index(citations)
    span_id = next(iter(span_index))
    parsed = {
        "abstain": False,
        "resolution_mode": "NEEDS_CLARIFICATION",
        "detected_framing_or_tone": "Keluhan subjektif",
        "summary_indonesian": (
            "Berdasarkan Pasal 999 dan UU No. 8 Tahun 1999, denda "
            "Rp999.000.000 berlaku."
        ),
        "summary_english": "Under Pasal 999, a Rp999.000.000 fine applies.",
        "claims": [{
            "claim_text_indonesian": "Pasal 999 mewajibkan denda.",
            "claim_text_english": "Pasal 999 requires a fine.",
            "citation_id": "PERDA_BALI_06_2023_LEVY",
            "span_ids": [span_id],
            "exact_source_span": "",
        }],
        "user_guidance": {
            "missing_context_diagnosis": ["Lokasi kejadian belum jelas."],
            "what_user_should_do_next": ["Tulis kronologi."],
            "suggested_query_rewrites": [
                "Wisatawan lokal ditolak masuk di beach club Bali",
            ],
            "relevant_authority_or_channel": "BPSK",
        },
    }

    result = _pipeline(parsed).answer(
        citations=citations,
        system_prompt="test",
        user_prompt="test",
        fallback_summary="fallback",
        resolution_mode="NEEDS_CLARIFICATION",
        taxonomy={
            "candidate_clusters": ["DISKRIMINASI_DAN_KONSUMEN"],
            "is_factually_complete": False,
            "tone": "Keluhan subjektif",
        },
        top_score=0.8,
        fallback_guidance={
            "suggested_query_rewrites": [
                "Wisatawan lokal ditolak masuk dan dibedakan di beach club Bali",
                "Pelaku usaha restoran menolak melayani pengunjung lokal",
                "Staf tempat wisata menghina pengunjung berdasarkan etnis",
            ],
            "relevant_authority_or_channel": "BPSK",
        },
        allowed_rupiah={"150000"},
    )

    assert result["resolution_mode"] == "NEEDS_CLARIFICATION"
    assert result["claims"] == []
    assert "Pasal 999" not in (result["summary_id"] or "")
    assert "UU No. 8 Tahun 1999" not in (result["summary_id"] or "")
    assert "Rp999.000.000" not in (result["summary_id"] or "")
    assert len(result["user_guidance"]["suggested_query_rewrites"]) == 3


def test_pipeline_tier1_downgrades_when_all_claims_fail(citations, monkeypatch):
    monkeypatch.setenv("AI_MODE", "required")
    parsed = {
        "abstain": False,
        "resolution_mode": "VERIFIED_GROUNDED",
        "detected_framing_or_tone": "Kronologi faktual",
        "summary_indonesian": "Wisatawan asing wajib membayar pungutan Rp150.000.",
        "summary_english": "Foreign tourists must pay the IDR 150,000 levy.",
        "claims": [{
            "claim_text_indonesian": "Klaim tanpa span yang valid.",
            "claim_text_english": "A claim without a valid span.",
            "citation_id": "PERDA_BALI_06_2023_LEVY",
            "span_ids": ["PERDA_BALI_06_2023_LEVY#s999"],
            "exact_source_span": "",
        }],
        "user_guidance": {
            "missing_context_diagnosis": [],
            "what_user_should_do_next": [],
            "suggested_query_rewrites": [],
            "relevant_authority_or_channel": "",
        },
    }

    result = _pipeline(parsed).answer(
        citations=citations,
        system_prompt="test",
        user_prompt="test",
        fallback_summary="fallback",
        resolution_mode="VERIFIED_GROUNDED",
        taxonomy={"candidate_clusters": ["PUNGUTAN_DAN_KEWAJIBAN_WNA"]},
        top_score=0.8,
        allowed_rupiah={"150000"},
    )

    assert result["resolution_mode"] == "NEEDS_CLARIFICATION"
    assert result["claims"] == []
    assert result["guard_status"] in {"AI_OUTPUT_DITOLAK", "FALLBACK_GUARD"}

def test_pipeline_rejects_fake_rupiah_substring_match(citations, monkeypatch):
    monkeypatch.setenv("AI_MODE", "optional")
    span_index = build_span_index(citations)
    span_id = next(iter(span_index))

    # Rp500.000 is fake, should NOT match Rp150.000,00 substring
    parsed = {
        "abstain": False,
        "summary_id": "Wisatawan asing wajib membayar denda Rp500.000 di Bali.",
        "summary_en": "Foreign tourists must pay a 500,000 fine in Bali.",
        "claims": [{
            "claim_text_id": "Wisatawan asing wajib membayar denda Rp500.000 di Bali.",
            "claim_text_en": "Foreign tourists must pay a 500,000 fine in Bali.",
            "citation_id": "PERDA_BALI_06_2023_LEVY",
            "span_ids": [span_id],
        }],
    }

    result = _pipeline(parsed).answer(
        citations=citations,
        system_prompt="test",
        user_prompt="test",
        fallback_summary="fallback",
    )

    assert result["ai_synthesis_status"] == "deterministic"
    assert result["guard_status"] == "FALLBACK_GUARD"


def test_pipeline_rejects_external_url(citations, monkeypatch):
    monkeypatch.setenv("AI_MODE", "optional")
    span_index = build_span_index(citations)
    span_id = next(iter(span_index))

    parsed = {
        "abstain": False,
        "summary_id": "Bayar retribusi via http://evil.example/pay resmi.",
        "summary_en": "Pay levy via http://evil.example/pay official.",
        "claims": [{
            "claim_text_id": "Wisatawan asing wajib membayar pungutan Rp150.000.",
            "claim_text_en": "Foreign tourists must pay the IDR 150,000 levy.",
            "citation_id": "PERDA_BALI_06_2023_LEVY",
            "span_ids": [span_id],
        }],
    }

    result = _pipeline(parsed).answer(
        citations=citations,
        system_prompt="test",
        user_prompt="test",
        fallback_summary="fallback",
    )

    assert result["ai_synthesis_status"] == "deterministic"
    assert result["guard_status"] == "FALLBACK_GUARD"


def test_pipeline_rejects_invented_number(citations, monkeypatch):
    monkeypatch.setenv("AI_MODE", "optional")
    span_index = build_span_index(citations)
    span_id = next(iter(span_index))

    parsed = {
        "abstain": False,
        "summary_id": "Pembayaran pungutan berlaku selama 30 hari di Bali.",
        "summary_en": "Levy payment is valid for 30 days in Bali.",
        "claims": [{
            "claim_text_id": "Wisatawan asing wajib membayar pungutan Rp150.000.",
            "claim_text_en": "Foreign tourists must pay the IDR 150,000 levy.",
            "citation_id": "PERDA_BALI_06_2023_LEVY",
            "span_ids": [span_id],
        }],
    }

    result = _pipeline(parsed).answer(
        citations=citations,
        system_prompt="test",
        user_prompt="test",
        fallback_summary="fallback",
    )

    assert result["ai_synthesis_status"] == "deterministic"
    assert result["guard_status"] == "FALLBACK_GUARD"


def test_pipeline_rejects_contradiction_phrase(citations, monkeypatch):
    monkeypatch.setenv("AI_MODE", "optional")
    span_index = build_span_index(citations)
    span_id = next(iter(span_index))

    parsed = {
        "abstain": False,
        "summary_id": "Semua wisatawan dibebaskan dari semua kewajiban pungutan.",
        "summary_en": "All tourists are exempt from all levy payments.",
        "claims": [{
            "claim_text_id": "Wisatawan asing wajib membayar pungutan Rp150.000.",
            "claim_text_en": "Foreign tourists must pay the IDR 150,000 levy.",
            "citation_id": "PERDA_BALI_06_2023_LEVY",
            "span_ids": [span_id],
        }],
    }

    result = _pipeline(parsed).answer(
        citations=citations,
        system_prompt="test",
        user_prompt="test",
        fallback_summary="fallback",
    )

    assert result["ai_synthesis_status"] == "deterministic"
    assert result["guard_status"] == "FALLBACK_GUARD"


def test_pipeline_rejects_fabricated_duration_unit():
    """B1: Numbers with units must match exact values in citations, not stray digits."""
    sample_citations = [{
        "reg_id": "TEST_REG",
        "official_doc_title": "Test Law",
        "tier": "1A",
        "tier_label": "UU",
        "pasal": "Pasal 10 ayat (3)",
        "quoted_text": "Sesuai Pasal 10 ayat (3), wisatawan wajib melapor dalam waktu 24 jam.",
        "penalties": "Denda",
        "source_url": "https://example.com/law",
    }]

    valid_text = "Wisatawan wajib melapor dalam waktu 24 jam sesuai ketentuan Pasal 10."
    assert GroundedAIPipeline._guard_text(valid_text, sample_citations) is True

    fabricated_text = "Wisatawan diberikan batas waktu 3 hari untuk melapor sesuai Pasal 10."
    assert GroundedAIPipeline._guard_text(fabricated_text, sample_citations) is False
