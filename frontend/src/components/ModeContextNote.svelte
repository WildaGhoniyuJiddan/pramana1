<script>
  import { onMount } from 'svelte';
  import { requestContextNote } from '../lib/api.js';

  let { onOpenDoc = () => {} } = $props();

  let postContent = $state('');
  let loading = $state(false);
  let errorMsg = $state('');
  let result = $state(null);
  let copySuccess = $state(false);
  let activePresetIdx = $state(0);
  let activeCiteIdx = $state(0);
  let showTechAudit = $state(false);

  const PRESETS = [
    {
      label: '01 // Pohon Keramat Pura',
      tag: 'TERVERIFIKASI',
      text: 'Viral di medsos: seorang wisatawan bule memanjat pohon beringin keramat di kawasan pura Tabanan tanpa pakaian dan berteriak kasar kepada warga lokal saat ditegur.'
    },
    {
      label: '02 // Pungutan Rp150.000',
      tag: 'TERVERIFIKASI',
      text: 'Beredar video wisatawan asing berdebat di bandara menolak membayar retribusi turis asing 150000 di loket Love Bali dan mengaku tidak tahu aturan tersebut.'
    },
    {
      label: '03 // Klaim "Kebal Hukum"',
      tag: 'FRAMING',
      text: 'Semua bule di Bali kebal hukum dan polisi diam saja! Harusnya langsung dideportasi sekarang juga tanpa pandang bulu!'
    },
    {
      label: '04 // Uji Abstain',
      tag: 'ABSTAIN',
      text: 'Kucing oranye tertidur di atas meja kasir restoran dan meminta ikan tongkol goreng dari pengunjung.'
    }
  ];

  onMount(() => {
    applyPreset(PRESETS[0], 0, true);
  });

  function applyPreset(p, idx, autoRun = false) {
    activePresetIdx = idx;
    postContent = p.text;
    if (autoRun) handleSubmit();
  }

  async function handleSubmit(e) {
    if (e) e.preventDefault();
    if (!postContent.trim()) {
      errorMsg = 'Masukkan teks klaim atau postingan untuk dianalisis.';
      return;
    }
    loading = true;
    errorMsg = '';

    try {
      result = await requestContextNote({ post_content: postContent });
      activeCiteIdx = 0;
    } catch (err) {
      errorMsg = err.message || 'Gagal memproses catatan konteks.';
    } finally {
      loading = false;
    }
  }

  async function copyComment() {
    if (!result || !result.copyable_comment) return;
    try {
      await navigator.clipboard.writeText(result.copyable_comment);
      copySuccess = true;
      setTimeout(() => (copySuccess = false), 2500);
    } catch (e) {
      console.error(e);
    }
  }
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
            02
          </span>
          <span class="px-3 py-0.5 text-[11px] font-semibold">Public Context Verifier</span>
        </div>

        <h1 class="opero-h1 text-[30px] sm:text-[42px]">
          Verifikasi <span class="opero-serif">Klaim Insiden</span> &amp; Rujukan Pasal
        </h1>
      </div>

      <!-- Preset Selector Buttons -->
      <div class="flex flex-wrap items-center gap-2">
        {#each PRESETS as preset, idx}
          <button
            type="button"
            onclick={() => applyPreset(preset, idx, true)}
            style={activePresetIdx === idx
              ? 'background-color: #0c249c; color: #ffffff; border: 1.5px solid #0a0a0a; box-shadow: 2px 2px 0px #0a0a0a;'
              : 'background-color: #f3f1eb; color: #0a0a0a; border: 1.5px solid #0a0a0a;'}
            class="brutal-press px-3 py-2 font-mono text-[11px] font-semibold cursor-pointer"
          >
            {preset.label}
          </button>
        {/each}
      </div>
    </div>
  </section>

  <!-- 2. WORKSPACE GRID -->
  <section class="px-5 sm:px-10 py-6 sm:py-8">
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">

      <!-- LEFT COLUMN: INPUT CARD (5 cols) -->
      <div class="lg:col-span-5">
        <div class="brutal-card p-5 sm:p-6 space-y-5" style="background-color: #f3f1eb;">
          <div class="flex items-center justify-between pb-3" style="border-bottom: 1px solid #cdc9be;">
            <span class="font-mono text-[10px] font-bold px-2 py-0.5" style="background-color: #dfd6c3; color: #0a0a0a; border: 1px solid #0a0a0a;">
              NARASI KLAIM
            </span>
            <span class="font-mono text-[11px]" style="color: #5c5952;">Dual-Layer Guard</span>
          </div>

          <form onsubmit={handleSubmit} class="space-y-4">
            <div>
              <label for="post-content" class="block text-xs font-semibold mb-1.5" style="color: #0a0a0a;">
                Teks Unggahan atau Klaim Pelanggaran
              </label>
              <textarea
                id="post-content"
                bind:value={postContent}
                rows="5"
                placeholder="Tempel teks unggahan media sosial, keluhan warga, atau klaim pelanggaran aturan di sini..."
                style="background-color: #ffffff; color: #0a0a0a; border: 1.5px solid #0a0a0a;"
                class="w-full p-3 text-xs sm:text-[13px] focus:outline-none leading-relaxed"
              ></textarea>
            </div>

            {#if errorMsg}
              <div class="p-3 text-xs font-medium" style="background-color: #ffffff; border: 1.5px solid #c92a2a; color: #c92a2a;">
                {errorMsg}
              </div>
            {/if}

            <button
              type="submit"
              disabled={loading}
              style="background-color: #0c249c; color: #ffffff; padding: 3px; border: 1.5px solid #0a0a0a; box-shadow: 3px 3px 0px #0a0a0a;"
              class="opero-split-btn brutal-press w-full inline-flex items-center justify-between text-xs font-medium cursor-pointer disabled:opacity-50"
            >
              <span class="px-4 py-2 font-semibold">
                {loading ? 'Memverifikasi Korpus JDIH...' : 'Uji Klaim & Susun Konteks'}
              </span>
              <span
                style="background-color: #dfd8c8; color: #0a0a0a;"
                class="opero-arrow-box w-8 h-8 flex items-center justify-center font-mono text-xs font-bold"
              >
                ↗
              </span>
            </button>
          </form>

          <!-- Clean Architectural Protocol Footnote -->
          <div class="pt-3 space-y-2 text-[11px]" style="border-top: 1px solid #cdc9be; color: #4a4740;">
            <div class="flex items-start gap-2.5">
              <svg class="w-4 h-4 shrink-0 mt-0.5" viewBox="0 0 18 18" fill="none">
                <rect x="2.5" y="2.5" width="13" height="13" stroke="#0a0a0a" stroke-width="1.5" />
                <path d="M5.5 9l2.5 2.5 4.5-5" stroke="#0a0a0a" stroke-width="1.5" />
              </svg>
              <span class="leading-snug">
                <strong>Layer-1 Verbatim:</strong> Setiap kutipan dicocokkan langsung dengan naskah asli JDIH Bali.
              </span>
            </div>
            <div class="flex items-start gap-2.5">
              <svg class="w-4 h-4 shrink-0 mt-0.5" viewBox="0 0 18 18" fill="none">
                <circle cx="9" cy="9" r="6.5" stroke="#0a0a0a" stroke-width="1.5" />
                <path d="M5 5l8 8" stroke="#0a0a0a" stroke-width="1.5" />
              </svg>
              <span class="leading-snug">
                <strong>Layer-2 Abstain:</strong> Topik di luar cakupan hukum ditolak otomatis tanpa spekulasi.
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- RIGHT COLUMN: HIERARCHICAL VERIFICATION DOSSIER (7 cols) -->
      <div class="lg:col-span-7 space-y-5">
        {#if result}
          {#if result.status === 'TIDAK_DITEMUKAN'}
            <!-- ABSTAIN CARD -->
            <div class="brutal-card p-6 sm:p-8 space-y-4" style="background-color: #dfd6c3;">
              <div class="flex items-center justify-between">
                <span class="font-mono text-[10px] font-bold px-2 py-0.5" style="background-color: #0a0a0a; color: #ffffff;">
                  LAYER-2 ABSTAIN // ZERO HALLUCINATION
                </span>
                <span class="font-mono text-xs font-bold" style="color: #0a0a0a;">TIDAK DITEMUKAN</span>
              </div>

              <h2 class="opero-h1 text-2xl sm:text-3xl">
                Di Luar Cakupan <span class="opero-serif">Korpus Hukum</span> Bali
              </h2>

              <p class="text-xs sm:text-sm leading-relaxed" style="color: #3a3935;">
                {result.neutral_summary}
              </p>

              <div class="p-3 bg-white font-mono text-[11px]" style="border: 1.5px solid #0a0a0a;">
                Status: Sintesis dibatalkan secara deterministik karena klaim tidak terkait dengan instrumen Perda atau SE Gubernur Bali yang terdata.
              </div>
            </div>
          {:else}
            <!-- STEP 1: PRIMARY FOCUS - CATATAN KONTEKS NETRAL -->
            <div class="brutal-card-cobalt p-5 sm:p-6 space-y-4">
              <div class="flex flex-wrap items-center justify-between gap-2">
                <span
                  class="font-mono text-[10px] font-bold px-2 py-0.5"
                  style="background-color: #dfd6c3; color: #0a0a0a; border: 1px solid #0a0a0a;"
                >
                  01 // CATATAN KONTEKS NETRAL (SIAP PUBLIKASI)
                </span>

                {#if result.copyable_comment}
                  <button
                    type="button"
                    onclick={copyComment}
                    style="background-color: #dfd6c3; color: #0a0a0a; border: 1.5px solid #0a0a0a; box-shadow: 2px 2px 0px #0a0a0a;"
                    class="brutal-press px-3 py-1 font-mono text-[11px] font-bold inline-flex items-center gap-1.5 cursor-pointer"
                  >
                    <svg class="w-3.5 h-3.5" viewBox="0 0 18 18" fill="none">
                      <rect x="5.5" y="5.5" width="9" height="9" stroke="#0a0a0a" stroke-width="1.5" />
                      <path d="M12.5 5.5V3.5h-9v9h2" stroke="#0a0a0a" stroke-width="1.5" />
                    </svg>
                    <span>{copySuccess ? 'Tersalin' : 'Salin Catatan'}</span>
                  </button>
                {/if}
              </div>

              <p class="text-sm sm:text-base leading-relaxed font-normal" style="color: #ffffff;">
                {result.neutral_summary}
              </p>

              {#if result.framing_markers && result.framing_markers.length > 0}
                <div class="p-3.5 space-y-2" style="background-color: #f3f1eb; color: #0a0a0a; border: 1.5px solid #0a0a0a;">
                  <span class="font-mono text-[10px] font-bold uppercase block" style="color: #0c249c;">
                    Penanda Retorika Sensasional Terdeteksi ({result.framing_markers.length})
                  </span>
                  {#each result.framing_markers as marker}
                    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs pt-1" style="border-top: 1px solid #cdc9be;">
                      <span class="font-mono font-bold px-1.5 py-0.5 bg-white" style="border: 1px solid #0a0a0a;">
                        "{marker.phrase}"
                      </span>
                      <span style="color: #3a3935;">{marker.reason}</span>
                    </div>
                  {/each}
                </div>
              {/if}
            </div>

            <!-- STEP 2: SECONDARY FOCUS - VERBATIM CITATION INSPECTOR -->
            <div class="brutal-card p-5 sm:p-6 space-y-4" style="background-color: #f3f1eb;">
              <div class="flex flex-wrap items-center justify-between gap-2 pb-3" style="border-bottom: 1px solid #cdc9be;">
                <span class="font-mono text-[10px] font-bold px-2 py-0.5" style="background-color: #dfd6c3; color: #0a0a0a; border: 1px solid #0a0a0a;">
                  02 // RUJUKAN PASAL VERBATIM ({result.citations.length} DOKUMEN)
                </span>
                <span class="font-mono text-[11px] font-bold" style="color: #0c249c;">
                  LAYER-1 EXACT MATCH
                </span>
              </div>

              {#if result.citations.length > 1}
                <div class="flex flex-wrap gap-2">
                  {#each result.citations as cite, idx}
                    <button
                      type="button"
                      onclick={() => (activeCiteIdx = idx)}
                      style={activeCiteIdx === idx
                        ? 'background-color: #0c249c; color: #ffffff; border: 1.5px solid #0a0a0a; box-shadow: 2px 2px 0px #0a0a0a;'
                        : 'background-color: #ffffff; color: #0a0a0a; border: 1.5px solid #0a0a0a;'}
                      class="brutal-press px-3 py-1.5 font-mono text-[11px] font-semibold cursor-pointer"
                    >
                      0{idx + 1} · {cite.pasal}
                    </button>
                  {/each}
                </div>
              {/if}

              {#if result.citations[activeCiteIdx]}
                {@const activeCite = result.citations[activeCiteIdx]}
                <div
                  class="p-5 bg-white space-y-4"
                  style="border: 1.5px solid #0a0a0a; box-shadow: 3px 3px 0px #0a0a0a;"
                >
                  <div class="flex flex-wrap items-center justify-between gap-2 pb-2.5" style="border-bottom: 1px solid #e6e4de;">
                    <span class="font-mono text-[10px] font-bold px-2 py-0.5" style="background-color: #0c249c; color: #ffffff;">
                      TINGKAT {activeCite.tier} · {activeCite.tier_label}
                    </span>
                    <span class="font-mono text-xs font-bold" style="color: #0a0a0a;">
                      {activeCite.pasal}
                    </span>
                  </div>

                  <h3 class="text-sm sm:text-base font-medium leading-snug" style="color: #0a0a0a;">
                    {activeCite.official_doc_title}
                  </h3>

                  <!-- Full-border architectural quote box (no cliché left stripe) -->
                  <div
                    class="p-4 text-xs sm:text-[13px] leading-relaxed"
                    style="background-color: #f3f1eb; border: 1.5px solid #0a0a0a; color: #0a0a0a;"
                  >
                    "{activeCite.quoted_text}"
                  </div>

                  {#if activeCite.penalties}
                    <div
                      class="p-3 text-xs space-y-1"
                      style="background-color: #dfd6c3; border: 1px solid #0a0a0a; color: #0a0a0a;"
                    >
                      <span class="font-mono text-[10px] font-bold uppercase block">
                        Ketentuan Sanksi Resmi
                      </span>
                      <p class="leading-snug">{activeCite.penalties}</p>
                    </div>
                  {/if}

                  <div class="pt-1 flex justify-end">
                    <button
                      type="button"
                      onclick={() => onOpenDoc(activeCite)}
                      style="background-color: #0a0a0a; color: #ffffff; padding: 2px; border: 1.5px solid #0a0a0a;"
                      class="brutal-press inline-flex items-center gap-2 text-xs font-medium cursor-pointer"
                    >
                      <span class="px-2.5 py-1 font-mono text-[11px]">Buka Naskah Asli</span>
                      <span
                        style="background-color: #dfd6c3; color: #0a0a0a;"
                        class="w-6 h-6 flex items-center justify-center font-mono text-xs font-bold"
                      >
                        ↗
                      </span>
                    </button>
                  </div>
                </div>
              {/if}

              <!-- Collapsible Audit Footer -->
              <div class="pt-1 flex items-center justify-between text-[11px] font-mono" style="color: #5c5952;">
                <button
                  type="button"
                  onclick={() => (showTechAudit = !showTechAudit)}
                  class="underline hover:text-black cursor-pointer"
                >
                  {showTechAudit ? 'Sembunyikan Diagnostik Verifier' : 'Tampilkan Diagnostik Verifier'}
                </button>
                <span>Confidence: {result.confidence}</span>
              </div>

              {#if showTechAudit}
                <div class="p-3 bg-white font-mono text-[11px] space-y-1" style="border: 1px solid #0a0a0a;">
                  <div>ENGINE: <strong>{result.ai_engine}</strong></div>
                  <div>GUARD: <strong>{result.guard_status}</strong></div>
                  <div>CONFIDENCE: <strong>{result.confidence}</strong></div>
                </div>
              {/if}
            </div>
          {/if}
        {/if}
      </div>

    </div>
  </section>
</div>
