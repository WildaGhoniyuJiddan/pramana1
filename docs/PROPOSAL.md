# PROPOSAL SOLUSI & MVP AI WEB
## BALI DIGIFEST 2026 - AI WEB INNOVATION CHALLENGE

- **Nama Produk:** PRAMANA (Platform AI Strict-RAG Kepatuhan Hukum & Konteks Regulasi Pariwisata Bali)
- **Tema Ruang Lingkup:** Bali Smart Society (Pariwisata, Budaya, Layanan Publik, & Sistem Informasi Cerdas)
- **Kategori:** Mahasiswa / Umum

---

## 1. Problem & Background

Sebagai destinasi pariwisata utama dunia, Bali menghadapi tantangan krusial pada titik temu antara pertumbuhan kunjungan wisatawan, pelestarian kesucian budaya (*Sad Kerthi* / *Tri Hita Karana*), dan ketertiban hukum:

1. **Asimetri Informasi Regulasi & Kalender Adat:** Banyak pelanggaran yang dilakukan wisatawan (seperti memasuki area *Utama Mandala* Pura tanpa busana adat, memanjat pohon keramat, mengabaikan Pungutan Wisatawan Asing Rp150.000 (Perda Bali No. 6 Tahun 2023), hingga keluar penginapan saat Hari Suci Nyepi) terjadi akibat ketidaktahuan terhadap aturan spesifik daerah yang tersebar dalam dokumen hukum formal.
2. **Eskalasi Disinformasi & Polarisasi di Media Sosial:** Ketika insiden wisatawan menjadi viral, ruang diskusi publik sering dipenuhi generalisasi sensasional (*framing* emosional) tanpa rujukan pasal yang tepat.
3. **Risiko Halusinasi pada AI Generatif Konvensional:** Penggunaan *chatbot* LLM biasa untuk menanyakan aturan hukum lokal sangat berisiko karena LLM cenderung mengarang nomor pasal atau mencampuradukkan opini internet dengan produk hukum resmi.

---

## 2. Target User

1. **Wisatawan Mancanegara (WNA) & Nusantara (WNI):** Membutuhkan panduan pra-perjalanan yang jelas, terverifikasi, dan terintegrasi dengan kalender perangkat mereka sebelum tiba di Bali.
2. **Pelaku Industri Akomodasi (Hotel, Villa, Concierge, & Agen Perjalanan):** Membutuhkan alat otomatis untuk membuat ringkasan aturan lokal (*Trip Brief*) yang siap dikirimkan ke tamu tanpa melanggar privasi data pemesanan.
3. **Masyarakat Umum, Kreator Konten, & Jurnalis:** Membutuhkan alat pemeriksa fakta hukum (*Context Note*) untuk menyematkan kutipan pasal resmi yang netral pada diskusi publik.

---

## 3. Proposed Solution

**Pramana** menyelesaikan masalah di atas melalui platform web berbasis **Strict-RAG (Retrieval-Augmented Generation)** dengan jaminan **Nol Halusinasi Kutipan (*Zero Hallucination Guarantee*)** dalam dua alur pengguna utama:

- **User Journey 1: Mode Pencegahan (Trip Brief):** Pengguna memasukkan rencana rute atau catatan pemesanan beserta tanggal perjalanan $\rightarrow$ Sistem menyamarkan data pribadi (PII) secara otomatis $\rightarrow$ Sistem memeriksa bentrok tanggal dengan Hari Suci Nyepi (*Catur Brata Penyepian*) dan upacara Pawukon $\rightarrow$ Sistem mengekstrak pasal hukum yang relevan dan menyusun ringkasan eksekutif beserta tombol unduh kalender `.ics` dan salin teks.
- **User Journey 2: Mode Verifikasi (Context Note):** Pengguna menempelkan teks unggahan viral atau klaim insiden $\rightarrow$ Sistem mendeteksi frasa sensasional/generalisasi $\rightarrow$ Sistem mencari dasar hukum di korpus resmi JDIH Bali $\rightarrow$ Jika ditemukan, sistem menghasilkan Catatan Konteks netral dengan kutipan *verbatim*; jika klaim berada di luar cakupan hukum, sistem menolak berspekulasi (**Strict Abstain / `TIDAK_DITEMUKAN`**).

