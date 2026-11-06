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
import re
from typing import List, Dict, Any, Optional, Tuple, Set

from backend.services.corpus_loader import (
    CorpusManager,
    DEFAULT_RELEVANCE_THRESHOLD,
)
from backend.services.legal_taxonomy import choose_epistemic_mode

CORPUS_SCOPE = "corpus"

PASAL_PATTERN = re.compile(
    r"\bPasal\s+\d+[A-Za-z]?(?:\s+Ayat\s*\(?\d+\)?)?",
    re.IGNORECASE,
)
AYAT_PATTERN = re.compile(r"\bAyat\s*\(?\d+\)?", re.IGNORECASE)
STATUTE_PATTERN = re.compile(
    r"\b(?:UU|Undang[- ]Undang|Perda|Peraturan Daerah|Pergub|"
    r"Peraturan Gubernur|SE|Surat Edaran|SKB|Kepgub|Keputusan Gubernur)"
    r"(?:\s+(?:RI|Bali|Gubernur|Kapolri|Provinsi))*"
    r"\s*(?:No\.?|Nomor)?\s*\d+\s*(?:Tahun|/)\s*\d{4}\b",
    re.IGNORECASE,
)
GENERIC_STATUTE_PATTERN = re.compile(
    r"\b(?:KUHP|KUHPerdata|UU\s+ITE|"
    r"(?:Undang[- ]Undang|UU)\s+(?:HAM|ITE|Konsumen|Kepariwisataan|"
    r"Keimigrasian))\b",
    re.IGNORECASE,
)
RUPIAH_PATTERN = re.compile(r"Rp\s?[\d.,]+", re.IGNORECASE)
FOREIGN_CURRENCY_PATTERN = re.compile(
    r"\b(?:US\$\s?[\d.,]+|\d[\d.,]*\s*(?:dolar|dollar|USD))\b",
    re.IGNORECASE,
)

ID_REGULATION_REPLACEMENT = "ketentuan dalam regulasi terkait"
EN_REGULATION_REPLACEMENT = "the relevant regulation"
ID_PROVISION_REPLACEMENT = "ketentuan terkait"
EN_PROVISION_REPLACEMENT = "the relevant provision"
ID_UNVERIFIED_AMOUNT = "nominal yang tidak terverifikasi"
EN_UNVERIFIED_AMOUNT = "an unverified amount"


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

    def verify_and_filter_citations(
        self,
        citations: List[Dict[str, Any]],
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


def _replacement(lang: str, kind: str) -> str:
    if kind == "provision":
        return EN_PROVISION_REPLACEMENT if lang == "en" else ID_PROVISION_REPLACEMENT
    if kind == "amount":
        return EN_UNVERIFIED_AMOUNT if lang == "en" else ID_UNVERIFIED_AMOUNT
    return EN_REGULATION_REPLACEMENT if lang == "en" else ID_REGULATION_REPLACEMENT


def sanitize_statute_references(
    text: Optional[str],
    lang: str = "id",
    allowed_rupiah: Optional[Set[str]] = None,
) -> Optional[str]:
    """Remove unverified article/statute/currency references from free text.

    Tier 2 and Tier 3 are allowed to give practical guidance, but they must not
    smuggle in a specific article number or fine amount that is not grounded in
    the corpus. This function is deliberately deterministic.
    """
    if not text:
        return text

    cleaned = PASAL_PATTERN.sub(_replacement(lang, "regulation"), text)
    cleaned = AYAT_PATTERN.sub(_replacement(lang, "provision"), cleaned)
    cleaned = STATUTE_PATTERN.sub(_replacement(lang, "regulation"), cleaned)
    cleaned = GENERIC_STATUTE_PATTERN.sub(
        _replacement(lang, "regulation"), cleaned
    )

    if allowed_rupiah is not None:
        def currency_repl(match: re.Match) -> str:
            digits = re.sub(r"\D", "", match.group(0))
            if digits and any(digits in allowed for allowed in allowed_rupiah):
                return match.group(0)
            return _replacement(lang, "amount")

        cleaned = RUPIAH_PATTERN.sub(currency_repl, cleaned)
        cleaned = FOREIGN_CURRENCY_PATTERN.sub(
            _replacement(lang, "amount"), cleaned
        )

    return " ".join(cleaned.split())


def _sanitize_guidance(
    guidance: Dict[str, Any],
    lang: str,
    allowed_rupiah: Optional[Set[str]],
) -> Dict[str, Any]:
    sanitized = dict(guidance or {})
    for key in (
        "missing_context_diagnosis",
        "what_user_should_do_next",
        "suggested_query_rewrites",
    ):
        values = sanitized.get(key)
        if isinstance(values, list):
            sanitized[key] = [
                sanitize_statute_references(item, lang, allowed_rupiah)
                for item in values
                if isinstance(item, str) and item.strip()
            ]
    authority = sanitized.get("relevant_authority_or_channel")
    if isinstance(authority, str):
        sanitized["relevant_authority_or_channel"] = (
            sanitize_statute_references(authority, lang, allowed_rupiah)
        )
    return sanitized


def enforce_epistemic_safety(
    result: Dict[str, Any],
    citations: List[Dict[str, Any]],
    top_score: float,
    taxonomy: Dict[str, Any],
    allowed_rupiah: Optional[Set[str]] = None,
) -> Dict[str, Any]:
    """Hard-lock citations for non-grounded modes and sanitize free text.

    Tier 1 claims are kept only when the pipeline marked them verified. If no
    verified claim survives, the response is downgraded to Tier 2 so the user
    still receives useful guidance instead of a dead end.
    """
    mode = result.get("resolution_mode")
    if mode not in {
        "VERIFIED_GROUNDED",
        "NEEDS_CLARIFICATION",
        "OUT_OF_SCOPE_GUIDANCE",
    }:
        mode = choose_epistemic_mode(top_score, taxonomy)

    if mode == "VERIFIED_GROUNDED":
        claims = [
            claim for claim in (result.get("claims") or [])
            if isinstance(claim, dict) and claim.get("verified") is True
        ]
        result["claims"] = claims
        if not claims and result.get("ai_synthesis_status") == "llm":
            mode = "NEEDS_CLARIFICATION"

    # Guidance and tone are free text. Scrub specific article/statute
    # references even in Tier 1 because the verified citations are rendered
    # separately by the UI.
    result["detected_framing_or_tone"] = sanitize_statute_references(
        result.get("detected_framing_or_tone"), "id", allowed_rupiah
    )
    guidance = result.get("user_guidance")
    if isinstance(guidance, dict):
        result["user_guidance"] = _sanitize_guidance(
            guidance, "id", allowed_rupiah
        )

    if mode != "VERIFIED_GROUNDED":
        result["claims"] = []
        result["summary_id"] = sanitize_statute_references(
            result.get("summary_id"), "id", allowed_rupiah
        )
        result["summary_en"] = sanitize_statute_references(
            result.get("summary_en"), "en", allowed_rupiah
        )
        if result.get("guard_status") not in {
            "AI_TIDAK_TERSEDIA", "AI_OUTPUT_DITOLAK", "AI_ABSTAIN",
            "FALLBACK_GUARD", "FALLBACK_DETERMINISTIK",
        }:
            result["guard_status"] = "EPISTEMIC_HARD_LOCK"

    result["resolution_mode"] = mode
    return result
