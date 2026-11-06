# PRAMANA

**Platform edukasi konteks regulasi pariwisata Bali berbasis Strict-RAG**

Bali DigiFest 2026 — AI Web Innovation Challenge

> **Status: prototipe.** Pramana bukan nasihat hukum resmi. Kutipan diverifikasi terhadap **korpus lokal Pramana**, bukan diverifikasi ulang secara real-time ke JDIH. Selalu periksa naskah resmi pada tautan sumber.

---

## Status Implementasi

| Bagian | Status | Catatan |
| :--- | :--- | :--- |
| Retrieval deterministik + abstain (Layer-2) | ✅ Live | Ambang relevansi normalisasi `0.5` + pemotongan relatif `0.75` dari skor teratas |
| Registry provenance korpus | ✅ Live | 29 dokumen registry, 40 chunk retrieval, validasi silang `document_id`, status teks, dan amendment |
| PII masking (5 kategori) | ✅ Live | Email, telepon, kode booking, kartu, paspor. Bersifat best-effort, bukan DLP penuh |
| Kalender Nyepi & Pawukon | ✅ Live | Cakupan deterministik 2025–2028, jendela Nyepi 24 jam |
| Ekspor `.ics` (RFC 5545) | ✅ Live | Escaping teks, line folding, UID stabil, validasi tanggal |
| AI Core Hardening | ✅ Live | Structured output, evidence span, claim verifier, `AI_MODE`, telemetri, eval harness |
| 3-Tier Epistemic Routing | ✅ Live | `VERIFIED_GROUNDED`, `NEEDS_CLARIFICATION`, `OUT_OF_SCOPE_GUIDANCE`; hard-lock sitasi untuk Tier 2/3 |
| Active Legal Triage | ✅ Live | Diagnosis unsur yang kurang, langkah konkret, kanal resmi, dan 3 query rewrite yang bisa diklik |
| Mode 1 — Trip Brief | 🟡 Prototype | Retrieval, kalender, PII, ICS, teks WhatsApp; AI-first dengan triage bila konteks kurang |
| Mode 2 — Context Note | 🟡 Prototype | Sitasi korpus, deteksi framing, claim verifier, triage aktif; AI-first |
| Mode 3 — Smart Gate (NFC/QR) | 🟡 Prototype | 3 zona, kartu deterministik, AI brief grounded, TTS, QR; offline belum |
| Corpus Explorer | 🟡 Prototype | Menampilkan registry dokumen, chunk retrieval, provenance, dan keterbatasan korpus |
| Sintesis Gemini | 🟡 Prototype | Structured JSON + evidence span; `AI_MODE=required` di submission |
| Verifikasi silang JDIH real-time | ⚪ Planned | Belum diimplementasikan |
| Benchmark publik | 🟡 Internal eval | 45 kasus berlabel; baseline `--mode fast` dan live di `eval/results/`; belum benchmark publik |
| Antarmuka bilingual ID/EN | 🟡 Prototype | Smart Gate ID/EN; ringkasan AI Mode 1/2 punya toggle ID/EN |

---

## Deskripsi

Pramana membantu dua kelompok masalah:

1. **Wisatawan** yang perlu memahami aturan kawasan suci, pungutan wisatawan asing, lalu lintas, dan penutupan Nyepi sebelum berangkat.
2. **Masyarakat, jurnalis, dan pengelola akomodasi** yang perlu merespons klaim viral tentang insiden wisata dengan konteks hukum yang dapat ditelusuri, bukan spekulasi.

Aplikasi ini tidak menjawab pertanyaan hukum bebas. Ia mengambil kecocokan dari korpus regulasi terbatas, menampilkan sumber, dan memilih salah satu dari tiga mode epistemik: `VERIFIED_GROUNDED` (bukti cukup), `NEEDS_CLARIFICATION` (konteks belum lengkap), atau `OUT_OF_SCOPE_GUIDANCE` (di luar cakupan). Pada dua mode terakhir, sitasi pasal dikunci kosong secara deterministik dan AI tetap memberi panduan praktis.

### Mode 1 — Trip Brief

