"""Optional hybrid retrieval using pre-computed embeddings.

The corpus is static, so document vectors are built offline by
``scripts/build_embeddings.py``. At runtime only the query is embedded. If the
embeddings file is missing, stale, or the embedding call fails, the engine
falls back to deterministic keyword retrieval.
"""

import hashlib
import json
import logging
import math
import os
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger("pramana.hybrid")

from backend.services.ai_config import (
    GEMINI_EMBEDDING_MODEL,
    get_ai_mode,
    get_gemini_api_key,
)
from backend.services.corpus_loader import CorpusManager

EMBEDDINGS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "corpus",
    "embeddings.json",
)
EMBEDDING_API_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_EMBEDDING_MODEL}:embedContent"
)


def corpus_checksum(corpus_mgr: CorpusManager) -> str:
    payload = json.dumps(
        [(reg["id"], reg["text"]) for reg in corpus_mgr.get_all()],
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def embed_text(text: str, task_type: str = "RETRIEVAL_QUERY") -> List[float]:
    api_key = get_gemini_api_key()
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY tidak tersedia")
    payload = {
        "model": f"models/{GEMINI_EMBEDDING_MODEL}",
        "content": {"parts": [{"text": text}]},
        "taskType": task_type,
        "outputDimensionality": 768,
    }
    with httpx.Client(timeout=15.0) as client:
        response = client.post(
            EMBEDDING_API_URL,
            json=payload,
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": api_key,
            },
        )
    if response.status_code != 200:
        raise RuntimeError(f"Embedding HTTP {response.status_code}")
    data = response.json()
    values = data.get("embedding", {}).get("values")
    if not isinstance(values, list) or not values:
        raise RuntimeError("Embedding response has no values")
    return [float(value) for value in values]


def _cosine(left: List[float], right: List[float]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0
    dot = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(a * a for a in left))
    right_norm = math.sqrt(sum(b * b for b in right))
    if not left_norm or not right_norm:
        return 0.0
    return dot / (left_norm * right_norm)


class HybridRetriever:
    def __init__(
        self,
        corpus_mgr: CorpusManager,
        embeddings_path: str = EMBEDDINGS_PATH,
    ):
        self.corpus_mgr = corpus_mgr
        self.embeddings_path = embeddings_path
        self._vectors: Dict[str, List[float]] = {}
        self._checksum = ""
        self.load()

    def load(self) -> None:
        self._vectors = {}
        self._checksum = ""
        if not os.path.exists(self.embeddings_path):
            return
        try:
            with open(self.embeddings_path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
        except (OSError, json.JSONDecodeError):
            return
        if data.get("corpus_checksum") != corpus_checksum(self.corpus_mgr):
            return
        vectors = data.get("vectors")
        if not isinstance(vectors, dict):
            return
        self._vectors = vectors
        self._checksum = data["corpus_checksum"]

    @property
    def available(self) -> bool:
        return (
            get_ai_mode() != "disabled"
            and bool(self._vectors)
            and bool(get_gemini_api_key())
        )

    @property
    def vector_count(self) -> int:
        return len(self._vectors)

    def semantic_scores(
        self, query_embedding: List[float]
    ) -> Dict[str, float]:
        if not self._vectors:
            return {}
        # Dimension check against stored vector dimension
        first_vec = next(iter(self._vectors.values()), None)
        if first_vec and len(query_embedding) != len(first_vec):
            logger.warning(
                "Embedding dimension mismatch: query dim %d != stored vector dim %d",
                len(query_embedding),
                len(first_vec),
            )
            raise ValueError(
                f"Embedding dimension mismatch: query has {len(query_embedding)} dimensions, "
                f"stored vectors have {len(first_vec)} dimensions"
            )
        scores = {}
        for reg_id, vector in self._vectors.items():
            if not isinstance(vector, list):
                continue
            scores[reg_id] = max(0.0, _cosine(query_embedding, vector))
        return scores

    def search_scored(
        self,
        query: str,
        query_embedding: List[float],
        top_k: int = 5,
        min_score: float = 0.5,
    ) -> List[Dict[str, Any]]:
        keyword_items = self.corpus_mgr.search_regulations_scored(
            query, top_k=max(top_k * 2, 10), min_score=0.0
        )
        keyword_by_id = {
            item["regulation"]["id"]: item for item in keyword_items
        }
        try:
            semantic = self.semantic_scores(query_embedding)
        except ValueError as err:
            logger.warning("Dimension mismatch in semantic search, using pure keyword: %s", err)
            semantic = {}

        candidates = set(keyword_by_id) | set(semantic)
        scored = []
        for reg_id in candidates:
            reg = self.corpus_mgr.get_by_id(reg_id)
            if not reg:
                continue
            keyword_score = keyword_by_id.get(reg_id, {}).get("score", 0.0)
            vector_score = semantic.get(reg_id, 0.0)
            combined = round(
                (0.6 * keyword_score) + (0.4 * vector_score), 4
            )
            if combined < min_score:
                continue
            scored.append({
                "regulation": reg,
                "score": combined,
                "matched_terms": keyword_by_id.get(
                    reg_id, {}
                ).get("matched_terms", []),
                "keyword_score": keyword_score,
                "vector_score": round(vector_score, 4),
                "retrieval_mode": "hybrid",
            })

        if not scored:
            return []

        scored.sort(key=lambda item: (-item["score"], item["regulation"]["id"]))
        top_score = scored[0]["score"]
        relative_floor = max(min_score, top_score * 0.75)
        scored = [item for item in scored if item["score"] >= relative_floor]
        return scored[:top_k]
