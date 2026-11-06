"""
Dual-Layer Verifier for Pramana Strict-RAG.

1. Layer 1 (Deterministic): checks that a quoted passage exists inside the
   locally registered corpus chunk, then records provenance and a quote hash.
2. Layer 2 (Guard): enforces the abstain principle using the normalized
   retrieval relevance score.

Important limitation: Layer 1 proves a quote exists in the local corpus. It
does not independently re-download or re-validate the statute against JDIH.
"""

import hashlib
from typing import List, Dict, Any, Optional, Tuple

from backend.services.corpus_loader import (
    CorpusManager,
    DEFAULT_RELEVANCE_THRESHOLD,
)

CORPUS_SCOPE = "corpus"


def _normalize_text(value: str) -> str:
    """Collapse whitespace so formatting differences do not break matching."""
    return " ".join((value or "").strip().split())


def quote_sha256(quote: str) -> str:
    """Return a stable SHA-256 hash of the normalized quote."""
    return hashlib.sha256(_normalize_text(quote).encode("utf-8")).hexdigest()


class DualLayerVerifier:
    def __init__(self, corpus_mgr: Optional[CorpusManager] = None):
        self.corpus_mgr = corpus_mgr or CorpusManager.get_instance()

    def verify_layer1_exact_match(self, quote: str, reg_id: str) -> bool:
        """
        Layer 1 Deterministic Verifier:
        Verifies that a quoted legal passage exists character-for-character
        inside the locally registered regulation chunk (whitespace-normalized).
        """
        if not quote or not reg_id:
            return False

        reg = self.corpus_mgr.get_by_id(reg_id)
        if not reg:
            return False

        clean_quote = _normalize_text(quote)
        clean_corpus = _normalize_text(reg.get("text", ""))

        if not clean_quote or not clean_corpus:
            return False

        return clean_quote in clean_corpus

    def _apply_provenance(
        self,
        citation: Dict[str, Any],
        reg: Dict[str, Any],
        quote: str,
    ) -> None:
        """Attach corpus provenance to a citation after Layer-1 verification."""
        citation["official_doc_title"] = reg["doc_title"]
        citation["tier"] = reg["tier"]
        citation["tier_label"] = reg.get("tier_label", f"Tingkat {reg['tier']}")
        # Always overwrite legal identifiers with corpus values so a caller
        # cannot attach a fabricated article number to a real quote.
        citation["reg_id"] = reg["id"]
        citation["pasal"] = reg.get("pasal", "")
        citation["penalties"] = reg.get("penalties", "")
        citation["source_url"] = reg.get("source_url", "")
        citation["source_note"] = reg.get("source_note")
        citation["verified_layer1"] = True
        citation["verification_scope"] = CORPUS_SCOPE
        citation["quote_sha256"] = quote_sha256(quote)
        citation["last_verified_date"] = reg.get("last_verified_date")
        citation["status"] = reg.get("status")
        citation["status_note"] = reg.get("status_note")
        citation["is_verbatim"] = bool(reg.get("is_verbatim", True))
        citation["document_id"] = reg.get("document_id")
        citation["text_status"] = reg.get("text_status")
        citation["source_type"] = reg.get("source_type")
        citation["source_pdf_url"] = reg.get("source_pdf_url")
        citation["source_pdf_sha256"] = reg.get("source_pdf_sha256")
        citation["related_document_ids"] = reg.get("related_document_ids", [])
        citation["superseded_by"] = reg.get("superseded_by")
        citation["superseded_by_url"] = reg.get("superseded_by_url")
        citation["title_en"] = reg.get("title_en")
        citation["text_en"] = reg.get("text_en")
        citation["status_note_en"] = reg.get("status_note_en")
        citation["source_note_en"] = reg.get("source_note_en")
        citation["penalties_en"] = reg.get("penalties_en")
        citation["category_en"] = reg.get("category_en")
        citation["tier_label_en"] = reg.get("tier_label_en")
        citation["translation_status"] = reg.get("translation_status")
        citation["text_original"] = reg.get("text", quote)

    def verify_and_filter_citations(
        self,
        citations: List[Dict[str, Any]],
        lang: str = "id",
    ) -> List[Dict[str, Any]]:
        """
        Filter out citations that fail Layer 1 or reference unknown regulations,
        and propagate provenance fields from the corpus.
        """
        verified: List[Dict[str, Any]] = []

        for cite in citations:
            reg_id = cite.get("reg_id", "")
            quote = cite.get("quoted_text", "")
            reg = self.corpus_mgr.get_by_id(reg_id)

            if not reg:
                continue

            if quote:
                if not self.verify_layer1_exact_match(quote, reg_id):
                    continue
            else:
                quote = reg.get("text", "")
                cite["quoted_text"] = quote

            if not quote:
                continue

            self._apply_provenance(cite, reg, quote)

            # Apply display fields according to lang
            is_en = (lang == "en")
            cite["display_text"] = (cite.get("text_en") if is_en and cite.get("text_en") else cite.get("text_original"))
            cite["display_title"] = (cite.get("title_en") if is_en and cite.get("title_en") else cite.get("official_doc_title"))
            cite["display_status_note"] = (cite.get("status_note_en") if is_en and cite.get("status_note_en") else cite.get("status_note"))
            cite["display_source_note"] = (cite.get("source_note_en") if is_en and cite.get("source_note_en") else cite.get("source_note"))
            cite["display_penalties"] = (cite.get("penalties_en") if is_en and cite.get("penalties_en") else cite.get("penalties"))

            verified.append(cite)

        return verified

    def enforce_layer2_guard(
        self,
        retrieved_regulations: List[Dict[str, Any]],
        confidence_threshold: float = DEFAULT_RELEVANCE_THRESHOLD,
        retrieval_scores: Optional[List[float]] = None,
    ) -> Tuple[bool, str]:
        """
        Layer 2 Guard:
        Abstains when nothing was retrieved or when the best retrieval score is
        below the relevance threshold. If callers pass regulations directly
        without scores, presence alone is accepted for backward compatibility.
        """
        if not retrieved_regulations:
            return False, "TIDAK_DITEMUKAN"

        scores = retrieval_scores
        if scores is None:
            scores = [
                reg.get("_retrieval_score")
                for reg in retrieved_regulations
                if isinstance(reg.get("_retrieval_score"), (int, float))
            ]

        numeric_scores = [
            float(score) for score in (scores or [])
            if isinstance(score, (int, float))
        ]

        # An explicit score list that contains no usable numbers must not be
        # treated as "grounded by presence alone".
        if retrieval_scores is not None and not numeric_scores:
            return False, "TIDAK_DITEMUKAN"

        if numeric_scores and max(numeric_scores) < confidence_threshold:
            return False, "TIDAK_DITEMUKAN"

        return True, "TERVERIFIKASI"
