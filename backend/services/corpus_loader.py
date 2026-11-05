"""
Corpus Loader and Legal Document Indexer for Pramana Strict-RAG.
Reads structured JSON corpus, validates data integrity, and provides fast
deterministic keyword retrieval with a normalized relevance score.
"""

import json
import os
import re
from typing import List, Dict, Any, Optional

CORPUS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "corpus",
    "bali_regulations.json"
)

# A normalized score is used so Layer-2 can enforce a single, meaningful
# threshold instead of relying on an integer score that grows with query length.
DEFAULT_RELEVANCE_THRESHOLD = 0.5

# After the best match is found, keep only results reasonably close to it.
# This prevents weak incidental matches from being cited alongside a precise hit.
RELATIVE_SCORE_RATIO = 0.75

REQUIRED_FIELDS = (
    "id", "doc_title", "tier", "category", "bab", "pasal", "text",
    "source_url", "keywords",
)

TOKEN_PATTERN = re.compile(r"[a-z0-9]+")

# Common Indonesian stopwords to prevent false-positive matching on generic
# verbs/prepositions.
STOPWORDS = {
    "yang", "dan", "di", "ke", "dari", "pada", "untuk", "ini", "itu", "dengan",
    "atau", "bisa", "ada", "tidak", "adalah", "seperti", "membuat", "dalam",
    "akan", "oleh", "bagi", "secara", "sudah", "hanya", "serta", "saat",
    "juga", "para", "sebuah", "suatu", "agar", "karena", "tetapi", "namun",
    "tersebut", "merupakan", "dapat", "harus", "wajib", "sangat", "lebih",
}


class CorpusManager:
    _instance: Optional["CorpusManager"] = None

    def __init__(self, file_path: str = CORPUS_PATH):
        self.file_path = file_path
        self.metadata: Dict[str, Any] = {}
        self.tiers: Dict[str, str] = {}
        self.regulations: List[Dict[str, Any]] = []
        self._id_index: Dict[str, Dict[str, Any]] = {}
        self.load()

    @classmethod
    def get_instance(cls) -> "CorpusManager":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def load(self):
        """Load corpus from JSON file, validate it, and build fast lookups."""
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"Corpus file not found at: {self.file_path}")

        with open(self.file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self._validate(data)
        self.metadata = data.get("metadata", {})
        self.tiers = data.get("tiers", {})
        self.regulations = data.get("regulations", [])
        self._id_index = {reg["id"]: reg for reg in self.regulations}

    def _validate(self, data: Dict[str, Any]) -> None:
        """Fail fast on malformed corpus data instead of serving broken citations."""
        if not isinstance(data, dict):
            raise ValueError("Corpus root must be a JSON object.")

        regulations = data.get("regulations")
        tiers = data.get("tiers", {})
        if not isinstance(regulations, list) or not regulations:
            raise ValueError("Corpus must contain a non-empty 'regulations' list.")
        if not isinstance(tiers, dict) or not tiers:
            raise ValueError("Corpus must contain a non-empty 'tiers' object.")

        seen_ids = set()
        for index, reg in enumerate(regulations):
            if not isinstance(reg, dict):
                raise ValueError(f"Regulation at index {index} must be a JSON object.")

            missing = [field for field in REQUIRED_FIELDS if not reg.get(field)]
            if missing:
                raise ValueError(
                    f"Regulation '{reg.get('id', index)}' is missing required fields: "
                    f"{', '.join(missing)}"
                )

            reg_id = reg["id"]
            if reg_id in seen_ids:
                raise ValueError(f"Duplicate regulation id: {reg_id}")
            seen_ids.add(reg_id)

            if reg["tier"] not in tiers:
                raise ValueError(
                    f"Regulation '{reg_id}' references unknown tier '{reg['tier']}'."
                )

            if not isinstance(reg["keywords"], list):
                raise ValueError(f"Regulation '{reg_id}' must have a 'keywords' list.")

    def get_by_id(self, reg_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve exact regulation entry by ID."""
        return self._id_index.get(reg_id)

    def _tokenize(self, query: str) -> List[str]:
        tokens = TOKEN_PATTERN.findall((query or "").lower())
        return [
            token for token in tokens
            if len(token) > 2 and token not in STOPWORDS
        ]

    def search_regulations_scored(
        self,
        query: str,
        top_k: int = 5,
        min_score: float = DEFAULT_RELEVANCE_THRESHOLD,
    ) -> List[Dict[str, Any]]:
        """
        Deterministic keyword retrieval that returns the score and matched terms.

        Each token contributes its best match weight, then the final score
        combines the strongest match with query coverage:

            score = best_weight * (0.6 + 0.4 * coverage)

        This prevents a single generic word from grounding an entire query while
        still allowing a precise legal keyword to retrieve its statute.
        """
        tokens = self._tokenize(query)
        if not tokens:
            return []

        scored_results: List[Dict[str, Any]] = []

        for reg in self.regulations:
            text_lower = reg["text"].lower()
            title_lower = reg["doc_title"].lower()
            cat_lower = reg.get("category", "").lower()
            keywords = [k.lower() for k in reg.get("keywords", [])]

            matched_terms: List[str] = []
            weights: List[float] = []

            for token in tokens:
                best_weight = 0.0

                # 1. Official keyword list (strongest signal).
                if any(token in keyword for keyword in keywords):
                    best_weight = max(best_weight, 1.0)
                # 2. Document title.
                if token in title_lower:
                    best_weight = max(best_weight, 0.85)
                # 3. Category.
                if token in cat_lower:
                    best_weight = max(best_weight, 0.7)
                # 4. Main text (weakest signal).
                if token in text_lower:
                    best_weight = max(best_weight, 0.55)

                if best_weight > 0:
                    matched_terms.append(token)
                    weights.append(best_weight)

            if not weights:
                continue

            coverage = len(weights) / len(tokens)
            score = max(weights) * (0.6 + 0.4 * coverage)

            if score >= min_score:
                scored_results.append({
                    "regulation": reg,
                    "score": round(score, 4),
                    "matched_terms": matched_terms,
                })

        if not scored_results:
            return []

        # Stable ordering: score descending, then regulation id.
        scored_results.sort(
            key=lambda item: (-item["score"], item["regulation"]["id"])
        )

        top_score = scored_results[0]["score"]
        relative_floor = max(min_score, top_score * RELATIVE_SCORE_RATIO)
        scored_results = [
            item for item in scored_results if item["score"] >= relative_floor
        ]

        return scored_results[:top_k]

    def search_regulations(
        self,
        query: str,
        top_k: int = 5,
        min_score: float = DEFAULT_RELEVANCE_THRESHOLD,
    ) -> List[Dict[str, Any]]:
        """Return only the regulation records for a deterministic keyword query."""
        return [
            item["regulation"]
            for item in self.search_regulations_scored(
                query, top_k=top_k, min_score=min_score
            )
        ]

    def get_all(self) -> List[Dict[str, Any]]:
        """Get all loaded regulation records."""
        return self.regulations
