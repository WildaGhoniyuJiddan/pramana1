"""Tests for the colloquial-to-legal taxonomy and epistemic routing."""

from backend.services.legal_taxonomy import (
    assess_factual_completeness,
    build_deterministic_guidance,
    build_triage_summary,
    choose_epistemic_mode,
    detect_registry_only,
)


def test_subjective_complaint_is_triage_not_complete():
    taxonomy = assess_factual_completeness(
        "direndahkan, disepelekan, dianggap tidak memiliki uang"
    )
    assert taxonomy["candidate_clusters"] == ["DISKRIMINASI_DAN_KONSUMEN"]
    assert taxonomy["is_factually_complete"] is False
    assert taxonomy["has_location"] is False
    assert len(taxonomy["missing_elements"]) >= 2
    assert choose_epistemic_mode(0.9, taxonomy) == "NEEDS_CLARIFICATION"


def test_concrete_consumer_denial_is_complete():
    taxonomy = assess_factual_completeness(
        "Wisatawan lokal ditolak masuk dan dibedakan syarat minimum spend "
        "dengan WNA di beach club Bali"
    )
    assert taxonomy["candidate_clusters"] == ["DISKRIMINASI_DAN_KONSUMEN"]
    assert taxonomy["is_factually_complete"] is True
    assert taxonomy["has_location"] is True
    assert taxonomy["has_action"] is True
    assert choose_epistemic_mode(0.8, taxonomy) == "VERIFIED_GROUNDED"


def test_registry_only_detection_accepts_surat_edaran_phrasing():
    assert (
        detect_registry_only("Apa isi SE Gubernur Bali 7/2025?")
        == "Surat Edaran Gubernur Bali No. 7 Tahun 2025"
    )
    assert detect_registry_only("Bagaimana aturan awig-awig desa adat?")
    assert detect_registry_only("Apa pedoman SKB ITE?")
    assert detect_registry_only("Apa isi SE Kapolri?")
    assert detect_registry_only("Apa isi SE Gubernur Bali 4/2023?") is None


def test_out_of_scope_has_no_cluster_and_gets_guidance():
    taxonomy = assess_factual_completeness("Harga kopi di Canggu terlalu mahal.")
    assert taxonomy["candidate_clusters"] == []
    assert choose_epistemic_mode(0.0, taxonomy) == "OUT_OF_SCOPE_GUIDANCE"
    guidance = build_deterministic_guidance(
        taxonomy, "OUT_OF_SCOPE_GUIDANCE"
    )
    assert guidance["missing_context_diagnosis"]
    assert len(guidance["what_user_should_do_next"]) == 3
    assert len(guidance["suggested_query_rewrites"]) == 3
    assert guidance["relevant_authority_or_channel"]


def test_triage_summary_is_empathetic_and_specific():
    taxonomy = assess_factual_completeness(
        "direndahkan, disepelekan, dianggap tidak memiliki uang"
    )
    summary = build_triage_summary(taxonomy, "NEEDS_CLARIFICATION", "id")
    assert "direndahkan" in summary.lower() or "merendahkan" in summary.lower()
    assert "Pasal 999" not in summary
