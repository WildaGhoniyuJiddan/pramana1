# Audit Korpus dan Provenance — Pramana v1.2.0

Tanggal audit: **5 November 2026**

Dokumen ini menjelaskan bagaimana 21 entri manifest bantuan
(`bali_regulations.json`) dipetakan ke korpus Pramana. Manifest diperlakukan
sebagai **index dokumen**, bukan korpus siap pakai: manifest tidak memuat teks
pasal dan tidak otomatis boleh dikutip.

## 1. Prinsip yang Dipakai

1. **Registry terpisah dari chunk retrieval.** `documents` mencatat asal dan
   status dokumen; `regulations` hanya memuat chunk yang teksnya tersimpan dan
   boleh dipakai retrieval.
2. **Tidak mengarang teks.** Dokumen tanpa teks terverifikasi tetap berada di
   registry dengan `text_status: "belum-diambil"` atau `"non-verbatim"` dan
   `regulation_ids: []`.
3. **`is_verbatim` harus konsisten dengan `text_status`.** Chunk verbatim hanya
   boleh memakai `text_status: "verbatim"` (atau
   `"verbatim-teks-reproduksi-resmi"` bila sumbernya reproduksi portal resmi).
4. **Normalisasi hanya pada spasi/format.** Kata, istilah, angka, dan tanda
   baca tidak diubah. Ekstraksi PDF sering menyisipkan atau menghilangkan spasi
   (`( cashless)`, `perundang - undangan`); perbandingan audit dilakukan dengan
   menghapus seluruh spasi agar urutan karakter tetap teruji.
5. **Status URL manifest tidak diklaim sebagai verifikasi ulang.** Field
   `manifest_url_status_http` disalin dari manifest. Field `source_check`
   mencatat apa yang benar-benar dilakukan di repo ini (`pdf_downloaded`,
   `manifest_only`, `existing_corpus_chunk`). Pada 5 November 2026, 22 URL
   halaman sumber dicek dan semuanya merespons HTTP 200; pemeriksaan tautan ini
   tidak sama dengan verifikasi isi atau kesegaran dokumen.

## 2. Peta Tier

| Tier | Arti di Pramana | Contoh |
| :--- | :--- | :--- |
| `1A` | Hukum nasional (UU) | UU 15/2023, UU 18/2025, UU 6/2011 |
| `1B` | Hukum daerah (Perda/Pergub) | Perda 2/2025, Pergub 25/2025, Perda 4/2019 |
| `2` | Kebijakan/pedoman (SE, Seruan Bersama, Kepgub) | SE 7/2025, Seruan Bersama Nyepi |
| `3` | Norma adat (Awig-awig/Pararem) | Awig-awig Penglipuran dan Tenganan |

Manifest memberi tier `3` kepada Perda 4/2019 dan Pergub 4/2020. Di Pramana
keduanya dipetakan ke **`1B`** karena merupakan hukum daerah, bukan norma adat.
Tier `3` hanya dipakai untuk naskah Awig-awig/Pararem itu sendiri.

## 3. Audit 21 Entri Manifest

Kolom “Manifest” adalah status teks yang tercatat di manifest. Kolom “Pramana”
adalah keputusan korpus v1.2.0.

