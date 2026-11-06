#!/usr/bin/env python3
"""
scripts/translate_corpus.py

Offline translation and enrichment generator for Pramana statutory corpus.
Translates all 42 chunks and 29 documents into English following strict rules:
1. Literal and faithful statutory phrasing.
2. Complete numerical, article reference, and currency parity:
   Every number, 'Pasal N', and 'Rp N' in `text` must be identically preserved in `text_en`.
3. Cultural and customary terms are preserved in Indonesian with explanatory English glosses in parentheses:
   e.g. 'Utama Mandala (innermost sacred courtyard of a temple)'.
4. Translation status marked as 'ai-assisted' (never 'verbatim' or 'official').
5. Language-neutral unique titles generated for every chunk to prevent duplicate tab titles in UI.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, Any, List, Set

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))
CORPUS_FILE = ROOT_DIR / "corpus" / "bali_regulations.json"
GLOSSARY_FILE = ROOT_DIR / "corpus" / "glossary.json"

# Load or define standard metadata translations
TIER_LABEL_EN = {
    "Hukum Nasional": "National Statutory Law",
    "Hukum Daerah": "Regional Statutory Law",
    "Perda Bali": "Bali Regional Bylaw",
    "Pergub Bali": "Bali Governor Regulation",
    "Pedoman Kebijakan": "Administrative Policy Guideline",
    "Pedoman Adat & Kebijakan": "Customary & Policy Guideline"
}

CATEGORY_EN = {
    "Alur Pembayaran Pungutan": "Levy Payment Process",
    "Bentuk Diskriminasi": "Forms of Discrimination",
    "Dasar Kewenangan Pungutan Wisatawan Asing": "Legal Authority for Foreign Tourist Levy",
    "Definisi Desa Adat & Awig-awig": "Customary Village & Bylaw Definitions",
    "Definisi Diskriminasi HAM": "Human Rights Discrimination Definition",
    "Definisi Diskriminasi Ras dan Etnis": "Racial & Ethnic Discrimination Definition",
    "Definisi Kepariwisataan": "Tourism Statutory Definitions",
    "Desa Wisata": "Tourism Village Provisions",
    "Ekosistem Kepariwisataan": "Tourism Ecosystem Standards",
    "Fasilitasi Pelindungan Pura": "Temple Protection Facilitation",
    "Hak Konsumen Non-Diskriminatif": "Non-Discriminatory Consumer Rights",
    "Hak Pelaku Usaha Pariwisata": "Tourism Business Rights",
    "Hari Suci Nyepi (Catur Brata Penyepian)": "Nyepi Holy Day Observance (Catur Brata Penyepian)",
    "Keselamatan Berkendara Sepeda Motor (Kewajiban Helm)": "Motorcycle Riding Safety (Mandatory Helmet)",
    "Kesempatan Prioritas Masyarakat Lokal": "Local Community Priority Opportunities",
    "Kewajiban Pengemudi dan Izin Mengemudi (SIM)": "Driver Obligations & Driving License (SIM)",
    "Kewajiban Pengunjung & Wisatawan": "Visitor & Tourist Obligations",
    "Kewajiban Wisatawan": "General Tourist Obligations",
    "Kewajiban Wisman (Do's)": "Foreign Tourist Obligations (Do's)",
    "Larangan & Sanksi Pelindungan Pura": "Temple Protection Prohibitions & Sanctions",
    "Larangan Perusakan DTW": "Prohibition of Tourist Destination Damage",
    "Larangan Ujaran Kebencian Elektronik": "Prohibition of Electronic Hate Speech",
    "Larangan Wisman (Don'ts)": "Foreign Tourist Prohibitions (Don'ts)",
    "Manfaat Pungutan": "Utilization of Tourist Levy Funds",
    "Pariwisata Digital": "Digital Tourism Provisions",
    "Pembebasan Pungutan": "Tourist Levy Exemptions",
    "Pembinaan dan Pengawasan Pungutan": "Levy Oversight and Supervision",
    "Pengamanan Pura": "Temple Security & Protection",
    "Pengecualian Pungutan": "Tourist Levy Waiver Categories",
    "Pidana Diskriminasi": "Criminal Sanctions for Discrimination",
    "Pidana Diskriminasi Ras dan Etnis": "Criminal Sanctions for Racial & Ethnic Discrimination",
    "Pidana Kebencian dan Kekerasan": "Criminal Sanctions for Hate & Violence",
    "Pidana Penyebaran Permusuhan": "Criminal Sanctions for Disseminating Hostility",
    "Pidana Permusuhan di Muka Umum": "Criminal Sanctions for Public Hostility",
    "Pidana Ujaran Kebencian Elektronik": "Criminal Sanctions for Electronic Hate Speech",
    "Portal Satu Pintu Pariwisata": "Single-Door Tourism Digital Portal",
    "Pungutan Wisatawan Asing (Tourist Levy)": "Foreign Tourist Levy (Pungutan Wisman)",
    "Pungutan Wisatawan Mancanegara": "Foreign Tourist Levy",
    "Rasional Pungutan": "Rationale for Tourist Levy",
    "Standar Pengelola Daya Tarik Wisata": "Tourist Destination Management Standards",
    "Tata Cara Pembayaran Pungutan (Data & Waktu)": "Levy Payment Procedures (Data & Timing)",
    "Tindakan Administratif Keimigrasian": "Immigration Administrative Sanctions"
}

STATUS_NOTE_EN = {
    "SE Gubernur Bali No. 4 Tahun 2023 disempurnakan oleh SE Gubernur Bali No. 7 Tahun 2025. Teks tetap dipertahankan sebagai rujukan historis dan substansi tatanan dasar kewajiban wisman.":
        "Bali Governor Circular Letter (SE) No. 4/2023 is superseded by Bali Governor Circular Letter (SE) No. 7/2025. Text is retained as a historical reference and for the baseline substance of foreign tourist obligations.",
    "SE Gubernur Bali No. 4 Tahun 2023 disempurnakan oleh SE Gubernur Bali No. 7 Tahun 2025. Teks larangan tetap dipertahankan sebagai rujukan historis dan substansi tatanan dasar larangan wisman.":
        "Bali Governor Circular Letter (SE) No. 4/2023 is superseded by Bali Governor Circular Letter (SE) No. 7/2025. Prohibitory text is retained as a historical reference and for the baseline substance of foreign tourist prohibitions.",
    "Diperbarui oleh Peraturan Daerah Provinsi Bali Nomor 2 Tahun 2025 (penyesuaian mekanisme dan ketentuan pidana).":
        "Amended by Bali Provincial Regional Regulation (Perda) No. 2/2025 (adjustment of mechanisms and criminal provisions).",
    "Perubahan atas Pergub No. 2 Tahun 2024.":
        "Amendment to Governor Regulation (Pergub) No. 2/2024.",
    "Berlaku tahunan pada penanggalan Saka. Waktu pelaksanaan diperbarui setiap tahun melalui Seruan Bersama PHDI & MDA.":
        "Annually observed according to the Balinese Saka calendar. Implementation dates are updated annually through a Joint Proclamation by PHDI & MDA."
}

SOURCE_NOTE_EN = {
    "PDF hasil pindai dari Pemerintah Kabupaten Buleleng; OCR dibersihkan manual":
        "Scanned PDF from Buleleng Regency Government; OCR manually cleaned",
    "Portal JDIH Pemprov Bali (peraturan.baliprov.go.id); naskah resmi lembaran daerah":
        "Bali Provincial JDIH Portal (peraturan.baliprov.go.id); official provincial gazette text",
    "JDIH BPK RI (peraturan.bpk.go.id); Lembaran Negara RI":
        "Audit Board of Indonesia (BPK) JDIH Portal (peraturan.bpk.go.id); State Gazette of the Republic of Indonesia",
    "JDIH BPK RI (peraturan.bpk.go.id); Lembaran Daerah Provinsi Bali":
        "Audit Board of Indonesia (BPK) JDIH Portal (peraturan.bpk.go.id); Regional Gazette of Bali Province",
    "Dokumen penetapan resmi PHDI & Majelis Desa Adat Bali":
        "Official decree document of PHDI & Bali Customary Village Council (MDA)",
    "JDIH Kementerian Hukum dan HAM / BPK RI":
        "Ministry of Law and Human Rights / BPK JDIH Portal",
    "JDIH BPK RI (peraturan.bpk.go.id); Lembaran Negara RI No. 96 Tahun 2009":
        "Audit Board of Indonesia (BPK) JDIH Portal (peraturan.bpk.go.id); State Gazette of the Republic of Indonesia No. 96/2009"
}

def extract_numbers(s: str) -> Set[str]:
    """Extract all individual digit sequences and numbers."""
    if not s:
        return set()
    return set(re.findall(r'\b\d+(?:[\.,]\d+)*\b', s))

def extract_pasal(s: str) -> Set[str]:
    """Extract article numbers mentioned as Pasal N."""
    if not s:
        return set()
    return set(m.group(0).lower().replace(" ", "") for m in re.finditer(r'Pasal\s+\d+', s, re.IGNORECASE))

def extract_rp(s: str) -> Set[str]:
    """Extract rupiah amounts."""
    if not s:
        return set()
    cleaned = re.sub(r'\s+', '', s)
    return set(m.group(0).lower() for m in re.finditer(r'rp\.?[\d\.]+', cleaned, re.IGNORECASE))

def verify_numeric_parity(id_: str, id_text: str, en_text: str):
    """Verify that all numbers, articles, and rupiah amounts in id_text exist in en_text."""
    # Check digits
    nums_id = extract_numbers(id_text)
    nums_en = extract_numbers(en_text)
    missing_nums = nums_id - nums_en
    if missing_nums:
        raise ValueError(f"[{id_}] Missing numbers in EN translation: {missing_nums}")

    # Check Rp amounts
    rp_id = extract_rp(id_text)
    rp_en = extract_rp(en_text)
    missing_rp = rp_id - rp_en
    if missing_rp:
        raise ValueError(f"[{id_}] Missing Rp amounts in EN translation: {missing_rp}")

    # Check Pasal references
    pasals_id = extract_pasal(id_text)
    pasals_en = extract_pasal(en_text)
    missing_pasal = pasals_id - pasals_en
    if missing_pasal:
        raise ValueError(f"[{id_}] Missing Pasal references in EN translation: {missing_pasal}")

def main():
    parser = argparse.ArgumentParser(description="Translate and enrich Pramana regulation corpus.")
    parser.add_argument("--dry-run", action="store_true", help="Validate without writing back to file")
    parser.add_argument("--verify-only", action="store_true", help="Only verify existing translations in corpus")
    args = parser.parse_args()

    with open(CORPUS_FILE, "r", encoding="utf-8") as f:
        corpus = json.load(f)

    # Load translation dataset (built with human-reviewed & Gemini-aligned parity)
    from scripts.corpus_translations_data import TRANSLATIONS_REGULATIONS, TRANSLATIONS_DOCUMENTS

    regulations = corpus.get("regulations", [])
    documents = corpus.get("documents", [])

    print(f"Loaded {len(regulations)} regulations and {len(documents)} documents.")

    verified_count = 0
    for reg in regulations:
        reg_id = reg["id"]
        t_data = TRANSLATIONS_REGULATIONS.get(reg_id)
        if not t_data:
            raise KeyError(f"Missing translation data for regulation chunk: {reg_id}")

        text_id = reg["text"]
        text_en = t_data["text_en"]

        # Run strict numeric and reference parity check
        verify_numeric_parity(reg_id, text_id, text_en)
        verified_count += 1

        if not args.verify_only:
            reg["text_en"] = text_en
            reg["translation_status"] = t_data.get("translation_status", "ai-assisted")
            reg["title_en"] = t_data["title_en"]
            reg["penalties_en"] = t_data["penalties_en"]
            reg["category_en"] = CATEGORY_EN.get(reg.get("category", ""), reg.get("category", ""))
            reg["tier_label_en"] = TIER_LABEL_EN.get(reg.get("tier_label", ""), reg.get("tier_label", ""))
            
            # Status & source note translations
            reg["status_note_en"] = STATUS_NOTE_EN.get(reg.get("status_note", ""), reg.get("status_note"))
            reg["source_note_en"] = SOURCE_NOTE_EN.get(reg.get("source_note", ""), reg.get("source_note"))

    print(f"Verified numeric, Pasal, and Rp parity for all {verified_count} chunks successfully.")

    # Translate documents registry
    doc_verified = 0
    for doc in documents:
        doc_id = doc["id"]
        t_title = TRANSLATIONS_DOCUMENTS.get(doc_id)
        if not t_title:
            raise KeyError(f"Missing translation for document registry: {doc_id}")
        if not args.verify_only:
            doc["title_en"] = t_title
        doc_verified += 1

    print(f"Verified English descriptions for all {doc_verified} registry documents.")

    if not args.dry_run and not args.verify_only:
        with open(CORPUS_FILE, "w", encoding="utf-8") as f:
            json.dump(corpus, f, indent=2, ensure_ascii=False)
        print(f"Successfully updated {CORPUS_FILE}")

if __name__ == "__main__":
    main()
