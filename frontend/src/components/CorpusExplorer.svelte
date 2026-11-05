<script>
  import { onMount } from 'svelte';
  import { fetchCorpus } from '../lib/api.js';
  import { i18n, DICT } from '../lib/i18n.svelte.js';

  let t = $derived(DICT[i18n.lang].corpus);

  let corpusData = $state(null);
  let loading = $state(true);
  let errorMsg = $state('');
  let searchQuery = $state('');
  let selectedTier = $state('ALL');
  let activeReg = $state(null);
  let activeDoc = $state(null);
  let viewMode = $state('chunks');

  let tierOptions = $derived([
    { id: 'ALL', label: i18n.lang === 'en' ? 'ALL' : 'SEMUA' },
    { id: '1A', label: 'T.1A // UU NASIONAL' },
    { id: '1B', label: 'T.1B // PERDA & PERGUB' },
    { id: '2', label: 'T.2 // SE & PEDOMAN' },
    { id: '3', label: 'T.3 // NORMA ADAT' }
  ]);

  const TEXT_STATUS_LABELS = {
    verbatim: { id: 'VERBATIM', en: 'VERBATIM' },
    'verbatim-ocr-dibersihkan': { id: 'VERBATIM (OCR)', en: 'VERBATIM (OCR)' },
    'verbatim-teks-reproduksi-resmi': { id: 'VERBATIM PORTAL', en: 'VERBATIM PORTAL' },
    compilation: { id: 'KOMPILASI', en: 'COMPILATION' },
    'non-verbatim': { id: 'NON-VERBATIM', en: 'NON-VERBATIM' },
    'belum-diambil': { id: 'BELUM DIAMBIL', en: 'PENDING EXTRACTION' }
  };

  const COVERAGE_LABELS = {
    full: { id: 'LENGKAP', en: 'FULL' },
    excerpt: { id: 'KUTIPAN', en: 'EXCERPT' },
    secondary: { id: 'SEKUNDER', en: 'SECONDARY' },
    none: { id: 'TIDAK ADA', en: 'NONE' }
  };

  const CATEGORY_MAP_EN = {
    "Kewajiban Wisman (Do's)": "Foreign Tourist Obligations (Do's)",
    "Larangan Wisman (Don'ts)": "Foreign Tourist Restrictions (Don'ts)",
    'Kewajiban Pengunjung & Wisatawan': 'Visitor & Tourist Obligations',
    'Pungutan Wisatawan Asing (Tourist Levy)': 'Foreign Tourist Levy (Love Bali)',
    'Tindakan Administratif Keimigrasian': 'Immigration Administrative Sanctions',
    'Hari Suci Nyepi (Catur Brata Penyepian)': 'Nyepi Holy Day (Catur Brata Observance)',
    'Dasar Kewenangan Pungutan Wisatawan Asing': 'Statutory Authority for Tourist Levy',
    'Tata Cara Pembayaran Pungutan (Data & Waktu)': 'Levy Payment Procedures (Data & Timing)',
    'Larangan & Sanksi Pelindungan Pura': 'Temple Protection Prohibitions & Sanctions',
    'Definisi Desa Adat & Awig-awig': 'Customary Village & Awig-awig Customary Law',
    'Definisi Kepariwisataan': 'Tourism Legal Definitions',
    'Ekosistem Kepariwisataan': 'Tourism Governance Ecosystem',
    'Kesempatan Prioritas Masyarakat Lokal': 'Local Community Priority Opportunities',
    'Desa Wisata': 'Tourism Village Regulations',
    'Hak Pelaku Usaha Pariwisata': 'Tourism Business Operator Rights',
    'Kewajiban Wisatawan': 'Statutory Tourist Obligations',
    'Pungutan Wisatawan Mancanegara': 'International Tourist Levy',
    'Manfaat Pungutan': 'Tourist Levy Fund Allocation',
    'Pembinaan dan Pengawasan Pungutan': 'Levy Supervision and Auditing',
    'Rasional Pungutan': 'Levy Rationale & Justification',
    'Pengecualian Pungutan': 'Levy Exemptions & Exclusions',
    'Pembebasan Pungutan': 'Levy Waiver Procedures',
    'Alur Pembayaran Pungutan': 'Levy Payment Workflow',
    'Standar Pengelola Daya Tarik Wisata': 'Tourist Attraction Management Standards',
    'Larangan Perusakan DTW': 'Prohibition on Damaging Tourism Attractions',
    'Pariwisata Digital': 'Digital Tourism Systems',
    'Portal Satu Pintu Pariwisata': 'Integrated Tourism Portal',
    'Fasilitasi Pelindungan Pura': 'Temple Sacred Ground Facilitation',
    'Pengamanan Pura': 'Temple Security & Pecalang Enforcement',
    'Definisi Diskriminasi Ras dan Etnis': 'Racial and Ethnic Discrimination Definitions',
    'Bentuk Diskriminasi': 'Forms of Prohibited Discrimination',
    'Pidana Diskriminasi': 'Criminal Penalties for Discrimination',
    'Pidana Kebencian dan Kekerasan': 'Criminal Penalties for Hate and Violence',
    'Larangan Ujaran Kebencian Elektronik': 'Prohibition on Electronic Hate Speech',
    'Pidana Ujaran Kebencian Elektronik': 'Criminal Sanctions for Online Hate Speech',
    'Pidana Permusuhan di Muka Umum': 'Public Incitement & Hostility Penalties',
    'Pidana Penyebaran Permusuhan': 'Dissemination of Hostility Penalties',
    'Pidana Diskriminasi Ras dan Etnis': 'Racial Discrimination Penalties',
    'Definisi Diskriminasi HAM': 'Human Rights Discrimination Definitions',
    'Hak Konsumen Non-Diskriminatif': 'Non-Discriminatory Consumer Rights'
  };

  function translateCategory(cat) {
    if (i18n.lang === 'en') {
      return CATEGORY_MAP_EN[cat] || cat;
    }
    return cat;
  }

  function translateStatus(status) {
    if (i18n.lang === 'en') {
      if (status === 'Berlaku') return 'Active';
      if (status === 'Disempurnakan') return 'Superseded';
      if (status === 'Berlaku Tahunan') return 'Annual Observance';
      if (status === 'Tidak berlaku') return 'Repealed';
      return status || 'Unrecorded';
    }
    return status || 'Tidak dicatat';
  }

  function translateTierLabel(label) {
    if (i18n.lang === 'en') {
      if (label === 'Pedoman Kebijakan') return 'Policy Guidance';
      if (label === 'Perda & Pergub') return 'Regional & Governor Regulation';
      if (label === 'UU Nasional') return 'National Law';
      if (label === 'Norma Adat') return 'Customary Law';
    }
    return label;
  }

  function textStatusLabel(status, isVerbatim) {
    const item = status ? TEXT_STATUS_LABELS[status] : null;
    if (item) return i18n.lang === 'en' ? item.en : item.id;
    return isVerbatim === false ? 'NON-VERBATIM' : 'VERBATIM';
  }

  function textStatusStyle(status, isVerbatim) {
    if (status === 'verbatim' || status === 'verbatim-ocr-dibersihkan' || status === 'verbatim-teks-reproduksi-resmi') {
      return 'background-color: #e7f0ff; color: #0c249c; border: 1px solid #0c249c;';
    }
    if (status === 'compilation' || status === 'non-verbatim') {
      return 'background-color: #fff3cd; color: #8a3b00; border: 1px solid #8a3b00;';
    }
    if (status === 'belum-diambil') {
      return 'background-color: #ece9e2; color: #5c5952; border: 1px solid #8c877c;';
    }
    return isVerbatim === false
      ? 'background-color: #fff3cd; color: #8a3b00; border: 1px solid #8a3b00;'
      : 'background-color: #e7f0ff; color: #0c249c; border: 1px solid #0c249c;';
  }

  function coverageLabel(value) {
    const item = COVERAGE_LABELS[value];
    if (item) return i18n.lang === 'en' ? item.en : item.id;
    return value || (i18n.lang === 'en' ? 'NONE' : 'TIDAK ADA');
  }

  function translateScope(scope) {
    if (i18n.lang === 'en' && scope) {
      if (scope.includes('21 dokumen diverifikasi per 2026-11-05')) {
        return '21 documents verified as of 2026-11-05 via Bali Provincial JDIH, National BPK JDIH, Ministry of Home Affairs JDIH, Directorate General of Immigration, and Parisada Hindu Dharma Indonesia. Primary sources prioritized; documents without official verbatim text marked non-retrieval.';
      }
    }
    return scope;
  }

  function translateGap(gap) {
    if (i18n.lang === 'en' && gap) {
      if (gap.includes('Perda 5/2020 pasal 33')) {
        return 'Regional Regulation 5/2020 Art. 33 (DTW damage prohibition) referenced via JDIH official consolidated text; full per-page OCR pending.';
      }
      if (gap.includes('SE PHDI 2026')) {
        return 'PHDI Circular 2026 is an annual decree; corpus must be updated each Saka New Year (next Nyepi).';
      }
      if (gap.includes('UU 6/2011 Pasal 75')) {
        return 'Immigration Law 6/2011 Art. 75(1) sourced from Directorate General of Immigration official text; Art. 75 is not among the articles amended by Law 63/2024 based on the official amendment text.';
      }
    }
    return gap;
  }

  function openRegulation(regId) {
    const reg = corpusData?.regulations?.find((item) => item.id === regId);
    if (reg) {
      activeReg = reg;
      viewMode = 'chunks';
    }
  }

  async function loadCorpus() {
    loading = true;
    errorMsg = '';
    try {
      corpusData = await fetchCorpus();
      if (corpusData?.regulations?.length) {
        activeReg = corpusData.regulations[0];
      }
      if (corpusData?.documents?.length) {
        activeDoc = corpusData.documents[0];
      }
    } catch (e) {
      console.error(e);
      errorMsg = i18n.lang === 'en'
        ? 'Failed to load regulation corpus. Ensure backend is running, then try again.'
        : 'Gagal memuat korpus regulasi. Pastikan backend berjalan, lalu coba lagi.';
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    loadCorpus();
  });

  let filteredRegs = $derived.by(() => {
    if (!corpusData?.regulations) return [];
    return corpusData.regulations.filter((reg) => {
      const matchesTier = selectedTier === 'ALL' || reg.tier === selectedTier;
      const q = searchQuery.trim().toLowerCase();
      if (!q) return matchesTier;
      const hay = `${reg.doc_title} ${reg.category} ${reg.pasal} ${reg.text} ${(reg.keywords || []).join(' ')}`.toLowerCase();
      return matchesTier && hay.includes(q);
    });
  });

  let filteredDocs = $derived.by(() => {
    if (!corpusData?.documents) return [];
    return corpusData.documents.filter((doc) => {
      const matchesTier = selectedTier === 'ALL' || doc.tier === selectedTier;
      const q = searchQuery.trim().toLowerCase();
      if (!q) return matchesTier;
      const hay = `${doc.title} ${doc.doc_type} ${doc.doc_number || ''} ${doc.year || ''} ${doc.status} ${doc.provenance_note || ''}`.toLowerCase();
      return matchesTier && hay.includes(q);
    });
  });
