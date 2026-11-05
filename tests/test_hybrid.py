"""Tests for optional hybrid retrieval plumbing."""

import json
from pathlib import Path

from backend.services.corpus_loader import CorpusManager
from backend.services.hybrid_retrieval import (
    HybridRetriever,
    corpus_checksum,
)


def test_corpus_checksum_is_stable():
    corpus = CorpusManager.get_instance()
    assert corpus_checksum(corpus) == corpus_checksum(corpus)
    assert len(corpus_checksum(corpus)) == 64


def test_hybrid_retriever_unavailable_without_embeddings(tmp_path):
    corpus = CorpusManager.get_instance()
    retriever = HybridRetriever(corpus, str(tmp_path / "missing.json"))
    assert retriever.available is False
    assert retriever.vector_count == 0


def test_hybrid_retriever_loads_matching_embeddings(tmp_path):
    corpus = CorpusManager.get_instance()
    first = corpus.get_all()[0]
    path = tmp_path / "embeddings.json"
    path.write_text(
        json.dumps({
            "model": "test",
            "dimension": 2,
            "corpus_checksum": corpus_checksum(corpus),
            "vectors": {first["id"]: [1.0, 0.0]},
        }),
        encoding="utf-8",
    )

    retriever = HybridRetriever(corpus, str(path))
    assert retriever.vector_count == 1
    scores = retriever.semantic_scores([1.0, 0.0])
    assert scores[first["id"]] == 1.0


def test_hybrid_retriever_rejects_stale_embeddings(tmp_path):
    corpus = CorpusManager.get_instance()
    path = tmp_path / "embeddings.json"
    path.write_text(
        json.dumps({
            "model": "test",
            "dimension": 2,
            "corpus_checksum": "stale",
            "vectors": {"x": [1.0, 0.0]},
        }),
        encoding="utf-8",
    )
    retriever = HybridRetriever(corpus, str(path))
    assert retriever.vector_count == 0
