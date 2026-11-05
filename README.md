# PRAMANA

**Platform edukasi konteks regulasi pariwisata Bali berbasis Strict-RAG**

Bali DigiFest 2026 — AI Web Innovation Challenge

> **Status: prototipe.** Pramana bukan nasihat hukum resmi. Kutipan diverifikasi terhadap **korpus lokal Pramana**, bukan diverifikasi ulang secara real-time ke JDIH. Selalu periksa naskah resmi pada tautan sumber.

---

## Status Implementasi

| Bagian | Status | Catatan |
| :--- | :--- | :--- |
| Retrieval deterministik + abstain (Layer-2) | ✅ Live | Ambang relevansi normalisasi `0.5` + pemotongan relatif `0.75` dari skor teratas |
| Registry provenance korpus | ✅ Live | 22 dokumen registry, 10 chunk retrieval, validasi silang `document_id` dan status teks |
| PII masking (5 kategori) | ✅ Live | Email, telepon, kode booking, kartu, paspor. Bersifat best-effort, bukan DLP penuh |
| Kalender Nyepi & Pawukon | ✅ Live | Cakupan deterministik 2025–2028, jendela Nyepi 24 jam |
| Ekspor `.ics` (RFC 5545) | ✅ Live | Escaping teks, line folding, UID stabil, validasi tanggal |
| Mode 1 — Trip Brief | 🟡 Prototype | Retrieval, kalender, PII, ICS, teks WhatsApp; ringkasan AI opsional |
| Mode 2 — Context Note | 🟡 Prototype | Sitasi korpus, deteksi framing, abstain; ringkasan AI opsional |
| Mode 3 — Smart Gate (NFC/QR) | 🟡 Prototype | 3 zona, kartu deterministik, AI brief grounded, TTS, QR; offline belum |
| Corpus Explorer | 🟡 Prototype | Menampilkan registry dokumen, chunk retrieval, provenance, dan keterbatasan korpus |
| Sintesis Gemini | 🟡 Prototype | Butuh `GEMINI_API_KEY`; test otomatis memakai fallback deterministik |
| Verifikasi silang JDIH real-time | ⚪ Planned | Belum diimplementasikan |
| Benchmark publik | ⚪ Planned | Belum ada angka akurasi/halusinasi yang diukur |
| Antarmuka bilingual ID/EN | 🟡 Prototype | Smart Gate sudah ID/EN; Mode 1 dan 2 masih Bahasa Indonesia |

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

### Mode 3 — Smart Gate (NFC/QR)

- `/totem` menampilkan direktori gerbang; `/totem/{zone_id}` adalah halaman tujuan URL NFC/QR.
- Tiga zona awal: Bandara I Gusti Ngurah Rai, Pura Besakih, dan Pantai Melasti.
- Kartu zona bersifat **deterministik**: checklist praktis + sitasi yang sudah lolos Layer-1.
- AI brief 2–3 kalimat dibuat dari sitasi terverifikasi; jika Gemini tidak tersedia atau menyebut pasal/angka di luar bukti, sistem memakai template deterministik.
- Teks pasal asli tetap Bahasa Indonesia; terjemahan hanya untuk panduan praktis.
- Audio memakai Web Speech API bawaan browser, bukan API TTS eksternal.
- QR dibuat lokal di browser. NFC memakai URL record pada tag NTAG213; tidak memakai Web NFC API.
- Tombol “Tandai Sudah Dibaca” hanya menyimpan status di `localStorage` perangkat, bukan check-in server dan bukan bukti hukum.
- Rujukan yang sudah disempurnakan (SE Gubernur Bali No. 4 Tahun 2023) ditampilkan terpisah sebagai **rujukan historis**, bukan aturan aktif.
- Mode ini belum memiliki cache offline/PWA.

---

## Apa Arti “Verifikasi” di Pramana

Pramana sengaja membedakan beberapa tingkat klaim:

