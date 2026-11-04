"""
Unit tests for Pramana Regulation Corpus integrity and retrieval.
"""

import os
import pytest
from backend.services.corpus_loader import CorpusManager


@pytest.fixture
def corpus_mgr():
    return CorpusManager.get_instance()


def test_corpus_loading_and_metadata(corpus_mgr):
    assert corpus_mgr.metadata["version"] == "1.0.0"
    assert len(corpus_mgr.regulations) >= 6
    assert "1A" in corpus_mgr.tiers
    assert "1B" in corpus_mgr.tiers
    assert "2" in corpus_mgr.tiers


def test_all_regulations_have_required_fields(corpus_mgr):
    required_fields = ["id", "doc_title", "tier", "category", "bab", "pasal", "text", "source_url", "keywords"]
    for reg in corpus_mgr.regulations:
        for field in required_fields:
            assert field in reg, f"Field '{field}' missing in regulation {reg.get('id')}"
            assert len(str(reg[field])) > 0, f"Field '{field}' is empty in regulation {reg.get('id')}"


def test_search_exact_keywords(corpus_mgr):
    # Test Nyepi query
    nyepi_results = corpus_mgr.search_regulations("aturan catur brata nyepi pecalang")
    assert len(nyepi_results) > 0
    assert nyepi_results[0]["id"] == "KETENTUAN_HARI_RAYA_NYEPI"

    # Test Deportation / Immigration query
    imigrasi_results = corpus_mgr.search_regulations("deportasi orang asing pelanggaran izin tinggal")
    assert len(imigrasi_results) > 0
    assert imigrasi_results[0]["id"] == "UU_06_2011_PASAL_75"

    # Test Tourist Levy query
    levy_results = corpus_mgr.search_regulations("pungutan wisatawan asing 150000 love bali")
    assert len(levy_results) > 0
    assert levy_results[0]["id"] == "PERDA_BALI_06_2023_LEVY"

    # Test Sacred Tree climbing query
    tree_results = corpus_mgr.search_regulations("memanjat pohon suci pakaian tidak pantas")
    assert len(tree_results) > 0
    assert tree_results[0]["id"] == "SE_GUB_04_2023_DONT"


def test_irrelevant_query_abstain(corpus_mgr):
    # Query totally outside legal domain
    results = corpus_mgr.search_regulations("resep membuat rendang daging sapi padang bumbu kelapa")
    assert len(results) == 0
