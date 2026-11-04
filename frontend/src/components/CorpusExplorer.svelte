<script>
  import { onMount } from 'svelte';
  import { fetchCorpus } from '../lib/api.js';

  let corpusData = $state(null);
  let loading = $state(true);
  let searchQuery = $state('');
  let selectedTier = $state('ALL');
  let activeReg = $state(null);

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

    <!-- Atmospheric Opero Banner + Filter Bar -->
    <div class="p-3 sm:p-4" style="border-bottom: 1px solid #cdc9be;">
      <div
        class="relative overflow-hidden p-6 sm:p-8 flex flex-col md:flex-row md:items-end justify-between gap-6"
        style="background-color: #091e8a; color: #ffffff; border: 1.5px solid #0a0a0a; box-shadow: 4px 4px 0px #0a0a0a;"
      >
        <img
          src="/assets/opero_bali_hero.jpg"
          alt="Pointillist Bali Sky"
          class="absolute inset-0 w-full h-full object-cover opacity-35 pointer-events-none"
          style="object-position: center 25%;"
        />
        <div
          class="absolute inset-0 pointer-events-none"
          style="background: linear-gradient(90deg, rgba(8, 24, 115, 0.94) 0%, rgba(8, 24, 115, 0.72) 60%, rgba(8, 24, 115, 0.55) 100%);"
        ></div>

        <div class="relative z-10">
          <div class="inline-flex items-center text-[11px] font-mono mb-3" style="background-color: rgba(255,255,255,0.14); color: #ffffff; border-radius: 2px; padding: 2px;">
            <span style="background-color: #dfd8c8; color: #0a0a0a; border-radius: 1px;" class="px-2 py-0.5 font-bold">§</span>
            <span class="px-3 py-0.5">Domain Publik · Pasal 42 UU No. 28 Tahun 2014</span>
          </div>
          <h1 class="opero-h1 text-3xl sm:text-5xl" style="color: #ffffff;">
            Indeks <span class="opero-serif" style="color: #dfd8c8;">Korpus Hukum</span> JDIH Bali
          </h1>
        </div>

        <div class="relative z-10 flex flex-wrap items-center gap-2">
          <input
            type="search"
            bind:value={searchQuery}
            placeholder="Cari pasal, kata kunci, topik..."
            style="background-color: #ffffff; color: #0a0a0a; border-radius: 3px;"
            class="px-3.5 py-2 text-xs focus:outline-none w-60 shadow-xs"
          />
          <div class="inline-flex font-mono text-[11px] p-0.5" style="background-color: rgba(255,255,255,0.16); border-radius: 3px;">
            {#each ['ALL', '1A', '1B', '2'] as tier}
              <button
                type="button"
                onclick={() => (selectedTier = tier)}
                style={selectedTier === tier
                  ? 'background-color: #dfd8c8; color: #0a0a0a; border-radius: 2px; font-weight: 600;'
                  : 'color: #ffffff;'}
                class="px-3 py-1.5 transition-colors cursor-pointer"
              >
                {tier === 'ALL' ? 'SEMUA' : `T.${tier}`}
              </button>
            {/each}
          </div>
        </div>
      </div>
    </div>

    {#if loading}
      <div class="p-12 text-center font-mono text-xs" style="color: #5e5d58;">
        Memuat indeks korpus regulasi...
      </div>
    {:else if corpusData}
      <div class="grid grid-cols-1 lg:grid-cols-12">

        <!-- Left Index Column (4 cols) -->
        <div class="lg:col-span-4" style="background-color: #f2f0ea; border-right: 1px solid #c8c4ba;">
          <div class="px-5 py-3 flex items-center justify-between font-mono text-[10px] uppercase tracking-wider" style="background-color: #dfd8c8; color: #0a0a0a; border-bottom: 1px solid #c8c4ba;">
            <span class="font-semibold">Instrumen Terindeks ({filteredRegs.length})</span>
            <span>v{corpusData.metadata?.version || '1.0.0'}</span>
          </div>

          {#each filteredRegs as reg}
            <button
              type="button"
              onclick={() => (activeReg = reg)}
              style={activeReg?.id === reg.id
                ? 'background-color: #0c249c; color: #ffffff; border-bottom: 1px solid #0c249c;'
                : 'background-color: #f2f0ea; color: #0a0a0a; border-bottom: 1px solid #c8c4ba;'}
              class="w-full text-left p-5 transition-colors block hover:opacity-95"
            >
              <div class="flex items-center justify-between gap-2 font-mono text-[10px]">
                <span style={activeReg?.id === reg.id ? 'color: #dfd8c8;' : 'color: #0c249c; font-weight: 600;'}>
                  TINGKAT {reg.tier} · {reg.tier_label}
                </span>
                <span style={activeReg?.id === reg.id ? 'color: #dfd8c8;' : 'color: #5e5d58;'}>
                  {reg.pasal}
                </span>
              </div>
              <h3 class="text-sm font-semibold mt-1.5 leading-snug">{reg.category}</h3>
              <p class="text-xs mt-1 line-clamp-2" style={activeReg?.id === reg.id ? 'color: rgba(255,255,255,0.85);' : 'color: #5e5d58;'}>
                {reg.doc_title}
              </p>
            </button>
          {/each}
        </div>

        <!-- Right Verbatim Document Dossier (8 cols) -->
        <div class="lg:col-span-8 bg-white">
          {#if activeReg}
            <div class="px-6 py-3.5 flex flex-wrap items-center justify-between gap-2 font-mono text-[11px]" style="background-color: #dfd8c8; color: #0a0a0a; border-bottom: 1px solid #c8c4ba;">
              <div class="flex items-center gap-3">
                <span>ID DOKUMEN: <strong>{activeReg.id}</strong></span>
                <span>|</span>
                <span style="color: #0c249c;" class="font-bold">STATUS: {activeReg.status}</span>
              </div>
              <a
                href={activeReg.source_url}
                target="_blank"
                rel="noopener noreferrer"
                style="color: #0c249c;"
                class="font-semibold hover:underline"
              >
                Buka Tautan Resmi JDIH ↗
              </a>
            </div>

            <div class="p-6 sm:p-8 space-y-6">
              <div class="pb-5" style="border-bottom: 1px solid #c8c4ba;">
                <span class="font-mono text-[10px] uppercase tracking-wider font-semibold block" style="color: #0c249c;">
                  Nomenklatur Peraturan Resmi
                </span>
                <h2 class="text-lg sm:text-2xl font-normal mt-1 leading-snug" style="color: #0a0a0a;">
                  {activeReg.doc_title}
                </h2>
                <p class="font-mono text-xs mt-2" style="color: #5e5d58;">
                  {activeReg.bab}: {activeReg.pasal}
                </p>
              </div>

              <div>
                <span class="font-mono text-[10px] uppercase tracking-wider font-semibold block mb-2" style="color: #5e5d58;">
                  Batang Tubuh / Teks Verbatim (Rujukan Layer-1 Verifier)
                </span>
                <blockquote class="p-5 font-mono text-xs sm:text-[13px] leading-relaxed whitespace-pre-line" style="background-color: #f2f0ea; border-left: 3px solid #0c249c; color: #0a0a0a;">
                  {activeReg.text}
                </blockquote>
              </div>

              <div class="grid grid-cols-1 md:grid-cols-12 gap-4 pt-4 text-xs" style="border-top: 1px solid #c8c4ba;">
                <div class="md:col-span-3 font-mono text-[10px] uppercase font-semibold" style="color: #0a0a0a;">
                  Ketentuan Sanksi
                </div>
                <div class="md:col-span-9 leading-relaxed" style="color: #333330;">
                  {activeReg.penalties}
                </div>
              </div>

              <div class="grid grid-cols-1 md:grid-cols-12 gap-4 pt-4 text-xs" style="border-top: 1px solid #c8c4ba;">
                <div class="md:col-span-3 font-mono text-[10px] uppercase font-semibold" style="color: #0a0a0a;">
                  Indeks Kata Kunci
                </div>
                <div class="md:col-span-9 flex flex-wrap gap-1.5">
                  {#each activeReg.keywords || [] as kw}
                    <span class="px-2.5 py-1 font-mono text-[11px]" style="background-color: #f2f0ea; border: 1px solid #c8c4ba; color: #0a0a0a;">
                      {kw}
                    </span>
                  {/each}
                </div>
              </div>
            </div>
          {/if}
        </div>

      </div>
    {/if}
  </div>
</div>
