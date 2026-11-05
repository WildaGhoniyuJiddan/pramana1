"""
Strict-RAG Engine for Pramana.

Executes deterministic retrieval plus optional Gemini synthesis for:
- Mode 1: Trip Brief (prevention before travel)
- Mode 2: Context Note (neutral post analysis with exact corpus citations)

The engine is deliberately conservative: if no corpus chunk clears the
relevance threshold, it abstains instead of generating an unsupported answer.
"""

import os
from typing import Dict, Any, List, Optional, Tuple

import httpx
from dotenv import load_dotenv

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

load_dotenv()

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
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


class StrictRAGEngine:
    def __init__(self):
        self.corpus_mgr = CorpusManager.get_instance()
        self.verifier = DualLayerVerifier(self.corpus_mgr)

    def _call_gemini_strict(
        self,
        system_instruction: str,
        user_prompt: str,
    ) -> Tuple[Optional[str], str]:
        """
        Call Gemini REST API with strict grounding constraints.

        The API key is sent in the x-goog-api-key header, never in the URL.
        Returns (summary, engine_label); summary is None when the local
        deterministic fallback must be used.
        """
        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if not api_key or api_key == "your_gemini_api_key_here":
            return None, "deterministic-strict-rag (local fallback)"

        payload = {
            "system_instruction": {
                "parts": [{"text": system_instruction}]
            },
            "contents": [
                {"role": "user", "parts": [{"text": user_prompt}]}
            ],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 450,
            },
        }

        try:
            with httpx.Client(timeout=8.0) as client:
                resp = client.post(
                    GEMINI_API_URL,
                    json=payload,
                    headers={
                        "Content-Type": "application/json",
                        "x-goog-api-key": api_key,
                    },
                )
                if resp.status_code == 200:
                    data = resp.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts and "text" in parts[0]:
                            return (
                                parts[0]["text"].strip(),
                                f"{GEMINI_MODEL} + dual-layer-verifier",
                            )
                return None, "deterministic-strict-rag (api fallback)"
        except Exception:
            return None, "deterministic-strict-rag (error fallback)"

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
        scored = self.corpus_mgr.search_regulations_scored(masked_text, top_k=4)
        lowered = masked_text.lower()

        if any(trigger in lowered for trigger in TEMPLE_TRIGGERS):
            scored = self._merge_scored(
                scored,
                self.corpus_mgr.search_regulations_scored(TEMPLE_QUERY, top_k=4),
            )

        if any(trigger in lowered for trigger in TRAFFIC_TRIGGERS):
            scored = self._merge_scored(
                scored,
                self.corpus_mgr.search_regulations_scored(TRAFFIC_QUERY, top_k=2),
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
                "ai_synthesis_status": "deterministic",
                "masked_itinerary": masked_text,
                "pii_redacted_count": sum(pii_counts.values()),
                "start_date": start_date,
                "end_date": effective_end_date,
                "calendar_conflicts": calendar_check,
                "briefing_items": [],
                "ai_synthesis": abstain_summary,
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

        corpus_context = "\n".join(
            f"- [{reg['id']}] {reg['doc_title']} ({reg.get('pasal', '')}) "
            f"| status: {reg.get('status', '-')} | teks: {reg['text']}"
            for reg in matched_regs
        )
        sys_prompt = (
            "Anda adalah mesin kepatuhan hukum Strict-RAG Pramana. "
            "Susun ringkasan eksekutif perjalanan 2-3 kalimat, bahasa Indonesia "
            "formal, tanpa emoji. Gunakan HANYA regulasi terlampir dan status "
            "kalender Bali. Jangan mengarang pasal, sanksi, atau nomor peraturan "
            "di luar daftar."
        )
        user_prompt = (
            f"Rencana Perjalanan (Disamarkan PII): {masked_text}\n"
            f"Tanggal: {start_date} s/d {effective_end_date} | "
            f"Status Wisman: {traveler_origin}\n"
            f"Bentrok Nyepi: {calendar_check.get('has_nyepi', False)}\n"
            f"Regulasi Resmi Terkait:\n{corpus_context}"
        )
        llm_summary, engine_label = self._call_gemini_strict(sys_prompt, user_prompt)

        if llm_summary:
            ai_synthesis = llm_summary
            ai_synthesis_status = "llm"
        else:
            calendar_note = self._calendar_note(calendar_check)
            categories = ", ".join(
                item["category"] for item in briefing_items[:3]
            )
            ai_synthesis = (
                f"{calendar_note} Berdasarkan korpus regulasi Pramana, ditemukan "
                f"{len(briefing_items)} instrumen yang relevan: {categories}. "
                "Cakupan verifikasi terbatas pada korpus lokal; periksa tautan "
                "sumber resmi pada setiap butir."
            ).strip()
            ai_synthesis_status = "deterministic"

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
            "ai_engine": engine_label,
            "ai_synthesis_status": ai_synthesis_status,
            "masked_itinerary": masked_text,
            "pii_redacted_count": sum(pii_counts.values()),
            "start_date": start_date,
            "end_date": effective_end_date,
            "calendar_conflicts": calendar_check,
            "briefing_items": briefing_items,
            "ai_synthesis": ai_synthesis,
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

        scored = self.corpus_mgr.search_regulations_scored(masked_text, top_k=3)
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
                "confidence": "TIDAK_DITEMUKAN",
                "confidence_note": CONFIDENCE_NOTE,
                "verification_scope": "corpus",
                "masked_post": masked_text,
                "pii_redacted_count": sum(pii_counts.values()),
                "neutral_summary": abstain_text,
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
                "confidence": "TIDAK_DITEMUKAN",
                "confidence_note": CONFIDENCE_NOTE,
                "verification_scope": "corpus",
                "masked_post": masked_text,
                "pii_redacted_count": sum(pii_counts.values()),
                "neutral_summary": abstain_text,
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

        corpus_context = "\n".join(
            f"- {citation['official_doc_title']} ({citation['pasal']}): "
            f"{citation['quoted_text']}"
            for citation in citations
        )
        sys_prompt = (
            "Anda adalah penyusun Catatan Konteks Hukum Netral Pramana "
            "(Strict-RAG). Tulis ringkasan konteks hukum yang objektif, netral, "
            "tanpa menghakimi individu, dan tanpa emoji (maksimal 3 kalimat). "
            "Wajib merujuk secara akurat pada judul peraturan dan pasal yang "
            "diberikan. Jangan menambah fakta di luar teks."
        )
        user_prompt = (
            f"Teks Klaim/Postingan (Disamarkan PII): {masked_text}\n"
            f"Dasar Hukum Terverifikasi:\n{corpus_context}"
        )
        llm_summary, engine_label = self._call_gemini_strict(sys_prompt, user_prompt)

        if llm_summary:
            neutral_summary = llm_summary
            ai_synthesis_status = "llm"
        else:
            text = top_reg.get("text", "")
            excerpt = text[:240] + ("..." if len(text) > 240 else "")
            neutral_summary = (
                f"Berdasarkan {top_reg['doc_title']} "
                f"({top_reg.get('pasal', '')}), ketentuan yang relevan adalah: "
                f"{excerpt} Catatan ini tidak menyatakan individu bersalah."
            )
            ai_synthesis_status = "deterministic"

        return {
            "status": "TERVERIFIKASI",
            "guard_status": guard_status,
            "ai_engine": engine_label,
            "ai_synthesis_status": ai_synthesis_status,
            "confidence": confidence,
            "confidence_note": CONFIDENCE_NOTE,
            "verification_scope": "corpus",
            "masked_post": masked_text,
            "pii_redacted_count": sum(pii_counts.values()),
            "neutral_summary": neutral_summary,
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
