<script>
  import { requestContextNote } from '../lib/api.js';

  let { onOpenDoc = () => {} } = $props();

  let postContent = $state('');
  let loading = $state(false);
  let errorMsg = $state('');
  let result = $state(null);
  let copySuccess = $state(false);

  const PRESETS = [
    {
      label: '🚨 Kasus Pura: Bule Manjat Pohon Suci',
      text: 'Viral di medsos: seorang wisatawan bule memanjat pohon beringin keramat di kawasan pura Tabanan tanpa pakaian dan berteriak kasar kepada warga lokal saat ditegur.'
    },
    {
      label: '💳 Kasus Pungutan: Menolak Bayar Tourist Levy',
      text: 'Beredar video wisatawan asing berdebat di bandara menolak membayar retribusi turis asing 150000 di loket Love Bali dan mengaku tidak tahu aturan tersebut.'
    },
    {
      label: '🔥 Uji Framing: "Semua bule kebal hukum"',
      text: 'Semua bule di Bali kebal hukum dan polisi diam saja! Harusnya langsung dideportasi sekarang juga tanpa pandang bulu!'
    },
    {
      label: '🛡️ Uji Abstain: Klaim di Luar Domain',
      text: 'Kucing oranye tertidur di atas meja kasir restoran dan meminta ikan tongkol goreng dari pengunjung.'
    }
  ];

  function applyPreset(p) {
    postContent = p.text;
  }

  async function handleSubmit(e) {
    if (e) e.preventDefault();
    if (!postContent.trim()) {
      errorMsg = 'Harap masukkan teks postingan atau klaim yang ingin dianalisis.';
      return;
    }
    loading = true;
    errorMsg = '';
    result = null;

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
      setTimeout(() => copySuccess = false, 2500);
    } catch (e) {
      console.error(e);
    }
  }
</script>