| # | ID manifest | Dokumen | Tier manifest → Pramana | Manifest | Pramana | Chunk |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `uu-15-2023` | UU 15/2023 tentang Provinsi Bali | 1 → 1A | verbatim | `verbatim` | `UU_15_2023_PASAL_8` |
| 2 | `uu-18-2025` | UU 18/2025 tentang Perubahan Ketiga UU 10/2009 | 1 → 1A | verbatim | `belum-diambil` | — |
| 3 | `uu-11-2010` | UU 11/2010 tentang Cagar Budaya | 1 → 1A | verbatim | `belum-diambil` | — |
| 4 | `uu-22-2009` | UU 22/2009 tentang Lalu Lintas dan Angkutan Jalan | 1 → 1A | verbatim | `belum-diambil` | — |
| 5 | `uu-6-2011` | UU 6/2011 tentang Keimigrasian | 1 → 1A | verbatim | `verbatim` | `UU_06_2011_PASAL_75` |
| 6 | `se-gubernur-bali-7-2025` | SE Gubernur Bali 7/2025 | 2 → 2 | non-verbatim | `non-verbatim` | — |
| 7 | `perda-bali-2-2025` | Perda Bali 2/2025 (perubahan Perda 6/2023) | 2 → 1B | verbatim | `verbatim` | `PERDA_BALI_06_2023_LEVY` |
| 8 | `perda-bali-6-2023` | Perda Bali 6/2023 tentang Pungutan WNA | 2 → 1B | verbatim | `belum-diambil` | — |
| 9 | `pergub-bali-2-2024` | Pergub Bali 2/2024 tentang Tata Cara Pembayaran | 2 → 1B | verbatim | `belum-diambil` | — |
| 10 | `pergub-bali-25-2025` | Pergub Bali 25/2025 (perubahan Pergub 2/2024) | 2 → 1B | verbatim | `verbatim` | `PERGUB_BALI_25_2025_PASAL_9_12` |
| 11 | `pergub-bali-36-2023` | Pergub Bali 36/2023 (dicabut) | 2 → 1B | belum-diambil | `belum-diambil` | — |
| 12 | `perda-bali-5-2020` | Perda Bali 5/2020 tentang Kepariwisataan Budaya Bali | 2 → 1B | verbatim | `verbatim` | `PERDA_BALI_05_2020_PASAL_15` |
| 13 | `pergub-bali-52-2021` | Pergub Bali 52/2021 (pelaksanaan Perda 5/2020) | 2 → 1B | verbatim | `belum-diambil` | — |
| 14 | `pergub-bali-25-2020` | Pergub Bali 25/2020 tentang Pelindungan Pura | 2 → 1B | verbatim | `verbatim` | `PERGUB_BALI_25_2020_PASAL_45_46` |
| 15 | `perda-bali-2-2023` | Perda Bali 2/2023 tentang RTRW 2023–2043 | 2 → 1B | verbatim | `belum-diambil` | — |
| 16 | `seruan-bersama-nyepi-2026` | Seruan Bersama Nyepi 2026 | 2 → 2 | verbatim-teks-reproduksi-resmi | `compilation` | `KETENTUAN_HARI_RAYA_NYEPI` |
| 17 | `kepgub-bali-699-2025` | Kepgub Bali 699/03-L/HK/2025 | 2 → 2 | belum-diambil | `belum-diambil` | — |
| 18 | `perda-bali-4-2019` | Perda Bali 4/2019 tentang Desa Adat | 3 → **1B** | verbatim | `verbatim` | `PERDA_BALI_04_2019_PASAL_1` |
| 19 | `pergub-bali-4-2020` | Pergub Bali 4/2020 (pelaksanaan Perda 4/2019) | 3 → **1B** | verbatim | `belum-diambil` | — |
| 20 | `awig-awig-desa-adat-penglipuran` | Awig-awig Desa Adat Penglipuran | 3 → 3 | non-verbatim | `non-verbatim` | — |
| 21 | `awig-awig-desa-adat-tenganan-pegringsingan` | Awig-awig Desa Adat Tenganan Pegringsingan | 3 → 3 | non-verbatim | `non-verbatim` | — |

Dokumen tambahan di luar manifest:

| ID | Dokumen | Tier | Status | Chunk |
| :--- | :--- | :--- | :--- | :--- |
| `se-gubernur-bali-4-2023` | SE Gubernur Bali 4/2023 (disempurnakan SE 7/2025) | 2 | `verbatim` | `SE_GUB_04_2023_DO`, `SE_GUB_04_2023_DONT` |

Dokumen legacy dipertahankan karena dua chunk Phase 0 sudah merujuk padanya.
Menghapusnya akan memutus provenance dan ID lama.

