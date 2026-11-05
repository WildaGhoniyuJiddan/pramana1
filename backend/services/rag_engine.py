"""
Strict-RAG Engine for Pramana.

Executes deterministic retrieval plus optional Gemini synthesis for:
- Mode 1: Trip Brief (prevention before travel)
- Mode 2: Context Note (neutral post analysis with exact corpus citations)

The engine is deliberately conservative: if no corpus chunk clears the
relevance threshold, it abstains instead of generating an unsupported answer.
"""

import json
import os
import re
import time
from typing import Dict, Any, List, Optional, Tuple

import httpx
from dotenv import load_dotenv

from backend.services import ai_metrics
from backend.services.ai_config import (
    GEMINI_MODEL,
    get_ai_mode,
    get_gemini_api_key,
)
from backend.services.ai_pipeline import GroundedAIPipeline
from backend.services.corpus_loader import (
    CorpusManager,
    DEFAULT_RELEVANCE_THRESHOLD,
)
from backend.services.verifier import DualLayerVerifier
from backend.services.ocr_masking import mask_pii
from backend.services.calendar_service import (
    check_holiday_conflicts,
    generate_ics_calendar,
)
from backend.services.hybrid_retrieval import HybridRetriever, embed_text
from backend.services.zone_registry import ZoneRegistry

load_dotenv()

GEMINI_API_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_MODEL}:generateContent"
)
PUBLIC_BASE_URL = os.getenv("PRAMANA_PUBLIC_URL", "").strip().rstrip("/")

DISCLAIMER = (
    "Pramana adalah alat edukasi konteks aturan pariwisata berbasis korpus lokal. "
    "Keluaran sistem bukan nasihat hukum resmi dan tidak menggantikan teks "
    "peraturan resmi pada JDIH."
)
CONFIDENCE_NOTE = (
    "Skor keyakinan dihitung dari kecocokan kata kunci pada korpus lokal, "
    "bukan dari uji entailment semantik atau verifikasi silang real-time ke JDIH."
)
TEMPLE_TRIGGERS = (
    "pura", "temple", "ubud", "besakih", "uluwatu", "batur",
    "pantai", "beach", "tempat suci", "pratima",
)
TRAFFIC_TRIGGERS = (
    "motor", "sepeda", "lalu lintas", "sim", "helm", "kendaraan",
)
TEMPLE_QUERY = "pura tempat suci pakaian adat larangan memanjat pohon"
TRAFFIC_QUERY = "kendaraan bermotor sim helm lalu lintas"

ZONE_LANGUAGES = ("id", "en")
ZONE_DISCLAIMER = {
    "id": (
        "Kartu gerbang ini adalah panduan edukasi berbasis korpus lokal "
        "Pramana. Bukan nasihat hukum, bukan bukti pembayaran, dan bukan "
        "verifikasi real-time ke JDIH. Teks asli Bahasa Indonesia tetap "
        "menjadi rujukan."
    ),
    "en": (
        "This gate card is educational guidance based on the local Pramana "
        "corpus. It is not legal advice, not proof of payment, and not a "
        "real-time JDIH verification. The original Indonesian legal text "
        "remains authoritative."
    ),
}
ARTICLE_PATTERN = re.compile(r"\bPasal\s+(\d+[A-Za-z]?)\b", re.IGNORECASE)
RUPIAH_PATTERN = re.compile(r"Rp\s?([\d.,]+)", re.IGNORECASE)