---

## 4. AI Implementation

- **Metode & Model AI:** Arsitektur hibrida yang menggabungkan **Google Gemini API (`gemini-2.5-flash`, `temperature=0.1`)**, **Deterministic Legal Retriever**, **Dual-Layer Verifier**, dan **Regex PII Masking**.
- **Input:**
  - *Mode 1:* Teks rencana perjalanan/booking, tanggal mulai & selesai, status wisatawan (WNA/WNI).
  - *Mode 2:* Teks klaim insiden atau keterangan unggahan media sosial.
- **Proses & Alasan AI Diperlukan:**
  1. *PII Masking (`ocr_masking.py`):* Menyamarkan email, telepon, paspor, kartu kredit, dan kode booking sebelum teks menyentuh model AI.
  2. *Retrieval & Layer-2 Abstain Guard (`corpus_loader.py` & `verifier.py`):* Menyeleksi pasal relevan dari korpus dan memblokir pemanggilan LLM jika tidak ada bukti hukum yang cukup.
  3. *Constrained LLM Synthesis (`rag_engine.py`):* Gemini 2.5 Flash menyusun sintesis ringkas yang mudah dipahami pengguna namun terikat ketat (*grounded*) hanya pada teks pasal yang lolos seleksi. Dilengkapi *deterministic fallback* agar sistem tetap berfungsi 100% apabila jaringan API eksternal terputus.
  4. *Layer-1 Verbatim Match (`verifier.py`):* Memvalidasi bahwa kutipan pasal yang ditampilkan sama persis karakter-demi-karakter dengan dokumen resmi JDIH.
- **Output:** Ringkasan kepatuhan rute, peringatan kalender Nyepi, pendeteksi *framing* emosional, kutipan pasal *verbatim*, komentar siap salin, dan berkas kalender `.ics`.

---

## 5. MVP & Key Features

### Fitur Inti (Sudah Berfungsi Penuh saat Submission)
1. **Mode 1: Trip Brief Generator** dengan deteksi otomatis kewajiban Pungutan Wisman (Love Bali) dan aturan kawasan suci.
2. **Mode 2: Viral Claim Context Note** dengan pendeteksi *framing* sensasional dan mekanisme *Zero-Hallucination Abstain*.
3. **Dual-Layer Verifier (Layer-1 Exact Match & Layer-2 Abstain Gate).**
4. **Automated PII Masking Engine** untuk 5 kategori data sensitif.
5. **Deterministic Balinese Calendar Engine** (Data resmi Nyepi 2025–2028, Pengerupukan, Galungan, Kuningan) + **RFC 5545 `.ics` Calendar Exporter**.
6. **Interactive Verbatim Statute Drawer & Transparency Modal** untuk menginspeksi teks penuh peraturan dan tautan asli JDIH.

---

## 6. Technical Architecture

```text
[User Browser]
      │
      ▼
[Frontend: Svelte 5 + Vite + Tailwind CSS]
      │  REST JSON API (/api/v1/trip-brief, /api/v1/context-note, /api/v1/corpus)
      ▼
[Backend: Python FastAPI Server]
      ├──► 1. PII Masking Service (ocr_masking.py)
      ├──► 2. Balinese Calendar Service (calendar_service.py -> Nyepi/Pawukon + .ics)
      ├──► 3. Legal Corpus Manager (corpus_loader.py -> corpus/bali_regulations.json)
      ├──► 4. Dual-Layer Verifier (verifier.py -> Layer-1 Exact Match & Layer-2 Abstain)
      └──► 5. Strict-RAG AI Engine (rag_engine.py -> Gemini 2.5 Flash API + Fallback)
      │
      ▼
[Verified Response -> UI Cards, Verbatim Statute Drawer, WhatsApp Copy, & .ics Download]
```

