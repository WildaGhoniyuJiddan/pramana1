"""Deterministic evidence-span index for claim-level verification.

Each span is a contiguous substring of a corpus chunk after whitespace
normalisation. Span IDs are stable for a given chunk text and ordering, so the
LLM can reference them without copying legal text.
"""

import re
from typing import Any, Dict, List

SPAN_SPLIT_PATTERN = re.compile(
    r"(?<=[.;])\s+(?=(?:\(?\d+\)|[a-z]\.|[A-Z]|Pasal\b))"
)
MAX_SPAN_CHARS = 420


def normalize_text(value: str) -> str:
    return " ".join((value or "").strip().split())


def split_evidence_spans(text: str, max_chars: int = MAX_SPAN_CHARS) -> List[str]:
    clean = normalize_text(text)
    if not clean:
        return []

    parts = SPAN_SPLIT_PATTERN.split(clean)
    spans: List[str] = []
    current = ""

    for part in parts:
        part = part.strip()
        if not part:
            continue

        if len(part) > max_chars:
            if current:
                spans.append(current)
                current = ""
            for piece in re.split(r"(?<=[;,])\s+", part):
                piece = piece.strip()
                while len(piece) > max_chars:
                    spans.append(piece[:max_chars].strip())
                    piece = piece[max_chars:].strip()
                if piece:
                    spans.append(piece)
            continue

        if current and len(current) + 1 + len(part) <= max_chars:
            current = f"{current} {part}"
        else:
            if current:
                spans.append(current)
            current = part

    if current:
        spans.append(current)

    return [span for span in spans if len(span) >= 12]


def build_span_index(regulations: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    index: Dict[str, Dict[str, Any]] = {}
    for reg in regulations:
        reg_id = reg.get("id") or reg.get("reg_id")
        text = reg.get("text") or reg.get("quoted_text", "")
        for position, span_text in enumerate(
            split_evidence_spans(text), start=1
        ):
            span_id = f"{reg_id}#s{position}"
            index[span_id] = {
                "span_id": span_id,
                "citation_id": reg_id,
                "text": span_text,
            }
    return index


def span_context_for_citations(
    citations: List[Dict[str, Any]],
    max_spans_per_citation: int = 8,
) -> Dict[str, Any]:
    """Build a compact, JSON-serialisable evidence context for the LLM."""
    context = []
    for citation in citations:
        reg_id = citation["reg_id"]
        spans = split_evidence_spans(citation.get("quoted_text", ""))[
            :max_spans_per_citation
        ]
        context.append({
            "citation_id": reg_id,
            "title": citation.get("official_doc_title", ""),
            "pasal": citation.get("pasal", ""),
            "text_status": citation.get("text_status", ""),
            "spans": [
                {"span_id": f"{reg_id}#s{index}", "text": text}
                for index, text in enumerate(spans, start=1)
            ],
        })
    return {"citations": context}
