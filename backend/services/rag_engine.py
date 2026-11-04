"""
Strict-RAG Engine for Pramana.
Executes high-assurance, zero-hallucination retrieval for:
- Mode 1: Trip Brief (prevention before travel)
- Mode 2: Context Note (neutral post analysis with exact statutes)
"""

import os
from typing import Dict, Any, List, Optional
from backend.services.corpus_loader import CorpusManager
from backend.services.verifier import DualLayerVerifier
from backend.services.ocr_masking import mask_pii
from backend.services.calendar_service import check_holiday_conflicts, generate_ics_calendar


class StrictRAGEngine:
    def __init__(self):
        self.corpus_mgr = CorpusManager.get_instance()
        self.verifier = DualLayerVerifier(self.corpus_mgr)

    def analyze_trip_itinerary(
        self,
        itinerary_text: str,
        start_date: str,
        end_date: Optional[str] = None,
        traveler_origin: str = "international"
    ) -> Dict[str, Any]:
        """
        Mode 1: Generate comprehensive, verified Trip Brief.
        1. Mask PII from user itinerary.
        2. Check Balinese calendar for Nyepi / ceremony conflicts.
        3. Retrieve strictly applicable regulations.
        4. Generate WhatsApp-ready summary and ICS export.
        """
        masked_text, pii_counts = mask_pii(itinerary_text)

        # 1. Calendar conflict detection
        calendar_check = check_holiday_conflicts(start_date, end_date)

        # 2. Strict Retrieval
        matched_regs = self.corpus_mgr.search_regulations(itinerary_text, top_k=4)

        # Always include Tourist Levy for international tourists visiting Bali
        if traveler_origin.lower() in ["international", "wisman", "asing"]:
            levy_reg = self.corpus_mgr.get_by_id("PERDA_BALI_06_2023_LEVY")
            if levy_reg and levy_reg not in matched_regs:
                matched_regs.insert(0, levy_reg)

        # 3. Always check sacred places / attire rule if temple/pura/ubud mentioned
        if any(w in itinerary_text.lower() for w in ["pura", "temple", "ubud", "besakih", "uluwatu", "batur", "pantai", "beach"]):
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

        # Format WhatsApp text
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
            "masked_itinerary": masked_text,
            "pii_redacted_count": sum(pii_counts.values()),
            "start_date": start_date,
            "end_date": end_date or start_date,
            "calendar_conflicts": calendar_check,
            "briefing_items": briefing_items,
            "whatsapp_text": wa_text,
            "ics_content": ics_calendar,
            "disclaimer": "Pramana adalah sistem edukasi konteks aturan pariwisata berbasis Strict-RAG, bukan pemberi nasihat hukum resmi."
        }

    def analyze_viral_post(self, post_content: str) -> Dict[str, Any]:
        """
        Mode 2: Generate neutral, verifiable Context Note for viral tourism content.
        1. Mask PII from user post.
        2. Detect emotional framing markers (generalizations, unverified sensational claims).
        3. Retrieve exact applicable statutes from verified corpus.
        4. Abstain if no official statute covers the claimed incident.
        """
        masked_text, pii_counts = mask_pii(post_content)

        # Search corpus
        matched_regs = self.corpus_mgr.search_regulations(post_content, top_k=3)
        is_grounded, guard_status = self.verifier.enforce_layer2_guard(matched_regs)

        if not is_grounded:
            return {
                "status": "TIDAK_DITEMUKAN",
                "guard_status": "ABSTAIN",
                "confidence": "TIDAK_DITEMUKAN",
                "masked_post": masked_text,
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

        # Build citations
        citations = []
        for reg in matched_regs:
            citations.append({
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

        # Neutral summary construction
        top_reg = matched_regs[0]
        neutral_summary = (
            f"Berdasarkan {top_reg['doc_title']} ({top_reg.get('pasal', '')}), "
            f"aktivitas yang dibahas memiliki ketentuan hukum mengikat: {top_reg['text'][:200]}... "
            f"Penindakan administratif atau sanksi diatur secara proporsional sesuai ketentuan yang berlaku."
        )

        return {
            "status": "TERVERIFIKASI",
            "guard_status": guard_status,
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
            f"📅 Tanggal: {date_span}",
            ""
        ]

        if calendar_check.get("has_nyepi"):
            lines.append("⚠️ *PERINGATAN NYEPI (Catur Brata Penyepian)*")
            lines.append("Pada tanggal tersebut berlaku larangan keluar hotel, pemadaman lampu luar, penutupan bandara, dan pemadaman data seluler selama 24 jam.")
            lines.append("")

        lines.append("📋 *Aturan Utama yang Wajib Dipatuhi:*")
        for i, item in enumerate(briefing_items[:3], 1):
            lines.append(f"{i}. *{item['category']}* ({item['tier_label']})")
            lines.append(f"   {item['summary'][:120]}...")

        lines.append("")
        lines.append("🔗 Verifikasi naskah resmi: https://pramana.balidigifest.id")
        return "\n".join(lines)
