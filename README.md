# PRAMANA - Platform AI Strict-RAG Kepatuhan Hukum & Konteks Regulasi Pariwisata Bali

**Bali DigiFest 2026 - AI Web Innovation Challenge**  
*Build with AI, Solve for Bali*

---

## Description

**Pramana** adalah aplikasi web berbasis *Strict Retrieval-Augmented Generation (Strict-RAG)* yang dirancang untuk mencegah pelanggaran hukum/adat oleh wisatawan di Bali serta meredam disinformasi pada unggahan insiden viral melalui kutipan pasal resmi *verbatim* (tanpa halusinasi).

Pramana bekerja dalam dua mode terintegrasi:
1. **Mode 1: Trip Brief (Pencegahan Pra-Perjalanan)**: Menganalisis rencana rute perjalanan wisatawan, menyamarkan data pribadi (*PII Masking*), mendeteksi bentrok kalender Hari Suci Nyepi (*Catur Brata Penyepian*) maupun upacara Pawukon, serta menyusun ringkasan aturan mengikat lengkap dengan ekspor kalender `.ics` (RFC 5545) dan format pesan teks.
2. **Mode 2: Context Note (Verifikasi Klaim & Edukasi Publik)**: Menganalisis teks postingan viral atau klaim insiden, mendeteksi penanda bingkai emosional/generalisasi sensasional, dan menyajikan Catatan Konteks netral beserta kutipan *verbatim* dari JDIH Provinsi Bali dan Hukum Nasional. Jika klaim berada di luar cakupan hukum yang terverifikasi, sistem secara ketat menerapkan prinsip **Abstain (`TIDAK_DITEMUKAN`)**.

---

## Problem & Target User

### Masalah Utama
1. **Asimetri Informasi Regulasi & Adat:** Wisatawan mancanegara (WNA) maupun domestik sering melanggar aturan kawasan suci (Pura), kewajiban Pungutan Wisatawan Asing (Perda Bali No. 6 Tahun 2023), ketertiban lalu lintas, hingga pembatasan total 24 jam saat Hari Suci Nyepi karena informasi tersebar di berbagai dokumen birokrasi.
2. **Polarisasi & Informasi Keliru di Media Sosial:** Unggahan viral terkait insiden wisatawan di Bali kerap dibumbui generalisasi sensasional tanpa merujuk pada pasal hukum yang berlaku, sementara *chatbot* AI generatif biasa rentan mengarang nomor pasal (*halusinasi hukum*).

### Target Pengguna
- **Wisatawan Mancanegara & Nusantara:** Membutuhkan panduan kepatuhan hukum dan kalender adat yang akurat sebelum tiba di Bali.
- **Pelaku Akomodasi, Agen Perjalanan, & Concierge Hotel:** Membutuhkan alat pembuat *Trip Brief* cepat (teks dan kalender `.ics`) untuk tamu mereka.
- **Masyarakat Umum, Jurnalis, & Komunitas Digital Bali:** Membutuhkan alat verifikasi konteks hukum netral berbasis sumber resmi untuk merespons klaim viral.

---

## Key Features

### Core Features (Sudah Berfungsi Penuh pada MVP)
- **Dual-Mode Strict-RAG Engine:** Mendukung analisis rencana perjalanan (*Trip Brief*) dan verifikasi klaim insiden (*Context Note*).
- **Dual-Layer Hallucination Verifier:**
  - *Layer 1 (Deterministic Exact Match):* Memastikan setiap kutipan pasal cocok karakter-demi-karakter terhadap naskah korpus JDIH.
  - *Layer 2 (Abstain Guard):* Menolak berspekulasi (`TIDAK_DITEMUKAN`) apabila kueri berada di luar domain regulasi yang terdaftar.
- **Automated PII Masking (Pelindung Privasi):** Menyamarkan alamat email, nomor telepon, nomor paspor, kartu pembayaran, dan kode pemesanan (*booking code* / PNR) secara otomatis sebelum data dikirim ke model AI.
- **Deterministic Balinese Calendar Conflict Engine:** Mendeteksi bentrok tanggal perjalanan terhadap Hari Suci Nyepi (2025–2028), Malam Pengerupukan (Ogoh-ogoh), serta Hari Raya Galungan dan Kuningan.
- **Sensational Framing Detector:** Mendeteksi frasa generalisasi atau provokasi dalam teks klaim viral dan memisahkannya dari fakta hukum objektif.
- **Interactive Verbatim Statute Drawer & Export:** Panel pembaca naskah asli pasal secara penuh, fitur salin sekali klik, serta generator berkas kalender `.ics` sesuai standar RFC 5545.

---

## Tech Stack