## 4. Sepuluh Chunk Retrieval

| Chunk | Dokumen | Status | Sumber teks |
| :--- | :--- | :--- | :--- |
| `SE_GUB_04_2023_DO` | `se-gubernur-bali-4-2023` | `verbatim` | PDF SE 4/2023, Pemkab Buleleng |
| `SE_GUB_04_2023_DONT` | `se-gubernur-bali-4-2023` | `verbatim` | PDF SE 4/2023, Pemkab Buleleng |
| `PERDA_BALI_05_2020_PASAL_15` | `perda-bali-5-2020` | `verbatim` | Chunk Phase 0; halaman BPK + PDF peraturan.go.id |
| `PERDA_BALI_06_2023_LEVY` | `perda-bali-2-2025` | `verbatim` | PDF BPK Perda 2/2025, Pasal 4A, 5, 16A |
| `UU_06_2011_PASAL_75` | `uu-6-2011` | `verbatim` | Chunk Phase 0; halaman peraturan.go.id |
| `KETENTUAN_HARI_RAYA_NYEPI` | `seruan-bersama-nyepi-2026` | `compilation` | Kompilasi pedoman tahunan; portal resmi BMC/Kesbangpol |
| `UU_15_2023_PASAL_8` | `uu-15-2023` | `verbatim` | PDF BPK, Pasal 8 ayat (3)–(4) |
| `PERGUB_BALI_25_2025_PASAL_9_12` | `pergub-bali-25-2025` | `verbatim` | PDF BPK, Pasal 9 dan 12 |
| `PERGUB_BALI_25_2020_PASAL_45_46` | `pergub-bali-25-2020` | `verbatim` | PDF BPK, Pasal 45–46 |
| `PERDA_BALI_04_2019_PASAL_1` | `perda-bali-4-2019` | `verbatim` | PDF Pemkab Buleleng, definisi Pasal 1 |

Alias kompatibilitas: `PERDA_BALI_02_2025_LEVY` → `PERDA_BALI_06_2023_LEVY`.
ID kanonis tetap ID lama agar `rag_engine.py`, test, dan respons API lama tidak
patah.

## 5. PDF Resmi dan SHA-256

PDF berikut diunduh pada audit ini dan diperiksa dengan `pypdf`:

| Dokumen | Ukuran | SHA-256 |
| :--- | :--- | :--- |
| UU 15/2023 | 850.718 B | `55CEFC4203F13AC308105529DDFEC3F9BF9151F8AB5E17B5E642586804F8EEEE` |
| UU 18/2025 | 3.351.210 B | `EEC25171D5E457DBDFAF8AC8AA4BF945C3A81382F463C85AFBFC5356A1644194` |
| Perda 2/2025 | 305.912 B | `B722B6208AEF750B485E0EE6AECB1A997CCC7A537D184B1EB207B77FE1280691` |
| Perda 6/2023 | 392.880 B | `84207BF2CCEF0DAB25FAEC1F1F8151C92EDF038002657BA8B05D4336AFAC6B1E` |
| Pergub 2/2024 | 431.898 B | `CD88EE1793C15224924A6BA804DD763B00D5A3CA2E7E600313AFF7B3662E5D24` |
| Pergub 25/2025 | 356.382 B | `DAD78B75B6EBB3C47E7734718D0BD950CBA595A6C737FD6670520F754EB5C525` |
| Pergub 25/2020 | 233.292 B | `FD670C346A7ED03DA5B87486DF7A697E429CEE12427EBA9685E450A12E03291D` |
| Perda 4/2019 | 733.712 B | `5BBFF1012865990AD3AE902A23AD86D349797D2BE8A0D1047107485C51559C34` |
| Pergub 4/2020 | 684.087 B | `208EEBB67AD6A518936F164CC5495949E76270496FAF95AAB8A5093BFC7DF8B1` |

PDF tidak disimpan di repo. Hash dicatat agar unduhan ulang dapat dibandingkan.

## 6. Keputusan Teknis per Kasus

