# Smart Gate (Mode 3) — Implementasi Phase 2A

Tanggal: **5 November 2026**

Mode 3 adalah ekstensi lapangan dari Pramana, bukan pengganti Mode 1/2. Tujuannya
memberi kartu kepatuhan lokasi yang dapat dibuka dari URL NFC/QR di gerbang
wisata. Semua aturan tetap berasal dari chunk korpus yang sudah lolos Layer-1.

## 1. Prinsip

1. **Registry bukan sumber hukum.** `corpus/zones.json` hanya memetakan zona ke
   chunk yang sudah ada.
2. **Sitasi tidak dibuat AI.** AI hanya meringkas sitasi terverifikasi.
3. **Rujukan historis dipisahkan.** Chunk yang sudah disempurnakan tidak masuk
   checklist aktif.
4. **Tanpa PII.** Mode 3 hanya menerima `zone_id` dan `lang`.
5. **Tanpa offline.** Tidak ada service worker atau cache API pada Phase 2A.
6. **Tanpa Web NFC.** NFC ditulis sebagai URL record (mis. NTAG213); QR memakai
   URL yang sama.

## 2. Zona dan Bukti

| Zona | Chunk aktif | Bukti historis | Batas klaim |
| :--- | :--- | :--- | :--- |
| `bandara-ngurah-rai` | `PERDA_BALI_06_2023_LEVY`, `PERGUB_BALI_25_2025_PASAL_9_12`, `UU_15_2023_PASAL_8` | — | Pungutan, pengecualian, data pembayaran, sanksi administratif |
| `pura-besakih` | `PERGUB_BALI_25_2020_PASAL_45_46`, `PERDA_BALI_05_2020_PASAL_15` | `SE_GUB_04_2023_DO`, `SE_GUB_04_2023_DONT` | Larangan masuk Cuntaka/Sebel, penodaan, kewajiban umum. Aturan busana terbaru belum tersedia di korpus |
| `pantai-melasti` | `PERDA_BALI_05_2020_PASAL_15` | `SE_GUB_04_2023_DONT` | Kewajiban umum dan larangan mengotori. Tidak ada aturan spesifik Melasti di korpus |

Chunk historis hanya muncul di bagian “Rujukan Historis” dan tidak dipakai
untuk AI brief.

## 3. API

| Metode | Path | Keterangan |
| :--- | :--- | :--- |
| `GET` | `/api/v1/zones` | Direktori zona |
| `GET` | `/api/v1/totem/{zone_id}?lang=id\|en` | Kartu deterministik + sitasi |
| `POST` | `/api/v1/totem/{zone_id}/brief` | AI brief grounded; fallback deterministik |

`POST /brief` masuk rate limit yang sama dengan Mode 1/2.

Respons kartu memuat:

- nama, kategori, lokasi, dan catatan cakupan;
- checklist praktis;
- `citations` hasil Layer-1;
- `historical_citations` terpisah;
- `tts_text`;
- `rules_version` dan `last_verified_date`.

## 4. AI Brief

Urutan:

1. Ambil kartu deterministik dan sitasi Layer-1.
2. Bangun evidence span IDs dari teks sitasi.
3. Kirim hanya sitasi aktif + span IDs + checklist ke Gemini dalam satu panggilan.
4. Minta JSON `summary_id`, `summary_en`, `claims[]` dengan `citation_id` dan `span_ids`.
5. Verifier Python memeriksa:
   - `citation_id` ada di hasil retrieval;
   - `span_ids` benar-benar milik sitasi tersebut;
   - tidak ada nomor pasal/nominal rupiah di luar bukti;
   - claim memakai span yang valid.
6. Jika `AI_MODE=required` dan AI gagal/abstain, UI menampilkan status eksplisit; template deterministik tidak menyamar sebagai jawaban AI. Jika `optional`, template dipakai untuk pengembangan.

Status yang dikembalikan:

- `ai_synthesis_status: "llm"` + `guard_status: "LLM_GROUNDED"`;
- `ai_synthesis_status: "deterministic"` + `guard_status: "FALLBACK_DETERMINISTIK"`;
- `ai_synthesis_status: "deterministic"` + `guard_status: "FALLBACK_GUARD"` bila
  output AI ditolak;
- `ai_synthesis_status: "unavailable"` + `guard_status: "AI_TIDAK_TERSEDIA"`;
- `ai_synthesis_status: "abstain"` + `guard_status: "AI_ABSTAIN"`.

## 5. UI

- `/totem` — direktori tiga gerbang + QR.
- `/totem/{zone_id}` — kartu gerbang, toggle ID/EN, AI brief, checklist, sitasi,
  rujukan historis, TTS, QR, dan konfirmasi lokal.
- Bahasa awal mengikuti `navigator.language`; pengguna dapat mengganti manual.
- TTS memakai Web Speech API dan harus dipicu tombol (bukan autoplay).
- Konfirmasi lokal disimpan di `localStorage` dengan kunci
  `pramana.totem.{zone_id}.{rules_version}`.

## 6. Demo 60 Detik

1. Buka `/totem`.
2. Pilih **Bandara I Gusti Ngurah Rai**.
3. Tunjukkan kartu EN, tekan **Play Audio**.
4. Buka salah satu sitasi dan tunjukkan `DOC:` + SHA-256.
5. Ganti ke ID.
6. Tekan **Tandai Sudah Dibaca** dan tunjukkan status lokal.
7. Kembali, buka **Pura Besakih**, dan tunjukkan bagian **Rujukan Historis**.

## 7. Menambah Zona

1. Pastikan chunk sudah ada di `corpus/bali_regulations.json` dan berstatus
   `verbatim`.
2. Tambahkan entri ke `corpus/zones.json`.
3. Isi `regulation_ids` hanya dengan chunk aktif.
4. Isi `historical_regulation_ids` hanya untuk chunk yang punya
   `superseded_by`/`status: "Disempurnakan"`.
5. Jalankan `pytest`; startup akan gagal jika referensi zona tidak valid.

## 8. Belum Diimplementasikan

- Offline/PWA dan cache kartu.
- Web NFC API.
- Check-in server-side atau verifikasi identitas.
- Bilingual penuh untuk Mode 1/2.
- Benchmark publik.