| Istilah | Arti sebenarnya |
| :--- | :--- |
| **Layer-1 exact match** | Kutipan ada di dalam teks entri korpus lokal setelah normalisasi spasi. Ini bukan verifikasi independen ke JDIH. |
| **Layer-2 guard** | Tidak ada hasil retrieval yang melewati ambang skor, sehingga sistem abstain sebelum memanggil LLM. |
| **`is_verbatim: true`** | Entri korpus disimpan sebagai kutipan teks, bukan ringkasan. |
| **`is_verbatim: false`** | Entri adalah ringkasan/kompilasi. UI tidak menampilkannya sebagai bunyi pasal verbatim. |
| **`text_status`** | Status teks eksplisit: `verbatim`, `compilation`, `non-verbatim`, atau `belum-diambil`. Chunk `compilation` tidak boleh dikutip sebagai bunyi pasal. |
| **`retrieval_eligible`** | Hanya `true` untuk dokumen yang memiliki chunk teks tersimpan. Dokumen `belum-diambil`/`non-verbatim` tidak menambah hasil retrieval. |
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

### Korpus regulasi (`corpus/bali_regulations.json` v1.2.0)

Korpus memakai dua lapis yang sengaja dipisahkan:

- **`documents` — registry provenance (22 dokumen):** 21 entri manifest bantuan yang diaudit pada 5 November 2026, ditambah dokumen legacy SE Gubernur Bali No. 4 Tahun 2023 karena dua chunk Phase 0 merujuk padanya. Registry mencatat status teks, cakupan, sumber PDF, SHA-256, dan keputusan audit. **Registry bukan bukti kutipan dan tidak menambah hasil retrieval.**
- **`regulations` — chunk retrieval (10 chunk):** hanya chunk yang teksnya tersimpan dan boleh diverifikasi Layer-1.

Sepuluh chunk yang diindeks:

1. SE Gubernur Bali No. 4 Tahun 2023 — kewajiban wisatawan mancanegara (`verbatim`).
2. SE Gubernur Bali No. 4 Tahun 2023 — larangan wisatawan mancanegara (`verbatim`).
3. Perda Bali No. 5 Tahun 2020 Pasal 15 — kewajiban pengunjung (`verbatim`).
4. Perda Bali No. 6 Tahun 2023 jo. No. 2 Tahun 2025 Pasal 4A, 5, dan 16A — pungutan wisatawan asing (`verbatim`; ID lama `PERDA_BALI_06_2023_LEVY` dipertahankan untuk kompatibilitas, alias `PERDA_BALI_02_2025_LEVY` tersedia).
5. UU No. 6 Tahun 2011 Pasal 75 — tindakan administratif keimigrasian (`verbatim`).
6. Ketentuan Hari Suci Nyepi — kompilasi pedoman tahunan (`compilation`, non-verbatim).
7. UU No. 15 Tahun 2023 Pasal 8 ayat (3)–(4) — dasar kewenangan pungutan (`verbatim`).
8. Pergub Bali No. 25 Tahun 2025 Pasal 9 dan 12 — data serta waktu pembayaran pungutan (`verbatim`).
9. Pergub Bali No. 25 Tahun 2020 Pasal 45–46 — larangan dan sanksi pelindungan Pura (`verbatim`).
10. Perda Bali No. 4 Tahun 2019 Pasal 1 — definisi Desa Adat, Awig-awig, dan Pararem (`verbatim`).

Catatan penting:

- **SE Gubernur Bali No. 4 Tahun 2023 telah disempurnakan oleh SE No. 7 Tahun 2025.** Teks lama tetap disimpan sebagai rujukan historis dengan `status: "Disempurnakan"`. SE 7/2025 hanya ada di registry (`non-verbatim`, `retrieval_eligible: false`) karena PDF resminya belum diperoleh.
- Entri pungutan kini berupa **kutipan verbatim** Pasal 4A, 5, dan 16A Perda No. 2 Tahun 2025, bukan parafrase. Teks asli Perda 6/2023 tidak digabung ke dalam kutipan.
- Perda Bali No. 6 Tahun 2023 dan UU No. 18 Tahun 2025 sudah diunduh PDF resminya, tetapi belum dijadikan chunk karena teks lengkapnya belum lolos verifikasi karakter. Keduanya berstatus `belum-diambil` di registry.
- Awig-awig Penglipuran dan Tenganan hanya tersedia lewat literatur akademik sekunder; keduanya berstatus `non-verbatim`, Tier 3, dan tidak diindeks.
- Setiap chunk mencantumkan `document_id`, `text_status`, `source_type`, dan bila relevan `source_pdf_url`, `source_pdf_sha256`, serta `related_document_ids`.
- Audit lengkap 21 entri manifest, termasuk URL dan keputusan pemetaan tier, ada di [`docs/CORPUS_PROVENANCE.md`](docs/CORPUS_PROVENANCE.md).

### Kalender deterministik

- Cakupan: **2025–2028**.
- Nyepi: 2025-03-29, 2026-03-19, 2027-03-08, 2028-03-26.
- Jendela Nyepi dihitung **24 jam**, dari pukul 06.00 WITA sampai 06.00 WITA keesokan harinya. Perjalanan yang hanya menyentuh pagi setelah tanggal Nyepi tetap ditandai sebagai `PARTIAL`.
- Galungan/Kuningan 2026: **17 Juni** dan **27 Juni**.
- Di luar 2025–2028, sistem mengembalikan `coverage_warning` dan tidak mengklaim bebas konflik.

---

## Tech Stack

- **Frontend:** Svelte 5 (runes), Vite 5.4.x, Tailwind CSS 3, Web Speech API, `qrcode`.
- **Backend:** Python 3.11+ (diuji pada 3.12.10), FastAPI, Pydantic v2, Uvicorn, HTTPX.
- **Penyimpanan:** JSON korpus terstruktur dan zone registry di memori; tidak ada database.
- **AI opsional:** Google Gemini API (`gemini-2.5-flash`, `temperature=0.1`). Tanpa API key, sistem memakai ringkasan deterministik.
- **Testing:** Pytest + FastAPI TestClient.

---

## Arsitektur

```text
Input (itinerary / klaim viral / zone_id)
        │
        ▼
[1] PII masking (regex, 5 kategori) — hanya Mode 1/2
        │
        ├──► [2a] Kalender Bali: Nyepi 24 jam, Pengerupukan, Pawukon
        │
        ├──► [2b] Zone registry: Smart Gate /totem/{zone_id}
        │
        ▼
[3] Retrieval kata kunci berbobot + skor normalisasi
        │
        ▼
[4] Layer-2 guard: skor ≥ 0.5 dan ≥ 0.75 × skor teratas?
        │
        ├── TIDAK ──► Abstain deterministik (tanpa LLM) + ICS tetap dibuat
        │
        ▼ YA
[5] Gemini opsional (jika ada API key) ──► fallback deterministik bila gagal
        │
        ▼
[6] Layer-1: cek kutipan terhadap teks korpus + SHA-256 + provenance
        │
        ▼
JSON terstruktur ──► UI, Smart Gate card, teks WhatsApp, ekspor .ics
```

Catatan: ringkasan LLM tidak melewati Layer-1. Yang diverifikasi adalah kutipan pasal yang diambil dari korpus, bukan kebenaran parafrase LLM. Pada Smart Gate, AI brief juga ditolak jika menyebut nomor pasal atau nominal rupiah di luar sitasi.

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

Status terakhir dijalankan (5 November 2026): **89 passed**. Build frontend dengan Vite 5.4.21 juga berhasil. Dua peringatan deprecation berasal dari kombinasi Starlette/HTTPX di lingkungan test, bukan kegagalan aplikasi.

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
| `GET` | `/api/v1/health` | Status, versi korpus, jumlah chunk/dokumen, cakupan kalender, dan scope verifikasi. |
| `GET` | `/api/v1/corpus` | Metadata korpus, tier, chunk retrieval, dan registry dokumen. |
| `GET` | `/api/v1/zones` | Direktori zona Smart Gate. |
| `GET` | `/api/v1/totem/{zone_id}?lang=id\|en` | Kartu zona deterministik + sitasi Layer-1. |
| `POST` | `/api/v1/totem/{zone_id}/brief` | AI brief grounded; fallback deterministik; rate-limited. |
| `POST` | `/api/v1/trip-brief` | Mode 1. Validasi tanggal ISO, rentang tanggal, dan origin. |
| `POST` | `/api/v1/context-note` | Mode 2. Validasi teks tidak kosong. |

