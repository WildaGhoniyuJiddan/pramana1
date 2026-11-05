# PRAMANA

**Platform edukasi konteks regulasi pariwisata Bali berbasis Strict-RAG**

Bali DigiFest 2026 — AI Web Innovation Challenge

> **Status: prototipe.** Pramana bukan nasihat hukum resmi. Kutipan diverifikasi terhadap **korpus lokal Pramana**, bukan diverifikasi ulang secara real-time ke JDIH. Selalu periksa naskah resmi pada tautan sumber.

---

## Status Implementasi

| Bagian | Status | Catatan |
| :--- | :--- | :--- |
| Retrieval deterministik + abstain (Layer-2) | ✅ Live | Ambang relevansi normalisasi `0.5` + pemotongan relatif `0.75` dari skor teratas |
| PII masking (5 kategori) | ✅ Live | Email, telepon, kode booking, kartu, paspor. Bersifat best-effort, bukan DLP penuh |
| Kalender Nyepi & Pawukon | ✅ Live | Cakupan deterministik 2025–2028, jendela Nyepi 24 jam |
| Ekspor `.ics` (RFC 5545) | ✅ Live | Escaping teks, line folding, UID stabil, validasi tanggal |
| Mode 1 — Trip Brief | 🟡 Prototype | Retrieval, kalender, PII, ICS, teks WhatsApp; ringkasan AI opsional |
| Mode 2 — Context Note | 🟡 Prototype | Sitasi korpus, deteksi framing, abstain; ringkasan AI opsional |
| Corpus Explorer | 🟡 Prototype | Menampilkan provenance, status entri, dan keterbatasan korpus |
| Sintesis Gemini | 🟡 Prototype | Butuh `GEMINI_API_KEY`; test otomatis memakai fallback deterministik |
| Verifikasi silang JDIH real-time | ⚪ Planned | Belum diimplementasikan |
| Benchmark publik | ⚪ Planned | Belum ada angka akurasi/halusinasi yang diukur |
| Antarmuka bilingual ID/EN | ⚪ Planned | Belum diimplementasikan |

---

## Deskripsi

Pramana membantu dua kelompok masalah:

1. **Wisatawan** yang perlu memahami aturan kawasan suci, pungutan wisatawan asing, lalu lintas, dan penutupan Nyepi sebelum berangkat.
2. **Masyarakat, jurnalis, dan pengelola akomodasi** yang perlu merespons klaim viral tentang insiden wisata dengan konteks hukum yang dapat ditelusuri, bukan spekulasi.

Aplikasi ini tidak menjawab pertanyaan hukum bebas. Ia mengambil kecocokan dari korpus regulasi terbatas, menampilkan sumber, dan memilih **abstain** (`TIDAK_DITEMUKAN`) ketika tidak ada kecocokan yang melewati ambang relevansi.

### Mode 1 — Trip Brief

- Menyamarkan PII dari teks rencana perjalanan.
- Mendeteksi bentrok dengan Nyepi 24 jam, Malam Pengerupukan, Galungan, dan Kuningan.
- Mengambil entri korpus yang relevan dan menerapkan Layer-2 guard.
- Menambahkan entri pungutan untuk wisatawan internasional **setelah** grounding berhasil.
- Menghasilkan teks WhatsApp dan berkas kalender `.ics` (tersedia juga saat abstain).

### Mode 2 — Context Note

- Menyamarkan PII dari teks postingan/klaim.
- Mendeteksi frasa framing sensasional (generalisasi, tuduhan tanpa dasar, dan sejenisnya).
- Mengambil entri korpus yang relevan, lalu memverifikasi kutipan terhadap teks korpus (Layer-1).
- Menghasilkan catatan konteks netral dan komentar yang dapat disalin, atau abstain.

---

## Apa Arti “Verifikasi” di Pramana

Pramana sengaja membedakan beberapa tingkat klaim:

| Istilah | Arti sebenarnya |
| :--- | :--- |
| **Layer-1 exact match** | Kutipan ada di dalam teks entri korpus lokal setelah normalisasi spasi. Ini bukan verifikasi independen ke JDIH. |
| **Layer-2 guard** | Tidak ada hasil retrieval yang melewati ambang skor, sehingga sistem abstain sebelum memanggil LLM. |
| **`is_verbatim: true`** | Entri korpus disimpan sebagai kutipan teks, bukan ringkasan. |
| **`is_verbatim: false`** | Entri adalah ringkasan/kompilasi. UI tidak menampilkannya sebagai bunyi pasal verbatim. |
| **`confidence`** | Dihitung dari skor kecocokan kata kunci. Nilai tertinggi yang diberikan adalah `SEDANG`; sistem tidak mengklaim `TINGGI`. |
| **`ai_synthesis_status: llm`** | Ringkasan disusun LLM dan **tidak** diverifikasi Layer-1. Hanya kutipan pasal yang diverifikasi terhadap korpus. |

