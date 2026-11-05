<script>
  import { onMount } from 'svelte';
  import { fetchCorpus } from '../lib/api.js';

  let corpusData = $state(null);
  let loading = $state(true);
  let errorMsg = $state('');
  let searchQuery = $state('');
  let selectedTier = $state('ALL');
  let activeReg = $state(null);

  const TIER_OPTIONS = [
    { id: 'ALL', label: 'SEMUA' },
    { id: '1A', label: 'T.1A // UU NASIONAL' },
    { id: '1B', label: 'T.1B // PERDA BALI' },
    { id: '2', label: 'T.2 // SE GUBERNUR' }
  ];

  async function loadCorpus() {
    loading = true;
    errorMsg = '';
    try {
      corpusData = await fetchCorpus();
      if (corpusData?.regulations?.length) {
        activeReg = corpusData.regulations[0];
      }
    } catch (e) {
      console.error(e);
      errorMsg = 'Gagal memuat korpus regulasi. Pastikan backend berjalan, lalu coba lagi.';
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
          <span class="px-3 py-0.5 text-[11px] font-semibold">Statutory Corpus Index</span>
        </div>

        <h1 class="opero-h1 text-[30px] sm:text-[42px]">
          Indeks <span class="opero-serif">Korpus Hukum</span> Pramana
        </h1>
      </div>

      <!-- Search & Tier Filter -->
      <div class="flex flex-wrap items-center gap-2">
        <input
          type="search"
          bind:value={searchQuery}
          placeholder="Cari pasal, kata kunci..."
          style="background-color: #ffffff; color: #0a0a0a; border: 1.5px solid #0a0a0a;"
          class="px-3 py-1.5 text-xs font-mono focus:outline-none w-56"
        />

        {#each TIER_OPTIONS as opt}
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
        Memuat indeks korpus regulasi...
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
          Coba Lagi
        </button>
      </div>
    {:else if corpusData}
      {#if corpusData.metadata}
        <div class="brutal-card p-4 sm:p-5 mb-5 space-y-2" style="background-color: #f3f1eb;">
          <div class="flex flex-wrap items-center justify-between gap-2">
            <span class="font-mono text-[10px] font-bold px-2 py-0.5" style="background-color: #dfd6c3; color: #0a0a0a; border: 1px solid #0a0a0a;">
              PROVENANCE KORPUS · v{corpusData.metadata.version || '-'}
            </span>
            <span class="font-mono text-[11px]" style="color: #5c5952;">
              Diverifikasi: {corpusData.metadata.last_verified_date || corpusData.metadata.last_updated || '-'}
            </span>
          </div>
          {#if corpusData.metadata.verification_scope}
            <p class="text-[11px] leading-snug" style="color: #3a3935;">
              {corpusData.metadata.verification_scope}
            </p>
          {/if}
          {#if corpusData.metadata.known_gaps?.length}
            <div class="p-3 text-[11px] leading-snug" style="background-color: #fff3cd; border: 1px solid #8a3b00; color: #5c2d00;">
              <strong>Keterbatasan yang diketahui:</strong>
              <ul class="list-disc pl-4 mt-1 space-y-0.5">
                {#each corpusData.metadata.known_gaps as gap}
                  <li>{gap}</li>
                {/each}
              </ul>
            </div>
          {/if}
        </div>
      {/if}

      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">

        <!-- LEFT COLUMN: INSTRUMENT SELECTOR (5 cols) -->
        <div class="lg:col-span-5">
          <div class="brutal-card p-5 space-y-3" style="background-color: #f3f1eb;">
            <div class="flex items-center justify-between pb-2.5" style="border-bottom: 1px solid #cdc9be;">
              <span class="font-mono text-[10px] font-bold px-2 py-0.5" style="background-color: #dfd6c3; color: #0a0a0a; border: 1px solid #0a0a0a;">
                DAFTAR INSTRUMEN ({filteredRegs.length})
              </span>
              <span class="font-mono text-[11px]" style="color: #5c5952;">
                Domain Publik UU 28/2014
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
                      0{idx + 1} // TINGKAT {reg.tier}
                    </span>
                    <span style={activeReg?.id === reg.id ? 'color: #dfd6c3;' : 'color: #5c5952;'}>
                      {reg.pasal}
                    </span>
                  </div>
                  <h3 class="text-xs sm:text-sm font-semibold mt-1 leading-snug">{reg.category}</h3>
                  <div class="flex flex-wrap gap-1.5 mt-2 font-mono text-[9px] font-bold">
                    <span class="px-1.5 py-0.5" style="background-color: #f3f1eb; color: #0a0a0a; border: 1px solid #0a0a0a;">
                      {reg.status || 'Status tidak dicatat'}
                    </span>
                    <span
                      class="px-1.5 py-0.5"
                      style={reg.is_verbatim === false
                        ? 'background-color: #fff3cd; color: #8a3b00; border: 1px solid #8a3b00;'
                        : 'background-color: #e7f0ff; color: #0c249c; border: 1px solid #0c249c;'}
                    >
                      {reg.is_verbatim === false ? 'RINGKASAN' : 'VERBATIM'}
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
                  ID: {activeReg.id} · {activeReg.tier_label}
                </span>

                {#if activeReg.source_url}
                  <a
                    href={activeReg.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    style="background-color: #dfd6c3; color: #0a0a0a; border: 1.5px solid #0a0a0a; box-shadow: 2px 2px 0px #0a0a0a;"
                    class="brutal-press px-3 py-1 font-mono text-[11px] font-bold inline-flex items-center gap-1.5"
                  >
                    <span>Buka Sumber Resmi</span>
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
                  Status: {activeReg.status || 'Tidak dicatat'}
                </span>
                <span
                  class="font-mono text-[10px] font-bold px-2 py-0.5"
                  style={activeReg.is_verbatim === false
                    ? 'background-color: #fff3cd; color: #8a3b00; border: 1px solid #8a3b00;'
                    : 'background-color: #e7f0ff; color: #0c249c; border: 1px solid #0c249c;'}
                >
                  {activeReg.is_verbatim === false ? 'Ringkasan, bukan kutipan verbatim' : 'Teks verbatim korpus'}
                </span>
                {#if activeReg.last_verified_date}
                  <span class="font-mono text-[10px] font-bold px-2 py-0.5" style="background-color: #ffffff; color: #5c5952; border: 1px solid #cdc9be;">
                    Diverifikasi {activeReg.last_verified_date}
                  </span>
                {/if}
              </div>

              {#if activeReg.status_note}
                <p class="text-[11px] leading-snug" style="color: #8a3b00;">{activeReg.status_note}</p>
              {/if}
              {#if activeReg.source_note}
                <p class="text-[11px] leading-snug" style="color: #5c5952;">Catatan sumber: {activeReg.source_note}</p>
              {/if}
              {#if activeReg.superseded_by}
                <p class="text-[11px] leading-snug" style="color: #5c5952;">
                  Disempurnakan oleh:
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
                    ? 'Ringkasan Tersimpan (Bukan Kutipan Verbatim)'
                    : 'Teks Tersimpan (Rujukan Layer-1 Korpus)'}
                </span>
                <div
                  class="p-4 sm:p-5 text-xs sm:text-[13px] leading-relaxed whitespace-pre-line"
                  style="background-color: #f3f1eb; border: 1.5px solid #0a0a0a; color: #0a0a0a;"
                >
                  {activeReg.text}
                </div>
                {#if activeReg.is_verbatim === false}
                  <p class="font-mono text-[10px] leading-snug" style="color: #8a3b00;">
                    Entri ini adalah ringkasan/kompilasi. Jangan dikutip sebagai bunyi pasal verbatim.
                  </p>
                {/if}
              </div>

              {#if activeReg.penalties}
                <div
                  class="p-4 text-xs space-y-1"
                  style="background-color: #dfd6c3; border: 1.5px solid #0a0a0a; color: #0a0a0a;"
                >
                  <span class="font-mono text-[10px] uppercase font-bold block">
                    Ketentuan Sanksi &amp; Penegakan
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
    {/if}
  </section>
</div>