- Menyamarkan PII dari teks rencana perjalanan.
- Mendeteksi bentrok dengan Nyepi 24 jam, Malam Pengerupukan, Galungan, dan Kuningan.
- Mengambil entri korpus yang relevan dan menerapkan routing epistemik.
- Menambahkan entri pungutan untuk wisatawan internasional **setelah** grounding berhasil.
- Jika konteks belum lengkap, memberi diagnosis, langkah awal, kanal resmi, dan 3 query rewrite yang bisa diklik.
- Menghasilkan teks WhatsApp dan berkas kalender `.ics` (tersedia juga saat triage).

### Mode 2 — Context Note

- Menyamarkan PII dari teks postingan/klaim.
- Mendeteksi frasa framing sensasional (generalisasi, tuduhan tanpa dasar, dan sejenisnya).
- Mengambil entri korpus yang relevan, lalu memverifikasi kutipan terhadap teks korpus (Layer-1).
- Menghasilkan catatan konteks netral dan komentar yang dapat disalin.
- Jika input masih subjektif/awam, menghasilkan triage dengan 3 skenario perbaikan; jika di luar cakupan, memberi panduan non-hukum yang jujur.

### Mode 3 — Smart Gate (NFC/QR)

- `/totem` menampilkan direktori gerbang; `/totem/{zone_id}` adalah halaman tujuan URL NFC/QR.
- Tiga zona awal: Bandara I Gusti Ngurah Rai, Pura Besakih, dan Pantai Melasti.
- Kartu zona bersifat **deterministik**: checklist praktis + sitasi yang sudah lolos Layer-1.
- AI brief 2–3 kalimat dibuat dari sitasi terverifikasi; jika Gemini tidak tersedia atau menyebut pasal/angka di luar bukti, sistem memakai template deterministik.
- Teks pasal asli tetap Bahasa Indonesia; terjemahan hanya untuk panduan praktis.
- Audio memakai Web Speech API bawaan browser, bukan API TTS eksternal.
- QR dibuat lokal di browser dengan margin quiet zone 4 modul dan error correction level H agar lebih tahan saat dipindai dari foto. NFC memakai URL record pada tag NTAG213; tidak memakai Web NFC API.
- Jika `PRAMANA_PUBLIC_URL` diisi, QR mengarah ke URL publik tersebut; jika kosong, QR memakai origin browser. Saat origin masih `localhost`/`127.0.0.1`, UI menampilkan peringatan bahwa QR tidak dapat dibuka dari perangkat lain.
- Tombol “Tandai Sudah Dibaca” hanya menyimpan status di `localStorage` perangkat, bukan check-in server dan bukan bukti hukum.
- Rujukan yang sudah disempurnakan (SE Gubernur Bali No. 4 Tahun 2023) ditampilkan terpisah sebagai **rujukan historis**, bukan aturan aktif.
- Mode ini belum memiliki cache offline/PWA.

---

## Apa Arti “Verifikasi” di Pramana

Pramana sengaja membedakan beberapa tingkat klaim:

| Istilah | Arti sebenarnya |
| :--- | :--- |
| **Layer-1 exact match** | Kutipan ada di dalam teks entri korpus lokal setelah normalisasi spasi. Ini bukan verifikasi independen ke JDIH. |
| **Layer-2 / routing epistemik** | Skor retrieval + kelengkapan fakta menentukan Tier 1/2/3. Tier 2/3 mengunci `citations = []`; AI tetap dipanggil untuk triage. |
| **`VERIFIED_GROUNDED`** | Skor ≥ 0.50 dan unsur peristiwa cukup; klaim wajib terikat ke `citation_id` dan evidence span yang valid. |
| **`NEEDS_CLARIFICATION`** | Skor 0.15–0.49, fakta belum lengkap, atau instrumen registry-only; AI memberi diagnosis, langkah, kanal resmi, dan 3 query rewrite. |
| **`OUT_OF_SCOPE_GUIDANCE`** | Skor < 0.15 dan tidak ada gugus hukum; AI menjelaskan batas cakupan dan memberi saran non-hukum. |
| **`is_verbatim: true`** | Entri korpus disimpan sebagai kutipan teks, bukan ringkasan. |
| **`is_verbatim: false`** | Entri adalah ringkasan/kompilasi. UI tidak menampilkannya sebagai bunyi pasal verbatim. |
| **`text_status`** | Status teks eksplisit: `verbatim`, `verbatim-ocr-dibersihkan`, `compilation`, `non-verbatim`, atau `belum-diambil`. Chunk `compilation` tidak boleh dikutip sebagai bunyi pasal. |
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

