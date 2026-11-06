"""
Unit tests for Mode 3 Smart Gate zone registry and AI brief.
"""

import json
from pathlib import Path

import pytest

from backend.services.corpus_loader import CorpusManager
from backend.services.evidence_spans import build_span_index
from backend.services.rag_engine import StrictRAGEngine
from backend.services.zone_registry import (
    ZONES_PATH,
    ZoneNotFoundError,
    ZoneRegistry,
)


@pytest.fixture
def engine(monkeypatch):
    monkeypatch.setenv("AI_MODE", "optional")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    return StrictRAGEngine()


def test_zone_registry_loads_three_zones():
    registry = ZoneRegistry.get_instance()
    assert len(registry.get_all()) == 3
    assert {zone["id"] for zone in registry.get_all()} == {
        "bandara-ngurah-rai",
        "pura-besakih",
        "pantai-melasti",
    }
    assert registry.metadata["version"] == "1.0.0"


def test_zone_current_chunks_are_verbatim_and_retrievable():
    corpus = CorpusManager.get_instance()
    registry = ZoneRegistry.get_instance()

    for zone in registry.get_all():
        for reg_id in zone["regulation_ids"]:
            reg = corpus.get_by_id(reg_id)
            assert reg is not None
            assert reg["is_verbatim"] is True
            assert reg["text_status"] == "verbatim"

            document = corpus.get_document_for_regulation(reg_id)
            assert document is not None
            assert document["retrieval_eligible"] is True


def test_zone_historical_chunks_are_explicitly_superseded():
    corpus = CorpusManager.get_instance()
    registry = ZoneRegistry.get_instance()

    historical_ids = [
        reg_id
        for zone in registry.get_all()
        for reg_id in zone.get("historical_regulation_ids", [])
    ]
    assert historical_ids

    for reg_id in historical_ids:
        reg = corpus.get_by_id(reg_id)
        assert reg is not None
        assert reg.get("superseded_by") or reg.get("status") == "Disempurnakan"


def test_zone_card_contains_verified_provenance(engine):
    card = engine.get_zone_card("bandara-ngurah-rai", "en")

    assert card["zone"]["name"] == "I Gusti Ngurah Rai Airport"
    assert card["language"] == "en"
    assert len(card["citations"]) == 3
    assert card["historical_citations"] == []
    assert card["tts_text"]
    assert card["disclaimer"]

    for citation in card["citations"]:
        assert citation["verified_layer1"] is True
        assert len(citation["quote_sha256"]) == 64
        assert citation["text_status"] == "verbatim"
        assert citation["document_id"]


def test_zone_card_keeps_historical_citations_separate(engine):
    card = engine.get_zone_card("pura-besakih", "id")

    assert len(card["citations"]) == 2
    assert len(card["historical_citations"]) == 2
    assert {c["reg_id"] for c in card["historical_citations"]} == {
        "SE_GUB_04_2023_DO",
        "SE_GUB_04_2023_DONT",
    }
    for citation in card["historical_citations"]:
        assert citation["status"] == "Disempurnakan"
        assert citation["superseded_by"]


def test_zone_card_rejects_unknown_zone(engine):
    with pytest.raises(ZoneNotFoundError):
        engine.get_zone_card("gerbang-tidak-ada", "id")


def test_zone_card_rejects_unknown_language(engine):
    with pytest.raises(ValueError, match="lang"):
        engine.get_zone_card("bandara-ngurah-rai", "fr")


def test_zone_brief_falls_back_without_gemini(engine):
    result = engine.analyze_zone_brief("bandara-ngurah-rai", "en")

    assert result["ai_synthesis_status"] == "deterministic"
    assert result["guard_status"] == "FALLBACK_DETERMINISTIK"
    assert result["ai_engine"] == "deterministic-template"
    assert result["brief"]
    assert "IDR 150,000" in result["brief"]
    assert len(result["citation_ids"]) == 3