- **Frontend:** Svelte 5 (Runes Reactivity), Vite 6, Tailwind CSS 3
- **Backend:** Python 3.11+, FastAPI, Pydantic v2, Uvicorn, HTTPX
- **Database / Storage:** Structured Legal Corpus JSON (`corpus/bali_regulations.json`) terindeks di memori dengan skema terverifikasi JDIH Provinsi Bali & Peraturan Nasional
- **AI / NLP Pipeline:** Google Gemini API (`gemini-2.5-flash` pada `temperature=0.1`) yang diikat secara ketat (*strictly grounded*) dengan *Dual-Layer Deterministic Verifier* dan *Regex PII Masking*
- **Testing:** Pytest & FastAPI TestClient (23 *automated test cases*)

---

## AI Implementation

Pramana mengimplementasikan arsitektur **Hybrid Strict-RAG + Dual-Layer Guard**:

1. **Input Sanitization (PII Masking):** Teks masukan pengguna diproses oleh modul `backend/services/ocr_masking.py` untuk menyamarkan 5 kategori data sensitif (`[EMAIL_DISAMARKAN]`, `[KODE_BOOKING_DISAMARKAN]`, `[PASPOR_DISAMARKAN]`, `[NOMOR_KARTU_DISAMARKAN]`, `[TELEPON_DISAMARKAN]`).
2. **Deterministic Legal Retrieval:** Modul `backend/services/corpus_loader.py` mengekstrak kandidat regulasi dari korpus resmi berdasarkan pembobotan kata kunci hukum, kategori, dan batang tubuh pasal dengan penyaringan *stopwords* bahasa Indonesia.
3. **Layer-2 Abstain Gate:** Modul `backend/services/verifier.py` memeriksa apakah terdapat dasar hukum yang melampaui ambang batas relevansi. Jika tidak ditemukan, alur dihentikan dan sistem mengembalikan status `TIDAK_DITEMUKAN` tanpa memanggil LLM (mencegah halusinasi).
4. **Constrained Gemini LLM Synthesis:** Teks yang telah disamarkan beserta potongan naskah pasal resmi dikirim ke Google Gemini API (`gemini-2.5-flash`, `temperature=0.1`) dengan instruksi sistem ketat untuk menyusun ringkasan eksekutif netral tanpa mengarang pasal di luar konteks. Apabila kunci API eksternal tidak tersedia atau terjadi gangguan jaringan, sistem memiliki *deterministic synthesis fallback* sehingga reliabilitas produk tetap 100%.
5. **Layer-1 Verbatim Verification:** Seluruh kutipan pasal yang ditampilkan pada antarmuka pengguna divalidasi secara deterministik (`verify_layer1_exact_match`) terhadap teks asli di korpus.

---

## Architecture / Data Flow

```text
User Input (Itinerary / Viral Claim)
       │
       ▼
[Frontend: Svelte 5 Web App]
       │  POST /api/v1/trip-brief  atau  POST /api/v1/context-note
       ▼
[1. PII Masking Service] ──► Menyamarkan Email, Telepon, Paspor, Kartu, Kode Booking
       │
       ├──► [2a. Balinese Calendar Engine] ──► Cek Bentrok Nyepi & Pawukon + Buat RFC 5545 (.ics)
       │
       ▼
[2b. Corpus Retriever] ────► Mengambil Pasal Relevan dari corpus/bali_regulations.json
       │
       ▼
[3. Layer-2 Abstain Guard] ► Jika 0 Pasal Cocok ──► Return Status: TIDAK_DITEMUKAN (Zero Hallucination)
       │
       ▼ (Jika Terbukti Ada Dasar Hukum)
[4. Gemini 2.5 Flash API] ─► Sintesis Ringkasan Kepatuhan / Catatan Konteks Netral (temp=0.1)
       │                     (Dilengkapi Deterministic Fallback jika API offline)
       ▼
[5. Layer-1 Exact Verifier]► Memvalidasi Kutipan Verbatim Karakter-per-Karakter
       │
       ▼
Structured JSON Response ──► Ditampilkan di UI + Drawer Naskah Asli + Ekspor .ics / Teks
```

---

## Installation / Run Instructions

### Prasyarat
- **Python** 3.11 atau lebih baru
- **Node.js** 18+ dan `npm`

### 1. Konfigurasi Environment
Salin berkas `.env.example` menjadi `.env` di direktori utama:
```bash
cp .env.example .env
```
*(Opsional)* Isi `GEMINI_API_KEY` pada `.env` untuk mengaktifkan sintesis melalui Google Gemini API. Sistem tetap dapat dijalankan penuh tanpa API key berkat *deterministic Strict-RAG fallback*.

### 2. Menjalankan Backend (FastAPI) & Pengujian Otomatis
```bash
# Aktifkan virtual environment (Windows PowerShell)
.\backend\venv\Scripts\Activate.ps1

# Atau instal dependensi jika belum terpasang
pip install -r backend/requirements.txt

# Jalankan seluruh test suite (23 pengujian unit & integrasi)
pytest -v

# Jalankan server API di port 8000
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Menjalankan Frontend (Svelte 5 + Vite)
Buka terminal baru dan jalankan:
```bash
cd frontend
npm install
npm run dev
```
Buka peramban di `http://localhost:5173`. Server Vite secara otomatis meneruskan permintaan `/api` ke `http://localhost:8000`.

