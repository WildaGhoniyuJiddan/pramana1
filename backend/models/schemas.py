"""
Pydantic schemas for Pramana API endpoints.
"""

import re
from datetime import date as Date
from typing import List, Dict, Any, Optional, Literal

from pydantic import BaseModel, Field, field_validator, model_validator


DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TRAVELER_ORIGIN_ALIASES = {
    "international": "international",
    "mancanegara": "international",
    "wisman": "international",
    "asing": "international",
    "wna": "international",
    "domestic": "domestic",
    "nusantara": "domestic",
    "wni": "domestic",
}


def _validate_iso_date(value: str, field_name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field_name} harus berupa string berformat YYYY-MM-DD")
    cleaned = value.strip()
    if not DATE_PATTERN.match(cleaned):
        raise ValueError(f"{field_name} harus berformat YYYY-MM-DD")
    try:
        Date.fromisoformat(cleaned)
    except ValueError as exc:
        raise ValueError(f"{field_name} bukan tanggal kalender yang valid") from exc
    return cleaned


# Mode 1: Trip Brief
class TripBriefRequest(BaseModel):
    itinerary_text: str = Field(
        ...,
        min_length=1,
        max_length=4000,
        description="Itinerary text or booking notes from traveler/hotel",
    )
    start_date: str = Field(..., description="Trip start date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="Trip end date (YYYY-MM-DD)")
    traveler_origin: str = Field(
        "international",
        description="Traveler origin ('international' or 'domestic')",
    )

    @field_validator("itinerary_text")
    @classmethod
    def validate_itinerary_text(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("itinerary_text tidak boleh kosong")
        return cleaned

    @field_validator("start_date")
    @classmethod
    def validate_start_date(cls, value: str) -> str:
        return _validate_iso_date(value, "start_date")

    @field_validator("end_date")
    @classmethod
    def validate_end_date(cls, value: Optional[str]) -> Optional[str]:
        if value is None or value == "":
            return None
        return _validate_iso_date(value, "end_date")

    @field_validator("traveler_origin")
    @classmethod
    def normalize_traveler_origin(cls, value: str) -> str:
        normalized = (value or "").strip().lower()
        if normalized not in TRAVELER_ORIGIN_ALIASES:
            raise ValueError("traveler_origin harus 'international' atau 'domestic'")
        return TRAVELER_ORIGIN_ALIASES[normalized]

    @model_validator(mode="after")
    def validate_date_range(self):
        if self.end_date and self.end_date < self.start_date:
            raise ValueError("end_date tidak boleh lebih awal dari start_date")
        return self


class BriefingItem(BaseModel):
    id: str
    title: str
    tier: str
    tier_label: str
    category: str
    pasal: str
    summary: str
    full_text: str
    penalties: str
    source_url: str
    source_note: Optional[str] = None
    last_verified_date: Optional[str] = None
    status: Optional[str] = None
    status_note: Optional[str] = None
    is_verbatim: bool = True
    document_id: Optional[str] = None
    text_status: Optional[str] = None
    source_type: Optional[str] = None
    source_pdf_url: Optional[str] = None
    source_pdf_sha256: Optional[str] = None
    related_document_ids: List[str] = Field(default_factory=list)
    superseded_by: Optional[str] = None
    superseded_by_url: Optional[str] = None


class TripBriefResponse(BaseModel):
    status: str
    guard_status: str
    ai_engine: str = "deterministic-strict-rag"
    ai_synthesis_status: str = "deterministic"
    masked_itinerary: str
    pii_redacted_count: int
    start_date: str
    end_date: str
    calendar_conflicts: Dict[str, Any]
    briefing_items: List[BriefingItem]
    ai_synthesis: Optional[str] = None
    whatsapp_text: str
    ics_content: str
    disclaimer: str
    verification_scope: str = "corpus"
    confidence: str = "TIDAK_DINILAI"
    confidence_note: Optional[str] = None


# Mode 2: Context Note
class ContextNoteRequest(BaseModel):
    post_content: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Text of viral post, incident description, or caption",
    )

    @field_validator("post_content")
    @classmethod
    def validate_post_content(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("post_content tidak boleh kosong")
        return cleaned


class FramingMarker(BaseModel):
    phrase: str
    reason: str


class CitationItem(BaseModel):
    reg_id: str
    official_doc_title: str
    tier: str
    tier_label: str
    pasal: str
    quoted_text: str
    penalties: str
    source_url: str
    source_note: Optional[str] = None
    verified_layer1: bool
    verification_scope: str = "corpus"
    quote_sha256: Optional[str] = None
    last_verified_date: Optional[str] = None
    status: Optional[str] = None
    status_note: Optional[str] = None
    is_verbatim: bool = True
    document_id: Optional[str] = None
    text_status: Optional[str] = None
    source_type: Optional[str] = None
    source_pdf_url: Optional[str] = None
    source_pdf_sha256: Optional[str] = None
    related_document_ids: List[str] = Field(default_factory=list)
    superseded_by: Optional[str] = None
    superseded_by_url: Optional[str] = None


class ContextNoteResponse(BaseModel):
    status: str
    guard_status: str
    ai_engine: str = "deterministic-strict-rag"
    confidence: str
    confidence_note: Optional[str] = None
    verification_scope: str = "corpus"
    masked_post: str
    pii_redacted_count: Optional[int] = 0
    neutral_summary: str
    framing_markers: List[FramingMarker]
    citations: List[CitationItem]
    copyable_comment: Optional[str] = None
    disclaimer: str


# Mode 3: Smart Gate / Zone cards
class ZoneSummary(BaseModel):
    id: str
    name: Dict[str, str]
    category: str
    location_note: Dict[str, str]
    regulation_ids: List[str]
    historical_regulation_ids: List[str] = Field(default_factory=list)
    rules_version: str
    last_verified_date: str


class ZoneListResponse(BaseModel):
    metadata: Dict[str, Any]
    zones: List[ZoneSummary]


class ZoneCard(BaseModel):
    id: str
    name: str
    category: str
    location_note: str
    scope_note: str
    practical_checks: List[str]
    regulation_ids: List[str]
    historical_regulation_ids: List[str] = Field(default_factory=list)
    rules_version: str
    last_verified_date: str
    available_languages: List[str] = Field(
        default_factory=lambda: ["id", "en"]
    )


class ZoneCardResponse(BaseModel):
    zone: ZoneCard
    language: str
    citations: List[CitationItem]
    historical_citations: List[CitationItem] = Field(default_factory=list)
    tts_text: str
    disclaimer: str
    verification_scope: str = "corpus"


class ZoneBriefRequest(BaseModel):
    lang: Literal["id", "en"] = "id"


class ZoneBriefResponse(BaseModel):
    zone_id: str
    language: str
    brief: str
    ai_engine: str
    ai_synthesis_status: str
    guard_status: str
    citation_ids: List[str] = Field(default_factory=list)
    disclaimer: str
    verification_scope: str = "corpus"


# Corpus listing
class CorpusResponse(BaseModel):
    metadata: Dict[str, Any]
    tiers: Dict[str, str]
    regulations: List[Dict[str, Any]]
    documents: List[Dict[str, Any]] = Field(default_factory=list)
