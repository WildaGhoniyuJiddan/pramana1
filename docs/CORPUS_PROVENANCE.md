# Audit Korpus dan Provenance — Pramana v1.3.0

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
   `manifest_only`, `existing_corpus_chunk`). Pada 5 November 2026, 29 URL
   halaman sumber dicek; 28 merespons HTTP 200 dan 123dok menolak permintaan
   otomatis dengan HTTP 403. Pemeriksaan tautan ini tidak sama dengan
   verifikasi isi atau kesegaran dokumen.

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
adalah keputusan korpus v1.3.0.

| # | ID manifest | Dokumen | Tier manifest → Pramana | Manifest | Pramana | Chunk |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `uu-15-2023` | UU 15/2023 tentang Provinsi Bali | 1 → 1A | verbatim | `verbatim` | `UU_15_2023_PASAL_8` |
| 2 | `uu-18-2025` | UU 18/2025 tentang Perubahan Ketiga UU 10/2009 | 1 → 1A | verbatim | `verbatim-ocr-dibersihkan` | `UU_18_2025_*` (7 pasal) |
| 3 | `uu-11-2010` | UU 11/2010 tentang Cagar Budaya | 1 → 1A | verbatim | `belum-diambil` | — |
| 4 | `uu-22-2009` | UU 22/2009 tentang Lalu Lintas dan Angkutan Jalan | 1 → 1A | verbatim | `verbatim` | `UU_22_2009_PASAL_77_281`, `_PASAL_291` |
| 5 | `uu-6-2011` | UU 6/2011 tentang Keimigrasian | 1 → 1A | verbatim | `verbatim` | `UU_06_2011_PASAL_75` |
| 6 | `se-gubernur-bali-7-2025` | SE Gubernur Bali 7/2025 | 2 → 2 | non-verbatim | `non-verbatim` | — |
| 7 | `perda-bali-2-2025` | Perda Bali 2/2025 (perubahan Perda 6/2023) | 2 → 1B | verbatim | `verbatim` | `PERDA_BALI_06_2023_LEVY` |
| 8 | `perda-bali-6-2023` | Perda Bali 6/2023 tentang Pungutan WNA | 2 → 1B | verbatim | `verbatim` | `PERDA_BALI_06_2023_PASAL_12`, `_PASAL_14`, `_PENJELASAN_UMUM` |
| 9 | `pergub-bali-2-2024` | Pergub Bali 2/2024 tentang Tata Cara Pembayaran | 2 → 1B | verbatim | `verbatim` | `PERGUB_BALI_02_2024_PASAL_6`, `_PASAL_7`, `_PASAL_11` |
| 10 | `pergub-bali-25-2025` | Pergub Bali 25/2025 (perubahan Pergub 2/2024) | 2 → 1B | verbatim | `verbatim` | `PERGUB_BALI_25_2025_PASAL_9_12` |
| 11 | `pergub-bali-36-2023` | Pergub Bali 36/2023 (dicabut) | 2 → 1B | belum-diambil | `belum-diambil` | — |
| 12 | `perda-bali-5-2020` | Perda Bali 5/2020 tentang Kepariwisataan Budaya Bali | 2 → 1B | verbatim | `verbatim` | `PERDA_BALI_05_2020_PASAL_15`, `_PASAL_6`, `_PASAL_7`, `_PASAL_25`, `_PASAL_26` |
| 13 | `pergub-bali-52-2021` | Pergub Bali 52/2021 (pelaksanaan Perda 5/2020) | 2 → 1B | verbatim | `belum-diambil` | — |
| 14 | `pergub-bali-25-2020` | Pergub Bali 25/2020 tentang Pelindungan Pura | 2 → 1B | verbatim | `verbatim` | `PERGUB_BALI_25_2020_PASAL_45_46`, `_PASAL_3_4`, `_PASAL_10` |
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
| Perda 5/2020 | 365.390 B | `29BA107211524EFD858B6630E35BA59C1AD128982A982572DF3B5DFA59551D5B` |
| UU 40/2008 | 108.314 B | `81C4DB83E2880C4AD9951140EE426C78BBB2C79695D75F5749238C538D48B232` |
| UU 1/2024 | 2.178.368 B | `8CDB6721DD5F46E45F13E8A3588C6C1EFC614EA4361CE94EFEBE40E8E4289D5F` |
| UU 1/2023 | 24.793.845 B | `975FC86CFA63204EE21810CB7A99918C3A16B5FD47E58DADD9562C5FF3F1DFA0` |
| UU 39/1999 | 190.041 B | `069C6DDAAAFC356CA332779B3BDED58E9BF4C3BF78704DAAEA19241F6604AD6F` |
| UU 8/1999 | 192.920 B | `DF253C489E78E66D9DA5337C85BEBE1384C68763AF2001335B4880B0F225D816` |
| UU 22/2009 | 642.264 B | `30CA5AE5C81CEB5A9427A71E8BABFF6585E5399AB3859620BB425B67CFF5F16F` |

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