Skor retrieval:

```text
skor = bobot_terbaik × (0.6 + 0.4 × cakupan_kueri)
bobot: kata kunci resmi = 1.0, judul = 0.85, kategori = 0.7, teks = 0.55
ambang minimum = 0.5
pemotongan relatif = 0.75 × skor teratas
```

Pemotongan relatif mencegah entri lemah ikut tersitasi hanya karena berbagi satu kata umum.

---

## Korpus dan Kalender

### Korpus regulasi (`corpus/bali_regulations.json` v1.1.0)

Enam entri, diverifikasi terakhir **5 November 2026**:

1. SE Gubernur Bali No. 4 Tahun 2023 — kewajiban wisatawan mancanegara (`is_verbatim: true`).
2. SE Gubernur Bali No. 4 Tahun 2023 — larangan wisatawan mancanegara (`is_verbatim: true`).
3. Perda Bali No. 5 Tahun 2020 Pasal 15 — kewajiban pengunjung (`is_verbatim: true`).
4. Perda Bali No. 6 Tahun 2023 jo. No. 2 Tahun 2025 — pungutan wisatawan asing (`is_verbatim: false`, ringkasan terstruktur).
5. UU No. 6 Tahun 2011 Pasal 75 — tindakan administratif keimigrasian (`is_verbatim: true`).
6. Ketentuan Hari Suci Nyepi — kompilasi pedoman tahunan (`is_verbatim: false`).

Catatan penting:

- **SE Gubernur Bali No. 4 Tahun 2023 telah disempurnakan oleh SE No. 7 Tahun 2025.** Teks lama tetap disimpan sebagai rujukan historis, dengan `status: "Disempurnakan"`, `superseded_by`, dan catatan di UI. Salinan lengkap SE 7/2025 belum dimasukkan sebagai entri terpisah.
- Entri pungutan adalah **parafrase**, bukan salinan Pasal 4–5 Perda 6/2023. Jangan mengutipnya sebagai bunyi pasal.
- Entri Nyepi adalah **kompilasi**, bukan satu pasal peraturan.
- Korpus belum memuat awig-awig/pararem desa adat secara menyeluruh.

Setiap entri mencantumkan `source_url`, `last_verified_date`, `status`, `status_note`, `is_verbatim`, dan bila relevan `superseded_by_url` serta `source_note`. `metadata.known_gaps` merangkum keterbatasan yang diketahui.

### Kalender deterministik

- Cakupan: **2025–2028**.
- Nyepi: 2025-03-29, 2026-03-19, 2027-03-08, 2028-03-26.
- Jendela Nyepi dihitung **24 jam**, dari pukul 06.00 WITA sampai 06.00 WITA keesokan harinya. Perjalanan yang hanya menyentuh pagi setelah tanggal Nyepi tetap ditandai sebagai `PARTIAL`.
- Galungan/Kuningan 2026: **17 Juni** dan **27 Juni**.
- Di luar 2025–2028, sistem mengembalikan `coverage_warning` dan tidak mengklaim bebas konflik.

---

## Tech Stack

- **Frontend:** Svelte 5 (runes), Vite 5.4.x, Tailwind CSS 3.
- **Backend:** Python 3.11+ (diuji pada 3.12.10), FastAPI, Pydantic v2, Uvicorn, HTTPX.
- **Penyimpanan:** JSON korpus terstruktur di memori; tidak ada database.
- **AI opsional:** Google Gemini API (`gemini-2.5-flash`, `temperature=0.1`). Tanpa API key, sistem memakai ringkasan deterministik.
- **Testing:** Pytest + FastAPI TestClient.

---

## Arsitektur

```text
Input (itinerary / klaim viral)
        │
        ▼
[1] PII masking (regex, 5 kategori)
        │
        ├──► [2a] Kalender Bali: Nyepi 24 jam, Pengerupukan, Pawukon
        │
        ▼
[2b] Retrieval kata kunci berbobot + skor normalisasi
        │
        ▼
[3] Layer-2 guard: skor ≥ 0.5 dan ≥ 0.75 × skor teratas?
        │
        ├── TIDAK ──► Abstain deterministik (tanpa LLM) + ICS tetap dibuat
        │
        ▼ YA
[4] Gemini opsional (jika ada API key) ──► fallback deterministik bila gagal
        │
        ▼
[5] Layer-1: cek kutipan terhadap teks korpus + SHA-256 + provenance
        │
        ▼
JSON terstruktur ──► UI, teks WhatsApp, ekspor .ics
```