<div class="space-y-6">
  <!-- Input Form Card -->
  <div class="bg-white rounded-xl border border-borderline p-5 sm:p-6 shadow-sm">
    <div class="flex items-center justify-between pb-4 border-b border-borderline">
      <div>
        <h2 class="text-lg font-bold text-ink-900">Input Postingan Viral / Klaim Insiden</h2>
        <p class="text-xs text-ink-500 mt-0.5">Hasilkan Catatan Konteks netral berpasal, deteksi framing emosional, dan rujuk naskah resmi.</p>
      </div>
      <span class="text-xs font-mono bg-emerald-50 text-emerald-800 border border-emerald-100 px-2.5 py-1 rounded-md">
        Mode Konteks & Edukasi
      </span>
    </div>

    <!-- Presets -->
    <div class="mt-4">
      <span class="text-xs font-medium text-ink-500 block mb-2">Preset Simulasi Pengujian:</span>
      <div class="flex flex-wrap gap-2">
        {#each PRESETS as preset}
          <button
            type="button"
            onclick={() => applyPreset(preset)}
            class="text-xs px-3 py-1.5 rounded-lg bg-canvas hover:bg-black/5 border border-borderline text-ink-700 transition-colors font-medium text-left"
          >
            {preset.label}
          </button>
        {/each}
      </div>
    </div>

    <form onsubmit={handleSubmit} class="mt-4 space-y-4">
      <div>
        <label for="post-content" class="block text-xs font-semibold text-ink-700 uppercase tracking-wider mb-1.5">
          Teks Postingan / Caption Medsos / Transkrip Video
        </label>
        <textarea
          id="post-content"
          bind:value={postContent}
          rows="3"
          placeholder="Tempel teks postingan viral, keluhan warga, atau berita insiden di sini..."
          class="w-full px-3.5 py-2.5 text-sm rounded-lg border border-borderline focus:outline-none focus:ring-2 focus:ring-ink-900 focus:border-transparent font-sans"
        ></textarea>
      </div>

      {#if errorMsg}
        <div class="p-3 bg-red-50 text-red-700 rounded-lg text-xs border border-red-200">
          {errorMsg}
        </div>
      {/if}

      <div class="flex items-center justify-between pt-2">
        <span class="text-[11px] text-ink-400">
          *Pramana tidak pernah menyatakan seseorang bersalah — menyajikan konteks aturan murni.
        </span>
        <button
          type="submit"
          disabled={loading}
          class="px-5 py-2.5 bg-ink-900 hover:bg-black text-white text-sm font-semibold rounded-lg shadow transition-all flex items-center gap-2 disabled:opacity-50"
        >
          {#if loading}
            <span class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
            <span>Menganalisis Konteks Hukum...</span>
          {:else}
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path></svg>
            <span>Analisis Catatan Konteks</span>
          {/if}
        </button>
      </div>
    </form>
  </div>

  <!-- Results Section -->
  {#if result}
    <div class="space-y-5 animate-in fade-in duration-300">
      
      <!-- Abstain Notice (TIDAK DITEMUKAN) -->
      {#if result.status === 'TIDAK_DITEMUKAN'}
        <div class="bg-gray-100 border border-gray-300 rounded-xl p-6 text-center shadow-sm">
          <div class="w-12 h-12 rounded-full bg-gray-200 mx-auto flex items-center justify-center text-gray-600 mb-3">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
          </div>
          <h3 class="font-bold text-gray-900 text-base">Aturan Tidak Ditemukan (Strict-RAG Abstain)</h3>
          <p class="text-xs text-gray-600 max-w-lg mx-auto mt-2 leading-relaxed">
            {result.neutral_summary}
          </p>
          <div class="mt-4 inline-block px-3 py-1 bg-white border border-gray-300 rounded-full text-[11px] font-mono text-gray-700">
            Status: ZERO HALLUCINATION ABSTAIN
          </div>
        </div>
      {:else}

        <!-- Status & Confidence Banner -->
        <div class="bg-white rounded-xl border border-borderline p-5 shadow-sm">
          <div class="flex items-center justify-between flex-wrap gap-2 pb-3 border-b border-borderline">
            <div class="flex items-center gap-2">
              <span class="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
              <span class="text-xs font-bold text-ink-900 uppercase tracking-wide">Status Verifikasi:</span>
              <span class="text-xs font-mono font-bold bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded">
                TERVERIFIKASI ({result.confidence})
              </span>
            </div>

            {#if result.copyable_comment}
              <button
                onclick={copyComment}
                class="px-3 py-1.5 bg-ink-900 hover:bg-black text-white text-xs font-medium rounded-lg shadow-sm transition-all flex items-center gap-1.5"
              >
                {#if copySuccess}
                  <span class="text-emerald-400 font-bold">✓ Tersalin!</span>
                {:else}
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3"></path></svg>
                  <span>Salin Komentar Catatan Konteks</span>
                {/if}
              </button>
            {/if}
          </div>

          <!-- Emotional Framing Markers (if any) -->
          {#if result.framing_markers && result.framing_markers.length > 0}
            <div class="mt-4 p-3 bg-amber-50/90 border border-amber-200 rounded-lg text-xs">
              <span class="font-bold text-amber-950 block mb-1">⚠️ Penanda Bingkai Sensasional Dideteksi:</span>
              <div class="space-y-1">
                {#each result.framing_markers as marker}
                  <div class="flex items-center gap-2 text-amber-900">
                    <span class="font-mono bg-amber-200/70 px-1.5 py-0.5 rounded text-[11px] font-semibold">
                      "{marker.phrase}"
                    </span>
                    <span>→ {marker.reason}</span>
                  </div>
                {/each}
              </div>
            </div>
          {/if}

          <!-- Neutral Summary Card -->
          <div class="mt-4">
            <span class="text-xs font-bold text-ink-900 uppercase tracking-wider block mb-1">
              Catatan Konteks Netral:
            </span>
            <div class="p-4 bg-canvas/80 border border-borderline rounded-lg text-sm text-ink-800 leading-relaxed font-sans">
              {result.neutral_summary}
            </div>
          </div>
        </div>

        <!-- Citations List -->
        <div class="space-y-3">
          <h3 class="text-sm font-bold text-ink-900 uppercase tracking-wider">
            Dasar Hukum Resmi & Kutipan Verbatim ({result.citations.length} Rujukan)
          </h3>

          {#each result.citations as cite}
            <div class="bg-white rounded-xl border border-borderline p-5 shadow-sm">
              <div class="flex items-center justify-between flex-wrap gap-2 pb-2.5 border-b border-borderline/60">
                <div class="flex items-center gap-2">
                  <span class={`text-[11px] font-mono px-2 py-0.5 rounded-full font-bold ${
                    cite.tier === '1A' ? 'bg-indigo-100 text-indigo-800' :
                    cite.tier === '1B' ? 'bg-emerald-100 text-emerald-800' :
                    'bg-amber-100 text-amber-800'
                  }`}>
                    {cite.tier_label}
                  </span>
                  <span class="text-xs font-mono font-semibold text-ink-700">{cite.pasal}</span>
                </div>

                <div class="flex items-center gap-2">
                  <span class="text-[11px] font-mono text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded flex items-center gap-1">
                    <span>✓ Layer 1 Verified</span>
                  </span>
                  <button
                    onclick={() => onOpenDoc(cite)}
                    class="text-xs text-azure-700 hover:text-azure-900 font-medium flex items-center gap-1"
                  >
                    <span>Buka Teks</span>
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
                  </button>
                </div>
              </div>

              <h4 class="text-sm font-bold text-ink-900 mt-2.5">{cite.official_doc_title}</h4>

              <blockquote class="mt-2.5 p-3.5 bg-canvas/60 border-l-4 border-ink-900 text-xs text-ink-800 leading-relaxed italic font-serif">
                "{cite.quoted_text}"
              </blockquote>

              {#if cite.penalties}
                <div class="mt-2.5 flex items-start gap-1.5 text-xs text-red-700">
                  <span class="font-bold shrink-0">Konsekuensi Hukum:</span>
                  <span>{cite.penalties}</span>
                </div>
              {/if}
            </div>
          {/each}
        </div>

      {/if}

      <!-- Disclaimer -->
      <div class="p-3 bg-canvas border border-borderline rounded-lg text-center text-[11px] text-ink-500">
        {result.disclaimer}
      </div>

    </div>
  {/if}
</div>
