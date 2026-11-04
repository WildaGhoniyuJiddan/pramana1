"""
Pydantic schemas for Pramana API endpoints.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


# Mode 1: Trip Brief
class TripBriefRequest(BaseModel):
    itinerary_text: str = Field(..., description="Itinerary text or booking notes from traveler/hotel")
    start_date: str = Field(..., description="Trip start date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="Trip end date (YYYY-MM-DD)")
    traveler_origin: str = Field("international", description="Traveler origin ('international' or 'domestic')")


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


class TripBriefResponse(BaseModel):
    status: str
    guard_status: str
    ai_engine: str = "deterministic-strict-rag"
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


# Mode 2: Context Note
class ContextNoteRequest(BaseModel):
    post_content: str = Field(..., description="Text of viral post, incident description, or caption")


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
    verified_layer1: bool


class ContextNoteResponse(BaseModel):
    status: str
    guard_status: str
    ai_engine: str = "deterministic-strict-rag"
    confidence: str
    masked_post: str
    pii_redacted_count: Optional[int] = 0
    neutral_summary: str
    framing_markers: List[FramingMarker]
    citations: List[CitationItem]
    copyable_comment: Optional[str] = None
    disclaimer: str


# Corpus listing
class CorpusResponse(BaseModel):
    metadata: Dict[str, Any]
    tiers: Dict[str, str]
    regulations: List[Dict[str, Any]]