## AI Core dan Evaluasi

Pramana memakai `AI_MODE` untuk mencegah AI “menghilang” diam-diam:

| Mode | Perilaku |
| :--- | :--- |
| `required` | AI wajib. Jika AI gagal, respons menjadi `unavailable`; tidak ada template yang menyamar sebagai jawaban AI. |
| `optional` | Fallback deterministik diizinkan untuk pengembangan/test. |
| `disabled` | AI dilewati; dipakai untuk baseline retrieval-only. |

Alur AI:

1. PII masking dan pemetaan bahasa awam ke 7 gugus hukum (`legal_taxonomy.py`).
2. Retrieval hybrid (keyword + embedding) dengan query expansion; skor dan kelengkapan fakta menentukan tier.
3. Untuk Tier 1: sitasi diverifikasi Layer-1, lalu Gemini menerima sitasi + evidence span IDs dan mengembalikan klaim terikat.
4. Untuk Tier 2/3: Gemini tetap dipanggil sebagai konsultan triage, tetapi `claims` dan `citations` dikunci kosong.
5. Python memverifikasi setiap claim (citation_id valid, span_ids milik sitasi, tidak ada pasal/rupiah liar) dan menyensor nomor pasal/nominal tak terverifikasi di teks bebas Tier 2/3.
6. Prompt injection dan permintaan pasal/nominal fiktif ditolak secara deterministik.

Telemetri tersedia di `GET /api/v1/ai/status` (tanpa prompt/PII), termasuk `total_requests`, `verified_grounded_count`, `needs_clarification_count`, `out_of_scope_count`, `guard_rejections_count`, `active_chunks_count`, `registry_docs_count`, dan `epistemic_routing_enabled`. Hybrid retrieval opsional memakai embedding korpus yang dihitung offline:

```bash
python scripts/build_embeddings.py   # butuh GEMINI_API_KEY
```

Hasilnya `corpus/embeddings.json`; runtime menghitung cosine query + keyword, dan otomatis kembali ke keyword jika file/API tidak tersedia. Vektor 40 chunk sudah disertakan; jalankan ulang skrip setelah korpus berubah. Eval harness ada di `eval/run_eval.py`:

```bash
python eval/run_eval.py --mode fast   # deterministik, tanpa AI
python eval/run_eval.py --mode live   # Gemini live + rate-limit-safe
```

Baseline internal 45 kasus: 15 in-scope, 10 triage, 10 out-of-scope, 4 adversarial, 6 PII. Dengan `gemini-3.1-flash-lite`, `--mode live` mencapai 45/45, 75 sitasi terverifikasi, 45 klaim, epistemic routing 1.0, guidance completeness 1.0, PII leak 0, dan latensi P50/P95 sekitar 4,3/7,7 detik. Setelah default diganti ke `gemini-3.5-flash`, targeted test Tier 1/2/3 berhasil, tetapi full 45-case run pada key uji lokal menemui `HTTP 429` untuk sebagian besar panggilan AI; routing dan guidance deterministik tetap 45/45. Untuk eval AI penuh dengan 3.5-flash, gunakan key/kuota yang mencukupi. **Ini bukan benchmark publik** dan tidak mengklaim “nol halusinasi”. Hasil lengkap ada di [`eval/results/latest.md`](eval/results/latest.md).

---

## Korpus dan Kalender

### Korpus regulasi (`corpus/bali_regulations.json` v1.3.0)

Korpus memakai dua lapis yang sengaja dipisahkan:

- **`documents` — registry provenance (29 dokumen):** 21 entri manifest awal, dokumen legacy SE Gubernur Bali No. 4 Tahun 2023, dan 7 dokumen tambahan Phase 2C. Registry mencatat status teks, cakupan, sumber PDF, SHA-256, dan keputusan audit. **Registry bukan bukti kutipan dan tidak menambah hasil retrieval.**
- **`regulations` — chunk retrieval (40 chunk):** hanya chunk yang teksnya tersimpan dan boleh diverifikasi Layer-1.

Cakupan chunk:

- **Kepariwisataan & pungutan:** SE 4/2023, Perda 5/2020, Perda 6/2023 (pasal yang tidak diubah), Perda 2/2025, Pergub 2/2024 (pasal yang tidak diubah), Pergub 25/2025, Pergub 25/2020, Perda 4/2019, UU 15/2023, UU 18/2025.
- **Wacana publik & diskriminasi:** UU 40/2008, UU 1/2024 (ITE), UU 1/2023 (KUHP), UU 39/1999 (HAM), UU 8/1999 (Perlindungan Konsumen).
- **Non-verbatim:** kompilasi Nyepi. SE 7/2025, SE Kapolri 6/2015, dan SKB ITE 2021 tetap registry-only.

Status teks:

- `verbatim` — kutipan dari PDF resmi.
- `verbatim-ocr-dibersihkan` — teks PDF dengan artefak OCR dibersihkan; bukan transkripsi mentah.
- `compilation` — kompilasi pedoman tahunan.
- `non-verbatim` — ringkasan/sumber sekunder.
- `belum-diambil` — teks belum tersedia.

Catatan penting:

- **Pasal yang diubah/dihapus tidak dimasukkan sebagai aturan aktif.** Perda 2/2025 mengubah Perda 6/2023 Pasal 1, 4, 5, 6, 7; Pergub 25/2025 mengubah Pergub 2/2024 Pasal 9, 12 dan menghapus Pasal 23.
- UU 18/2025 Pasal 20 dan Pasal 24 tidak dimasukkan karena cacat teks pada PDF/OCR; 7 pasal lain masuk dengan status `verbatim-ocr-dibersihkan`.
- SE Gubernur Bali No. 4 Tahun 2023 tetap disimpan sebagai rujukan historis; SE 7/2025 tidak diindeks karena tidak ada PDF resmi.
- Setiap chunk mencantumkan `document_id`, `text_status`, `source_type`, `source_chunk_id`, `ocr_cleaned`, dan `amendment_status`.
- Audit lengkap ada di [`docs/CORPUS_PROVENANCE.md`](docs/CORPUS_PROVENANCE.md).

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
- **AI:** Google Gemini API (`gemini-3.5-flash`, `temperature=0.1`) dengan structured JSON + evidence span verifier. `AI_MODE=required` untuk submission; `optional` untuk pengembangan.
- **Evaluasi:** `eval/run_eval.py`, 45 kasus berlabel, baseline `--mode fast` dan live `--mode live` dengan metrik epistemic routing, guidance completeness, citation/span validity, PII recall, dan latensi.
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

Status terakhir dijalankan (6 November 2026): **125 passed**. Build frontend dengan Vite 5.4.21 juga berhasil tanpa warning Svelte. Dua peringatan deprecation berasal dari kombinasi Starlette/HTTPX di lingkungan test, bukan kegagalan aplikasi.

---

## Konfigurasi Environment

| Variabel | Default | Fungsi |
| :--- | :--- | :--- |
| `AI_MODE` | `required` | `required` untuk submission; `optional` untuk dev; `disabled` untuk eval retrieval-only. |
| `GEMINI_API_KEY` | kosong | Wajib untuk AI. Jangan commit nilai asli. |
| `GEMINI_MODEL` | `gemini-3.5-flash` | Model generasi; dapat diganti via env. |
| `GEMINI_EMBEDDING_MODEL` | `gemini-embedding-001` | Diverifikasi ulang sebelum membangun embedding. |
| `PRAMANA_PUBLIC_URL` | kosong | Opsional. URL publik frontend untuk tautan QR dan teks WhatsApp, misalnya `https://pramana.example.com`. Jika kosong, tautan memakai origin browser. |
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
| `GET` | `/api/v1/health` | Status, versi korpus, jumlah chunk/dokumen, status AI, cakupan kalender, dan scope verifikasi. |
| `GET` | `/api/v1/ai/status` | Telemetri AI: mode, model, calls, failures, guard rejections, latency, dan counter epistemic routing. |
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

