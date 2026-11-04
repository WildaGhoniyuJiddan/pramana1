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

<div class="mx-auto" style="max-width: 1360px; width: 100%; border-left: 1px solid #cdc9be; border-right: 1px solid #cdc9be; background-color: #e6e4de; color: #0a0a0a; overflow: hidden;">
  <div>

    <!-- Header Strip -->
    <div class="p-6 sm:p-8" style="background-color: #dfd8c8; border-bottom: 1.5px solid #0a0a0a;">
      <div class="flex flex-col lg:flex-row lg:items-end justify-between gap-6">
        <div class="space-y-2">
          <div class="inline-flex items-center gap-2 text-[11px] font-semibold" style="color: #0c249c;">
            <span class="w-2 h-2 rounded-full inline-block" style="background-color: #0c249c;"></span>
            <span>KLARIFIKASI FAKTA &amp; RUJUKAN HUKUM RESMI</span>
          </div>
          <h1 class="opero-h1 text-2xl sm:text-4xl" style="color: #0a0a0a;">
            Uji Klaim &amp; <span class="opero-serif" style="color: #0c249c;">Catatan Konteks</span>
          </h1>
          <p class="text-xs sm:text-sm max-w-2xl leading-relaxed" style="color: #4a4943;">
            Validasi klaim atau kabar viral dengan naskah asli JDIH Provinsi Bali. Sistem menolak spekulasi dan hanya mengutip pasal yang terverifikasi.
          </p>
        </div>

        <!-- Scenario Chips -->
        <div class="space-y-2">
          <span class="block text-[10px] font-mono uppercase tracking-wider font-semibold" style="color: #5e5d58;">
            Coba Contoh Kasus:
          </span>
          <div class="flex flex-wrap gap-2">
            {#each PRESETS as preset, idx}
              <button
                type="button"
                onclick={() => applyPreset(preset, idx, true)}
                style={activePresetIdx === idx
                  ? 'background-color: #0c249c; color: #ffffff; border-color: #0a0a0a;'
                  : 'background-color: #ffffff; color: #0a0a0a; border-color: #c8c4ba;'}
                class="px-3 py-1.5 text-xs font-medium border rounded-xs transition-all hover:border-black cursor-pointer"
              >
                {preset.label}
              </button>
            {/each}
          </div>
        </div>
      </div>
    </div>

    <!-- Main 2-Pane Split Ledger -->
    <div class="grid grid-cols-1 lg:grid-cols-12">

      <!-- Left Pane: Claim Input (5 cols) -->
      <div class="lg:col-span-5 p-6 sm:p-7 space-y-6" style="background-color: #f2f0ea; border-right: 1px solid #c8c4ba;">
        <form onsubmit={handleSubmit} class="space-y-5">
          <div>
            <label for="post-content" class="block text-xs font-semibold mb-2" style="color: #0a0a0a;">
              Teks Klaim, Keluhan, atau Kabar Medsos
            </label>
            <textarea
              id="post-content"
              bind:value={postContent}
              rows="6"
              placeholder="Tempel teks unggahan media sosial, keluhan warga, atau klaim pelanggaran aturan di sini..."
              style="background-color: #ffffff; color: #0a0a0a; border: 1.5px solid #c8c4ba; border-radius: 4px;"
              class="w-full p-3.5 text-xs sm:text-sm focus:outline-none focus:border-black leading-relaxed"
            ></textarea>
            <span class="block text-[11px] mt-1.5" style="color: #5e5d58;">
              Prinsip netralitas: sistem merujuk naskah hukum resmi tanpa menghakimi pribadi.
            </span>
          </div>

          {#if errorMsg}
            <div class="p-3 bg-white text-xs font-medium" style="border-left: 3px solid #b91c1c; color: #b91c1c;">
              {errorMsg}
            </div>
          {/if}

          <div>
            <button
              type="submit"
              disabled={loading}
              style="background-color: #0c249c; color: #ffffff;"
              class="w-full inline-flex items-center justify-between px-4 py-3 text-xs font-semibold hover:opacity-95 transition-opacity disabled:opacity-50"
            >
              <span>{loading ? 'Memverifikasi Korpus JDIH...' : 'Periksa Klaim Sekarang'}</span>
              <span class="font-mono text-xs">→</span>
            </button>
          </div>
        </form>

        <div class="pt-5 space-y-2 text-xs" style="border-top: 1px solid #c8c4ba; color: #333330;">
          <span class="font-mono text-[10px] uppercase tracking-wider font-semibold block" style="color: #0c249c;">
            Prinsip Verifikasi
          </span>
          <p class="leading-relaxed">
            <strong>Pencocokan Pasti:</strong> Setiap kutipan pasal dicocokkan langsung terhadap naskah asli JDIH Provinsi Bali.
          </p>
          <p class="leading-relaxed">
            <strong>Tanpa Spekulasi:</strong> Jika peristiwa tidak diatur dalam regulasi, sistem akan langsung memberitahukan status tidak ditemukan.
          </p>
        </div>
      </div>

      <!-- Right Pane: Legal Verification Dossier (7 cols) -->
      <div class="lg:col-span-7 min-w-0" style="background-color: #e6e4de;">
        {#if result}
          {#key result.masked_post_content}
            <div class="animate-brutal-stamp">

              <!-- Top Bar: Quick Status & Copy -->
              <div class="px-6 py-4 flex flex-wrap items-center justify-between gap-3" style="background-color: #dfd8c8; border-bottom: 1px solid #c8c4ba;">
                <div class="flex items-center gap-2">
                  <span class="w-2 h-2 rounded-full" style={result.status === 'TIDAK_DITEMUKAN' ? 'background-color: #5e5d58;' : 'background-color: #15803d;'}></span>
                  <span class="text-xs font-bold" style="color: #0a0a0a;">
                    {result.status === 'TIDAK_DITEMUKAN' ? 'Di Luar Cakupan Regulasi' : 'Klarifikasi Siap Dibagikan'}
                  </span>
                </div>

                <div class="flex items-center gap-3">
                  <button
                    type="button"
                    onclick={() => (showTechAudit = !showTechAudit)}
                    class="text-[11px] font-mono underline hover:text-black"
                    style="color: #5e5d58;"
                  >
                    {showTechAudit ? 'Tutup Diagnostik' : 'Lihat Diagnostik'}
                  </button>

                  {#if result.copyable_comment}
                    <button
                      type="button"
                      onclick={copyComment}
                      style="background-color: #0c249c; color: #ffffff;"
                      class="px-3.5 py-1.5 text-xs font-medium hover:opacity-90 transition-opacity"
                    >
                      {copySuccess ? 'Tersalin' : 'Salin Catatan'}
                    </button>
                  {/if}
                </div>
              </div>

              <!-- Collapsible Tech Audit Drawer -->
              {#if showTechAudit}
                <div class="px-6 py-3 font-mono text-[11px] flex flex-wrap items-center gap-4 bg-white" style="border-bottom: 1px solid #c8c4ba; color: #4a4943;">
                  <span>ENGINE: <strong>{result.ai_engine || 'Strict-RAG'}</strong></span>
                  <span>GUARD: <strong>{result.guard_status}</strong></span>
                  <span>CONFIDENCE: <strong style="color: #0c249c;">{result.confidence}</strong></span>
                </div>
              {/if}

              {#if result.status === 'TIDAK_DITEMUKAN'}
                <div class="p-8 sm:p-10 bg-white space-y-4" style="border-bottom: 1px solid #c8c4ba;">
                  <div class="inline-flex items-center gap-2 px-2.5 py-1 text-xs font-semibold" style="background-color: #f2f0ea; color: #5e5d58;">
                    <span>STATUS: TIDAK DITEMUKAN</span>
                  </div>
                  <h2 class="text-xl sm:text-2xl font-normal tracking-tight" style="color: #0a0a0a;">
                    Dasar hukum tidak ditemukan di korpus regulasi resmi Bali.
                  </h2>
                  <p class="text-sm leading-relaxed max-w-2xl" style="color: #333330;">
                    {result.neutral_summary}
                  </p>
                  <p class="text-xs pt-3" style="border-top: 1px solid #e6e4de; color: #5e5d58;">
                    Sistem menolak membuat dugaan atau mengarang pasal untuk topik di luar naskah hukum yang terdata.
                  </p>
                </div>
              {:else}
                <!-- Neutral Context Note Summary -->
                <div class="p-6 sm:p-8 space-y-3 bg-white" style="border-bottom: 1px solid #c8c4ba;">
                  <span class="font-mono text-[10px] uppercase tracking-wider font-semibold block" style="color: #0c249c;">
                    Catatan Konteks Netral
                  </span>
                  <p class="text-base sm:text-lg leading-relaxed font-normal" style="color: #0a0a0a;">
                    {result.neutral_summary}
                  </p>
                </div>

                <!-- Sensational Framing Warning -->
                {#if result.framing_markers && result.framing_markers.length > 0}
                  <div class="p-6 space-y-3" style="background-color: #f7f5f0; border-bottom: 1px solid #c8c4ba;">
                    <div class="flex items-center gap-2">
                      <span class="text-xs font-semibold" style="color: #0a0a0a;">
                        Deteksi Narasi Sensasional atau Generalisasi ({result.framing_markers.length})
                      </span>
                    </div>
                    <div class="space-y-2">
                      {#each result.framing_markers as marker}
                        <div class="p-3 bg-white flex flex-col sm:flex-row sm:items-start justify-between gap-2 text-xs border" style="border-color: #dfd8c8;">
                          <span class="font-mono px-2 py-0.5 self-start font-semibold" style="background-color: #dfd8c8; color: #0a0a0a;">
                            "{marker.phrase}"
                          </span>
                          <span class="sm:max-w-md" style="color: #333330;">{marker.reason}</span>
                        </div>
                      {/each}
                    </div>
                  </div>
                {/if}

                <!-- Citations List -->
                <div>
                  <div class="px-6 py-3 flex items-center justify-between font-mono text-[10px] uppercase tracking-wider" style="background-color: #dfd8c8; color: #0a0a0a; border-bottom: 1px solid #c8c4ba;">
                    <span class="font-semibold">Rujukan Regulasi Terkait ({result.citations.length})</span>
                    <span>Tervalidasi Karakter demi Karakter</span>
                  </div>

                  {#each result.citations as cite}
                    <div class="p-6 grid grid-cols-1 md:grid-cols-12 gap-4 bg-white hover:bg-stone/20 transition-colors" style="border-bottom: 1px solid #c8c4ba;">
                      <div class="md:col-span-4 space-y-2">
                        <span class="text-[10px] font-mono px-2 py-0.5 inline-block font-semibold" style="background-color: #0c249c; color: #ffffff;">
                          {cite.tier_label || 'Regulasi'}
                        </span>
                        <h4 class="text-sm font-semibold" style="color: #0a0a0a;">{cite.pasal}</h4>
                        <button
                          type="button"
                          onclick={() => onOpenDoc(cite)}
                          style="color: #0c249c;"
                          class="inline-block text-xs font-semibold hover:underline"
                        >
                          Lihat Dokumen Lengkap →
                        </button>
                      </div>

                      <div class="md:col-span-8 space-y-2.5">
                        <p class="text-xs font-medium" style="color: #4a4943;">{cite.official_doc_title}</p>
                        <blockquote class="p-3.5 text-xs sm:text-sm leading-relaxed" style="background-color: #f7f5f0; border-left: 3px solid #0c249c; color: #0a0a0a;">
                          "{cite.quoted_text}"
                        </blockquote>
                        {#if cite.penalties}
                          <div class="text-xs flex items-baseline gap-2 pt-1" style="color: #333330;">
                            <span class="text-[11px] font-semibold shrink-0" style="color: #0a0a0a;">Sanksi:</span>
                            <span>{cite.penalties}</span>
                          </div>
                        {/if}
                      </div>
                    </div>
                  {/each}
                </div>
              {/if}

              {#if result.disclaimer}
                <div class="px-6 py-4 text-xs leading-relaxed" style="background-color: #f2f0ea; color: #5e5d58;">
                  {result.disclaimer}
                </div>
              {/if}

            </div>
          {/key}
        {/if}
      </div>

    </div>
  </div>
</div>