## 9. Tambahan Phase 2C — Korpus v1.3.0

Korpus memiliki **29 dokumen registry dan 42 chunk retrieval**. Sebanyak
30 chunk baru ditambahkan dari 10 dokumen: 5 dokumen baru dan 5 dokumen yang
sudah ada di registry:

| Dokumen | Chunk baru | Status |
| :--- | :--- | :--- |
| UU 18/2025 | 7 pasal | `verbatim-ocr-dibersihkan` |
| Perda 6/2023 | Pasal 12, 14, Penjelasan Umum | `verbatim` |
| Pergub 2/2024 | Pasal 6, 7, 11 | `verbatim` |
| Perda 5/2020 | Pasal 6, 7, 25, 26 | `verbatim` |
| Pergub 25/2020 | Pasal 3-4, 10 | `verbatim` |
| UU 40/2008 | 4 chunk | `verbatim` |
| UU 1/2024 | 2 chunk | `verbatim` |
| UU 1/2023 | 3 chunk | `verbatim` |
| UU 39/1999 | 1 chunk | `verbatim` |
| UU 8/1999 | 1 chunk | `verbatim` |

Tidak dimasukkan:

- **UU 18/2025 Pasal 20** — duplikasi klausul `e. pelayanan` pada teks PDF/OCR.
- **UU 18/2025 Pasal 24** — klausul `b. norma agama` tidak lengkap pada PDF resmi.
- **Perda 6/2023 Pasal 1, 4, 5, 6, 7** — diubah Perda 2/2025.
- **Pergub 2/2024 Pasal 9, 12** — diubah Pergub 25/2025; **Pasal 23** dihapus.
- **SE 7/2025, SE Kapolri 6/2015, SKB ITE 2021** — non-verbatim/sekunder;
  SE 7/2025 tetap registry-only.

Status baru `verbatim-ocr-dibersihkan` berarti teks berasal dari PDF resmi,
tetapi artefak OCR dibersihkan. Ini bukan transkripsi mentah dan tidak boleh
diklaim sebagai karakter-demi-karakter tanpa verifikasi ulang.

## 10. Batas yang Belum Ditutup

- 13 dari 21 dokumen manifest belum memiliki chunk retrieval.
- Status HTTP halaman sumber sudah dicek (28/29 merespons 200; 123dok menolak
  permintaan otomatis dengan 403), tetapi isi halaman/PDF tidak diverifikasi
  untuk semua dokumen. `source_check` mencatat tingkat verifikasi yang
  sebenarnya per dokumen.
- UU 11/2010, UU 22/2009, Pergub 52/2021, Perda 2/2023, dan Kepgub 699/2025
  belum diunduh/diverifikasi di repo ini.
- Teks lengkap tidak disimpan; hanya kutipan pasal terpilih.
- Layer-1 hanya mencocokkan kutipan dengan chunk lokal, bukan dengan JDIH.
