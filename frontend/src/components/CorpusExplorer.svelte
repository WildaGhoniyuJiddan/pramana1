<script>
  import { onMount } from 'svelte';
  import { fetchCorpus } from '../lib/api.js';

  let corpusData = $state(null);
  let loading = $state(true);
  let searchQuery = $state('');
  let selectedTier = $state('ALL');
  let activeReg = $state(null);

  const TIER_OPTIONS = [
    { id: 'ALL', label: 'Semua Regulasi' },
    { id: '1A', label: 'UU Nasional (1A)' },
    { id: '1B', label: 'Perda Bali (1B)' },
    { id: '2', label: 'Surat Edaran (2)' }
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

<div class="mx-auto" style="max-width: 1360px; width: 100%; border-left: 1px solid #cdc9be; border-right: 1px solid #cdc9be; background-color: #e6e4de; color: #0a0a0a; overflow: hidden;">
  <div>

    <!-- Header Strip -->
    <div class="p-6 sm:p-8" style="background-color: #dfd8c8; border-bottom: 1.5px solid #0a0a0a;">
      <div class="flex flex-col lg:flex-row lg:items-end justify-between gap-6">
        <div class="space-y-2">
          <div class="text-[11px] font-mono tracking-wider uppercase font-semibold" style="color: #0c249c;">
            PUSTAKA DOKUMEN RESMI JDIH PROVINSI BALI
          </div>
          <h1 class="opero-h1 text-2xl sm:text-4xl" style="color: #0a0a0a;">
            Eksplorasi <span class="opero-serif" style="color: #0c249c;">Korpus Regulasi</span>
          </h1>
          <p class="text-xs sm:text-sm max-w-2xl leading-relaxed" style="color: #4a4943;">
            Seluruh naskah hukum, Perda, dan Surat Edaran yang menjadi rujukan verifikasi. Bersumber langsung dari JDIH Bali dan domain publik.
          </p>
        </div>

        <!-- Search & Filter Controls -->
        <div class="space-y-2">
          <div class="flex flex-wrap items-center gap-2">
            <input
              type="search"
              bind:value={searchQuery}
              placeholder="Cari pasal atau kata kunci..."
              style="background-color: #ffffff; color: #0a0a0a; border: 1px solid #c8c4ba;"
              class="px-3.5 py-1.5 text-xs focus:outline-none focus:border-black w-64 rounded-xs"
            />
          </div>
          <div class="flex flex-wrap gap-1.5">
            {#each TIER_OPTIONS as opt}
              <button
                type="button"
                onclick={() => (selectedTier = opt.id)}
                style={selectedTier === opt.id
                  ? 'background-color: #0c249c; color: #ffffff; border-color: #0a0a0a;'
                  : 'background-color: #ffffff; color: #0a0a0a; border-color: #c8c4ba;'}
                class="px-2.5 py-1 text-xs font-medium border rounded-xs transition-all hover:border-black cursor-pointer"
              >
                {opt.label}
              </button>
            {/each}
          </div>
        </div>
      </div>
    </div>

    {#if loading}
      <div class="p-12 text-center text-xs" style="color: #5e5d58;">
        Memuat indeks korpus regulasi...
      </div>
    {:else if corpusData}
      <div class="grid grid-cols-1 lg:grid-cols-12">

        <!-- Left Index Column (5 cols) -->
        <div class="lg:col-span-5" style="background-color: #f2f0ea; border-right: 1px solid #c8c4ba;">
          <div class="px-5 py-3 flex items-center justify-between font-mono text-[10px] uppercase tracking-wider" style="background-color: #dfd8c8; color: #0a0a0a; border-bottom: 1px solid #c8c4ba;">
            <span class="font-semibold">Instrumen Terindeks ({filteredRegs.length})</span>
            <span>Versi {corpusData.metadata?.version || '1.0'}</span>
          </div>

          <div class="divide-y" style="border-color: #c8c4ba;">
            {#each filteredRegs as reg}
              <button
                type="button"
                onclick={() => (activeReg = reg)}
                style={activeReg?.id === reg.id
                  ? 'background-color: #0c249c; color: #ffffff;'
                  : 'background-color: #f2f0ea; color: #0a0a0a;'}
                class="w-full text-left p-5 transition-colors block hover:opacity-95 cursor-pointer"
              >
                <div class="flex items-center justify-between gap-2 text-xs">
                  <span class="font-semibold" style={activeReg?.id === reg.id ? 'color: #dfd8c8;' : 'color: #0c249c;'}>
                    {reg.tier_label || `Tingkat ${reg.tier}`}
                  </span>
                  <span class="font-mono text-[11px]" style={activeReg?.id === reg.id ? 'color: #dfd8c8;' : 'color: #5e5d58;'}>
                    {reg.pasal}
                  </span>
                </div>
                <h3 class="text-sm font-semibold mt-1.5 leading-snug">{reg.category}</h3>
                <p class="text-xs mt-1 line-clamp-2 leading-relaxed" style={activeReg?.id === reg.id ? 'color: rgba(255,255,255,0.85);' : 'color: #5e5d58;'}>
                  {reg.doc_title}
                </p>
              </button>
            {/each}
          </div>
        </div>

        <!-- Right Document Reader (7 cols) -->
        <div class="lg:col-span-7 bg-white min-w-0">
          {#if activeReg}
            <div class="px-6 py-3.5 flex flex-wrap items-center justify-between gap-2 text-xs" style="background-color: #dfd8c8; color: #0a0a0a; border-bottom: 1px solid #c8c4ba;">
              <div class="flex items-center gap-2">
                <span class="font-mono text-[11px]">DOKUMEN: <strong>{activeReg.id}</strong></span>
              </div>
              {#if activeReg.source_url}
                <a
                  href={activeReg.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  style="color: #0c249c;"
                  class="font-semibold hover:underline inline-flex items-center gap-1"
                >
                  <span>Buka Naskah Resmi di JDIH</span>
                  <span>↗</span>
                </a>
              {/if}
            </div>

            <div class="p-6 sm:p-8 space-y-6">
              <div class="pb-5" style="border-bottom: 1px solid #c8c4ba;">
                <span class="font-mono text-[10px] uppercase tracking-wider font-semibold block" style="color: #0c249c;">
                  Nomenklatur Regulasi
                </span>
                <h2 class="text-lg sm:text-xl font-normal mt-1 leading-snug" style="color: #0a0a0a;">
                  {activeReg.doc_title}
                </h2>
                <p class="text-xs font-semibold mt-2" style="color: #5e5d58;">
                  {activeReg.bab}: {activeReg.pasal}
                </p>
              </div>

              <div>
                <span class="font-mono text-[10px] uppercase tracking-wider font-semibold block mb-2" style="color: #5e5d58;">
                  Bunyi Naskah Resmi
                </span>
                <div class="p-4 sm:p-5 text-xs sm:text-sm leading-relaxed whitespace-pre-line" style="background-color: #faf9f6; border: 1px solid #dcd7cb; color: #0a0a0a;">
                  {activeReg.text}
                </div>
              </div>

              {#if activeReg.penalties}
                <div class="p-4 text-xs space-y-1" style="background-color: #f2f0ea; border: 1px solid #c8c4ba;">
                  <span class="font-mono text-[10px] uppercase font-semibold block" style="color: #0a0a0a;">
                    Ketentuan Sanksi
                  </span>
                  <p class="leading-relaxed" style="color: #333330;">
                    {activeReg.penalties}
                  </p>
                </div>
              {/if}

              {#if activeReg.keywords && activeReg.keywords.length > 0}
                <div class="pt-4 text-xs space-y-2" style="border-top: 1px solid #c8c4ba;">
                  <span class="font-mono text-[10px] uppercase font-semibold block" style="color: #5e5d58;">
                    Kata Kunci Terindeks
                  </span>
                  <div class="flex flex-wrap gap-1.5">
                    {#each activeReg.keywords as kw}
                      <span class="px-2.5 py-1 text-xs font-mono" style="background-color: #f2f0ea; border: 1px solid #c8c4ba; color: #0a0a0a;">
                        {kw}
                      </span>
                    {/each}
                  </div>
                </div>
              {/if}
            </div>
          {/if}
        </div>

      </div>
    {/if}
  </div>
</div>
