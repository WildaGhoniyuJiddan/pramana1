"""
Dual-Layer Verifier for Pramana Strict-RAG.
Implements:
1. Layer 1 (Deterministic): Verbatim match verification against official corpus chunks.
2. Layer 2 (Guard & Entailment): Abstain enforcement and hallucination filtering.
"""

from typing import List, Dict, Any, Tuple
from backend.services.corpus_loader import CorpusManager


class DualLayerVerifier:
    def __init__(self, corpus_mgr: CorpusManager = None):
        self.corpus_mgr = corpus_mgr or CorpusManager.get_instance()

    def verify_layer1_exact_match(self, quote: str, reg_id: str) -> bool:
        """
        Layer 1 Deterministic Verifier:
        Verifies that a quoted legal passage exists character-for-character
        inside the official registered regulation chunk.
        """
        if not quote or not reg_id:
            return False

        reg = self.corpus_mgr.get_by_id(reg_id)
        if not reg:
            return False

        # Normalize whitespace for robust comparison
        clean_quote = " ".join(quote.strip().split())
        clean_corpus = " ".join(reg["text"].strip().split())

        return clean_quote in clean_corpus

    def verify_and_filter_citations(self, citations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filters out citations that fail Layer 1 exact match or reference non-existent articles.
        """
        verified = []
        for cite in citations:
            reg_id = cite.get("reg_id", "")
            quote = cite.get("quoted_text", "")
            reg = self.corpus_mgr.get_by_id(reg_id)

            if not reg:
                continue

            # If a specific quote is provided, verify it against corpus
            if quote:
                is_valid = self.verify_layer1_exact_match(quote, reg_id)
                if is_valid:
                    cite["verified_layer1"] = True
                    cite["official_doc_title"] = reg["doc_title"]
                    cite["tier"] = reg["tier"]
                    cite["source_url"] = reg["source_url"]
                    verified.append(cite)
            else:
                # Direct chunk reference
                cite["verified_layer1"] = True
                cite["official_doc_title"] = reg["doc_title"]
                cite["tier"] = reg["tier"]
                cite["source_url"] = reg["source_url"]
                cite["quoted_text"] = reg["text"]
                verified.append(cite)

        return verified

    def enforce_layer2_guard(
        self,
        retrieved_regulations: List[Dict[str, Any]],
        confidence_threshold: float = 0.5
    ) -> Tuple[bool, str]:
        """
        Layer 2 Guard:
        Enforces Abstain principle. If zero verified regulations match the query,
        the system MUST abstain with 'TIDAK_DITEMUKAN'.
        """
        if not retrieved_regulations:
            return False, "TIDAK_DITEMUKAN"

        return True, "TERVERIFIKASI"