---

## 7. Innovation & Differentiation

| Aspek | Chatbot AI Umum / Pencarian Manual | PRAMANA (Strict-RAG) |
| :--- | :--- | :--- |
| **Akurasi Pasal Hukum** | Rentan mengarang nomor pasal (*halusinasi*). | **100% Verbatim** (diverifikasi karakter-per-karakter oleh *Layer-1 Verifier*). |
| **Klaim di Luar Aturan** | Tetap menjawab dengan spekulasi/opini. | **Strict Abstain (`TIDAK_DITEMUKAN`)** melalui *Layer-2 Guard*. |
| **Kalender Adat Bali** | Sering salah menghitung tanggal Nyepi/Saka. | **Deterministik** (mengunci jadwal Nyepi 2025–2028 & siklus Pawukon + ekspor `.ics`). |
| **Privasi Data (PII)** | Teks booking mentah langsung terkirim ke cloud. | **PII Masking Otomatis** sebelum diproses AI. |
| **Netralitas Konteks** | Mudah terbawa nada emosional prompt pengguna. | Mendeteksi *framing* sensasional dan memisahkan fakta hukum tanpa menghakimi individu. |

---

## 8. Impact & Development Potential

- **Manfaat Nyata bagi Bali:** Menurunkan insiden pelanggaran ketertiban umum dan kawasan suci melalui edukasi pra-perjalanan yang proaktif, mendukung kepatuhan pembayaran Pungutan Wisatawan Asing (Perda No. 6/2023), serta menyediakan rujukan hukum yang sejuk dan objektif di media sosial.
- **Potensi Pengembangan (Scalability):**
  - Integrasi langsung melalui API/Webhook dengan sistem pemesanan hotel (OTA) dan maskapai penerbangan.
  - Perluasan korpus mencakup *Awig-awig* dan *Pararem* spesifik per Desa Adat bekerja sama dengan Majelis Desa Adat (MDA) Provinsi Bali.
  - Dukungan multibahasa otomatis (Inggris, Mandarin, Rusia, Jepang) untuk rangkuman *Trip Brief* dengan tetap mempertahankan teks asli bahasa Indonesia sebagai rujukan hukum mengikat.
- **Keterbatasan MVP Saat Ini:** Korpus awal berfokus pada 6 regulasi tingkat nasional dan provinsi paling krusial bagi wisatawan; masukan saat ini berbasis teks.

---

## 9. Technology Disclosure

- **Frontend:** Svelte 5, Vite 6, Tailwind CSS 3
- **Backend:** Python 3.11+, FastAPI, Pydantic v2, Uvicorn, HTTPX
- **Database / Storage:** Structured JSON Legal Corpus (`corpus/bali_regulations.json`)
- **AI Model / Method:** Google Gemini API (`gemini-2.5-flash`) + Deterministic Strict-RAG + Dual-Layer Verifier + Regex PII Masking
- **Dataset:** Peraturan resmi dari JDIH Provinsi Bali (`jdih.baliprov.go.id`) dan `peraturan.go.id` (Domain Publik, Pasal 42 huruf b UU Hak Cipta No. 28/2014)
- **AI Coding Assistant:** Google Antigravity / Gemini digunakan sebagai asisten pengembangan kode dan pengujian; seluruh kode sumber dan arsitektur diuji serta dipertanggungjawabkan penuh oleh tim.

---

## 10. Submission Links

- **GitHub Repository:** *(Tautan repositori GitHub proyek Pramana)*
- **Deployment URL:** *(Tautan aplikasi web aktif)*
- **Demo Account:** Tidak memerlukan login (Seluruh fitur dapat langsung diuji oleh juri).
- **Release Tag:** `v1.0-submission`