1. **Korpus retrieval masih terkurasi manual**: 40 chunk dari 29 dokumen registry. Belum mencakup seluruh Perda, Pergub, SE, dan awig-awig desa adat.
2. **Retrieval berbasis kata kunci**, bukan embedding atau entailment semantik. Kueri dengan sinonim jauh dapat gagal retrieval dan memicu abstain.
3. **Tidak ada verifikasi real-time ke JDIH.** Layer-1 hanya mencocokkan kutipan dengan teks yang tersimpan di korpus.
4. **Ringkasan AI tidak diverifikasi Layer-1.** AI claims diverifikasi terhadap evidence span; kebenaran parafrase tetap terbatas.
5. **Kunci Gemini tidak tersedia di test otomatis**, sehingga jalur LLM end-to-end belum diuji tanpa key. Fallback deterministik yang diuji.
6. **Satu chunk non-verbatim** (kompilasi Nyepi). Chunk itu ditandai `compilation` dan tidak boleh dikutip sebagai bunyi pasal.
7. **UU 18/2025 memakai `verbatim-ocr-dibersihkan`.** Pasal 20 dan 24 tidak dimasukkan karena cacat teks.
8. **Pasal yang diubah/dihapus tidak diindeks.** Perda 6/2023 dan Pergub 2/2024 hanya memuat pasal yang tidak diubah/dihapus.
9. **Smart Gate baru mencakup 3 zona.** Pura Besakih dan Pantai Melasti memakai aturan umum serta rujukan historis.
10. **TTS bergantung pada browser/perangkat.** Tidak semua browser memiliki suara ID/EN; teks panduan tetap tersedia.
11. **Belum ada mode offline/PWA.** Smart Gate membutuhkan koneksi ke backend; offline ditunda.
12. **Kunci Gemini di deployment harus diset agar AI aktif.** Dengan `AI_MODE=required`, kegagalan AI menghasilkan status `unavailable`, bukan template.
13. **SE Gubernur Bali No. 7 Tahun 2025 hanya ada di registry**, bukan chunk retrieval, karena PDF resminya belum diperoleh.
14. **Kalender hanya 2025–2028.** Di luar rentang itu, hasil tidak lengkap dan diberi peringatan.
15. **Belum ada benchmark publik.** Eval internal 45 kasus bukan klaim akurasi universal.
16. **Belum ada QR/NFC verifikasi dokumen fisik.** QR/NFC hanya membuka URL; tidak memverifikasi identitas atau pembayaran.
17. **QR dari `localhost` tidak bisa dibuka di perangkat lain.** Untuk pengujian dari HP, set `PRAMANA_PUBLIC_URL` ke alamat LAN/publik frontend, misalnya `http://192.168.1.10:5173`.

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
- UU No. 40 Tahun 2008: `https://peraturan.bpk.go.id/Details/39733/uu-no-40-tahun-2008`
- UU No. 1 Tahun 2024 (ITE): `https://peraturan.bpk.go.id/Details/274494/uu-no-1-tahun-2024`
- UU No. 1 Tahun 2023 (KUHP): `https://peraturan.bpk.go.id/Details/234935/uu-no-1-tahun-2023`
- UU No. 39 Tahun 1999 (HAM): `https://peraturan.bpk.go.id/Details/45361/uu-no-39-tahun-1999`
- UU No. 8 Tahun 1999 (Perlindungan Konsumen): `https://peraturan.bpk.go.id/Details/45288/uu-no-8-tahun-1999`

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
| **AI Model / API** | Gemini API (`gemini-3.5-flash`, dapat diganti via `GEMINI_MODEL`) dengan structured JSON + evidence span verifier + Layer-1/Layer-2 guard |
| **Peran AI** | Menyusun ringkasan eksekutif (Mode 1), catatan konteks netral (Mode 2), dan AI brief Smart Gate (Mode 3) dari sitasi terverifikasi. AI tidak membuat sitasi; setiap claim harus menunjuk evidence span. `AI_MODE=required` di submission. |
| **Phygital Interface** | URL record NFC NTAG213 / QR, Web Speech API (TTS). Tidak memakai Web NFC API dan tidak memverifikasi identitas. |
| **Dataset** | Korpus kurasi manual dari sumber resmi; lihat bagian Sumber Data |
| **Open-source Libraries** | `fastapi`, `pydantic`, `uvicorn`, `httpx`, `python-dotenv`, `pytest`, `svelte`, `vite`, `tailwindcss`, `qrcode`, `lucide-svelte` |
| **Template / Boilerplate** | Dibangun khusus, tanpa template komersial pihak ketiga |
| **AI Coding Assistant** | Digunakan sebagai alat bantu pengembangan dan pengujian; arsitektur dan keputusan verifikasi tetap ditinjau manusia |
| **Pre-existing Components** | Tidak ada komponen komersial pihak ketiga |

---

## Tim

Tim Pengembang Pramana — Bali DigiFest 2026 AI Web Innovation Challenge.
