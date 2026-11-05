// Svelte 5 reactive i18n state and dictionaries

const initialLang =
  typeof localStorage !== 'undefined'
    ? localStorage.getItem('pramana_lang') || 'id'
    : 'id';

export const i18n = $state({
  lang: initialLang
});

export function setLanguage(newLang) {
  const clean = newLang === 'en' ? 'en' : 'id';
  i18n.lang = clean;
  if (typeof localStorage !== 'undefined') {
    localStorage.setItem('pramana_lang', clean);
  }
}

export const DICT = {
  id: {
    nav: {
      home: 'Beranda',
      tripBrief: 'Trip Brief',
      contextNote: 'Context Note',
      gate: 'Gerbang',
      corpus: 'Korpus',
      settings: 'Pengaturan'
    },
    settings: {
      badge: '05 // PREFERENSI PENGGUNA',
      title: 'Pengaturan',
      subtitle: 'Sesuaikan bahasa antarmuka, suara panduan audio di tempat wisata, dan riwayat perangkat.',
      langCardTitle: 'BAHASA ANTARMUKA',
      langCardSubtitle: 'Pilih bahasa tampilan untuk seluruh halaman aplikasi.',
      idLabel: 'Bahasa Indonesia',
      idDesc: 'Bahasa resmi dan rujukan naskah peraturan hukum Bali.',
      enLabel: 'English',
      enDesc: 'International traveler guidance and translated summaries.',
      audioCardTitle: 'PANDUAN AUDIO GERBANG',
      audioCardSubtitle: 'Atur suara yang berbicara saat kamu tap atau scan gerbang di tempat wisata.',
      voiceLang: 'BAHASA SUARA',
      speed: 'KECEPATAN SUARA',
      speedSlow: '0.85x (Lambat)',
      speedNormal: '1.0x (Normal)',
      speedFast: '1.15x (Cepat)',
      testVoiceBtn: '🔊 Tes Suara Panduan',
      stopVoiceBtn: '⏹ Hentikan Suara',
      storageCardTitle: 'DATA & PENYIMPANAN PERANGKAT',
      storageCardSubtitle: 'Semua preferensi disimpan secara lokal di browser kamu.',
      storageDesc: 'Pramana tidak menyimpan akun atau data pribadi kamu di server cloud.',
      clearDataBtn: 'Hapus Riwayat Gerbang & Reset Pengaturan'
    },
    gate: {
      badge: '04 // PANDUAN LOKASI WISATA',
      title: 'Gerbang Pintar',
      titleAccent: 'Pramana',
      subtitle: 'Kartu kepatuhan langsung di lokasi. Pilih gerbang wisata, dengarkan audio panduan, dan patuhi aturan setempat.',
      tapNote: 'Halaman ini otomatis terbuka saat kamu tap stiker NFC atau scan QR di gerbang masuk tempat wisata.',
      openGate: 'Buka Gerbang',
      scanQrBtn: '📷 Pindai QR / Tap NFC',
      allGates: 'Semua Gerbang',
      activeChunks: 'aturan aktif',
      historicalChunks: 'catatan historis',
      version: 'Versi aturan',
      aiBrief: 'Panduan Singkat',
      playAudio: 'Dengarkan Audio Panduan',
      stopAudio: 'Hentikan Audio',
      checks: 'Panduan Utama di Lokasi',
      legalBasis: 'Dasar Hukum Resmi',
      share: 'Bagikan Gerbang Ini',
      copyLink: 'Salin Tautan',
      copied: 'Tautan disalin.',
      scope: 'Catatan Kawasan'
    },
    trip: {
      badge: '01 // PANDUAN PRA-PERJALANAN',
      title: 'Panduan Kepatuhan Rute & Kalender Bali',
      subtitle: 'Periksa kepatuhan rencana perjalanan kamu dari penutupan Hari Suci Nyepi 24 jam, aturan kawasan suci pura, dan retribusi wisman.',
      inputLabel: 'Rencana Aktivitas & Tujuan Kunjungan',
      placeholder: 'Tulis rencana perjalanan, destinasi pura, sewa kendaraan, atau jadwal tiba...',
      startDate: 'Tanggal Tiba',
      endDate: 'Tanggal Pulang',
      travelerType: 'Kategori Wisatawan',
      typeInt: 'Wisatawan Mancanegara / WNA (Wajib Love Bali Rp150.000)',
      typeDom: 'Wisatawan Nusantara / WNI (Bebas Pungutan Wisman)',
      submitBtn: 'Susun Panduan Kepatuhan',
      loadingBtn: 'Memeriksa Korpus Hukum...',
      privacyNote: 'Data reservasi (email, nomor paspor, kode booking) disamarkan otomatis sebelum analisis.',
      downloadIcs: 'Unduh Jadwal Kalender (.ICS)',
      loveBaliLink: 'Portal Resmi Love Bali (Rp150k) ↗'
    },
    context: {
      badge: '02 // VERIFIKASI FAKTA & HUKUM',
      title: 'Catatan Konteks Aturan Viral',
      subtitle: 'Masukkan klaim atau video viral seputar insiden wisata di Bali untuk mendapatkan pasal hukum resmi dan fakta objektif.',
      inputLabel: 'Teks Unggahan / Klaim Insiden',
      placeholder: 'Tempel teks berita, caption media sosial, atau klaim insiden wisatawan...',
      submitBtn: 'Periksa Fakta Hukum',
      loadingBtn: 'Memeriksa Korpus Resmi...',
      framingDetected: 'Deteksi Framing Emosional',
      neutralSummary: 'Ringkasan Konteks Netral',
      abstainMsg: 'Klaim ini berada di luar cakupan korpus hukum pariwisata Pramana. Sistem menolak berspekulasi.'
    },
    corpus: {
      badge: '03 // REGISTRY DOKUMEN',
      title: 'Korpus Regulasi Bali',
      subtitle: 'Telusuri 40 chunk pasal resmi dan 29 dokumen terverifikasi dari JDIH BPK dan Pemprov Bali.'
    }
  },
  en: {
    nav: {
      home: 'Home',
      tripBrief: 'Trip Brief',
      contextNote: 'Context Note',
      gate: 'Smart Gate',
      corpus: 'Corpus',
      settings: 'Settings'
    },
    settings: {
      badge: '05 // USER PREFERENCES',
      title: 'Settings',
      subtitle: 'Configure interface language, on-site audio guide voice, and device storage.',
      langCardTitle: 'INTERFACE LANGUAGE',
      langCardSubtitle: 'Choose the display language for the entire application.',
      idLabel: 'Bahasa Indonesia',
      idDesc: 'Official language of Balinese statutory legal texts.',
      enLabel: 'English',
      enDesc: 'International traveler guidance and translated summaries.',
      audioCardTitle: 'ON-SITE AUDIO GUIDE (TTS)',
      audioCardSubtitle: 'Configure the spoken voice when tapping or scanning gate totems on site.',
      voiceLang: 'VOICE LANGUAGE',
      speed: 'SPEECH SPEED',
      speedSlow: '0.85x (Slow)',
      speedNormal: '1.0x (Normal)',
      speedFast: '1.15x (Fast)',
      testVoiceBtn: '🔊 Test Audio Guide',
      stopVoiceBtn: '⏹ Stop Voice',
      storageCardTitle: 'DEVICE DATA & STORAGE',
      storageCardSubtitle: 'All preferences are stored locally on your device browser.',
      storageDesc: 'Pramana does not store your accounts or personal data on cloud servers.',
      clearDataBtn: 'Clear Gate History & Reset Preferences'
    },
    gate: {
      badge: '04 // ON-SITE COMPLIANCE',
      title: 'Smart Gate',
      titleAccent: 'Pramana',
      subtitle: 'Location-specific compliance cards. Select a destination, listen to audio guidance, and respect sacred cultural grounds.',
      tapNote: 'This page automatically opens when you tap an NFC sticker or scan the QR code at destination entrance gates.',
      openGate: 'Open Gate',
      scanQrBtn: '📷 Scan QR / Tap NFC',
      allGates: 'All Gates',
      activeChunks: 'active rules',
      historicalChunks: 'historical notes',
      version: 'Rule version',
      aiBrief: 'Executive Summary',
      playAudio: 'Play Spoken Audio Guide',
      stopAudio: 'Stop Audio',
      checks: 'Key Rules on Site',
      legalBasis: 'Verified Legal Basis',
      share: 'Share This Gate',
      copyLink: 'Copy Link',
      copied: 'Link copied.',
      scope: 'Zone Scope'
    },
    trip: {
      badge: '01 // PRE-TRAVEL GUIDANCE',
      title: 'Bali Itinerary Compliance & Sacred Calendar',
      subtitle: 'Verify your itinerary against the 24-hour Nyepi islandwide lockdown, temple dress codes, and foreign tourist levy.',
      inputLabel: 'Travel Itinerary & Planned Activities',
      placeholder: 'Enter your destinations, temple visits, scooter rentals, or arrival dates...',
      startDate: 'Arrival Date',
      endDate: 'Departure Date',
      travelerType: 'Traveler Category',
      typeInt: 'International Traveler / Foreigner (Love Bali Rp150,000 Levy Applies)',
      typeDom: 'Domestic Traveler / Indonesian Citizen (Levy Exempt)',
      submitBtn: 'Generate Compliance Dossier',
      loadingBtn: 'Checking Legal Corpus...',
      privacyNote: 'Reservation data (emails, passport numbers, booking codes) are automatically masked before analysis.',
      downloadIcs: 'Download Calendar (.ICS)',
      loveBaliLink: 'Official Love Bali Portal (Rp150k) ↗'
    },
    context: {
      badge: '02 // FACT & LAW VERIFICATION',
      title: 'Viral Incident Context Note',
      subtitle: 'Paste viral posts or social media claims regarding Bali tourism incidents to obtain objective legal grounds.',
      inputLabel: 'Social Media Caption / Incident Claim',
      placeholder: 'Paste news text, captions, or tourism controversy claims...',
      submitBtn: 'Verify Legal Facts',
      loadingBtn: 'Checking Official Corpus...',
      framingDetected: 'Sensational Framing Detected',
      neutralSummary: 'Neutral Context Note',
      abstainMsg: 'This claim is outside the scope of Pramana legal corpus. The system strictly abstains from speculation.'
    },
    corpus: {
      badge: '03 // DOCUMENT REGISTRY',
      title: 'Bali Legal Corpus',
      subtitle: 'Browse 40 verified statutory chunks and 29 audited legal documents from JDIH BPK and Bali Provincial Government.'
    }
  }
};
