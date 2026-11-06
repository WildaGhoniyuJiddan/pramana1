"""
Unit tests for Dual-Layer Verifier.
"""

from backend.services.corpus_loader import CorpusManager
from backend.services.verifier import DualLayerVerifier, quote_sha256


def _verifier():
    return DualLayerVerifier(CorpusManager.get_instance())


def test_layer1_exact_match_success():
    verifier = _verifier()
    quote = "Memuliakan kesucian Pura, Pratima, dan Simbol-simbol Keagamaan"
    assert verifier.verify_layer1_exact_match(quote, "SE_GUB_04_2023_DO") is True


def test_layer1_normalizes_whitespace():
    verifier = _verifier()
    quote = "Memuliakan   kesucian Pura,\nPratima, dan Simbol-simbol Keagamaan"
    assert verifier.verify_layer1_exact_match(quote, "SE_GUB_04_2023_DO") is True


def test_layer1_exact_match_failure_hallucination():
    verifier = _verifier()
    quote = (
        "Wisatawan dilarang mengenakan baju berwarna merah "
        "di pantai Sanur pada hari Selasa"
    )
    assert verifier.verify_layer1_exact_match(quote, "SE_GUB_04_2023_DO") is False


def test_layer1_unknown_regulation_fails():
    verifier = _verifier()
    assert verifier.verify_layer1_exact_match("Pasal apa pun", "TIDAK_ADA") is False


def test_quote_hash_is_stable_and_normalized():
    assert quote_sha256("Pura  Suci") == quote_sha256("Pura Suci")
    assert len(quote_sha256("Pura Suci")) == 64
    assert quote_sha256("Pura Suci") != quote_sha256("Pura Kotor")


def test_verify_and_filter_citations_propagates_provenance():
    verifier = _verifier()
    quote = "Memuliakan kesucian Pura, Pratima, dan Simbol-simbol Keagamaan"
    citations = [{"reg_id": "SE_GUB_04_2023_DO", "quoted_text": quote}]

    verified = verifier.verify_and_filter_citations(citations)
    assert len(verified) == 1

    citation = verified[0]
    assert citation["official_doc_title"].startswith("Surat Edaran Gubernur Bali")
    assert citation["verified_layer1"] is True
    assert citation["verification_scope"] == "corpus"
    assert citation["quote_sha256"] == quote_sha256(quote)
    assert citation["source_url"].startswith("https://")
    assert citation["last_verified_date"] == "2026-11-05"
    assert citation["is_verbatim"] is True
    assert citation["status"] == "Disempurnakan"
    assert citation["document_id"] == "se-gubernur-bali-4-2023"
    assert citation["text_status"] == "verbatim"
    assert citation["source_type"] == "official_pdf"


def test_verify_and_filter_resolves_legacy_alias_to_canonical_id():
    verifier = _verifier()
    citations = [{"reg_id": "PERDA_BALI_02_2025_LEVY"}]

    verified = verifier.verify_and_filter_citations(citations)
    assert len(verified) == 1
    assert verified[0]["reg_id"] == "PERDA_BALI_06_2023_LEVY"
    assert verified[0]["document_id"] == "perda-bali-2-2025"
    assert verified[0]["text_status"] == "verbatim"
    assert "Pasal 16A" in verified[0]["quoted_text"]


def test_verify_and_filter_overwrites_fabricated_legal_identifiers():
    verifier = _verifier()
    quote = "Memuliakan kesucian Pura, Pratima, dan Simbol-simbol Keagamaan"
    citations = [{
        "reg_id": "SE_GUB_04_2023_DO",
        "quoted_text": quote,
        "pasal": "Pasal 999",
        "penalties": "Denda fiktif",
    }]

    verified = verifier.verify_and_filter_citations(citations)
    assert verified[0]["pasal"] == "Poin 1.a s/d 1.h"
    assert verified[0]["penalties"] != "Denda fiktif"


def test_verify_and_filter_citations_drops_invalid_entries():
    verifier = _verifier()
    citations = [
        {"reg_id": "TIDAK_ADA", "quoted_text": "Pasal fiktif"},
        {
            "reg_id": "SE_GUB_04_2023_DO",
            "quoted_text": "Wisatawan wajib memakai topi merah di pantai",
        },
    ]
    assert verifier.verify_and_filter_citations(citations) == []


