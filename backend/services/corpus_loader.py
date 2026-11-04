"""
Corpus Loader and Legal Document Indexer for Pramana Strict-RAG.
Reads structured JSON corpus, validates data integrity, and provides fast keyword/exact search.
"""

import json
import os
from typing import List, Dict, Any, Optional

CORPUS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "corpus",
    "bali_regulations.json"
)


# Common Indonesian stopwords to prevent false-positive matching on generic verbs/prepositions
STOPWORDS = {
    "yang", "dan", "di", "ke", "dari", "pada", "untuk", "ini", "itu", "dengan",
    "atau", "bisa", "ada", "tidak", "adalah", "seperti", "membuat", "dalam",
    "akan", "oleh", "bagi", "secara", "sudah", "hanya", "serta", "saat"
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
        """Load corpus from JSON file and construct fast lookups."""
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"Corpus file not found at: {self.file_path}")

        with open(self.file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.metadata = data.get("metadata", {})
        self.tiers = data.get("tiers", {})
        self.regulations = data.get("regulations", [])
        self._id_index = {reg["id"]: reg for reg in self.regulations}

    def get_by_id(self, reg_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve exact regulation entry by ID."""
        return self._id_index.get(reg_id)

    def search_regulations(self, query: str, top_k: int = 5, min_score: int = 4) -> List[Dict[str, Any]]:
        """
        Deterministic keyword search across corpus regulations.
        Excludes stopwords and requires minimum score to prevent false-positive hallucination.
        """
        if not query or not query.strip():
            return []

        tokens = [
            t.lower().strip()
            for t in query.split()
            if len(t.strip()) > 2 and t.lower().strip() not in STOPWORDS
        ]

        if not tokens:
            return []

        scored_results = []

        for reg in self.regulations:
            score = 0
            text_lower = reg["text"].lower()
            title_lower = reg["doc_title"].lower()
            cat_lower = reg.get("category", "").lower()
            keywords = [k.lower() for k in reg.get("keywords", [])]

            for token in tokens:
                # 1. Match in official keywords list (highest weight)
                for kw in keywords:
                    if token in kw:
                        score += 5
                # 2. Match in title
                if token in title_lower:
                    score += 4
                # 3. Match in category
                if token in cat_lower:
                    score += 3
                # 4. Match in main text
                if token in text_lower:
                    score += 2

            if score >= min_score:
                scored_results.append((score, reg))

        # Sort descending by score
        scored_results.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored_results[:top_k]]

    def get_all(self) -> List[Dict[str, Any]]:
        """Get all loaded regulation records."""
        return self.regulations
