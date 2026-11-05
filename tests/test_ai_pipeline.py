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
