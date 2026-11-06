"""
Unit tests for Pramana Regulation Corpus integrity and retrieval.
"""

import json
from pathlib import Path

import pytest

from backend.services.corpus_loader import (
    CORPUS_PATH,
    DEFAULT_RELEVANCE_THRESHOLD,
    RELATIVE_SCORE_RATIO,
    CorpusManager,
)


@pytest.fixture
def corpus_mgr():
    return CorpusManager.get_instance()


def test_corpus_loading_and_metadata(corpus_mgr):
    assert corpus_mgr.metadata["version"] == "1.3.0"
    assert corpus_mgr.metadata["last_verified_date"] in {"2026-11-05", "2026-11-06"}
    assert len(corpus_mgr.regulations) == 42
    assert len(corpus_mgr.documents) == 29
    assert corpus_mgr.metadata["total_documents"] == 29
    assert corpus_mgr.metadata["total_manifest_documents"] == 21
    assert corpus_mgr.metadata["total_regulation_chunks"] == 42
    assert corpus_mgr.metadata["document_registry"]["url_check"]["checked_date"] == "2026-11-05"
    assert "1A" in corpus_mgr.tiers
    assert "1B" in corpus_mgr.tiers
    assert "2" in corpus_mgr.tiers
    assert "3" in corpus_mgr.tiers
    assert corpus_mgr.metadata["known_gaps"]


def test_all_regulations_have_required_fields(corpus_mgr):
    required_fields = [
        "id", "doc_title", "tier", "category", "bab", "pasal", "text",
        "source_url", "keywords", "document_id", "text_status", "source_type",
        "is_verbatim",
    ]
    for reg in corpus_mgr.regulations:
        for field in required_fields:
            assert field in reg, f"Field '{field}' missing in regulation {reg.get('id')}"
            assert len(str(reg[field])) > 0, f"Field '{field}' is empty in {reg.get('id')}"

        assert reg["source_url"].startswith("https://")
        assert reg.get("last_verified_date"), f"Missing last_verified_date in {reg['id']}"
        assert reg.get("status"), f"Missing status in {reg['id']}"
        assert isinstance(reg.get("is_verbatim"), bool), f"Missing is_verbatim in {reg['id']}"

        document = corpus_mgr.get_document(reg["document_id"])
        assert document is not None, f"Unknown document in {reg['id']}"
        assert reg["id"] in document["regulation_ids"]
        assert document["retrieval_eligible"] is True


def test_document_registry_matches_chunks(corpus_mgr):
    assert len({doc["id"] for doc in corpus_mgr.documents}) == 29
    assert sum(1 for doc in corpus_mgr.documents if doc["in_manifest"]) == 21

    legacy = corpus_mgr.get_document("se-gubernur-bali-4-2023")
    assert legacy is not None
    assert legacy["in_manifest"] is False
    assert set(legacy["regulation_ids"]) == {
        "SE_GUB_04_2023_DO", "SE_GUB_04_2023_DONT",
    }

    for doc in corpus_mgr.documents:
        assert doc["tier"] in corpus_mgr.tiers
        actual = {
            reg["id"] for reg in corpus_mgr.regulations
            if reg["document_id"] == doc["id"]
        }
        assert actual == set(doc["regulation_ids"])

        if doc["retrieval_eligible"]:
            assert doc["regulation_ids"]
            assert doc["text_status"] not in {"non-verbatim", "belum-diambil"}
        else:
            assert doc["regulation_ids"] == []


def test_unretrieved_documents_are_honestly_marked(corpus_mgr):
    tourism_law = corpus_mgr.get_document("uu-18-2025")
    assert tourism_law["text_status"] == "verbatim-ocr-dibersihkan"
    assert tourism_law["retrieval_eligible"] is True
    assert tourism_law["regulation_ids"]

    pending = corpus_mgr.get_document("pergub-bali-52-2021")
    assert pending["text_status"] == "belum-diambil"
    assert pending["retrieval_eligible"] is False
    assert pending["regulation_ids"] == []

    circular = corpus_mgr.get_document("se-gubernur-bali-7-2025")
    assert circular["text_status"] == "non-verbatim"
    assert circular["retrieval_eligible"] is False

    for doc_id in (
        "awig-awig-desa-adat-penglipuran",
        "awig-awig-desa-adat-tenganan-pegringsingan",
    ):
        doc = corpus_mgr.get_document(doc_id)
        assert doc["tier"] == "3"
        assert doc["retrieval_eligible"] is False


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


def test_search_returns_only_documents_with_chunks(corpus_mgr):
    results = corpus_mgr.search_regulations(
        "undang undang cagar budaya benda cagar budaya", top_k=10
    )
    for reg in results:
        document = corpus_mgr.get_document_for_regulation(reg["id"])
        assert document is not None
        assert document["retrieval_eligible"] is True


def test_irrelevant_query_abstain(corpus_mgr):
    results = corpus_mgr.search_regulations(
        "resep membuat rendang daging sapi padang bumbu kelapa"
    )
    assert results == []