Catatan: ringkasan LLM tidak melewati Layer-1. Yang diverifikasi adalah kutipan pasal yang diambil dari korpus, bukan kebenaran parafrase LLM.

---

## Instalasi dan Menjalankan

### Prasyarat

- Python 3.11 atau lebih baru.
- Node.js 18+ dan `npm`.

### 1. Backend

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# Linux/macOS
# source .venv/bin/activate

pip install -r backend/requirements.txt
cp .env.example .env   # opsional; Windows: copy .env.example .env
uvicorn backend.main:app --reload --port 8000
```

API tersedia di `http://localhost:8000`, dokumentasi interaktif di `/docs`.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Buka `http://localhost:5173`. Vite meneruskan `/api` ke `http://localhost:8000` (lihat `frontend/vite.config.js`).

Build produksi:

```bash
cd frontend
npm run build
```

### 3. Menjalankan test

```bash
pytest -q
```

Status terakhir dijalankan (5 November 2026): **62 passed**. Build frontend dengan Vite 5.4.21 juga berhasil. Dua peringatan deprecation berasal dari kombinasi Starlette/HTTPX di lingkungan test, bukan kegagalan aplikasi.

---

## Konfigurasi Environment

| Variabel | Default | Fungsi |
| :--- | :--- | :--- |
| `GEMINI_API_KEY` | kosong | Opsional. Tanpa nilai, sintesis memakai fallback deterministik. |
| `GEMINI_MODEL` | `gemini-2.5-flash` | Model Gemini yang dipakai. |
| `PRAMANA_PUBLIC_URL` | kosong | Opsional. Ditambahkan ke teks WhatsApp sebagai tautan verifikasi. |
| `CORS_ALLOW_ORIGINS` | `http://localhost:5173,http://127.0.0.1:5173` | Daftar origin yang diizinkan, dipisahkan koma. |
| `RATE_LIMIT_WINDOW_SECONDS` | `60` | Jendela waktu rate limit. |
| `RATE_LIMIT_MAX_REQUESTS` | `60` | Maksimum request POST per klien per jendela. |
| `MAX_REQUEST_BODY_BYTES` | `65536` | Batas ukuran body berdasarkan header `Content-Length`. |
| `TRUST_PROXY_HEADERS` | `false` | Aktifkan hanya di belakang reverse proxy tepercaya yang menimpa `X-Forwarded-For`. |

Jangan commit `.env` atau kunci API nyata.

---

## Endpoint API

| Metode | Path | Keterangan |
| :--- | :--- | :--- |
| `GET` | `/api/v1/health` | Status, versi korpus, cakupan kalender, dan scope verifikasi. |
| `GET` | `/api/v1/corpus` | Metadata korpus, tier, dan seluruh entri. |
| `POST` | `/api/v1/trip-brief` | Mode 1. Validasi tanggal ISO, rentang tanggal, dan origin. |
| `POST` | `/api/v1/context-note` | Mode 2. Validasi teks tidak kosong. |

Kode kesalahan yang relevan: `422` untuk input tidak valid, `413` untuk body terlalu besar, `429` untuk rate limit, `500` untuk kegagalan internal dengan pesan generik.

`trip-brief` mengembalikan field `ics_content` (bukan `ics_calendar`). UI dan test memakai nama tersebut.

---

## Keamanan dan Batasan Operasional

- CORS dibatasi lewat environment; tidak lagi wildcard.
- Rate limit in-memory hanya berlaku per proses. Beberapa worker/Uvicorn dapat memiliki hitungan terpisah. Untuk produksi, gunakan limiter terpusat (misalnya Redis).
- Batas ukuran body hanya memeriksa `Content-Length`; request chunked tanpa header tersebut tidak tertangkap oleh pemeriksaan ini.
- `TRUST_PROXY_HEADERS=false` secara default agar klien tidak bisa memalsukan IP lewat `X-Forwarded-For`.
- Header keamanan dasar dikirim (`X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Permissions-Policy`, `Cache-Control`, CSP untuk `/api/`).
- Belum ada autentikasi. Jangan mengekspos instance ini untuk data sensitif tanpa lapisan tambahan.
- PII masking berbasis regex dan bersifat best-effort. Pola yang tidak dikenal bisa lolos.
- Pesan error 500 tidak membocorkan detail internal; detail lengkap hanya masuk log server.

---

## Keterbatasan yang Diketahui