class StrictRAGEngine:
    def __init__(self):
        self.corpus_mgr = CorpusManager.get_instance()
        self.verifier = DualLayerVerifier(self.corpus_mgr)
        self.zone_registry = ZoneRegistry.get_instance()
        self.hybrid = HybridRetriever(self.corpus_mgr)
        self._zone_brief_cache: Dict[Tuple[str, str, str], Dict[str, Any]] = {}
        self.ai_pipeline = GroundedAIPipeline(self._call_gemini_structured)

    @staticmethod
    def _parse_json_object(text: str) -> Optional[Dict[str, Any]]:
        clean = (text or "").strip()
        if clean.startswith("```"):
            clean = re.sub(r"^```(?:json)?\s*", "", clean)
            clean = re.sub(r"\s*```$", "", clean)

        try:
            value = json.loads(clean)
            return value if isinstance(value, dict) else None
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", clean, re.DOTALL)
            if not match:
                return None
            try:
                value = json.loads(match.group(0))
                return value if isinstance(value, dict) else None
            except json.JSONDecodeError:
                return None

    def _call_gemini_structured(
        self,
        system_instruction: str,
        user_prompt: str,
        response_schema: Dict[str, Any],
    ) -> Tuple[Optional[Dict[str, Any]], str, Dict[str, Any]]:
        """Call Gemini once with a JSON response schema.

        Returns (parsed_object, engine_label, metadata). The API key is sent in
        the x-goog-api-key header, never in the URL. No prompt or response body
        is written to logs.
        """
        api_key = get_gemini_api_key()
        if get_ai_mode() == "disabled":
            return None, "ai-disabled", {
                "error": "AI_MODE=disabled",
                "latency_ms": 0,
                "model": GEMINI_MODEL,
            }
        if not api_key:
            return None, "ai-unavailable", {
                "error": "GEMINI_API_KEY tidak tersedia",
                "latency_ms": 0,
                "model": GEMINI_MODEL,
            }

        ai_metrics.record_call()
        started = time.monotonic()
        payload = {
            "system_instruction": {
                "parts": [{"text": system_instruction}]
            },
            "contents": [
                {"role": "user", "parts": [{"text": user_prompt}]}
            ],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 1200,
                "responseMimeType": "application/json",
                "responseSchema": response_schema,
            },
        }

        try:
            with httpx.Client(timeout=20.0) as client:
                response = client.post(
                    GEMINI_API_URL,
                    json=payload,
                    headers={
                        "Content-Type": "application/json",
                        "x-goog-api-key": api_key,
                    },
                )
            latency_ms = int((time.monotonic() - started) * 1000)

            if response.status_code != 200:
                ai_metrics.record_failure(f"HTTP {response.status_code}")
                return None, f"{GEMINI_MODEL} (http error)", {
                    "error": f"HTTP {response.status_code}",
                    "latency_ms": latency_ms,
                    "model": GEMINI_MODEL,
                }

            data = response.json()
            candidates = data.get("candidates", [])
            parts = (
                candidates[0].get("content", {}).get("parts", [])
                if candidates
                else []
            )
            text = parts[0].get("text", "") if parts else ""
            parsed = self._parse_json_object(text)
            if not parsed:
                ai_metrics.record_failure("invalid_json")
                return None, f"{GEMINI_MODEL} (invalid json)", {
                    "error": "invalid_json",
                    "latency_ms": latency_ms,
                    "model": GEMINI_MODEL,
                }

            ai_metrics.record_success(latency_ms)
            return parsed, f"{GEMINI_MODEL} + span-verifier", {
                "error": "",
                "latency_ms": latency_ms,
                "model": GEMINI_MODEL,
            }
        except Exception as exc:  # noqa: BLE001 - classified for telemetry
            latency_ms = int((time.monotonic() - started) * 1000)
            ai_metrics.record_failure(type(exc).__name__)
            return None, f"{GEMINI_MODEL} (error fallback)", {
                "error": type(exc).__name__,
                "latency_ms": latency_ms,
                "model": GEMINI_MODEL,
            }

    @staticmethod
    def _is_international(origin: str) -> bool:
        return (origin or "").strip().lower() in {
            "international", "mancanegara", "wisman", "asing", "wna",
        }

    @staticmethod
    def _confidence_label(scores: List[float]) -> str:
        """Keyword retrieval cannot justify a 'high' confidence claim."""
        if not scores:
            return "TIDAK_DITEMUKAN"
        top_score = max(scores)
        if top_score >= 0.8:
            return "SEDANG"
        if top_score >= DEFAULT_RELEVANCE_THRESHOLD:
            return "RENDAH"
        return "TIDAK_DITEMUKAN"

    @staticmethod
    def _merge_scored(
        base: List[Dict[str, Any]],
        extra: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Merge scored retrieval results by regulation id, keeping the best score."""
        merged: Dict[str, Dict[str, Any]] = {
            item["regulation"]["id"]: item for item in base
        }
        for item in extra:
            reg_id = item["regulation"]["id"]
            existing = merged.get(reg_id)
            if existing is None or item["score"] > existing["score"]:
                merged[reg_id] = item
        return sorted(
            merged.values(),
            key=lambda item: (-item["score"], item["regulation"]["id"]),
        )

    @staticmethod
    def _calendar_note(calendar_check: Dict[str, Any]) -> str:
        if calendar_check.get("has_nyepi"):
            summary = calendar_check.get("nyepi_summary") or {}
            note = summary.get("overlap_note", "")
            return (
                "Perjalanan bersinggungan dengan jendela Nyepi 24 jam "
                "(pukul 06.00 WITA sampai 06.00 WITA keesokan harinya). "
                f"{note}"
            ).strip()

        events = calendar_check.get("events") or []
        if events:
            names = ", ".join(event["name"] for event in events[:3])
            return f"Terdapat peringatan kalender Bali: {names}."

        if calendar_check.get("coverage_warning"):
            return calendar_check["coverage_warning"]

        return ""

    @staticmethod
    def _detect_framing(text: str) -> List[Dict[str, str]]:
        framing_markers: List[Dict[str, str]] = []
        sensational_phrases = [
            ("semua bule", "Generalisasi terhadap seluruh wisatawan asing"),
            ("semua warga lokal", "Generalisasi terhadap warga lokal"),
            ("kebal hukum", "Asumsi tanpa rujukan status penegakan hukum"),
            ("polisi diam saja", "Klaim sensasional tanpa verifikasi otoritas"),
            ("adat barbar", "Pelanggaran etika dan penghinaan budaya"),
            ("deportasi sekarang juga", "Tuntutan sepihak di luar wewenang Imigrasi"),
            ("pemerintah tidak peduli", "Klaim tanpa bukti tentang respons pemerintah"),
        ]
        lowered = (text or "").lower()
        for phrase, reason in sensational_phrases:
            if phrase in lowered:
                framing_markers.append({"phrase": phrase, "reason": reason})
        return framing_markers

    def _build_briefing_items(
        self,
        regulations: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        briefing_items: List[Dict[str, Any]] = []
        for reg in regulations:
            text = reg.get("text", "")
            briefing_items.append({
                "id": reg["id"],
                "title": reg["doc_title"],
                "tier": reg["tier"],
                "tier_label": reg.get("tier_label", f"Tingkat {reg['tier']}"),
                "category": reg.get("category", "Regulasi"),
                "pasal": reg.get("pasal", ""),
                "summary": text[:280] + ("..." if len(text) > 280 else ""),
                "full_text": text,
                "penalties": reg.get(
                    "penalties",
                    "Sanksi administratif dan adat setempat.",
                ),
                "source_url": reg.get("source_url", ""),
                "source_note": reg.get("source_note"),
                "last_verified_date": reg.get("last_verified_date"),
                "status": reg.get("status"),
                "status_note": reg.get("status_note"),
                "is_verbatim": bool(reg.get("is_verbatim", True)),
                "document_id": reg.get("document_id"),
                "text_status": reg.get("text_status"),
                "source_type": reg.get("source_type"),
                "source_pdf_url": reg.get("source_pdf_url"),
                "source_pdf_sha256": reg.get("source_pdf_sha256"),
                "related_document_ids": reg.get("related_document_ids", []),
                "superseded_by": reg.get("superseded_by"),
                "superseded_by_url": reg.get("superseded_by_url"),
            })
        return briefing_items

    def _retrieve_scored(
        self,
        query: str,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """Hybrid retrieval when embeddings are available; keyword otherwise."""
        if self.hybrid.available:
            try:
                query_embedding = embed_text(query)
                hybrid_results = self.hybrid.search_scored(
                    query, query_embedding, top_k=top_k
                )
                if hybrid_results:
                    return hybrid_results
            except Exception:  # noqa: BLE001 - fall back to keyword
                pass
        return self.corpus_mgr.search_regulations_scored(query, top_k=top_k)

    def _build_citations_for_regulations(
        self,
        regulations: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        raw_citations = [
            {"reg_id": reg["id"], "quoted_text": reg["text"]}
            for reg in regulations
        ]
        return self.verifier.verify_and_filter_citations(raw_citations)

    @staticmethod
    def _validate_zone_language(lang: str) -> str:
        normalized = (lang or "").strip().lower()
        if normalized not in ZONE_LANGUAGES:
            raise ValueError("lang harus 'id' atau 'en'")
        return normalized

    def _build_zone_citations(
        self,
        zone: Dict[str, Any],
        historical: bool = False,
    ) -> List[Dict[str, Any]]:
        """Build Layer-1 verified citations for one zone."""
        field = "historical_regulation_ids" if historical else "regulation_ids"
        regulation_ids = zone.get(field, [])
        raw_citations = []
        for reg_id in regulation_ids:
            reg = self.corpus_mgr.get_by_id(reg_id)
            if not reg:
                raise ValueError(f"Chunk zona tidak ditemukan: {reg_id}")
            raw_citations.append({
                "reg_id": reg["id"],
                "quoted_text": reg["text"],
            })

        verified = self.verifier.verify_and_filter_citations(raw_citations)
        if len(verified) != len(regulation_ids):
            raise ValueError(
                "Kartu zona gagal verifikasi Layer-1 untuk chunk: "
                f"{', '.join(regulation_ids)}"
            )
        return verified

    def list_zones(self) -> Dict[str, Any]:
        """Return the zone directory used by the Smart Gate landing page."""
        zones = []
        for zone in self.zone_registry.get_all():
            zones.append({
                "id": zone["id"],
                "name": zone["name"],
                "category": zone["category"],
                "location_note": zone["location_note"],
                "regulation_ids": zone["regulation_ids"],
                "historical_regulation_ids": zone.get(
                    "historical_regulation_ids", []
                ),
                "rules_version": zone["rules_version"],
                "last_verified_date": zone["last_verified_date"],
            })
        return {
            "metadata": self.zone_registry.metadata,
            "zones": zones,
        }

    def get_zone_card(self, zone_id: str, lang: str = "id") -> Dict[str, Any]:
        """Return a deterministic zone card with Layer-1 verified citations."""
        lang = self._validate_zone_language(lang)
        zone = self.zone_registry.get_zone_or_raise(zone_id)

        citations = self._build_zone_citations(zone, historical=False)
        historical_citations = self._build_zone_citations(
            zone, historical=True
        )

        name = zone["name"][lang]
        location_note = zone["location_note"][lang]
        scope_note = zone["scope_note"][lang]
        practical_checks = [item[lang] for item in zone["practical_checks"]]
        citation_refs = "; ".join(
            f"{citation['official_doc_title']} ({citation['pasal']})"
            for citation in citations
        )
        tts_text = (
            f"{name}. {location_note} {scope_note} "
            f"Panduan utama: {' '.join(practical_checks)} "
            f"Rujukan resmi: {citation_refs}. "
            f"{ZONE_DISCLAIMER[lang]}"
        )

        return {
            "zone": {
                "id": zone["id"],
                "name": name,
                "category": zone["category"],
                "location_note": location_note,
                "scope_note": scope_note,
                "practical_checks": practical_checks,
                "regulation_ids": zone["regulation_ids"],
                "historical_regulation_ids": zone.get(
                    "historical_regulation_ids", []
                ),
                "rules_version": zone["rules_version"],
                "last_verified_date": zone["last_verified_date"],
                "available_languages": list(ZONE_LANGUAGES),
            },
            "language": lang,
            "citations": citations,
            "historical_citations": historical_citations,
            "tts_text": tts_text,
            "disclaimer": ZONE_DISCLAIMER[lang],
            "verification_scope": "corpus",
        }

    @staticmethod
    def _deterministic_zone_brief(
        zone: Dict[str, Any],
        citations: List[Dict[str, Any]],
        lang: str,
    ) -> str:
        checks = zone["practical_checks"][:3]
        titles = "; ".join(
            citation["official_doc_title"] for citation in citations
        )
        if lang == "en":
            return (
                f"At {zone['name']}, follow {len(zone['practical_checks'])} "
                f"key checks. {' '.join(checks)} "
                f"The verified legal basis is: {titles}. "
                "This is a deterministic template; the original Indonesian "
                "legal text remains authoritative."
            )
        return (
            f"Di {zone['name']}, ada {len(zone['practical_checks'])} panduan "
            f"utama. {' '.join(checks)} "
            f"Dasar hukum terverifikasi: {titles}. "
            "Ringkasan ini adalah template deterministik; teks asli Bahasa "
            "Indonesia tetap menjadi rujukan."
        )

    @staticmethod
    def _zone_brief_is_safe(
        text: str,
        citations: List[Dict[str, Any]],
    ) -> bool:
        """Reject LLM output that introduces article numbers or rupiah amounts
        outside the verified citation set."""
        if not text or len(text.strip()) < 20 or len(text) > 900:
            return False

        allowed_articles = set()
        allowed_rupiah = set()
        for citation in citations:
            for match in ARTICLE_PATTERN.finditer(citation.get("pasal", "")):
                allowed_articles.add(match.group(1).lower())
            for match in RUPIAH_PATTERN.finditer(
                citation.get("quoted_text", "")
            ):
                allowed_rupiah.add(re.sub(r"\D", "", match.group(1)))

        mentioned_articles = {
            match.group(1).lower()
            for match in ARTICLE_PATTERN.finditer(text)
        }
        if mentioned_articles - allowed_articles:
            return False

        for match in RUPIAH_PATTERN.finditer(text):
            digits = re.sub(r"\D", "", match.group(1))
            if digits and not any(
                digits in allowed for allowed in allowed_rupiah
            ):
                return False

        return True

    def analyze_zone_brief(
        self,
        zone_id: str,
        lang: str = "id",
    ) -> Dict[str, Any]:
        """Generate a grounded, bilingual Smart Gate brief.

        The model receives verified citations and evidence-span IDs. Python
        verifies every claim. If AI is required but unavailable, the response
        is an explicit unavailable state, not a silent template posing as AI.
        """
        lang = self._validate_zone_language(lang)
        card = self.get_zone_card(zone_id, lang)
        citations = card["citations"]
        raw_zone = self.zone_registry.get_zone_or_raise(zone_id)

        cache_key = (zone_id, lang, raw_zone["rules_version"])
        cached = self._zone_brief_cache.get(cache_key)
        if cached:
            return cached

        zone_id_view = {
            "name": raw_zone["name"]["id"],
            "practical_checks": [
                item["id"] for item in raw_zone["practical_checks"]
            ],
        }
        zone_en_view = {
            "name": raw_zone["name"]["en"],
            "practical_checks": [
                item["en"] for item in raw_zone["practical_checks"]
            ],
        }
        fallback_id = self._deterministic_zone_brief(
            zone_id_view, citations, "id"
        )
        fallback_en = self._deterministic_zone_brief(
            zone_en_view, citations, "en"
        )

        system_prompt = (
            "You are the Pramana Smart Gate compliance guide at a Bali "
            "tourist site. Use ONLY the verified citations and evidence spans "
            "supplied by the user. Do not invent rules, article numbers, "
            "sanctions, or fees. Return JSON with summary_id, summary_en, and "
            "claims. Each claim must cite one citation_id and one or more "
            "span_ids from that citation. Keep each summary to 2-3 sentences. "
            "State that the original Indonesian legal text is authoritative."
        )
        user_prompt = (
            f"Zone ID: {raw_zone['id']}\n"
            f"Zone name: {raw_zone['name']['id']} / {raw_zone['name']['en']}\n"
            f"Category: {raw_zone['category']}\n"
            f"Location: {raw_zone['location_note']['id']} / "
            f"{raw_zone['location_note']['en']}\n"
            f"Scope note: {raw_zone['scope_note']['id']} / "
            f"{raw_zone['scope_note']['en']}\n"
            "Practical checklist (ID):\n- "
            + "\n- ".join(zone_id_view["practical_checks"])
            + "\nPractical checklist (EN):\n- "
            + "\n- ".join(zone_en_view["practical_checks"])
        )
        result = self.ai_pipeline.answer(
            citations=citations,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            fallback_summary=fallback_id,
            fallback_summary_en=fallback_en,
        )

        selected_summary = (
            result["summary_id"] if lang == "id" else result["summary_en"]
        )
        if result["ai_synthesis_status"] == "unavailable":
            brief = (
                "Ringkasan AI tidak tersedia. Gunakan checklist dan sitasi "
                "terverifikasi di bawah."
                if lang == "id"
                else "AI summary is unavailable. Use the verified checklist "
                "and citations below."
            )
        else:
            brief = selected_summary or (
                fallback_id if lang == "id" else fallback_en
            )

        response = {
            "zone_id": zone_id,
            "language": lang,
            "brief": brief,
            "brief_id": result["summary_id"] or fallback_id,
            "brief_en": result["summary_en"] or fallback_en,
            "ai_engine": result["ai_engine"],
            "ai_synthesis_status": result["ai_synthesis_status"],
            "guard_status": result["guard_status"],
            "citation_ids": [citation["reg_id"] for citation in citations],
            "claims": result["claims"],
            "rejected_claims": result["rejected_claims"],
            "ai_latency_ms": result["latency_ms"],
            "model": result["model"],
            "disclaimer": ZONE_DISCLAIMER[lang],
            "verification_scope": "corpus",
        }
        if result["ai_synthesis_status"] == "llm":
            self._zone_brief_cache[cache_key] = response
        return response

    def analyze_trip_itinerary(
        self,
        itinerary_text: str,
        start_date: str,
        end_date: Optional[str] = None,
        traveler_origin: str = "international",
    ) -> Dict[str, Any]:
        """
        Mode 1: Generate a verified Trip Brief.

        Steps:
        1. Mask PII before downstream processing or any AI call.
        2. Check the Balinese calendar for Nyepi and ceremony conflicts.
        3. Retrieve scored corpus regulations and enforce the relevance guard.
        4. Synthesize only after grounding, or abstain with calendar facts only.
        5. Generate WhatsApp text and RFC 5545 ICS export.
        """
        masked_text, pii_counts = mask_pii(itinerary_text)
        effective_end_date = end_date or start_date

        calendar_check = check_holiday_conflicts(start_date, effective_end_date)

        # Primary retrieval plus deterministic query expansion for common
        # travel triggers. Every expansion still has to clear the score guard.
        scored = self._retrieve_scored(masked_text, top_k=4)
        lowered = masked_text.lower()

        if any(trigger in lowered for trigger in TEMPLE_TRIGGERS):
            scored = self._merge_scored(
                scored,
                self._retrieve_scored(TEMPLE_QUERY, top_k=4),
            )

        if any(trigger in lowered for trigger in TRAFFIC_TRIGGERS):
            scored = self._merge_scored(
                scored,
                self._retrieve_scored(TRAFFIC_QUERY, top_k=2),
            )

        matched_regs = [item["regulation"] for item in scored]
        scores = [item["score"] for item in scored]
        is_grounded, guard_status = self.verifier.enforce_layer2_guard(
            matched_regs,
            retrieval_scores=scores,
        )

        if not is_grounded:
            calendar_note = self._calendar_note(calendar_check)
            abstain_summary = (
                "Tidak ditemukan aturan spesifik di korpus Pramana yang cocok "
                "dengan rencana perjalanan ini. Sistem tidak menyusun klaim "
                "hukum tambahan."
            )
            if calendar_note:
                abstain_summary = f"{calendar_note} {abstain_summary}"

            ics_calendar = generate_ics_calendar(
                title="Pramana: Bali Travel Brief",
                description=(
                    f"Status verifikasi: TIDAK_DITEMUKAN. "
                    f"Bentrok Nyepi: {calendar_check.get('has_nyepi', False)}."
                ),
                start_date_str=start_date,
                end_date_str=effective_end_date,
            )

            return {
                "status": "TIDAK_DITEMUKAN",
                "guard_status": guard_status,
                "ai_engine": "dual-layer-guard (abstain)",
                "ai_synthesis_status": "abstain",
                "masked_itinerary": masked_text,
                "pii_redacted_count": sum(pii_counts.values()),
                "start_date": start_date,
                "end_date": effective_end_date,
                "calendar_conflicts": calendar_check,
                "briefing_items": [],
                "ai_synthesis": abstain_summary,
                "ai_synthesis_en": (
                    "No specific rule in the Pramana corpus matched this "
                    "itinerary. The system does not add legal claims."
                ),
                "ai_claims": [],
                "ai_rejected_claims": 0,
                "ai_latency_ms": 0,
                "ai_model": "",
                "ai_guard_status": "TIDAK_DITEMUKAN",
                "whatsapp_text": self._build_whatsapp_text(
                    masked_text,
                    start_date,
                    effective_end_date,
                    calendar_check,
                    [],
                    is_grounded=False,
                ),
                "ics_content": ics_calendar,
                "disclaimer": DISCLAIMER,
                "verification_scope": "corpus",
                "confidence": "TIDAK_DITEMUKAN",
                "confidence_note": CONFIDENCE_NOTE,
            }

        # The levy applies to every international visitor, but it is added only
        # after the query has been grounded and is never used to justify the
        # grounding decision itself.
        if self._is_international(traveler_origin):
            levy_reg = self.corpus_mgr.get_by_id("PERDA_BALI_06_2023_LEVY")
            if levy_reg and all(reg["id"] != levy_reg["id"] for reg in matched_regs):
                matched_regs.append(levy_reg)

        briefing_items = self._build_briefing_items(matched_regs)
        confidence = self._confidence_label(scores)
        citations = self._build_citations_for_regulations(matched_regs)

        calendar_note = self._calendar_note(calendar_check)
        categories = ", ".join(
            item["category"] for item in briefing_items[:3]
        )
        fallback_summary = (
            f"{calendar_note} Berdasarkan korpus regulasi Pramana, ditemukan "
            f"{len(briefing_items)} instrumen yang relevan: {categories}. "
            "Cakupan verifikasi terbatas pada korpus lokal; periksa tautan "
            "sumber resmi pada setiap butir."
        ).strip()
        fallback_summary_en = (
            f"Based on the Pramana corpus, {len(briefing_items)} relevant "
            f"instruments were found: {categories}. Verification is limited "
            "to the local corpus; check the official source links."
        )
        system_prompt = (
            "You are the Pramana Strict-RAG trip compliance engine. Return "
            "JSON with summary_id, summary_en, and claims. Use ONLY the "
            "supplied citations and evidence spans. Each claim must cite one "
            "citation_id and one or more span_ids. Do not invent articles, "
            "sanctions, or fees. Mention the calendar status only when it is "
            "provided in the user prompt."
        )
        user_prompt = (
            f"Rencana Perjalanan (Disamarkan PII): {masked_text}\n"
            f"Tanggal: {start_date} s/d {effective_end_date} | "
            f"Status Wisman: {traveler_origin}\n"
            f"Bentrok Nyepi: {calendar_check.get('has_nyepi', False)}\n"
            f"Catatan Kalender: {calendar_note or 'Tidak ada peringatan.'}"
        )
        ai_result = self.ai_pipeline.answer(
            citations=citations,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            fallback_summary=fallback_summary,
            fallback_summary_en=fallback_summary_en,
        )

        if ai_result["ai_synthesis_status"] == "unavailable":
            ai_synthesis = (
                "Ringkasan AI tidak tersedia. Sitasi terverifikasi tetap "
                "ditampilkan di bawah."
            )
            ai_synthesis_en = (
                "AI summary is unavailable. The verified citations are still "
                "shown below."
            )
        else:
            ai_synthesis = ai_result["summary_id"] or fallback_summary
            ai_synthesis_en = (
                ai_result["summary_en"] or fallback_summary_en
            )

        wa_text = self._build_whatsapp_text(
            masked_text,
            start_date,
            effective_end_date,
            calendar_check,
            briefing_items,
            is_grounded=True,
        )

        ics_calendar = generate_ics_calendar(
            title="Pramana: Bali Travel Brief",
            description=(
                f"Status verifikasi: {guard_status}. "
                f"Bentrok Nyepi: {calendar_check.get('has_nyepi', False)}. "
                "Periksa sumber resmi pada setiap butir."
            ),
            start_date_str=start_date,
            end_date_str=effective_end_date,
        )

        return {
            "status": "SUCCESS",
            "guard_status": guard_status,
            "ai_engine": ai_result["ai_engine"],
            "ai_synthesis_status": ai_result["ai_synthesis_status"],
            "masked_itinerary": masked_text,
            "pii_redacted_count": sum(pii_counts.values()),
            "start_date": start_date,
            "end_date": effective_end_date,
            "calendar_conflicts": calendar_check,
            "briefing_items": briefing_items,
            "ai_synthesis": ai_synthesis,
            "ai_synthesis_en": ai_synthesis_en,
            "ai_claims": ai_result["claims"],
            "ai_rejected_claims": ai_result["rejected_claims"],
            "ai_latency_ms": ai_result["latency_ms"],
            "ai_model": ai_result["model"],
            "ai_guard_status": ai_result["guard_status"],
            "whatsapp_text": wa_text,
            "ics_content": ics_calendar,
            "disclaimer": DISCLAIMER,
            "verification_scope": "corpus",
            "confidence": confidence,
            "confidence_note": CONFIDENCE_NOTE,
        }

    def analyze_viral_post(self, post_content: str) -> Dict[str, Any]:
        """
        Mode 2: Generate a neutral, verifiable Context Note for viral content.

        Abstains when no corpus regulation clears the relevance threshold.
        """
        masked_text, pii_counts = mask_pii(post_content)
        framing_markers = self._detect_framing(masked_text)

        scored = self._retrieve_scored(masked_text, top_k=3)
        matched_regs = [item["regulation"] for item in scored]
        scores = [item["score"] for item in scored]

        is_grounded, guard_status = self.verifier.enforce_layer2_guard(
            matched_regs,
            retrieval_scores=scores,
        )

        if not is_grounded:
            abstain_text = (
                "Tidak ditemukan regulasi atau norma hukum di korpus resmi "
                "Bali yang mengatur atau mengonfirmasi klaim ini. Pramana "
                "memilih abstain daripada berspekulasi."
            )
            return {
                "status": "TIDAK_DITEMUKAN",
                "guard_status": guard_status,
                "ai_engine": "dual-layer-guard (abstain)",
                "ai_synthesis_status": "abstain",
                "confidence": "TIDAK_DITEMUKAN",
                "confidence_note": CONFIDENCE_NOTE,
                "verification_scope": "corpus",
                "masked_post": masked_text,
                "pii_redacted_count": sum(pii_counts.values()),
                "neutral_summary": abstain_text,
                "neutral_summary_en": (
                    "No regulation or legal norm in the Pramana corpus "
                    "matches or confirms this claim. Pramana abstains rather "
                    "than speculate."
                ),
                "ai_claims": [],
                "ai_rejected_claims": 0,
                "ai_latency_ms": 0,
                "ai_model": "",
                "ai_guard_status": "TIDAK_DITEMUKAN",
                "framing_markers": framing_markers,
                "citations": [],
                "copyable_comment": (
                    "Catatan Konteks (Pramana): Tidak ditemukan dasar hukum "
                    "dalam korpus lokal untuk klaim ini. Hindari menyimpulkan "
                    "kesalahan individu tanpa dokumen resmi."
                ),
                "disclaimer": DISCLAIMER,
            }

        raw_citations = []
        for reg in matched_regs:
            raw_citations.append({
                "reg_id": reg["id"],
                "official_doc_title": reg["doc_title"],
                "tier": reg["tier"],
                "tier_label": reg.get("tier_label", f"Tingkat {reg['tier']}"),
                "pasal": reg.get("pasal", ""),
                "quoted_text": reg["text"],
                "penalties": reg.get("penalties", ""),
                "source_url": reg.get("source_url", ""),
                "source_note": reg.get("source_note"),
                "document_id": reg.get("document_id"),
                "text_status": reg.get("text_status"),
                "source_type": reg.get("source_type"),
                "source_pdf_url": reg.get("source_pdf_url"),
                "source_pdf_sha256": reg.get("source_pdf_sha256"),
                "related_document_ids": reg.get("related_document_ids", []),
                "verified_layer1": True,
            })

        citations = self.verifier.verify_and_filter_citations(raw_citations)

        if not citations:
            abstain_text = (
                "Kutipan yang ditemukan tidak lolos verifikasi Layer-1 "
                "terhadap korpus lokal. Pramana memilih abstain."
            )
            return {
                "status": "TIDAK_DITEMUKAN",
                "guard_status": "TIDAK_DITEMUKAN",
                "ai_engine": "dual-layer-guard (abstain)",
                "ai_synthesis_status": "abstain",
                "confidence": "TIDAK_DITEMUKAN",
                "confidence_note": CONFIDENCE_NOTE,
                "verification_scope": "corpus",
                "masked_post": masked_text,
                "pii_redacted_count": sum(pii_counts.values()),
                "neutral_summary": abstain_text,
                "neutral_summary_en": (
                    "The retrieved quotation did not pass Layer-1 verification "
                    "against the local corpus. Pramana abstains."
                ),
                "ai_claims": [],
                "ai_rejected_claims": 0,
                "ai_latency_ms": 0,
                "ai_model": "",
                "ai_guard_status": "TIDAK_DITEMUKAN",
                "framing_markers": framing_markers,
                "citations": [],
                "copyable_comment": (
                    "Catatan Konteks (Pramana): Kutipan tidak lolos verifikasi "
                    "korpus. Tidak ada kesimpulan hukum yang disampaikan."
                ),
                "disclaimer": DISCLAIMER,
            }

        confidence = self._confidence_label(scores)
        top_reg = matched_regs[0]
        top_citation = citations[0]

        fallback_summary = (
            f"Berdasarkan {top_reg['doc_title']} "
            f"({top_reg.get('pasal', '')}), ketentuan yang relevan adalah: "
            f"{top_reg.get('text', '')[:240]}"
            f"{'...' if len(top_reg.get('text', '')) > 240 else ''} "
            "Catatan ini tidak menyatakan individu bersalah."
        )
        fallback_summary_en = (
            f"Based on {top_reg['doc_title']} "
            f"({top_reg.get('pasal', '')}), the relevant provision is: "
            f"{top_reg.get('text', '')[:240]}"
            f"{'...' if len(top_reg.get('text', '')) > 240 else ''} "
            "This note does not establish individual guilt."
        )
        system_prompt = (
            "You are the Pramana neutral legal-context writer (Strict-RAG). "
            "Return JSON with summary_id, summary_en, and claims. Use ONLY the "
            "supplied citations and evidence spans. Each claim must cite one "
            "citation_id and one or more span_ids. Do not add facts, article "
            "numbers, or sanctions outside the evidence. The summary must be "
            "objective, neutral, and must not declare any individual guilty."
        )
        user_prompt = (
            f"Teks Klaim/Postingan (Disamarkan PII): {masked_text}\n"
            "Framing markers: "
            + (", ".join(item["phrase"] for item in framing_markers) or "none")
        )
        ai_result = self.ai_pipeline.answer(
            citations=citations,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            fallback_summary=fallback_summary,
            fallback_summary_en=fallback_summary_en,
        )

        if ai_result["ai_synthesis_status"] == "abstain":
            abstain_text = (
                "AI menilai permintaan ini tidak dapat dijawab secara aman "
                "dari bukti korpus. Pramana memilih abstain daripada "
                "mengarang atau mengikuti instruksi yang menyimpang."
            )
            return {
                "status": "TIDAK_DITEMUKAN",
                "guard_status": "TIDAK_DITEMUKAN",
                "ai_engine": ai_result["ai_engine"],
                "ai_synthesis_status": "abstain",
                "confidence": "TIDAK_DITEMUKAN",
                "confidence_note": CONFIDENCE_NOTE,
                "verification_scope": "corpus",
                "masked_post": masked_text,
                "pii_redacted_count": sum(pii_counts.values()),
                "neutral_summary": abstain_text,
                "neutral_summary_en": (
                    "The AI judged this request unsafe to answer from the "
                    "corpus evidence. Pramana abstains instead of inventing "
                    "or following a prompt injection."
                ),
                "ai_claims": [],
                "ai_rejected_claims": 0,
                "ai_latency_ms": ai_result["latency_ms"],
                "ai_model": ai_result["model"],
                "ai_guard_status": ai_result["guard_status"],
                "framing_markers": framing_markers,
                "citations": [],
                "copyable_comment": (
                    "Catatan Konteks (Pramana): Permintaan ini tidak dijawab "
                    "karena tidak aman atau tidak didukung bukti korpus."
                ),
                "disclaimer": DISCLAIMER,
            }

        if ai_result["ai_synthesis_status"] == "unavailable":
            neutral_summary = (
                "Ringkasan AI tidak tersedia. Sitasi terverifikasi tetap "
                "ditampilkan di bawah."
            )
            neutral_summary_en = (
                "AI summary is unavailable. The verified citations are still "
                "shown below."
            )
        else:
            neutral_summary = ai_result["summary_id"] or fallback_summary
            neutral_summary_en = (
                ai_result["summary_en"] or fallback_summary_en
            )

        return {
            "status": "TERVERIFIKASI",
            "guard_status": guard_status,
            "ai_engine": ai_result["ai_engine"],
            "ai_synthesis_status": ai_result["ai_synthesis_status"],
            "confidence": confidence,
            "confidence_note": CONFIDENCE_NOTE,
            "verification_scope": "corpus",
            "masked_post": masked_text,
            "pii_redacted_count": sum(pii_counts.values()),
            "neutral_summary": neutral_summary,
            "neutral_summary_en": neutral_summary_en,
            "ai_claims": ai_result["claims"],
            "ai_rejected_claims": ai_result["rejected_claims"],
            "ai_latency_ms": ai_result["latency_ms"],
            "ai_model": ai_result["model"],
            "ai_guard_status": ai_result["guard_status"],
            "framing_markers": framing_markers,
            "citations": citations,
            "copyable_comment": (
                f"Catatan Konteks (Pramana):\n{neutral_summary}\n"
                f"Rujukan: {top_citation['official_doc_title']} "
                f"({top_citation['pasal']})\n"
                f"Sumber: {top_citation['source_url']}\n\n{DISCLAIMER}"
            ),
            "disclaimer": DISCLAIMER,
        }

    def _build_whatsapp_text(
        self,
        itinerary: str,
        start_date: str,
        end_date: Optional[str],
        calendar_check: Dict[str, Any],
        briefing_items: List[Dict[str, Any]],
        is_grounded: bool = True,
    ) -> str:
        date_span = f"{start_date}" + (
            f" s/d {end_date}" if end_date and end_date != start_date else ""
        )
        lines = [
            "*PRAMANA: Bali Trip Brief & Local Rules*",
            f"Tanggal: {date_span}",
            "",
        ]

        if calendar_check.get("has_nyepi"):
            lines.append("*PERINGATAN NYEPI (Catur Brata Penyepian)*")
            lines.append(
                "Berlaku larangan keluar hotel, pemadaman lampu luar, "
                "penutupan bandara, dan pemadaman data seluler selama 24 jam "
                "(06.00 WITA sampai 06.00 WITA keesokan harinya)."
            )
            lines.append("")

        if not is_grounded:
            lines.append("*STATUS: TIDAK_DITEMUKAN*")
            lines.append(
                "Tidak ditemukan aturan spesifik di korpus Pramana yang cocok "
                "dengan rencana perjalanan ini. Tidak ada klaim hukum tambahan "
                "yang disusun."
            )
        else:
            lines.append("*Aturan Utama yang Wajib Dipatuhi:*")
            for index, item in enumerate(briefing_items[:3], 1):
                lines.append(
                    f"{index}. *{item['category']}* ({item['tier_label']})"
                )
                summary = item["summary"][:120]
                lines.append(f"   {summary}...")

        if briefing_items:
            lines.append("")
            lines.append(f"Sumber: {briefing_items[0].get('source_url', '')}")

        if PUBLIC_BASE_URL:
            lines.append(f"Verifikasi naskah resmi: {PUBLIC_BASE_URL}")

        lines.append("")
        lines.append(f"Disclaimer: {DISCLAIMER}")
        return "\n".join(lines)