def test_provenance_and_non_verbatim_flags(corpus_mgr):
    levy = corpus_mgr.get_by_id("PERDA_BALI_06_2023_LEVY")
    assert levy is not None
    assert levy["is_verbatim"] is True
    assert levy["text_status"] == "verbatim"
    assert levy["document_id"] == "perda-bali-2-2025"
    assert "peraturan.bpk.go.id" in levy["source_url"]
    assert len(levy["source_pdf_sha256"]) == 64
    assert "Pasal 4A" in levy["text"]
    assert "Pasal 16A" in levy["text"]
    assert "Rp150.000,00" in levy["text"]

    nyepi = corpus_mgr.get_by_id("KETENTUAN_HARI_RAYA_NYEPI")
    assert nyepi is not None
    assert nyepi["is_verbatim"] is False
    assert nyepi["text_status"] == "compilation"

    se_do = corpus_mgr.get_by_id("SE_GUB_04_2023_DO")
    assert se_do["superseded_by"] == "SE Gubernur Bali No. 7 Tahun 2025"
    assert se_do["superseded_by_url"].startswith("https://")


def test_ocr_cleaned_status_and_amended_articles(corpus_mgr):
    tourism = corpus_mgr.get_by_id("UU_18_2025_PASAL_57A")
    assert tourism is not None
    assert tourism["text_status"] == "verbatim-ocr-dibersihkan"
    assert tourism["is_verbatim"] is True
    assert tourism["ocr_cleaned"] is True

    # Articles amended or deleted by the amending statutes must not be
    # discoverable as current chunks.
    assert corpus_mgr.get_by_id("PERDA_BALI_06_2023_PASAL_5") is None
    assert corpus_mgr.get_by_id("PERGUB_BALI_02_2024_PASAL_9") is None
    assert corpus_mgr.get_by_id("PERGUB_BALI_02_2024_PASAL_23") is None


def test_legacy_levy_alias_resolves_to_canonical_id(corpus_mgr):
    canonical = corpus_mgr.get_by_id("PERDA_BALI_06_2023_LEVY")
    alias = corpus_mgr.get_by_id("PERDA_BALI_02_2025_LEVY")

    assert alias is canonical
    assert corpus_mgr.resolve_regulation_id("PERDA_BALI_02_2025_LEVY") == (
        "PERDA_BALI_06_2023_LEVY"
    )
    assert corpus_mgr.resolve_regulation_id("TIDAK_ADA") is None


def test_unknown_id_returns_none(corpus_mgr):
    assert corpus_mgr.get_by_id("TIDAK_ADA") is None


def _write_corpus_copy(tmp_path: Path, mutate) -> str:
    data = json.loads(Path(CORPUS_PATH).read_text(encoding="utf-8"))
    mutate(data)
    path = tmp_path / "corpus.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return str(path)


def test_loader_rejects_retrieval_eligible_document_without_chunks(tmp_path):
    def mutate(data):
        document = next(
            doc for doc in data["documents"] if doc["id"] == "pergub-bali-52-2021"
        )
        document["retrieval_eligible"] = True

    path = _write_corpus_copy(tmp_path, mutate)
    with pytest.raises(ValueError, match="no regulation chunks"):
        CorpusManager(path)


def test_loader_rejects_verbatim_flag_mismatch(tmp_path):
    def mutate(data):
        regulation = next(
            reg for reg in data["regulations"] if reg["id"] == "UU_15_2023_PASAL_8"
        )
        regulation["text_status"] = "non-verbatim"

    path = _write_corpus_copy(tmp_path, mutate)
    with pytest.raises(ValueError, match="inconsistent with text_status"):
        CorpusManager(path)


def test_loader_rejects_unknown_document_reference(tmp_path):
    def mutate(data):
        regulation = next(
            reg for reg in data["regulations"] if reg["id"] == "UU_15_2023_PASAL_8"
        )
        regulation["document_id"] = "dokumen-tidak-ada"

    path = _write_corpus_copy(tmp_path, mutate)
    with pytest.raises(ValueError, match="unknown document_id"):
        CorpusManager(path)


def test_uu_22_2009_traffic_regulations_retrieval(corpus_mgr):
    sim_results = corpus_mgr.search_regulations("turis sewa motor tanpa sim di bali")
    assert any(r["id"] == "UU_22_2009_PASAL_77_281" for r in sim_results)

    en_sim_results = corpus_mgr.search_regulations("tourist renting scooter without driving license")
    assert any(r["id"] == "UU_22_2009_PASAL_77_281" for r in en_sim_results)

    helmet_results = corpus_mgr.search_regulations("naik motor tidak pakai helm sni")
    assert any(r["id"] == "UU_22_2009_PASAL_291" for r in helmet_results)

    en_helmet_results = corpus_mgr.search_regulations("riding motorbike without helmet in bali")
    assert any(r["id"] == "UU_22_2009_PASAL_291" for r in en_helmet_results)
