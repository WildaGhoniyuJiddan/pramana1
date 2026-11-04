<script>
  import { onMount } from 'svelte';
  import { fetchCorpus } from '../lib/api.js';

  let corpusData = $state(null);
  let loading = $state(true);
  let searchQuery = $state('');
  let selectedTier = $state('ALL');
  let activeReg = $state(null);

  const TIER_OPTIONS = [
    { id: 'ALL', label: 'SEMUA' },
    { id: '1A', label: 'T.1A // UU NASIONAL' },
    { id: '1B', label: 'T.1B // PERDA BALI' },
    { id: '2', label: 'T.2 // SE GUBERNUR' }
  ];

  onMount(async () => {
    try {
      corpusData = await fetchCorpus();
      if (corpusData?.regulations?.length) {
        activeReg = corpusData.regulations[0];
      }
    } catch (e) {
      console.error(e);
    } finally {
      loading = false;
    }
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
          Indeks <span class="opero-serif">Korpus Hukum</span> JDIH Bali
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
    {:else if corpusData}
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
                    <span>Portal Resmi JDIH</span>
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

              <div class="space-y-2">
                <span class="font-mono text-[10px] uppercase font-bold block" style="color: #0c249c;">
                  Bunyi Naskah Verbatim (Rujukan Layer-1)
                </span>
                <div
                  class="p-4 sm:p-5 text-xs sm:text-[13px] leading-relaxed whitespace-pre-line"
                  style="background-color: #f3f1eb; border: 1.5px solid #0a0a0a; color: #0a0a0a;"
                >
                  {activeReg.text}
                </div>
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
