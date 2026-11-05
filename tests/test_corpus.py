"""
Unit tests for Pramana Regulation Corpus integrity and retrieval.
"""

import pytest

from backend.services.corpus_loader import (
    DEFAULT_RELEVANCE_THRESHOLD,
    RELATIVE_SCORE_RATIO,
    CorpusManager,
)


@pytest.fixture
def corpus_mgr():
    return CorpusManager.get_instance()


def test_corpus_loading_and_metadata(corpus_mgr):
    assert corpus_mgr.metadata["version"] == "1.1.0"
    assert corpus_mgr.metadata["last_verified_date"] == "2026-11-05"
    assert len(corpus_mgr.regulations) >= 6
    assert "1A" in corpus_mgr.tiers
    assert "1B" in corpus_mgr.tiers
    assert "2" in corpus_mgr.tiers
    assert corpus_mgr.metadata["known_gaps"]


def test_all_regulations_have_required_fields(corpus_mgr):
    required_fields = [
        "id", "doc_title", "tier", "category", "bab", "pasal", "text",
        "source_url", "keywords",
    ]
    for reg in corpus_mgr.regulations:
        for field in required_fields:
            assert field in reg, f"Field '{field}' missing in regulation {reg.get('id')}"
            assert len(str(reg[field])) > 0, f"Field '{field}' is empty in {reg.get('id')}"

        assert reg["source_url"].startswith("https://")
        assert reg.get("last_verified_date"), f"Missing last_verified_date in {reg['id']}"
        assert reg.get("status"), f"Missing status in {reg['id']}"
        assert isinstance(reg.get("is_verbatim"), bool), f"Missing is_verbatim in {reg['id']}"


def test_search_scored_returns_relevance_metadata(corpus_mgr):
    results = corpus_mgr.search_regulations_scored(
        "aturan catur brata nyepi pecalang", top_k=4
    )
    assert results
    top = results[0]
    assert top["regulation"]["id"] == "KETENTUAN_HARI_RAYA_NYEPI"
    assert top["score"] >= DEFAULT_RELEVANCE_THRESHOLD
    assert "nyepi" in top["matched_terms"]

    # Relative cutoff should drop weak incidental matches such as entries that
    # only share the generic word "aturan".
    assert all(
        item["score"] >= top["score"] * RELATIVE_SCORE_RATIO for item in results
    )
    assert len(results) == 1


def test_search_exact_keywords(corpus_mgr):
    nyepi_results = corpus_mgr.search_regulations("aturan catur brata nyepi pecalang")
    assert len(nyepi_results) > 0
    assert nyepi_results[0]["id"] == "KETENTUAN_HARI_RAYA_NYEPI"

    imigrasi_results = corpus_mgr.search_regulations(
        "deportasi orang asing pelanggaran izin tinggal"
    )
    assert len(imigrasi_results) > 0
    assert imigrasi_results[0]["id"] == "UU_06_2011_PASAL_75"

    levy_results = corpus_mgr.search_regulations(
        "pungutan wisatawan asing 150000 love bali"
    )
    assert len(levy_results) > 0
    assert levy_results[0]["id"] == "PERDA_BALI_06_2023_LEVY"

    tree_results = corpus_mgr.search_regulations(
        "memanjat pohon suci pakaian tidak pantas"
    )
    assert len(tree_results) > 0
    assert tree_results[0]["id"] == "SE_GUB_04_2023_DONT"


def test_irrelevant_query_abstain(corpus_mgr):
    results = corpus_mgr.search_regulations(
        "resep membuat rendang daging sapi padang bumbu kelapa"
    )
    assert results == []


def test_provenance_and_non_verbatim_flags(corpus_mgr):
    levy = corpus_mgr.get_by_id("PERDA_BALI_06_2023_LEVY")
    assert levy is not None
    assert levy["is_verbatim"] is False
    assert levy["text_status"] == "paraphrase"
    assert "peraturan.bpk.go.id" in levy["source_url"]

    nyepi = corpus_mgr.get_by_id("KETENTUAN_HARI_RAYA_NYEPI")
    assert nyepi is not None
    assert nyepi["is_verbatim"] is False
    assert nyepi["text_status"] == "compilation"

    se_do = corpus_mgr.get_by_id("SE_GUB_04_2023_DO")
    assert se_do["superseded_by"] == "SE Gubernur Bali No. 7 Tahun 2025"
    assert se_do["superseded_by_url"].startswith("https://")


def test_unknown_id_returns_none(corpus_mgr):
    assert corpus_mgr.get_by_id("TIDAK_ADA") is None