### UU 18/2025 tidak dijadikan chunk

PDF resmi tersedia, tetapi lapisan OCR memuat artefak seperti `digunalan` dan
`2OO9`. Mengekstrak Pasal 57A dari lapisan tersebut berisiko mengklaim teks
yang tidak persis. Dokumen tetap di registry dengan `belum-diambil`.

### Perda 6/2023 tidak diduplikasi

Perda 2/2025 mengubah Pasal 4, 5, dan 16 Perda 6/2023. Chunk pungutan memakai
teks operatif Perda 2/2025 (Pasal 4A, 5, 16A) dan menautkan
`related_document_ids: ["perda-bali-6-2023"]`. Teks batang tubuh Perda 6/2023
tidak digabung agar tidak ada dua versi pasal yang bersaing.

### SE 7/2025 hanya registry

Sumber yang tersedia adalah artikel Bali Media Center, bukan PDF SE. Artikel
portal resmi tetap bukan naskah peraturan. Status `non-verbatim` dan
`retrieval_eligible: false` mencegahnya menjadi dasar jawaban.

### Seruan Bersama Nyepi adalah kompilasi

Manifest mencatat `verbatim-teks-reproduksi-resmi`, tetapi chunk korpus adalah
kompilasi pedoman tahunan (Catur Brata, penutupan bandara, pemadaman data).
Karena itu registry memakai `text_status: "compilation"` dan
`coverage: "secondary"`, sementara `manifest_text_status` tetap mencatat status
asli manifest.

### Awig-awig tidak diklaim verbatim

Naskah resmi Penglipuran dan Tenganan tidak dipublikasikan terbuka. Yang
tersedia hanya literatur akademik sekunder. Keduanya Tier 3, `non-verbatim`,
dan tidak diindeks.

### Kepgub 699/2025 dan Pergub 36/2023

Kepgub 699/2025 hanya terkonfirmasi eksistensinya lewat FAQ resmi Love Bali;
teks resminya belum ditemukan. Pergub 36/2023 sudah dicabut. Keduanya tidak
diambil dan tidak diindeks.

## 7. Verifikasi Kutipan

Setiap chunk verbatim baru dibandingkan dengan teks hasil ekstraksi PDF resmi.
Perbandingan dilakukan setelah menghapus seluruh spasi, sehingga artefak
pemisahan baris PDF tidak menghasilkan positif palsu. Seluruh paragraf pada
lima chunk baru cocok dengan urutan karakter PDF:

- `PERDA_BALI_06_2023_LEVY` → Perda 2/2025 (16/16 blok)
- `UU_15_2023_PASAL_8` → UU 15/2023 (2/2 blok)
- `PERGUB_BALI_25_2025_PASAL_9_12` → Pergub 25/2025 (7/7 blok)
- `PERGUB_BALI_25_2020_PASAL_45_46` → Pergub 25/2020 (10/10 blok)
- `PERDA_BALI_04_2019_PASAL_1` → Perda 4/2019 (6/6 blok)

Verifikasi ini membuktikan kutipan berasal dari PDF yang diunduh. Verifikasi ini
**bukan** verifikasi real-time ke JDIH dan tidak menjamin PDF tersebut masih
versi terbaru pada saat dibaca.

## 8. Batas yang Belum Ditutup

- 13 dari 21 dokumen manifest belum memiliki chunk retrieval.
- Status HTTP halaman sumber sudah dicek (22/22 merespons 200), tetapi isi
  halaman/PDF tidak diverifikasi untuk semua dokumen. `source_check` mencatat
  tingkat verifikasi yang sebenarnya per dokumen.
- UU 11/2010, UU 22/2009, Pergub 52/2021, Perda 2/2023, dan Kepgub 699/2025
  belum diunduh/diverifikasi di repo ini.
- Teks lengkap tidak disimpan; hanya kutipan pasal terpilih.
- Layer-1 hanya mencocokkan kutipan dengan chunk lokal, bukan dengan JDIH.
