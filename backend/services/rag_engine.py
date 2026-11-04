"""
Strict-RAG Engine for Pramana.
Executes high-assurance, zero-hallucination retrieval and Gemini LLM synthesis for:
- Mode 1: Trip Brief (prevention before travel)
- Mode 2: Context Note (neutral post analysis with exact statutes)
"""

import os
import json
from typing import Dict, Any, List, Optional, Tuple
import httpx
from dotenv import load_dotenv
from backend.services.corpus_loader import CorpusManager
from backend.services.verifier import DualLayerVerifier
from backend.services.ocr_masking import mask_pii
from backend.services.calendar_service import check_holiday_conflicts, generate_ics_calendar

load_dotenv()

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"


class StrictRAGEngine:
    def __init__(self):
        self.corpus_mgr = CorpusManager.get_instance()
        self.verifier = DualLayerVerifier(self.corpus_mgr)

    def _call_gemini_strict(self, system_instruction: str, user_prompt: str) -> Tuple[Optional[str], str]:
        """
        Calls Gemini REST API with strict grounding constraints (temperature 0.1).
        Only receives PII-masked inputs and retrieved official statute chunks.
        Gracefully falls back to deterministic synthesis if API key is missing or network fails.
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
            }
        }

        try:
            with httpx.Client(timeout=8.0) as client:
                resp = client.post(
                    f"{GEMINI_API_URL}?key={api_key}",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                if resp.status_code == 200:
                    data = resp.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts and "text" in parts[0]:
                            return parts[0]["text"].strip(), f"{GEMINI_MODEL} + dual-layer-verifier"
                return None, "deterministic-strict-rag (api fallback)"
        except Exception:
            return None, "deterministic-strict-rag (error fallback)"

    def analyze_trip_itinerary(
        self,
        itinerary_text: str,
        start_date: str,
        end_date: Optional[str] = None,
        traveler_origin: str = "international"
    ) -> Dict[str, Any]:
        """
        Mode 1: Generate comprehensive, verified Trip Brief.
        1. Mask PII from user itinerary before any downstream processing or AI call.
        2. Check Balinese calendar for Nyepi / ceremony conflicts.
        3. Retrieve strictly applicable regulations.
        4. Call Gemini LLM (strictly grounded on retrieved articles) or deterministic synthesizer.
        5. Generate WhatsApp-ready summary and ICS export.
        """
        masked_text, pii_counts = mask_pii(itinerary_text)

        # 1. Calendar conflict detection
        calendar_check = check_holiday_conflicts(start_date, end_date)

        # 2. Strict Retrieval (using masked text for privacy)
        matched_regs = self.corpus_mgr.search_regulations(masked_text, top_k=4)

        # Always include Tourist Levy for international tourists visiting Bali
        if traveler_origin.lower() in ["international", "wisman", "asing"]:
            levy_reg = self.corpus_mgr.get_by_id("PERDA_BALI_06_2023_LEVY")
            if levy_reg and levy_reg not in matched_regs:
                matched_regs.insert(0, levy_reg)

        # 3. Always check sacred places / attire rule if temple/pura/ubud mentioned
        if any(w in masked_text.lower() for w in ["pura", "temple", "ubud", "besakih", "uluwatu", "batur", "pantai", "beach"]):
            do_reg = self.corpus_mgr.get_by_id("SE_GUB_04_2023_DO")
            dont_reg = self.corpus_mgr.get_by_id("SE_GUB_04_2023_DONT")
            if do_reg and do_reg not in matched_regs:
                matched_regs.append(do_reg)
            if dont_reg and dont_reg not in matched_regs:
                matched_regs.append(dont_reg)

        # 4. Enforce Layer 2 Guard
        is_grounded, guard_status = self.verifier.enforce_layer2_guard(matched_regs)

        # Format items into structured briefing points
        briefing_items = []
        for reg in matched_regs:
            briefing_items.append({
                "id": reg["id"],
                "title": reg["doc_title"],
                "tier": reg["tier"],
                "tier_label": reg.get("tier_label", f"Tingkat {reg['tier']}"),
                "category": reg.get("category", "Regulasi"),
                "pasal": reg.get("pasal", ""),
                "summary": reg["text"][:280] + ("..." if len(reg["text"]) > 280 else ""),
                "full_text": reg["text"],
                "penalties": reg.get("penalties", "Sanksi administratif dan adat setempat."),
                "source_url": reg["source_url"]
            })

        # 5. Synthesize executive brief via Gemini (grounded strictly on retrieved corpus + calendar)
        corpus_context = "\n".join(
            f"- [{r['id']}] {r['doc_title']} ({r.get('pasal', '')}): {r['text']}"
            for r in matched_regs
        )
        sys_prompt = (
            "Anda adalah mesin kepatuhan hukum Strict-RAG Pramana. "
            "Tugas Anda menyusun ringkasan eksekutif perjalanan (2-3 kalimat padat, bahasa Indonesia formal, tanpa emoji) "
            "HANYA berdasarkan regulasi terlampir dan status kalender Bali. Dilarang mengarang pasal di luar daftar."
        )
        user_prompt = (
            f"Rencana Perjalanan (Disamarkan PII): {masked_text}\n"
            f"Tanggal: {start_date} s/d {end_date or start_date} | Status Wisman: {traveler_origin}\n"
            f"Bentrok Nyepi: {calendar_check.get('has_nyepi', False)}\n"
            f"Regulasi Resmi Terkait:\n{corpus_context}"
        )
        llm_summary, engine_label = self._call_gemini_strict(sys_prompt, user_prompt)

        if not llm_summary:
            nyepi_note = (
                "Perjalanan bersinggungan langsung dengan Hari Suci Nyepi (penghentian aktivitas 24 jam penuh). "
                if calendar_check.get("has_nyepi") else ""
            )
            reg_titles = ", ".join(r["category"] for r in briefing_items[:3])
            llm_summary = (
                f"{nyepi_note}Berdasarkan analisis rute terhadap korpus JDIH Provinsi Bali, "
                f"ditemukan {len(briefing_items)} instrumen regulasi wajib terkait: {reg_titles}."
            )

        # Format WhatsApp text (Zero emojis)
        wa_text = self._build_whatsapp_text(masked_text, start_date, end_date, calendar_check, briefing_items)

        # Generate ICS Calendar
        ics_calendar = generate_ics_calendar(
            title="Pramana: Bali Travel Brief & Rules",
            description=f"Aturan perjalanan Bali terverifikasi. Nyepi: {calendar_check.get('has_nyepi', False)}. Cek detail di Pramana.",
            start_date_str=start_date,
            end_date_str=end_date or start_date
        )

        return {
            "status": "SUCCESS" if is_grounded else "TIDAK_DITEMUKAN",
            "guard_status": guard_status,
            "ai_engine": engine_label,
            "masked_itinerary": masked_text,
            "pii_redacted_count": sum(pii_counts.values()),
            "start_date": start_date,
            "end_date": end_date or start_date,
            "calendar_conflicts": calendar_check,
            "briefing_items": briefing_items,
            "ai_synthesis": llm_summary,
            "whatsapp_text": wa_text,
            "ics_content": ics_calendar,
            "disclaimer": "Pramana adalah sistem edukasi konteks aturan pariwisata berbasis Strict-RAG, bukan pemberi nasihat hukum resmi."
        }

    def analyze_viral_post(self, post_content: str) -> Dict[str, Any]:
        """
        Mode 2: Generate neutral, verifiable Context Note for viral tourism content.
        1. Mask PII from user post before any processing or LLM call.
        2. Detect emotional framing markers (generalizations, unverified sensational claims).
        3. Retrieve exact applicable statutes from verified corpus.
        4. Abstain if no official statute covers the claimed incident.
        5. Generate neutral context note via Gemini LLM + Layer 1 verbatim citation verification.
        """
        masked_text, pii_counts = mask_pii(post_content)

        # Search corpus using masked text
        matched_regs = self.corpus_mgr.search_regulations(masked_text, top_k=3)
        is_grounded, guard_status = self.verifier.enforce_layer2_guard(matched_regs)

        if not is_grounded:
            return {
                "status": "TIDAK_DITEMUKAN",
                "guard_status": "ABSTAIN",
                "ai_engine": "dual-layer-guard (abstain)",
                "confidence": "TIDAK_DITEMUKAN",
                "masked_post": masked_text,
                "pii_redacted_count": sum(pii_counts.values()),
                "neutral_summary": "Tidak ditemukan regulasi atau norma hukum di korpus resmi Bali yang mengatur atau mengonfirmasi klaim ini.",
                "framing_markers": [],
                "citations": [],
                "disclaimer": "Sistem Pramana menerapkan Strict-RAG: menolak berspekulasi jika dasar hukum resmi tidak ditemukan."
            }

        # Detect sensational framing phrases
        framing_markers = []
        sensational_phrases = [
            ("semua bule", "Generalisasi wisatawan"),
            ("kebal hukum", "Asumsi tanpa rujukan status penegakan hukum"),
            ("polisi diam saja", "Klaim sensasional tanpa verifikasi otoritas"),
            ("adat barbar", "Pelanggaran etika dan penghinaan budaya"),
            ("deportasi sekarang juga", "Tuntutan sepihak di luar wewenang Imigrasi")
        ]
        for phrase, reason in sensational_phrases:
            if phrase in post_content.lower():
                framing_markers.append({
                    "phrase": phrase,
                    "reason": reason
                })

        # Build & Layer-1 verify citations
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
                "source_url": reg["source_url"],
                "verified_layer1": True
            })
        citations = self.verifier.verify_and_filter_citations(raw_citations)

        # Neutral summary synthesis (Gemini LLM strictly grounded on verified citations, with deterministic fallback)
        top_reg = matched_regs[0]
        corpus_context = "\n".join(
            f"- {c['official_doc_title']} ({c['pasal']}): {c['quoted_text']}"
            for c in citations
        )
        sys_prompt = (
            "Anda adalah penyusun Catatan Konteks Hukum Netral Pramana (Strict-RAG). "
            "Tulis ringkasan konteks hukum yang objektif, netral, tanpa menghakimi individu, dan tanpa emoji (maksimal 3 kalimat). "
            "Wajib merujuk secara akurat pada judul peraturan dan pasal yang diberikan."
        )
        user_prompt = (
            f"Teks Klaim/Postingan (Disamarkan PII): {masked_text}\n"
            f"Dasar Hukum Terverifikasi:\n{corpus_context}"
        )
        llm_summary, engine_label = self._call_gemini_strict(sys_prompt, user_prompt)

        neutral_summary = llm_summary or (
            f"Berdasarkan {top_reg['doc_title']} ({top_reg.get('pasal', '')}), "
            f"aktivitas yang dibahas memiliki ketentuan hukum mengikat: {top_reg['text'][:200]}... "
            f"Penindakan administratif atau sanksi diatur secara proporsional sesuai ketentuan yang berlaku."
        )

        return {
            "status": "TERVERIFIKASI",
            "guard_status": guard_status,
            "ai_engine": engine_label,
            "confidence": "TINGGI",
            "masked_post": masked_text,
            "pii_redacted_count": sum(pii_counts.values()),
            "neutral_summary": neutral_summary,
            "framing_markers": framing_markers,
            "citations": citations,
            "copyable_comment": f"Catatan Konteks Resmi (Pramana):\n{neutral_summary}\nRujukan: {top_reg['doc_title']}\nSelengkapnya: {top_reg['source_url']}",
            "disclaimer": "Catatan Konteks Pramana disusun secara netral berbasis dokumen hukum resmi tanpa menyatakan individu bersalah."
        }

    def _build_whatsapp_text(
        self,
        itinerary: str,
        start_date: str,
        end_date: Optional[str],
        calendar_check: Dict[str, Any],
        briefing_items: List[Dict[str, Any]]
    ) -> str:
        date_span = f"{start_date}" + (f" s/d {end_date}" if end_date and end_date != start_date else "")
        lines = [
            f"*PRAMANA — Bali Trip Brief & Local Rules*",
            f"Tanggal: {date_span}",
            ""
        ]

        if calendar_check.get("has_nyepi"):
            lines.append("*PERINGATAN NYEPI (Catur Brata Penyepian)*")
            lines.append("Pada tanggal tersebut berlaku larangan keluar hotel, pemadaman lampu luar, penutupan bandara, dan pemadaman data seluler selama 24 jam.")
            lines.append("")

        lines.append("*Aturan Utama yang Wajib Dipatuhi:*")
        for i, item in enumerate(briefing_items[:3], 1):
            lines.append(f"{i}. *{item['category']}* ({item['tier_label']})")
            lines.append(f"   {item['summary'][:120]}...")

        lines.append("")
        lines.append("Verifikasi naskah resmi: https://pramana.balidigifest.id")
        return "\n".join(lines)