---

## Deployment URL

- **Production / Demo URL:** `https://pramana.balidigifest.id` *(atau jalankan secara lokal melalui `http://localhost:5173`)*
- **API Healthcheck:** `/api/v1/health`
- **Interactive API Docs (Swagger UI):** `/docs`

---

## Demo Account

Aplikasi **tidak memerlukan login atau akun khusus**. Juri dapat langsung menguji seluruh fitur menggunakan tombol **Skenario Uji** yang tersedia di halaman utama maupun memasukkan teks rencana perjalanan / klaim baru secara bebas.

---

## Known Limitations

1. **Cakupan Korpus MVP:** Korpus saat ini memuat 6 instrumen hukum prioritas kepariwisataan dan ketertiban umum Bali (UU Keimigrasian No. 6/2011, Perda Bali No. 5/2020, Perda Bali No. 6/2023 jo. No. 2/2025, SE Gubernur Bali No. 4/2023 Do's & Don'ts, serta Seruan Bersama PHDI/MDA tentang Hari Suci Nyepi). Peraturan tingkat desa adat (*Awig-awig* / *Pararem* spesifik per desa) belum terindeks seluruhnya.
2. **Input Berbasis Teks:** Pada versi MVP ini, masukan berupa teks rencana perjalanan atau salinan keterangan unggahan (*caption*/transkrip), belum memproses berkas video mentah secara langsung.

---

## Third-party Resources / Credits

- **Sumber Data Regulasi (Domain Publik, Pasal 42 huruf b UU No. 28 Tahun 2014 tentang Hak Cipta):**
  - Jaringan Dokumentasi dan Informasi Hukum (JDIH) Provinsi Bali (`https://jdih.baliprov.go.id`)
  - Portal Peraturan Perundang-undangan Republik Indonesia (`https://peraturan.go.id`)
  - Parisada Hindu Dharma Indonesia (PHDI) Provinsi Bali (`https://phdi.or.id`)
- **Open-Source Libraries:** FastAPI, Pydantic, Uvicorn, HTTPX, Pytest, Svelte 5, Vite, Tailwind CSS.
- **Tipografi & Aset Visual:** Font `Inter` dan `JetBrains Mono` (Google Fonts, OFL); ilustrasi lanskap Candi Bentar Bali dibuat khusus untuk proyek Pramana.

---

## AI & Technology Disclosure (Lampiran C)

| Komponen | Isi Peserta |
| :--- | :--- |
| **Nama Produk** | Pramana |
| **Framework / Frontend** | Svelte 5, Vite 6, Tailwind CSS 3 |
| **Backend / Runtime** | Python 3.11+, FastAPI, Uvicorn |
| **Database / Storage** | Structured JSON Legal Corpus (`corpus/bali_regulations.json`) |
| **Hosting / Deployment** | Cloud / Containerized Web Service (Frontend + FastAPI Backend) |
| **AI Model / API / Method** | Google Gemini API (`gemini-2.5-flash`) + Deterministic Strict-RAG Retriever + Dual-Layer Verifier + Regex PII Masking |
| **Peran AI dalam Produk** | Menyusun ringkasan eksekutif kepatuhan perjalanan (Mode 1) dan catatan konteks hukum netral (Mode 2) yang diikat ketat pada pasal resmi yang ditemukan oleh mesin pencari deterministik. |
| **Dataset / Data Source** | Korpus kurasi peraturan resmi dari JDIH Provinsi Bali dan peraturan.go.id (Domain Publik). |
| **Open-source Libraries** | `fastapi`, `pydantic`, `uvicorn`, `httpx`, `python-dotenv`, `pytest`, `svelte`, `vite`, `tailwindcss`. |
| **Template / Boilerplate** | Dibangun dari awal (*custom architecture*) tanpa template komersial pihak ketiga. |
| **AI Coding Assistant** | Google Antigravity / Gemini digunakan sebagai asisten pengembangan kode, pembuatan aset ilustrasi header, dan penyusunan pengujian unit. Seluruh arsitektur, logika verifikasi, dan kode sumber telah diuji serta dapat dipertanggungjawabkan penuh oleh tim. |
| **Pre-existing Components** | Tidak ada (*100% dikembangkan khusus untuk Bali DigiFest 2026 AI Web Innovation Challenge*). |
| **Third-party Assets / Credits** | Google Fonts (`Inter`, `JetBrains Mono` (SIL Open Font License)). |

---

## Team Members

- **Tim Pengembang Pramana** (Kategori Mahasiswa / Umum) - Bali DigiFest 2026 AI Web Innovation Challenge.