1. **Korpus kecil dan terkurasi manual**: 6 entri. Belum mencakup seluruh Perda, Pergub, SE, dan awig-awig desa adat.
2. **Retrieval berbasis kata kunci**, bukan embedding atau entailment semantik. Kueri dengan sinonim jauh dapat gagal retrieval dan memicu abstain.
3. **Tidak ada verifikasi real-time ke JDIH.** Layer-1 hanya mencocokkan kutipan dengan teks yang tersimpan di korpus.
4. **Ringkasan LLM tidak diverifikasi Layer-1.** UI menandai `ai_synthesis_status` agar pengguna tahu sumber ringkasan.
5. **Kunci Gemini tidak tersedia di test otomatis**, sehingga jalur LLM belum diuji end-to-end. Fallback deterministik yang diuji.
6. **Dua entri non-verbatim** (pungutan dan Nyepi). Keduanya ditandai jelas dan tidak boleh dikutip sebagai bunyi pasal.
7. **SE Gubernur Bali No. 7 Tahun 2025 belum masuk korpus** sebagai entri penuh.
8. **Kalender hanya 2025–2028.** Di luar rentang itu, hasil tidak lengkap dan diberi peringatan.
9. **Belum ada benchmark publik.** Tidak ada klaim akurasi, presisi, atau “nol halusinasi” yang diukur.
10. **Belum ada mode bilingual, QR/NFC, atau verifikasi dokumen fisik.** Semua fitur tersebut belum diimplementasikan.

---

## Sumber Data dan Kredit

Naskah peraturan perundang-undangan adalah domain publik berdasarkan **Pasal 42 huruf b UU No. 28 Tahun 2014 tentang Hak Cipta**. Tetap periksa naskah resmi pada sumbernya.

Sumber yang dipakai saat verifikasi:

- JDIH BPK: `https://peraturan.bpk.go.id/Details/146819/perda-prov-bali-no-5-tahun-2020`
- peraturan.go.id: `https://peraturan.go.id/files/perda-provinsi-bali-no-5-tahun-2020.pdf`
- JDIH BPK (Perda 2/2025): `https://peraturan.bpk.go.id/Details/323476/perda-prov-bali-no-2-tahun-2025`
- PDF SE Gubernur Bali 4/2023 (Pemkab Buleleng): `https://buleleng.bulelengkab.go.id/informasi/download/14_surat-edaran-gubernur-bali-nomor-04-tahun-2023-tentang-tatanan-baru-bagi-wisatawan-mancanegara-selama-berada-di-bali.pdf`
- Disparda Bali: `https://disparda.baliprov.go.id/peraturan-daerah`
- Kesbangpol Bali (Nyepi 2026): `https://kesbangpol.baliprov.go.id/seruan-bersama-tentang-pelaksanaan-hari-suci-nyepi-tahun-baru-caka-1948-tahun-2026`
- UU No. 6 Tahun 2011: `https://peraturan.go.id/id/uu-no-6-tahun-2011`

Pustaka open-source: FastAPI, Pydantic, Uvicorn, HTTPX, Pytest, Svelte 5, Vite, Tailwind CSS. Tipografi: Inter dan JetBrains Mono (Google Fonts, SIL Open Font License).

---

## AI dan Technology Disclosure

| Komponen | Isi |
| :--- | :--- |
| **Nama Produk** | Pramana |
| **Framework / Frontend** | Svelte 5, Vite 5.4.x, Tailwind CSS 3 |
| **Backend / Runtime** | Python 3.11+, FastAPI, Uvicorn |
| **Database / Storage** | JSON korpus di memori (`corpus/bali_regulations.json`) |
| **Hosting / Deployment** | Belum ada deployment publik yang diverifikasi; jalankan secara lokal atau self-hosted |
| **AI Model / API** | Gemini API opsional (`gemini-2.5-flash`) + retrieval deterministik + Layer-1/Layer-2 guard |
| **Peran AI** | Menyusun ringkasan eksekutif (Mode 1) dan catatan konteks netral (Mode 2) dari entri korpus yang sudah lolos guard. Tanpa API key, ringkasan dibuat deterministik. |
| **Dataset** | Korpus kurasi manual dari sumber resmi; lihat bagian Sumber Data |
| **Open-source Libraries** | `fastapi`, `pydantic`, `uvicorn`, `httpx`, `python-dotenv`, `pytest`, `svelte`, `vite`, `tailwindcss` |
| **Template / Boilerplate** | Dibangun khusus, tanpa template komersial pihak ketiga |
| **AI Coding Assistant** | Digunakan sebagai alat bantu pengembangan dan pengujian; arsitektur dan keputusan verifikasi tetap ditinjau manusia |
| **Pre-existing Components** | Tidak ada komponen komersial pihak ketiga |

---

## Tim

Tim Pengembang Pramana — Bali DigiFest 2026 AI Web Innovation Challenge.