</script>

<div
  class="mx-auto"
  style="max-width: 1360px; width: 100%; border-left: 1px solid #cdc9be; border-right: 1px solid #cdc9be; background-color: #e6e4de; color: #0a0a0a;"
>
  <!-- 1. EDITORIAL HEADER BAR -->
  <section
    class="px-5 sm:px-10 py-6 sm:py-8"
    style="border-bottom: 1px solid #cdc9be; background-color: #e6e4de;"
  >
    <div class="flex flex-col lg:flex-row lg:items-end justify-between gap-5">
      <div>
        <div
          class="inline-flex items-center text-xs font-medium mb-3"
          style="background-color: #0c249c; color: #ffffff; padding: 2px; border: 1.5px solid #0a0a0a; box-shadow: 2px 2px 0px #0a0a0a;"
        >
          <span
            style="background-color: #dfd6c3; color: #0a0a0a;"
            class="px-2 py-0.5 font-mono text-[10px] font-bold"
          >
            03
          </span>
          <span class="px-3 py-0.5 text-[11px] font-semibold">{t.badge}</span>
        </div>

        <h1 class="opero-h1 text-[30px] sm:text-[42px]">
          {t.title}
        </h1>
        <p class="text-xs sm:text-[13px] mt-1 max-w-xl" style="color: #4a4740;">
          {t.subtitle}
        </p>
      </div>

      <!-- Search & Tier Filter -->
      <div class="flex flex-wrap items-center gap-2">
        <input
          type="search"
          bind:value={searchQuery}
          placeholder={t.searchPlaceholder}
          style="background-color: #ffffff; color: #0a0a0a; border: 1.5px solid #0a0a0a;"
          class="px-3 py-1.5 text-xs font-mono focus:outline-none w-56"
        />

        {#each tierOptions as opt}
          <button
            type="button"
            onclick={() => (selectedTier = opt.id)}
            style={selectedTier === opt.id
              ? 'background-color: #0c249c; color: #ffffff; border: 1.5px solid #0a0a0a; box-shadow: 2px 2px 0px #0a0a0a;'
              : 'background-color: #f3f1eb; color: #0a0a0a; border: 1.5px solid #0a0a0a;'}
            class="brutal-press px-2.5 py-1.5 font-mono text-[11px] font-semibold cursor-pointer"
          >
            {opt.label}
          </button>
        {/each}
      </div>
    </div>
  </section>

  <!-- 2. WORKSPACE GRID -->
  <section class="px-5 sm:px-10 py-6 sm:py-8">
    {#if loading}
      <div class="p-12 text-center font-mono text-xs" style="color: #5c5952;">
        {t.loading}
      </div>
    {:else if errorMsg}
      <div class="brutal-card p-6 space-y-3" style="background-color: #ffffff; border-color: #c92a2a;">
        <p class="text-sm font-medium" style="color: #c92a2a;">{errorMsg}</p>
        <button
          type="button"
          onclick={loadCorpus}
          style="background-color: #0c249c; color: #ffffff; border: 1.5px solid #0a0a0a; box-shadow: 2px 2px 0px #0a0a0a;"
          class="brutal-press px-3 py-1.5 font-mono text-[11px] font-semibold cursor-pointer"
        >
          {i18n.lang === 'en' ? 'Try Again' : 'Coba Lagi'}
        </button>
      </div>
    {:else if corpusData}
      {#if corpusData.metadata}
        <div class="brutal-card p-4 sm:p-5 mb-5 space-y-2" style="background-color: #f3f1eb;">
          <div class="flex flex-wrap items-center justify-between gap-2">
            <span class="font-mono text-[10px] font-bold px-2 py-0.5" style="background-color: #dfd6c3; color: #0a0a0a; border: 1px solid #0a0a0a;">
              {i18n.lang === 'en' ? 'CORPUS PROVENANCE' : 'PROVENANCE KORPUS'} · v{corpusData.metadata.version || '-'}
            </span>
            <span class="font-mono text-[11px]" style="color: #5c5952;">
              {i18n.lang === 'en' ? 'Verified:' : 'Diverifikasi:'} {corpusData.metadata.last_verified_date || corpusData.metadata.last_updated || '-'}
            </span>
          </div>
          {#if corpusData.metadata.verification_scope}
            <p class="text-[11px] leading-snug" style="color: #3a3935;">
              {translateScope(corpusData.metadata.verification_scope)}
            </p>
          {/if}

          <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-1">
            <div class="p-2.5" style="background-color: #ffffff; border: 1px solid #0a0a0a;">
              <span class="font-mono text-[9px] uppercase block" style="color: #5c5952;">
                {i18n.lang === 'en' ? 'Document Registry' : 'Dokumen Registry'}
              </span>
              <span class="font-mono text-lg font-bold" style="color: #0a0a0a;">
                {corpusData.documents?.length ?? corpusData.metadata.total_documents ?? 0}
              </span>
            </div>
            <div class="p-2.5" style="background-color: #ffffff; border: 1px solid #0a0a0a;">
              <span class="font-mono text-[9px] uppercase block" style="color: #5c5952;">
                {i18n.lang === 'en' ? 'Manifest Entries' : 'Entri Manifest'}
              </span>
              <span class="font-mono text-lg font-bold" style="color: #0a0a0a;">
                {corpusData.metadata.total_manifest_documents ?? '-'}
              </span>
            </div>
            <div class="p-2.5" style="background-color: #ffffff; border: 1px solid #0a0a0a;">
              <span class="font-mono text-[9px] uppercase block" style="color: #5c5952;">
                {i18n.lang === 'en' ? 'Retrieval Chunks' : 'Chunk Retrieval'}
              </span>
              <span class="font-mono text-lg font-bold" style="color: #0c249c;">
                {corpusData.regulations?.length ?? 0}
              </span>
            </div>
            <div class="p-2.5" style="background-color: #ffffff; border: 1px solid #0a0a0a;">
              <span class="font-mono text-[9px] uppercase block" style="color: #5c5952;">
                {i18n.lang === 'en' ? 'Chunked Documents' : 'Dokumen Ber-Chunk'}
              </span>
              <span class="font-mono text-lg font-bold" style="color: #0a0a0a;">
                {corpusData.documents?.filter((doc) => doc.regulation_ids?.length).length ?? 0}
              </span>
            </div>
          </div>

          <div class="flex flex-wrap gap-2 pt-1">
            <button
              type="button"
              onclick={() => (viewMode = 'chunks')}
              style={viewMode === 'chunks'
                ? 'background-color: #0c249c; color: #ffffff; border: 1.5px solid #0a0a0a; box-shadow: 2px 2px 0px #0a0a0a;'
                : 'background-color: #ffffff; color: #0a0a0a; border: 1.5px solid #0a0a0a;'}
              class="brutal-press px-3 py-1.5 font-mono text-[10px] font-bold cursor-pointer"
            >
              {i18n.lang === 'en' ? 'RETRIEVAL CHUNKS' : 'CHUNK RETRIEVAL'} ({filteredRegs.length})
            </button>
            <button
              type="button"
              onclick={() => (viewMode = 'registry')}
              style={viewMode === 'registry'
                ? 'background-color: #0c249c; color: #ffffff; border: 1.5px solid #0a0a0a; box-shadow: 2px 2px 0px #0a0a0a;'
                : 'background-color: #ffffff; color: #0a0a0a; border: 1.5px solid #0a0a0a;'}
              class="brutal-press px-3 py-1.5 font-mono text-[10px] font-bold cursor-pointer"
            >
              {i18n.lang === 'en' ? 'DOCUMENT REGISTRY' : 'REGISTRY DOKUMEN'} ({filteredDocs.length})
            </button>
          </div>
          {#if corpusData.metadata.known_gaps?.length}
            <div class="p-3 text-[11px] leading-snug" style="background-color: #fff3cd; border: 1px solid #8a3b00; color: #5c2d00;">
              <strong>{i18n.lang === 'en' ? 'Known limitations:' : 'Keterbatasan yang diketahui:'}</strong>
              <ul class="list-disc pl-4 mt-1 space-y-0.5">
                {#each corpusData.metadata.known_gaps as gap}
                  <li>{translateGap(gap)}</li>
                {/each}
              </ul>
            </div>
          {/if}
        </div>
      {/if}

      {#if viewMode === 'chunks'}
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">

        <!-- LEFT COLUMN: INSTRUMENT SELECTOR (5 cols) -->
        <div class="lg:col-span-5">
          <div class="brutal-card p-5 space-y-3" style="background-color: #f3f1eb;">
            <div class="flex items-center justify-between pb-2.5" style="border-bottom: 1px solid #cdc9be;">
              <span class="font-mono text-[10px] font-bold px-2 py-0.5" style="background-color: #dfd6c3; color: #0a0a0a; border: 1px solid #0a0a0a;">
                {i18n.lang === 'en' ? 'INSTRUMENT DIRECTORY' : 'DAFTAR INSTRUMEN'} ({filteredRegs.length})
              </span>
              <span class="font-mono text-[11px]" style="color: #5c5952;">
                {i18n.lang === 'en' ? 'Public Domain Law 28/2014' : 'Domain Publik UU 28/2014'}
              </span>
            </div>

            <div class="space-y-2">
              {#each filteredRegs as reg, idx}
                <button
                  type="button"
                  onclick={() => (activeReg = reg)}
                  style={activeReg?.id === reg.id
                    ? 'background-color: #0c249c; color: #ffffff; border: 1.5px solid #0a0a0a; box-shadow: 2px 2px 0px #0a0a0a;'
                    : 'background-color: #ffffff; color: #0a0a0a; border: 1.5px solid #0a0a0a;'}
                  class="brutal-press w-full text-left p-3.5 block cursor-pointer"
                >
                  <div class="flex items-center justify-between gap-2 font-mono text-[10px]">
                    <span style={activeReg?.id === reg.id ? 'color: #dfd6c3; font-weight: 700;' : 'color: #0c249c; font-weight: 700;'}>
                      {String(idx + 1).padStart(2, '0')} // {i18n.lang === 'en' ? 'TIER' : 'TINGKAT'} {reg.tier}
                    </span>
                    <span style={activeReg?.id === reg.id ? 'color: #dfd6c3;' : 'color: #5c5952;'}>
                      {reg.pasal}
                    </span>
                  </div>
                  <h3 class="text-xs sm:text-sm font-semibold mt-1 leading-snug">{translateCategory(reg.category)}</h3>
                  <div class="flex flex-wrap gap-1.5 mt-2 font-mono text-[9px] font-bold">
                    <span class="px-1.5 py-0.5" style="background-color: #f3f1eb; color: #0a0a0a; border: 1px solid #0a0a0a;">
                      {translateStatus(reg.status)}
                    </span>
                    <span
                      class="px-1.5 py-0.5"
                      style={textStatusStyle(reg.text_status, reg.is_verbatim)}
                    >
                      {textStatusLabel(reg.text_status, reg.is_verbatim)}
                    </span>
                  </div>
                </button>
              {/each}
            </div>
          </div>
        </div>

        <!-- RIGHT COLUMN: ACTIVE DOCUMENT READER (7 cols) -->
        <div class="lg:col-span-7">
          {#if activeReg}
            <div class="brutal-card p-6 sm:p-7 space-y-5" style="background-color: #ffffff;">
              <div class="flex flex-wrap items-center justify-between gap-2 pb-4" style="border-bottom: 1px solid #cdc9be;">
                <span class="font-mono text-[10px] font-bold px-2 py-0.5" style="background-color: #0c249c; color: #ffffff; border: 1px solid #0a0a0a;">
                  ID: {activeReg.id} · {translateTierLabel(activeReg.tier_label)}
                </span>

                {#if activeReg.source_url}
                  <a
                    href={activeReg.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    style="background-color: #dfd6c3; color: #0a0a0a; border: 1.5px solid #0a0a0a; box-shadow: 2px 2px 0px #0a0a0a;"
                    class="brutal-press px-3 py-1 font-mono text-[11px] font-bold inline-flex items-center gap-1.5"
                  >
                    <span>{i18n.lang === 'en' ? 'Open Official Source' : 'Buka Sumber Resmi'}</span>
                    <span>↗</span>
                  </a>
                {/if}
              </div>

              <div class="space-y-1.5">
                <span class="font-mono text-[10px] uppercase font-bold block" style="color: #5c5952;">
                  {activeReg.bab} · {activeReg.pasal}
                </span>
                <h2 class="text-lg sm:text-xl font-medium leading-snug" style="color: #0a0a0a;">
                  {activeReg.doc_title}
                </h2>
              </div>

              <div class="flex flex-wrap gap-1.5">
                <span class="font-mono text-[10px] font-bold px-2 py-0.5" style="background-color: #f3f1eb; color: #0a0a0a; border: 1px solid #0a0a0a;">
                  {i18n.lang === 'en' ? 'Status' : 'Status'}: {translateStatus(activeReg.status)}
                </span>
                <span
                  class="font-mono text-[10px] font-bold px-2 py-0.5"
                  style={textStatusStyle(activeReg.text_status, activeReg.is_verbatim)}
                >
                  {textStatusLabel(activeReg.text_status, activeReg.is_verbatim)}
                </span>
                {#if activeReg.document_id}
                  <button
                    type="button"
                    onclick={() => { viewMode = 'registry'; activeDoc = corpusData.documents?.find((doc) => doc.id === activeReg.document_id) || activeDoc; }}
                    class="font-mono text-[10px] font-bold px-2 py-0.5 cursor-pointer"
                    style="background-color: #ffffff; color: #0c249c; border: 1px solid #0c249c;"
                  >
                    Registry: {activeReg.document_id}
                  </button>
                {/if}
                {#if activeReg.last_verified_date}
                  <span class="font-mono text-[10px] font-bold px-2 py-0.5" style="background-color: #ffffff; color: #5c5952; border: 1px solid #cdc9be;">
                    {i18n.lang === 'en' ? 'Verified' : 'Diverifikasi'} {activeReg.last_verified_date}
                  </span>
                {/if}
              </div>

              {#if activeReg.status_note}
                <p class="text-[11px] leading-snug" style="color: #8a3b00;">{activeReg.status_note}</p>
              {/if}
              {#if activeReg.source_note}
                <p class="text-[11px] leading-snug" style="color: #5c5952;">{i18n.lang === 'en' ? 'Source note:' : 'Catatan sumber:'} {activeReg.source_note}</p>
              {/if}
              {#if activeReg.superseded_by}
                <p class="text-[11px] leading-snug" style="color: #5c5952;">
                  {i18n.lang === 'en' ? 'Superseded by:' : 'Disempurnakan oleh:'}
                  {#if activeReg.superseded_by_url}
                    <a href={activeReg.superseded_by_url} target="_blank" rel="noopener noreferrer" class="underline" style="color: #0c249c;">
                      {activeReg.superseded_by}
                    </a>
                  {:else}
                    {activeReg.superseded_by}
                  {/if}
                </p>
              {/if}

              <div class="space-y-2">
                <span class="font-mono text-[10px] uppercase font-bold block" style="color: #0c249c;">
                  {activeReg.is_verbatim === false
                    ? (i18n.lang === 'en' ? 'Stored Text (Compilation / Non-Verbatim)' : 'Teks Tersimpan (Kompilasi/Non-Verbatim)')
                    : (i18n.lang === 'en' ? 'Stored Text (Layer-1 Corpus Reference)' : 'Teks Tersimpan (Rujukan Layer-1 Korpus)')}
                </span>
                <div
                  class="p-4 sm:p-5 text-xs sm:text-[13px] leading-relaxed whitespace-pre-line"
                  style="background-color: #f3f1eb; border: 1.5px solid #0a0a0a; color: #0a0a0a;"
                >
                  {activeReg.text}
                </div>
                {#if activeReg.is_verbatim === false}
                  <p class="font-mono text-[10px] leading-snug" style="color: #8a3b00;">
                    {i18n.lang === 'en'
                      ? 'This entry is a summary/compilation. Do not cite as verbatim statutory wording.'
                      : 'Entri ini adalah ringkasan/kompilasi. Jangan dikutip sebagai bunyi pasal verbatim.'}
                  </p>
                {/if}
              </div>

              {#if activeReg.penalties}
                <div
                  class="p-4 text-xs space-y-1"
                  style="background-color: #dfd6c3; border: 1.5px solid #0a0a0a; color: #0a0a0a;"
                >
                  <span class="font-mono text-[10px] uppercase font-bold block">
                    {i18n.lang === 'en' ? 'Sanctions & Enforcement Provisions' : 'Ketentuan Sanksi & Penegakan'}
                  </span>
                  <p class="leading-relaxed">{activeReg.penalties}</p>
                </div>
              {/if}

              {#if activeReg.keywords && activeReg.keywords.length > 0}
                <div class="pt-2 flex flex-wrap gap-1.5">
                  {#each activeReg.keywords as kw}
                    <span
                      class="px-2 py-0.5 font-mono text-[10px] font-semibold"
                      style="background-color: #f3f1eb; border: 1px solid #0a0a0a; color: #0a0a0a;"
                    >
                      #{kw}
                    </span>
                  {/each}
                </div>
              {/if}
            </div>
          {/if}
        </div>

      </div>
      {:else}
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        <!-- LEFT COLUMN: DOCUMENT REGISTRY -->
        <div class="lg:col-span-5">
          <div class="brutal-card p-5 space-y-3" style="background-color: #f3f1eb;">
            <div class="flex items-center justify-between pb-2.5" style="border-bottom: 1px solid #cdc9be;">
              <span class="font-mono text-[10px] font-bold px-2 py-0.5" style="background-color: #dfd6c3; color: #0a0a0a; border: 1px solid #0a0a0a;">
                {i18n.lang === 'en' ? 'DOCUMENT REGISTRY' : 'REGISTRY DOKUMEN'} ({filteredDocs.length})
              </span>
              <span class="font-mono text-[11px]" style="color: #5c5952;">
                {i18n.lang === 'en' ? 'Registry is not evidence of quotation' : 'Registry bukan bukti kutipan'}
              </span>
            </div>

            <div class="space-y-2 lg:max-h-[68vh] lg:overflow-y-auto lg:pr-1">
              {#each filteredDocs as doc, idx}
                <button
                  type="button"
                  onclick={() => (activeDoc = doc)}
                  style={activeDoc?.id === doc.id
                    ? 'background-color: #0c249c; color: #ffffff; border: 1.5px solid #0a0a0a; box-shadow: 2px 2px 0px #0a0a0a;'
                    : 'background-color: #ffffff; color: #0a0a0a; border: 1.5px solid #0a0a0a;'}
                  class="brutal-press w-full text-left p-3.5 block cursor-pointer"
                >
                  <div class="flex items-center justify-between gap-2 font-mono text-[10px]">
                    <span style={activeDoc?.id === doc.id ? 'color: #dfd6c3; font-weight: 700;' : 'color: #0c249c; font-weight: 700;'}>
                      {String(idx + 1).padStart(2, '0')} // {doc.doc_type.toUpperCase()}
                    </span>
                    <span style={activeDoc?.id === doc.id ? 'color: #dfd6c3;' : 'color: #5c5952;'}>
                      {doc.year || '-'} · T{doc.tier}
                    </span>
                  </div>
                  <h3 class="text-xs sm:text-sm font-semibold mt-1 leading-snug">{doc.title}</h3>
                  <div class="flex flex-wrap gap-1.5 mt-2 font-mono text-[9px] font-bold">
                    <span
                      class="px-1.5 py-0.5"
                      style={textStatusStyle(doc.text_status, false)}
                    >
                      {textStatusLabel(doc.text_status, false)}
                    </span>
                    <span class="px-1.5 py-0.5" style="background-color: #f3f1eb; color: #0a0a0a; border: 1px solid #0a0a0a;">
                      {doc.retrieval_eligible ? `${doc.regulation_ids.length} CHUNK` : (i18n.lang === 'en' ? 'NOT INDEXED' : 'TIDAK DIINDEKS')}
                    </span>
                  </div>
                </button>
              {/each}
            </div>
          </div>
        </div>

        <!-- RIGHT COLUMN: REGISTRY DETAIL -->
        <div class="lg:col-span-7">
          {#if activeDoc}
            <div class="brutal-card p-6 sm:p-7 space-y-5" style="background-color: #ffffff;">
              <div class="flex flex-wrap items-center justify-between gap-2 pb-4" style="border-bottom: 1px solid #cdc9be;">
                <span class="font-mono text-[10px] font-bold px-2 py-0.5" style="background-color: #0c249c; color: #ffffff; border: 1px solid #0a0a0a;">
                  DOC: {activeDoc.id} · {i18n.lang === 'en' ? 'TIER' : 'TINGKAT'} {activeDoc.tier}
                </span>
                {#if activeDoc.source_url}
                  <a
                    href={activeDoc.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    style="background-color: #dfd6c3; color: #0a0a0a; border: 1.5px solid #0a0a0a; box-shadow: 2px 2px 0px #0a0a0a;"
                    class="brutal-press px-3 py-1 font-mono text-[11px] font-bold inline-flex items-center gap-1.5"
                  >
                    <span>{i18n.lang === 'en' ? 'Source Page' : 'Halaman Sumber'}</span>
                    <span>↗</span>
                  </a>
                {/if}
              </div>

              <div class="space-y-1.5">
                <span class="font-mono text-[10px] uppercase font-bold block" style="color: #5c5952;">
                  {activeDoc.doc_type} {activeDoc.doc_number || ''} · {activeDoc.year || (i18n.lang === 'en' ? 'Year unrecorded' : 'Tahun tidak dicatat')}
                </span>
                <h2 class="text-lg sm:text-xl font-medium leading-snug" style="color: #0a0a0a;">
                  {activeDoc.title}
                </h2>
              </div>

              <div class="flex flex-wrap gap-1.5">
                <span class="font-mono text-[10px] font-bold px-2 py-0.5" style="background-color: #f3f1eb; color: #0a0a0a; border: 1px solid #0a0a0a;">
                  {i18n.lang === 'en' ? 'Status' : 'Status'}: {translateStatus(activeDoc.status)}
                </span>
                <span class="font-mono text-[10px] font-bold px-2 py-0.5" style={textStatusStyle(activeDoc.text_status, false)}>
                  {textStatusLabel(activeDoc.text_status, false)}
                </span>
                <span class="font-mono text-[10px] font-bold px-2 py-0.5" style="background-color: #ffffff; color: #5c5952; border: 1px solid #cdc9be;">
                  {i18n.lang === 'en' ? 'Coverage' : 'Cakupan'}: {coverageLabel(activeDoc.coverage)}
                </span>
                <span
                  class="font-mono text-[10px] font-bold px-2 py-0.5"
                  style={activeDoc.retrieval_eligible
                    ? 'background-color: #e7f0ff; color: #0c249c; border: 1px solid #0c249c;'
                    : 'background-color: #ece9e2; color: #5c5952; border: 1px solid #8c877c;'}
                >
                  {activeDoc.retrieval_eligible ? (i18n.lang === 'en' ? 'RETRIEVAL ELIGIBLE' : 'BOLEH RETRIEVAL') : 'REGISTRY-ONLY'}
                </span>
                <span class="font-mono text-[10px] font-bold px-2 py-0.5" style="background-color: #ffffff; color: #5c5952; border: 1px solid #cdc9be;">
                  {activeDoc.in_manifest ? 'MANIFEST 21' : (i18n.lang === 'en' ? 'LEGACY DOCUMENT' : 'DOKUMEN LEGACY')}
                </span>
              </div>

              {#if activeDoc.status_note}
                <p class="text-[11px] leading-snug" style="color: #8a3b00;">{activeDoc.status_note}</p>
              {/if}
              {#if activeDoc.provenance_note}
                <p class="text-[11px] leading-snug" style="color: #5c5952;">
                  {i18n.lang === 'en' ? 'Provenance note:' : 'Catatan provenance:'} {activeDoc.provenance_note}
                </p>
              {/if}

              <div class="p-4 space-y-2" style="background-color: #f3f1eb; border: 1.5px solid #0a0a0a;">
                <span class="font-mono text-[10px] uppercase font-bold block" style="color: #0c249c;">
                  {i18n.lang === 'en' ? 'Connected Retrieval Chunks' : 'Chunk Retrieval Terhubung'} ({activeDoc.regulation_ids?.length || 0})
                </span>
                {#if activeDoc.regulation_ids?.length}
                  <div class="flex flex-wrap gap-2">
                    {#each activeDoc.regulation_ids as regId}
                      <button
                        type="button"
                        onclick={() => openRegulation(regId)}
                        class="brutal-press px-2.5 py-1.5 font-mono text-[10px] font-bold cursor-pointer"
                        style="background-color: #ffffff; color: #0c249c; border: 1px solid #0c249c;"
                      >
                        {regId} ↗
                      </button>
                    {/each}
                  </div>
                {:else}
                  <p class="text-[11px] leading-snug" style="color: #8a3b00;">
                    {i18n.lang === 'en'
                      ? 'No chunks are indexed for this document. Registry does not expand retrieval results and cannot form the basis for answers.'
                      : 'Tidak ada chunk yang diindeks untuk dokumen ini. Registry tidak menambah hasil retrieval dan tidak boleh dijadikan dasar jawaban.'}
                  </p>
                {/if}
              </div>

              <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div class="p-3 space-y-1" style="background-color: #faf9f6; border: 1px solid #dcd7cb;">
                  <span class="font-mono text-[9px] uppercase font-bold block" style="color: #5c5952;">
                    {i18n.lang === 'en' ? 'Source URL' : 'Sumber Halaman'}
                  </span>
                  {#if activeDoc.source_url}
                    <a href={activeDoc.source_url} target="_blank" rel="noopener noreferrer" class="text-[11px] underline break-all" style="color: #0c249c;">
                      {activeDoc.source_url}
                    </a>
                  {:else}
                    <span class="text-[11px]">-</span>
                  {/if}
                </div>
                <div class="p-3 space-y-1" style="background-color: #faf9f6; border: 1px solid #dcd7cb;">
                  <span class="font-mono text-[9px] uppercase font-bold block" style="color: #5c5952;">
                    {i18n.lang === 'en' ? 'Official PDF' : 'PDF Resmi'}
                  </span>
                  {#if activeDoc.source_pdf_url}
                    <a href={activeDoc.source_pdf_url} target="_blank" rel="noopener noreferrer" class="text-[11px] underline break-all" style="color: #0c249c;">
                      {i18n.lang === 'en' ? 'Open PDF ↗' : 'Buka PDF ↗'}
                    </a>
                  {:else}
                    <span class="text-[11px]" style="color: #8a3b00;">
                      {i18n.lang === 'en' ? 'Not available yet' : 'Belum tersedia'}
                    </span>
                  {/if}
                </div>
              </div>

              {#if activeDoc.source_pdf_sha256}
                <p class="font-mono text-[10px] leading-relaxed break-all" style="color: #5c5952;">
                  SHA-256 PDF: {activeDoc.source_pdf_sha256}
                </p>
              {/if}

              <div class="flex flex-wrap gap-1.5 font-mono text-[10px]">
                <span class="px-2 py-0.5" style="background-color: #f3f1eb; border: 1px solid #0a0a0a;">
                  source_check: {activeDoc.source_check || '-'}
                </span>
                <span class="px-2 py-0.5" style="background-color: #f3f1eb; border: 1px solid #0a0a0a;">
                  manifest_text: {activeDoc.manifest_text_status || '-'}
                </span>
                <span class="px-2 py-0.5" style="background-color: #f3f1eb; border: 1px solid #0a0a0a;">
                  manifest_http: {activeDoc.manifest_url_status_http ?? '-'}
                </span>
                {#if activeDoc.last_verified_date}
                  <span class="px-2 py-0.5" style="background-color: #ffffff; border: 1px solid #cdc9be; color: #5c5952;">
                    {i18n.lang === 'en' ? 'Verified' : 'Diverifikasi'} {activeDoc.last_verified_date}
                  </span>
                {/if}
              </div>
            </div>
          {/if}
        </div>
      </div>
      {/if}
    {/if}
  </section>
</div>
