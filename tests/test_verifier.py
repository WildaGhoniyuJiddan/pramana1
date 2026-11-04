"""
Unit tests for Dual-Layer Verifier.
"""

from backend.services.verifier import DualLayerVerifier
from backend.services.corpus_loader import CorpusManager


def test_layer1_exact_match_success():
    corpus_mgr = CorpusManager.get_instance()
    verifier = DualLayerVerifier(corpus_mgr)

    # Exact snippet from SE No. 4 Tahun 2023
    quote = "Memuliakan kesucian Pura, Pratima, dan Simbol-simbol Keagamaan"
    assert verifier.verify_layer1_exact_match(quote, "SE_GUB_04_2023_DO") is True


def test_layer1_exact_match_failure_hallucination():
    corpus_mgr = CorpusManager.get_instance()
    verifier = DualLayerVerifier(corpus_mgr)

    # Fabricated / hallucinated legal clause
    quote = "Wisatawan dilarang mengenakan baju berwarna merah di pantai Sanur pada hari Selasa"
    assert verifier.verify_layer1_exact_match(quote, "SE_GUB_04_2023_DO") is False


def test_layer2_guard_abstain():
    corpus_mgr = CorpusManager.get_instance()
    verifier = DualLayerVerifier(corpus_mgr)

    # Empty retrieved list must return TIDAK_DITEMUKAN
    is_grounded, status = verifier.enforce_layer2_guard([])
    assert is_grounded is False
    assert status == "TIDAK_DITEMUKAN"
