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
  let showTechAudit = $state(false);

  const PRESETS = [
    {
      label: 'Pohon Keramat Pura',
      tag: 'TERVERIFIKASI',
      text: 'Viral di medsos: seorang wisatawan bule memanjat pohon beringin keramat di kawasan pura Tabanan tanpa pakaian dan berteriak kasar kepada warga lokal saat ditegur.'
    },
    {
      label: 'Pungutan Turis Rp150.000',
      tag: 'TERVERIFIKASI',
      text: 'Beredar video wisatawan asing berdebat di bandara menolak membayar retribusi turis asing 150000 di loket Love Bali dan mengaku tidak tahu aturan tersebut.'
    },
    {
      label: 'Klaim "Kebal Hukum"',
      tag: 'FRAMING',
      text: 'Semua bule di Bali kebal hukum dan polisi diam saja! Harusnya langsung dideportasi sekarang juga tanpa pandang bulu!'
    },
    {
      label: 'Klaim di Luar Regulasi',
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

<div class="mx-auto" style="max-width: 1360px; width: 100%; border-left: 1px solid #cdc9be; border-right: 1px solid #cdc9be; background-color: #e6e4de; color: #0a0a0a;">

  <!-- Compact Top Bar -->
  <div class="px-5 sm:px-8 py-4" style="border-bottom: 1px solid #cdc9be; background-color: #dfd8c8;">
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-3">
      <div>
        <h1 class="opero-h1 text-xl sm:text-2xl font-bold">
          Uji Klaim &amp; <span class="opero-serif font-normal">Catatan Konteks</span>
        </h1>
        <p class="text-xs text-ink-600 mt-0.5">
          Verifikasi klaim viral dan periksa rujukan regulasi resmi Bali dari naskah JDIH.
        </p>
      </div>

      <!-- Scenario Chips -->
      <div class="flex flex-wrap items-center gap-1.5">
        <span class="text-[11px] text-ink-500 font-mono">Contoh:</span>
        {#each PRESETS as preset, idx}
          <button
            type="button"
            onclick={() => applyPreset(preset, idx, true)}
            style={activePresetIdx === idx
              ? 'background-color: #0c249c; color: #ffffff; border-color: #0a0a0a;'
              : 'background-color: #ffffff; color: #0a0a0a; border-color: #c8c4ba;'}
            class="px-2.5 py-1 text-xs font-medium border rounded-xs transition-colors hover:border-black cursor-pointer"
          >
            {preset.label}
          </button>
        {/each}
      </div>
    </div>
  </div>

  <!-- Main 2-Pane Layout (Synchronized Viewport Height) -->
  <div class="grid grid-cols-1 lg:grid-cols-12 items-stretch min-h-[calc(100vh-155px)]">

    <!-- Left Pane: Claim Input -->
    <div
      class="lg:col-span-5 p-5 sm:p-6 space-y-4 flex flex-col justify-between"
      style="background-color: #f2f0ea; border-right: 1px solid #c8c4ba;"
    >
      <form onsubmit={handleSubmit} class="space-y-3.5">
        <div>
          <label for="post-content" class="block text-xs font-semibold mb-1" style="color: #0a0a0a;">
            Teks Klaim atau Kabar Medsos
          </label>
          <textarea
            id="post-content"
            bind:value={postContent}
            rows="6"
            placeholder="Tempel teks unggahan media sosial, keluhan warga, atau klaim pelanggaran aturan di sini..."
            style="background-color: #ffffff; color: #0a0a0a; border: 1.5px solid #c8c4ba; border-radius: 4px;"
            class="w-full p-3 text-xs sm:text-sm focus:outline-none focus:border-black leading-relaxed"
          ></textarea>
          <span class="block text-[11px] mt-1.5 text-ink-500">
            Sistem merujuk naskah hukum resmi secara objektif tanpa prasangka.
          </span>
        </div>

        {#if errorMsg}
          <div class="p-2.5 bg-red-50 text-xs font-medium text-red-700 border border-red-700">
            {errorMsg}
          </div>
        {/if}

        <button
          type="submit"
          disabled={loading}
          style="background-color: #0c249c; color: #ffffff;"
          class="w-full inline-flex items-center justify-between px-4 py-2.5 text-xs font-semibold hover:opacity-95 transition-opacity disabled:opacity-50 cursor-pointer"
        >
          <span>{loading ? 'Memverifikasi Korpus JDIH...' : 'Periksa Klaim Sekarang'}</span>
          <span class="font-mono text-xs">→</span>
        </button>
      </form>

      <div class="pt-3 text-[11px] text-ink-500 space-y-1" style="border-top: 1px solid #dcd7cb;">
        <div>Pencocokan verbatim terhadap naskah JDIH Bali. Klaim di luar cakupan aturan akan ditolak tanpa spekulasi.</div>
      </div>
    </div>

    <!-- Right Pane: Legal Verification Dossier (Scrollable Pane) -->
    <div
      class="lg:col-span-7 flex flex-col lg:max-h-[calc(100vh-155px)] overflow-hidden"
      style="background-color: #e6e4de;"
    >
      {#if result}
        <!-- Fixed Action Bar -->
        <div class="px-5 py-3 flex flex-wrap items-center justify-between gap-2 bg-white shrink-0" style="border-bottom: 1px solid #c8c4ba;">
          <div class="text-xs">
            <span class="font-bold uppercase tracking-wider font-mono" style="color: #0a0a0a;">
              {result.status === 'TIDAK_DITEMUKAN' ? 'Status: Di Luar Cakupan' : 'Status: Klarifikasi Siap'}
            </span>
          </div>

          <div class="flex items-center gap-3">
            <button
              type="button"
              onclick={() => (showTechAudit = !showTechAudit)}
              class="text-[11px] font-mono underline hover:text-black cursor-pointer text-ink-500"
            >
              {showTechAudit ? 'Tutup Diagnostik' : 'Diagnostik'}
            </button>

            {#if result.copyable_comment}
              <button
                type="button"
                onclick={copyComment}
                style="background-color: #0c249c; color: #ffffff;"
                class="px-2.5 py-1 text-xs font-medium hover:opacity-90 transition-opacity cursor-pointer"
              >
                {copySuccess ? 'Tersalin' : 'Salin Catatan'}
              </button>
            {/if}
          </div>
        </div>

        {#if showTechAudit}
          <div class="px-5 py-2 font-mono text-[11px] flex flex-wrap items-center gap-4 bg-white border-b" style="border-color: #c8c4ba; color: #4a4943;">
            <span>ENGINE: <strong>{result.ai_engine || 'Strict-RAG'}</strong></span>
            <span>GUARD: <strong>{result.guard_status}</strong></span>
            <span>CONFIDENCE: <strong style="color: #0c249c;">{result.confidence}</strong></span>
          </div>
        {/if}

        <!-- Scrollable Result Body -->
        <div class="flex-1 overflow-y-auto p-4 sm:p-5 space-y-3.5">
          {#if result.status === 'TIDAK_DITEMUKAN'}
            <div class="p-6 bg-white space-y-3 border" style="border-color: #c8c4ba;">
              <span class="text-xs font-mono font-semibold uppercase text-ink-500 block">
                Tidak Ditemukan Dasar Hukum
              </span>
              <h2 class="text-lg font-normal tracking-tight" style="color: #0a0a0a;">
                Klaim tidak diatur dalam korpus regulasi resmi Provinsi Bali.
              </h2>
              <p class="text-xs sm:text-sm leading-relaxed text-ink-700">
                {result.neutral_summary}
              </p>
              <p class="text-[11px] pt-2 text-ink-500 border-t" style="border-color: #e6e4de;">
                Sistem menolak berspekulasi jika materi berada di luar instrumen hukum yang terdata.
              </p>
            </div>
          {:else}
            <!-- Neutral Context Note Summary -->
            <div class="p-4 sm:p-5 bg-white space-y-2 border" style="border-color: #c8c4ba;">
              <span class="font-mono text-[10px] uppercase tracking-wider font-semibold block" style="color: #0c249c;">
                Catatan Konteks Netral
              </span>
              <p class="text-xs sm:text-sm leading-relaxed text-ink-900">
                {result.neutral_summary}
              </p>
            </div>

            <!-- Sensational Framing Warning -->
            {#if result.framing_markers && result.framing_markers.length > 0}
              <div class="p-4 space-y-2.5 bg-[#f7f5f0] border" style="border-color: #c8c4ba;">
                <span class="text-xs font-semibold text-ink-900 block">
                  Deteksi Narasi Sensasional atau Generalisasi ({result.framing_markers.length})
                </span>
                <div class="space-y-1.5">
                  {#each result.framing_markers as marker}
                    <div class="p-2.5 bg-white flex flex-col sm:flex-row sm:items-start justify-between gap-1.5 text-xs border" style="border-color: #dfd8c8;">
                      <span class="font-mono px-1.5 py-0.5 self-start font-semibold text-[11px]" style="background-color: #dfd8c8; color: #0a0a0a;">
                        "{marker.phrase}"
                      </span>
                      <span class="text-ink-700 sm:max-w-md text-[11.5px]">{marker.reason}</span>
                    </div>
                  {/each}
                </div>
              </div>
            {/if}

            <!-- Citations List -->
            <div class="space-y-2.5">
              <div class="flex items-center justify-between font-mono text-[10px] uppercase tracking-wider px-1 text-ink-600">
                <span class="font-semibold">Rujukan Regulasi Terkait ({result.citations.length})</span>
                <span>Pencocokan Verbatim</span>
              </div>

              {#each result.citations as cite}
                <div class="p-4 bg-white border space-y-2" style="border-color: #c8c4ba;">
                  <div class="flex flex-wrap items-center justify-between gap-2">
                    <div class="flex items-center gap-2">
                      <span class="text-[9.5px] font-mono px-1.5 py-0.5 inline-block font-semibold" style="background-color: #0c249c; color: #ffffff;">
                        {cite.tier_label || 'Regulasi'}
                      </span>
                      <span class="text-xs font-bold" style="color: #0a0a0a;">{cite.pasal}</span>
                    </div>
                    <button
                      type="button"
                      onclick={() => onOpenDoc(cite)}
                      style="color: #0c249c;"
                      class="text-xs font-semibold hover:underline cursor-pointer"
                    >
                      Buka Dokumen →
                    </button>
                  </div>

                  <p class="text-[11.5px] font-medium text-ink-600">{cite.official_doc_title}</p>

                  <div class="p-3 text-xs leading-relaxed" style="background-color: #faf9f6; border: 1px solid #dcd7cb; color: #0a0a0a;">
                    <p class="leading-relaxed">
                      "{cite.quoted_text}"
                    </p>
                  </div>

                  {#if cite.penalties}
                    <div class="text-xs flex items-baseline gap-1.5 pt-0.5 text-ink-700">
                      <strong class="text-ink-900 text-[11px]">Sanksi:</strong>
                      <span class="text-[11.5px]">{cite.penalties}</span>
                    </div>
                  {/if}
                </div>
              {/each}
            </div>
          {/if}

          {#if result.disclaimer}
            <div class="p-3 text-[11px] leading-relaxed text-ink-500 bg-[#f2f0ea]">
              {result.disclaimer}
            </div>
          {/if}
        </div>
      {:else}
        <div class="h-full flex items-center justify-center p-10 text-center text-ink-400">
          <p class="text-xs sm:text-sm max-w-xs">
            Masukkan teks klaim atau pilih salah satu contoh untuk menganalisis konteks hukumnya.
          </p>
        </div>
      {/if}
    </div>

  </div>
</div>