def test_verify_and_filter_fills_quote_when_omitted():
    verifier = _verifier()
    citations = [{"reg_id": "UU_06_2011_PASAL_75"}]
    verified = verifier.verify_and_filter_citations(citations)
    assert len(verified) == 1
    assert verified[0]["quoted_text"]
    assert verified[0]["quote_sha256"]


def test_layer2_guard_abstain_when_empty():
    verifier = _verifier()
    is_grounded, status = verifier.enforce_layer2_guard([])
    assert is_grounded is False
    assert status == "TIDAK_DITEMUKAN"


def test_layer2_guard_rejects_low_score():
    verifier = _verifier()
    reg = [{"id": "SE_GUB_04_2023_DO"}]
    is_grounded, status = verifier.enforce_layer2_guard(
        reg, retrieval_scores=[0.2]
    )
    assert is_grounded is False
    assert status == "TIDAK_DITEMUKAN"


def test_layer2_guard_accepts_threshold_score():
    verifier = _verifier()
    reg = [{"id": "SE_GUB_04_2023_DO"}]
    is_grounded, status = verifier.enforce_layer2_guard(
        reg, retrieval_scores=[0.5]
    )
    assert is_grounded is True
    assert status == "TERVERIFIKASI"


def test_layer2_guard_rejects_explicit_empty_scores():
    verifier = _verifier()
    reg = [{"id": "SE_GUB_04_2023_DO"}]
    is_grounded, status = verifier.enforce_layer2_guard(reg, retrieval_scores=[])
    assert is_grounded is False
    assert status == "TIDAK_DITEMUKAN"


def test_layer2_guard_reads_embedded_scores():
    verifier = _verifier()
    regs = [{"id": "SE_GUB_04_2023_DO", "_retrieval_score": 0.9}]
    is_grounded, status = verifier.enforce_layer2_guard(regs)
    assert is_grounded is True
    assert status == "TERVERIFIKASI"


def test_sanitize_statute_references_removes_article_and_amount():
    from backend.services.verifier import sanitize_statute_references

    text = (
        "Menurut Pasal 999 Ayat (2) UU No. 8 Tahun 1999, denda "
        "Rp999.000.000 dan 1000 dolar berlaku."
    )
    cleaned = sanitize_statute_references(
        text, "id", allowed_rupiah={"150000"}
    )
    assert "Pasal 999" not in cleaned
    assert "Ayat (2)" not in cleaned
    assert "UU No. 8 Tahun 1999" not in cleaned
    assert "Rp999.000.000" not in cleaned
    assert "1000 dolar" not in cleaned


def test_enforce_epistemic_safety_hard_locks_tier2():
    from backend.services.verifier import enforce_epistemic_safety

    result = {
        "summary_id": "Berdasarkan Pasal 999, denda Rp9.000.000 berlaku.",
        "summary_en": "Under Pasal 999, a fine applies.",
        "claims": [{"verified": True, "citation_id": "X", "span_ids": ["X#s1"]}],
        "resolution_mode": "NEEDS_CLARIFICATION",
        "detected_framing_or_tone": "Keluhan subjektif",
        "user_guidance": {
            "missing_context_diagnosis": ["Lokasi belum jelas."],
            "what_user_should_do_next": ["Tulis kronologi."],
            "suggested_query_rewrites": ["Saya ditolak masuk di beach club Bali"],
            "relevant_authority_or_channel": "BPSK",
        },
        "ai_synthesis_status": "llm",
        "guard_status": "LLM_TRIAGE",
    }
    cleaned = enforce_epistemic_safety(
        result,
        citations=[],
        top_score=0.4,
        taxonomy={"candidate_clusters": ["DISKRIMINASI_DAN_KONSUMEN"]},
        allowed_rupiah={"150000"},
    )
    assert cleaned["claims"] == []
    assert "Pasal 999" not in cleaned["summary_id"]
    assert "Rp9.000.000" not in cleaned["summary_id"]
    assert cleaned["guard_status"] == "EPISTEMIC_HARD_LOCK"