def test_zone_brief_rejects_hallucinated_article(engine, monkeypatch):
    card = engine.get_zone_card("bandara-ngurah-rai", "en")
    span_index = build_span_index(card["citations"])
    span_id = next(
        key for key in span_index
        if key.startswith("PERDA_BALI_06_2023_LEVY#")
    )
    parsed = {
        "abstain": False,
        "summary_id": "You must pay under Pasal 999 and Rp999.000.",
        "summary_en": "You must pay under Pasal 999 and Rp999.000.",
        "claims": [{
            "claim_text_id": "Pasal 999 mewajibkan Rp999.000.",
            "claim_text_en": "Pasal 999 requires Rp999.000.",
            "citation_id": "PERDA_BALI_06_2023_LEVY",
            "span_ids": [span_id],
        }],
    }
    monkeypatch.setattr(
        engine.ai_pipeline,
        "call_model",
        lambda *args, **kwargs: (
            parsed,
            "mock-gemini",
            {"latency_ms": 1, "model": "mock"},
        ),
    )

    result = engine.analyze_zone_brief("bandara-ngurah-rai", "en")

    assert result["ai_synthesis_status"] == "deterministic"
    assert result["guard_status"] == "FALLBACK_GUARD"
    assert result["resolution_mode"] == "VERIFIED_GROUNDED"
    assert result["citation_ids"]
    assert "Pasal 999" not in result["brief"]
    assert "Rp999.000" not in result["brief"]


def test_zone_brief_accepts_safe_llm_output(engine, monkeypatch):
    card = engine.get_zone_card("bandara-ngurah-rai", "en")
    span_index = build_span_index(card["citations"])
    span_id = next(
        key for key in span_index
        if key.startswith("PERDA_BALI_06_2023_LEVY#")
    )
    safe_text = (
        "Pay Rp150.000 before or during your stay and keep the electronic "
        "proof. The original Indonesian legal text remains authoritative."
    )
    parsed = {
        "abstain": False,
        "summary_id": "Wisatawan asing wajib membayar pungutan Rp150.000.",
        "summary_en": safe_text,
        "claims": [{
            "claim_text_id": (
                "Wisatawan asing wajib membayar pungutan Rp150.000."
            ),
            "claim_text_en": safe_text,
            "citation_id": "PERDA_BALI_06_2023_LEVY",
            "span_ids": [span_id],
        }],
    }
    monkeypatch.setattr(
        engine.ai_pipeline,
        "call_model",
        lambda *args, **kwargs: (
            parsed,
            "mock-gemini",
            {"latency_ms": 1, "model": "mock"},
        ),
    )

    result = engine.analyze_zone_brief("bandara-ngurah-rai", "en")

    assert result["ai_synthesis_status"] == "llm"
    assert result["guard_status"] == "LLM_GROUNDED"
    assert result["brief"] == safe_text
    assert result["ai_engine"] == "mock-gemini"
    assert len(result["claims"]) == 1


def test_zone_brief_supports_ai_abstain(engine, monkeypatch):
    monkeypatch.setattr(
        engine.ai_pipeline,
        "call_model",
        lambda *args, **kwargs: (
            {
                "abstain": True,
                "summary_id": "",
                "summary_en": "",
                "claims": [],
            },
            "mock-gemini",
            {"latency_ms": 1, "model": "mock"},
        ),
    )

    result = engine.analyze_zone_brief("bandara-ngurah-rai", "en")

    assert result["ai_synthesis_status"] == "abstain"
    assert result["guard_status"] == "AI_ABSTAIN"
    assert result["claims"] == []


def _write_zone_copy(tmp_path: Path, mutate) -> str:
    data = json.loads(Path(ZONES_PATH).read_text(encoding="utf-8"))
    mutate(data)
    path = tmp_path / "zones.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return str(path)


def test_zone_registry_rejects_unknown_chunk(tmp_path):
    def mutate(data):
        data["zones"][0]["regulation_ids"] = ["TIDAK_ADA"]

    path = _write_zone_copy(tmp_path, mutate)
    with pytest.raises(ValueError, match="unknown current chunk"):
        ZoneRegistry(path, CorpusManager.get_instance())


def test_zone_registry_rejects_historical_chunk_that_is_not_superseded(tmp_path):
    def mutate(data):
        data["zones"][0]["historical_regulation_ids"] = [
            "PERDA_BALI_05_2020_PASAL_15"
        ]

    path = _write_zone_copy(tmp_path, mutate)
    with pytest.raises(ValueError, match="not marked as superseded"):
        ZoneRegistry(path, CorpusManager.get_instance())
