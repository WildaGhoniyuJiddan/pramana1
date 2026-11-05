"""
Corpus Loader and Legal Document Indexer for Pramana Strict-RAG.
Reads structured JSON corpus, validates data integrity, and provides fast
deterministic keyword retrieval with a normalized relevance score.

Corpus v1.3.0 separates two layers:
- ``documents``: provenance registry for every audited document. Documents in
  this registry are not automatically citable.
- ``regulations``: retrieved chunks with verified text. Only these chunks can
  ground an answer or pass Layer-1 citation verification.
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
    "source_url", "keywords", "document_id", "text_status", "source_type",
    "is_verbatim",
)

DOCUMENT_REQUIRED_FIELDS = (
    "id", "title", "doc_type", "tier", "status", "source_url", "source_type",
    "text_status", "coverage", "retrieval_eligible", "regulation_ids",
    "in_manifest",
)

# Statuses used by the corpus and its registry. ``belum-diambil`` and
# ``non-verbatim`` documents must never be retrieval-eligible.
TEXT_STATUS_VALUES = {
    "verbatim",
    "verbatim-ocr-dibersihkan",
    "verbatim-teks-reproduksi-resmi",
    "compilation",
    "non-verbatim",
    "belum-diambil",
}
VERBATIM_TEXT_STATUSES = {
    "verbatim",
    "verbatim-ocr-dibersihkan",
    "verbatim-teks-reproduksi-resmi",
}
BLOCKED_RETRIEVAL_STATUSES = {"non-verbatim", "belum-diambil"}
COVERAGE_VALUES = {"full", "excerpt", "secondary", "none"}

TOKEN_PATTERN = re.compile(r"[a-z0-9]+")

# Common Indonesian & English stopwords to prevent false-positive matching on generic
# verbs/prepositions/quantifiers.
STOPWORDS = {
    "yang", "dan", "di", "ke", "dari", "pada", "untuk", "ini", "itu", "dengan",
    "atau", "bisa", "ada", "tidak", "adalah", "seperti", "membuat", "dalam",
    "akan", "oleh", "bagi", "secara", "sudah", "hanya", "serta", "saat",
    "juga", "para", "sebuah", "suatu", "agar", "karena", "tetapi", "namun",
    "tersebut", "merupakan", "dapat", "harus", "wajib", "sangat", "lebih",
    "atas", "nomor", "tahun", "tentang", "semua",
    # Generic words that do not identify a legal rule on their own.
    "orang", "tempat", "barang", "uang", "apa", "apakah", "berapa",
    "menurut", "sedang", "boleh", "masuk", "saya", "lama", "berlaku",
    "indonesia", "undang", "kuta", "hari", "jam", "bandara", "penerbangan",
    "delay", "restoran", "bersih", "visa", "turis", "hotel", "harga",
    "biaya", "papan", "surf", "sewa", "bintang", "mahal", "koper",
    "aplikasi", "online", "sore", "parah", "kemacetan", "terlalu",
    "pedagang", "menjual", "taksi", "error", "memesan", "harganya",
    "tiga",
    # English stopwords
    "the", "and", "is", "are", "was", "were", "at", "to", "in", "for", "of",
    "all", "do", "does", "did", "them", "they", "their", "this", "that", "it",
    "its", "really", "have", "has", "had", "you", "your", "with", "from", "by",
    "on", "posted", "about", "what", "how", "can", "will", "just", "out",
}

# Single-token queries made of these words are too weak to ground an answer.
GENERIC_QUERY_TOKENS = {
    "harga", "biaya", "hotel", "bandara", "penerbangan", "hari", "aplikasi",
    "online", "visa", "turis", "bintang", "mahal", "bersih", "koper",
    "delay", "restoran", "surf", "sewa", "papan", "pajak", "retribusi",
    "pura", "bali", "pantai", "candi", "desa", "aturan", "hukum", "wisata",
    "tourist", "temple", "indonesia", "island",
}

# Cross-lingual expansion for English viral posts and tourist queries
EN_TO_ID_SYNONYMS: Dict[str, List[str]] = {
    "tourist": ["wisatawan", "wisman"],
    "tourists": ["wisatawan", "wisman"],
    "foreign": ["wisman", "asing"],
    "foreigner": ["wisman", "asing"],
    "foreigners": ["wisman", "asing"],
    "deport": ["deportasi", "keimigrasian"],
    "deported": ["deportasi", "keimigrasian"],
    "deportation": ["deportasi", "keimigrasian"],
    "expel": ["deportasi", "keimigrasian"],
    "tree": ["pohon"],
    "trees": ["pohon"],
    "sacred": ["suci", "kesucian", "sakral"],
    "holy": ["suci", "sakral"],
    "temple": ["pura", "tempat suci"],
    "temples": ["pura", "tempat suci"],
    "shrine": ["pura", "tempat suci"],
    "levy": ["pungutan", "retribusi"],
    "tax": ["pungutan"],
    "fee": ["pungutan"],
    "pay": ["membayar", "pembayaran", "bayar"],
    "payment": ["pembayaran"],
    "150k": ["150000", "150"],
    "climb": ["memanjat", "menaiki"],
    "climbed": ["memanjat", "menaiki"],
    "climbing": ["memanjat", "menaiki"],
    "naked": ["telanjang", "busana"],
    "nude": ["telanjang", "busana"],
    "nudity": ["telanjang", "busana"],
    "clothes": ["busana", "pakaian"],
    "clothing": ["busana", "pakaian"],
    "dress": ["busana", "pakaian"],
    "scooter": ["sepeda motor", "kendaraan"],
    "motorbike": ["sepeda motor", "kendaraan"],
    "motorcycle": ["sepeda motor", "kendaraan"],
    "rental": ["rental", "sewa"],
    "rent": ["sewa", "rental"],
    "helmet": ["helm"],
    "license": ["sim", "pengemudi"],
    "driving": ["mengemudi", "berkendara"],
    "nyepi": ["nyepi", "catur brata"],
    "silent": ["nyepi", "penyepian"],
    "drone": ["drone", "pesawat tanpa awak"],
    "visa": ["visa", "keimigrasian", "izin tinggal"],
    "overstay": ["keimigrasian", "izin tinggal"],
    "work": ["bekerja", "usaha"],
    "working": ["bekerja", "usaha"],
    "illegal": ["tanpa izin", "melanggar"],
    "trash": ["sampah"],
    "littering": ["sampah"],
    "plastic": ["plastik"],
    "business": ["usaha", "bekerja"],
    "immigration": ["keimigrasian", "imigrasi"],
    "guide": ["pemandu", "guide"],
    "guides": ["pemandu", "guide"],
    "licensed": ["berlisensi", "resmi"],
    "money": ["uang", "kupva"],
    "currency": ["uang", "mata uang", "kupva"],
    "exchange": ["penukaran", "kupva"],
    "changers": ["kupva", "penukaran"],
    "changer": ["kupva", "penukaran"],
    "relics": ["pratima", "benda sakral"],
    "relic": ["pratima", "benda sakral"],
    "penalty": ["sanksi", "pidana"],
    "penalties": ["sanksi", "pidana"],
    "fine": ["sanksi", "denda"],
    "fines": ["sanksi", "denda"],
    "order": ["ketertiban"],
    "customs": ["adat"],
    "violates": ["melanggar"],
    "violate": ["melanggar"],
    "hotel": ["hotel", "penginapan"],
    "outside": ["keluar", "jalanan"],
    "walk": ["berjalan", "bepergian"],
}

MIN_TOKEN_COVERAGE = 0.34


class CorpusManager:
    _instance: Optional["CorpusManager"] = None

    def __init__(self, file_path: str = CORPUS_PATH):
        self.file_path = file_path
        self.metadata: Dict[str, Any] = {}
        self.tiers: Dict[str, str] = {}
        self.documents: List[Dict[str, Any]] = []
        self.regulations: List[Dict[str, Any]] = []
        self._document_index: Dict[str, Dict[str, Any]] = {}
        self._id_index: Dict[str, Dict[str, Any]] = {}
        self._alias_index: Dict[str, Dict[str, Any]] = {}
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
        self.documents = data.get("documents", [])
        self.regulations = data.get("regulations", [])

        self._document_index = {doc["id"]: doc for doc in self.documents}
        self._id_index = {reg["id"]: reg for reg in self.regulations}
        self._alias_index = {}
        for reg in self.regulations:
            for alias in reg.get("aliases", []) or []:
                self._alias_index[alias] = reg

    def _validate(self, data: Dict[str, Any]) -> None:
        """Fail fast on malformed corpus data instead of serving broken citations."""
        if not isinstance(data, dict):
            raise ValueError("Corpus root must be a JSON object.")

        regulations = data.get("regulations")
        documents = data.get("documents")
        tiers = data.get("tiers", {})
        if not isinstance(regulations, list) or not regulations:
            raise ValueError("Corpus must contain a non-empty 'regulations' list.")
        if not isinstance(documents, list) or not documents:
            raise ValueError("Corpus must contain a non-empty 'documents' registry.")
        if not isinstance(tiers, dict) or not tiers:
            raise ValueError("Corpus must contain a non-empty 'tiers' object.")

        document_ids = set()
        for index, doc in enumerate(documents):
            if not isinstance(doc, dict):
                raise ValueError(f"Document at index {index} must be a JSON object.")

            missing = [
                field for field in DOCUMENT_REQUIRED_FIELDS
                if field not in doc
            ]
            if missing:
                raise ValueError(
                    f"Document '{doc.get('id', index)}' is missing required "
                    f"fields: {', '.join(missing)}"
                )

            doc_id = doc["id"]
            if not isinstance(doc_id, str) or not doc_id.strip():
                raise ValueError(f"Document at index {index} has an invalid id.")
            if doc_id in document_ids:
                raise ValueError(f"Duplicate document id: {doc_id}")
            document_ids.add(doc_id)

            if doc["tier"] not in tiers:
                raise ValueError(
                    f"Document '{doc_id}' references unknown tier '{doc['tier']}'."
                )
            if doc["text_status"] not in TEXT_STATUS_VALUES:
                raise ValueError(
                    f"Document '{doc_id}' has unknown text_status "
                    f"'{doc['text_status']}'."
                )
            if doc["coverage"] not in COVERAGE_VALUES:
                raise ValueError(
                    f"Document '{doc_id}' has unknown coverage '{doc['coverage']}'."
                )
            if not isinstance(doc["retrieval_eligible"], bool):
                raise ValueError(
                    f"Document '{doc_id}' must have a boolean 'retrieval_eligible'."
                )
            if not isinstance(doc["in_manifest"], bool):
                raise ValueError(
                    f"Document '{doc_id}' must have a boolean 'in_manifest'."
                )
            if not isinstance(doc["regulation_ids"], list):
                raise ValueError(
                    f"Document '{doc_id}' must have a 'regulation_ids' list."
                )
            if doc["retrieval_eligible"]:
                if not doc["regulation_ids"]:
                    raise ValueError(
                        f"Document '{doc_id}' is retrieval-eligible but has no "
                        "regulation chunks."
                    )
                if doc["text_status"] in BLOCKED_RETRIEVAL_STATUSES:
                    raise ValueError(
                        f"Document '{doc_id}' cannot be retrieval-eligible with "
                        f"text_status '{doc['text_status']}'."
                    )
            elif doc["regulation_ids"]:
                raise ValueError(
                    f"Document '{doc_id}' is not retrieval-eligible but lists "
                    "regulation chunks."
                )

        seen_ids = set()
        seen_aliases = set()
        for index, reg in enumerate(regulations):
            if not isinstance(reg, dict):
                raise ValueError(f"Regulation at index {index} must be a JSON object.")

            missing = [
                field for field in REQUIRED_FIELDS
                if field not in reg or reg[field] in (None, "")
            ]
            if missing:
                raise ValueError(
                    f"Regulation '{reg.get('id', index)}' is missing required fields: "
                    f"{', '.join(missing)}"
                )

            reg_id = reg["id"]
            if reg_id in seen_ids:
                raise ValueError(f"Duplicate regulation id: {reg_id}")
            if reg_id in seen_aliases:
                raise ValueError(f"Regulation id collides with an alias: {reg_id}")
            seen_ids.add(reg_id)

            if reg["tier"] not in tiers:
                raise ValueError(
                    f"Regulation '{reg_id}' references unknown tier '{reg['tier']}'."
                )

            if not isinstance(reg["keywords"], list):
                raise ValueError(f"Regulation '{reg_id}' must have a 'keywords' list.")

            if not isinstance(reg["is_verbatim"], bool):
                raise ValueError(
                    f"Regulation '{reg_id}' must have a boolean 'is_verbatim'."
                )
            if reg["text_status"] not in TEXT_STATUS_VALUES:
                raise ValueError(
                    f"Regulation '{reg_id}' has unknown text_status "
                    f"'{reg['text_status']}'."
                )
            if reg["is_verbatim"] != (
                reg["text_status"] in VERBATIM_TEXT_STATUSES
            ):
                raise ValueError(
                    f"Regulation '{reg_id}' has is_verbatim="
                    f"{reg['is_verbatim']} inconsistent with text_status="
                    f"'{reg['text_status']}'."
                )

            if reg["document_id"] not in document_ids:
                raise ValueError(
                    f"Regulation '{reg_id}' references unknown document_id "
                    f"'{reg['document_id']}'."
                )

            if "ocr_cleaned" in reg and not isinstance(reg["ocr_cleaned"], bool):
                raise ValueError(
                    f"Regulation '{reg_id}' must have a boolean 'ocr_cleaned'."
                )
            if "amendment_status" in reg and reg["amendment_status"] not in {
                "current", "amended", "deleted",
            }:
                raise ValueError(
                    f"Regulation '{reg_id}' has unknown amendment_status "
                    f"'{reg['amendment_status']}'."
                )

            aliases = reg.get("aliases", []) or []
            if not isinstance(aliases, list):
                raise ValueError(f"Regulation '{reg_id}' must have an 'aliases' list.")
            for alias in aliases:
                if not isinstance(alias, str) or not alias.strip():
                    raise ValueError(
                        f"Regulation '{reg_id}' has an invalid alias: {alias!r}."
                    )
                if alias in seen_ids or alias in document_ids or alias in seen_aliases:
                    raise ValueError(f"Duplicate or colliding alias: {alias}")
                seen_aliases.add(alias)

        # Cross-check both directions of the document -> chunk relation.
        chunk_ids_by_document: Dict[str, set] = {doc_id: set() for doc_id in document_ids}
        for reg in regulations:
            chunk_ids_by_document[reg["document_id"]].add(reg["id"])

        for doc in documents:
            declared = set(doc["regulation_ids"])
            actual = chunk_ids_by_document[doc["id"]]
            if declared != actual:
                raise ValueError(
                    f"Document '{doc['id']}' regulation_ids do not match its "
                    f"chunks. Declared: {sorted(declared)}; actual: {sorted(actual)}."
                )
            for reg_id in doc["regulation_ids"]:
                if reg_id not in seen_ids:
                    raise ValueError(
                        f"Document '{doc['id']}' references unknown regulation "
                        f"'{reg_id}'."
                    )

    def get_by_id(self, reg_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a regulation entry by canonical ID or registered alias."""
        if not reg_id:
            return None
        return self._id_index.get(reg_id) or self._alias_index.get(reg_id)

    def resolve_regulation_id(self, reg_id: str) -> Optional[str]:
        """Return the canonical regulation ID for an ID or alias."""
        reg = self.get_by_id(reg_id)
        return reg["id"] if reg else None

    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a document registry entry by ID."""
        if not document_id:
            return None
        return self._document_index.get(document_id)

    def get_documents(self) -> List[Dict[str, Any]]:
        """Return all document registry entries."""
        return self.documents

    def get_document_for_regulation(
        self, reg_id: str
    ) -> Optional[Dict[str, Any]]:
        """Return the registry entry that owns a regulation chunk."""
        reg = self.get_by_id(reg_id)
        if not reg:
            return None
        return self.get_document(reg.get("document_id", ""))

    def get_regulations_for_document(self, document_id: str) -> List[Dict[str, Any]]:
        """Return the retrieval chunks that belong to a registry document."""
        return [
            reg for reg in self.regulations
            if reg.get("document_id") == document_id
        ]

    def get_stats(self) -> Dict[str, int]:
        """Return provenance counts used by health and corpus endpoints."""
        return {
            "total_regulations_indexed": len(self.regulations),
            "total_documents_registered": len(self.documents),
            "total_manifest_documents": sum(
                1 for doc in self.documents if doc.get("in_manifest")
            ),
            "total_documents_with_chunks": sum(
                1 for doc in self.documents if doc.get("regulation_ids")
            ),
        }

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
                candidates = [token] + EN_TO_ID_SYNONYMS.get(token, [])
                best_weight = 0.0

                for cand in candidates:
                    # 1. Official keyword list (strongest signal).
                    if any(cand in keyword for keyword in keywords):
                        best_weight = max(best_weight, 1.0)
                    # 2. Document title.
                    if cand in title_lower:
                        best_weight = max(best_weight, 0.85)
                    # 3. Category.
                    if cand in cat_lower:
                        best_weight = max(best_weight, 0.7)
                    # 4. Main text (weakest signal).
                    if cand in text_lower:
                        best_weight = max(best_weight, 0.55)

                if best_weight > 0:
                    matched_terms.append(token)
                    weights.append(best_weight)

            if not weights:
                continue

            coverage = len(weights) / len(tokens)
            best_weight = max(weights)

            # A single generic word is not enough evidence. Multi-token queries
            # must cover a meaningful share of their tokens.
            if len(tokens) == 1:
                if tokens[0] in GENERIC_QUERY_TOKENS or best_weight < 0.90:
                    continue
            elif coverage < MIN_TOKEN_COVERAGE:
                continue

            score = best_weight * (0.6 + 0.4 * coverage)

            # Demote explanation/elucidation chunks unless explicitly requested
            if reg["id"].endswith("_PENJELASAN_UMUM") or "penjelasan" in reg.get("pasal", "").lower():
                q_lower = query.lower()
                if "penjelasan" not in q_lower and "elucidation" not in q_lower:
                    score *= 0.6

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