Kode kesalahan yang relevan: `404` untuk zona tidak dikenal, `422` untuk input/language tidak valid, `413` untuk body terlalu besar, `429` untuk rate limit, `500` untuk kegagalan internal dengan pesan generik.

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

1. **Korpus retrieval kecil dan terkurasi manual**: 10 chunk dari 22 dokumen registry. Belum mencakup seluruh Perda, Pergub, SE, dan awig-awig desa adat.
2. **Retrieval berbasis kata kunci**, bukan embedding atau entailment semantik. Kueri dengan sinonim jauh dapat gagal retrieval dan memicu abstain.
3. **Tidak ada verifikasi real-time ke JDIH.** Layer-1 hanya mencocokkan kutipan dengan teks yang tersimpan di korpus.
4. **Ringkasan LLM tidak diverifikasi Layer-1.** UI menandai `ai_synthesis_status` agar pengguna tahu sumber ringkasan.
5. **Kunci Gemini tidak tersedia di test otomatis**, sehingga jalur LLM belum diuji end-to-end. Fallback deterministik yang diuji.
6. **Satu chunk non-verbatim** (kompilasi Nyepi). Chunk itu ditandai `compilation` dan tidak boleh dikutip sebagai bunyi pasal.
7. **Smart Gate baru mencakup 3 zona.** Pura Besakih dan Pantai Melasti memakai aturan umum serta rujukan historis; aturan busana terbaru (SE 7/2025) belum tersedia di korpus.
8. **TTS bergantung pada browser/perangkat.** Tidak semua browser memiliki suara ID/EN; teks panduan tetap tersedia.
9. **Belum ada mode offline/PWA.** Smart Gate membutuhkan koneksi ke backend; offline ditunda.
10. **Kunci Gemini di deployment harus diset agar AI brief aktif.** Tanpa kunci, Smart Gate tetap berfungsi dengan template deterministik.
11. **SE Gubernur Bali No. 7 Tahun 2025 hanya ada di registry**, bukan chunk retrieval, karena PDF resminya belum diperoleh.
12. **Kalender hanya 2025–2028.** Di luar rentang itu, hasil tidak lengkap dan diberi peringatan.
13. **Belum ada benchmark publik.** Tidak ada klaim akurasi, presisi, atau “nol halusinasi” yang diukur.
14. **Belum ada QR/NFC verifikasi dokumen fisik.** QR/NFC hanya membuka URL; tidak memverifikasi identitas atau pembayaran.

---

## Sumber Data dan Kredit

Naskah peraturan perundang-undangan adalah domain publik berdasarkan **Pasal 42 huruf b UU No. 28 Tahun 2014 tentang Hak Cipta**. Tetap periksa naskah resmi pada sumbernya.

Sumber yang dipakai saat verifikasi:

- JDIH BPK (UU 15/2023): `https://peraturan.bpk.go.id/Details/249375`
- JDIH BPK (UU 18/2025): `https://peraturan.bpk.go.id/Details/334481`
- JDIH BPK (Perda 2/2025): `https://peraturan.bpk.go.id/Details/323476/perda-prov-bali-no-2-tahun-2025`
- JDIH BPK (Perda 5/2020): `https://peraturan.bpk.go.id/Details/146819/perda-prov-bali-no-5-tahun-2020`
- peraturan.go.id (PDF Perda 5/2020): `https://peraturan.go.id/files/perda-provinsi-bali-no-5-tahun-2020.pdf`
- JDIH BPK (Pergub 25/2025): `https://peraturan.bpk.go.id/Details/345864`
- JDIH BPK (Pergub 25/2020): `https://peraturan.bpk.go.id/Details/148225`
- JDIH Bali (PDF Perda 6/2023): `https://jdih-backup.baliprov.go.id/uploads/produk-hukum/peraturan/2023/perda/2023pd0051006.pdf`
- JDIH Bali (PDF Pergub 4/2020): `https://jdih-backup.baliprov.go.id/uploads/produk-hukum/peraturan/2020/pergub/2020pg0051004.pdf`
- Pemkab Buleleng (PDF Perda 4/2019): `https://bulelengkab.go.id/informasi/download/peraturan-daerah-provinsi-bali-nomor-4-tahun-2019-tentang-desa-adat-di-bali-29.pdf`
- PDF SE Gubernur Bali 4/2023 (Pemkab Buleleng): `https://buleleng.bulelengkab.go.id/informasi/download/14_surat-edaran-gubernur-bali-nomor-04-tahun-2023-tentang-tatanan-baru-bagi-wisatawan-mancanegara-selama-berada-di-bali.pdf`
- Disparda Bali: `https://disparda.baliprov.go.id/peraturan-daerah`
- Kesbangpol Bali (Nyepi 2026): `https://kesbangpol.baliprov.go.id/seruan-bersama-tentang-pelaksanaan-hari-suci-nyepi-tahun-baru-caka-1948-tahun-2026`
- UU No. 6 Tahun 2011: `https://peraturan.go.id/id/uu-no-6-tahun-2011`

Rincian audit per dokumen, status teks, dan keputusan pemetaan tier: [`docs/CORPUS_PROVENANCE.md`](docs/CORPUS_PROVENANCE.md).

Pustaka open-source: FastAPI, Pydantic, Uvicorn, HTTPX, Pytest, Svelte 5, Vite, Tailwind CSS, `qrcode` (MIT), Lucide (ISC). Tipografi: Plus Jakarta Sans, Newsreader, dan JetBrains Mono (Google Fonts, SIL Open Font License).

---

## AI dan Technology Disclosure

| Komponen | Isi |
| :--- | :--- |
| **Nama Produk** | Pramana |
| **Framework / Frontend** | Svelte 5, Vite 5.4.x, Tailwind CSS 3 |
| **Backend / Runtime** | Python 3.11+, FastAPI, Uvicorn |
| **Database / Storage** | JSON korpus dan zone registry di memori (`corpus/bali_regulations.json`, `corpus/zones.json`); tidak ada database |
| **Hosting / Deployment** | Belum ada deployment publik yang diverifikasi; jalankan secara lokal atau self-hosted |
| **AI Model / API** | Gemini API opsional (`gemini-2.5-flash`) + retrieval deterministik + Layer-1/Layer-2 guard + template fallback |
| **Peran AI** | Menyusun ringkasan eksekutif (Mode 1), catatan konteks netral (Mode 2), dan AI brief Smart Gate (Mode 3) dari entri korpus yang sudah lolos guard. Tanpa API key, ringkasan dibuat deterministik. |
| **Phygital Interface** | URL record NFC NTAG213 / QR, Web Speech API (TTS). Tidak memakai Web NFC API dan tidak memverifikasi identitas. |
| **Dataset** | Korpus kurasi manual dari sumber resmi; lihat bagian Sumber Data |
| **Open-source Libraries** | `fastapi`, `pydantic`, `uvicorn`, `httpx`, `python-dotenv`, `pytest`, `svelte`, `vite`, `tailwindcss`, `qrcode`, `lucide-svelte` |
| **Template / Boilerplate** | Dibangun khusus, tanpa template komersial pihak ketiga |
| **AI Coding Assistant** | Digunakan sebagai alat bantu pengembangan dan pengujian; arsitektur dan keputusan verifikasi tetap ditinjau manusia |
| **Pre-existing Components** | Tidak ada komponen komersial pihak ketiga |

---

## Tim

Tim Pengembang Pramana — Bali DigiFest 2026 AI Web Innovation Challenge.
