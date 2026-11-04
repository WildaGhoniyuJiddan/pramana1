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

  const PRESETS = [
    {
      label: '01 · Kawasan Suci (Pohon Keramat Pura)',
      tag: 'TERVERIFIKASI',
      text: 'Viral di medsos: seorang wisatawan bule memanjat pohon beringin keramat di kawasan pura Tabanan tanpa pakaian dan berteriak kasar kepada warga lokal saat ditegur.'
    },
    {
      label: '02 · Pungutan Wisman (Love Bali Rp150.000)',
      tag: 'TERVERIFIKASI',
      text: 'Beredar video wisatawan asing berdebat di bandara menolak membayar retribusi turis asing 150000 di loket Love Bali dan mengaku tidak tahu aturan tersebut.'
    },
    {
      label: '03 · Framing Sensasional ("Kebal Hukum")',
      tag: 'FRAMING',
      text: 'Semua bule di Bali kebal hukum dan polisi diam saja! Harusnya langsung dideportasi sekarang juga tanpa pandang bulu!'
    },
    {
      label: '04 · Uji Abstain (Di Luar Domain Hukum)',
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

    <!-- Atmospheric Opero Banner + Preset Selector -->
    <div class="p-3 sm:p-4" style="border-bottom: 1px solid #cdc9be;">
      <div
        class="relative overflow-hidden p-6 sm:p-8 flex flex-col md:flex-row md:items-end justify-between gap-6"
        style="background-color: #091e8a; color: #ffffff; border: 1.5px solid #0a0a0a; box-shadow: 4px 4px 0px #0a0a0a;"
      >
        <img
          src="/assets/opero_bali_hero.jpg"
          alt="Pointillist Bali Sky"
          class="absolute inset-0 w-full h-full object-cover opacity-35 pointer-events-none"
          style="object-position: center 22%;"
        />
        <div
          class="absolute inset-0 pointer-events-none"
          style="background: linear-gradient(90deg, rgba(8, 24, 115, 0.94) 0%, rgba(8, 24, 115, 0.72) 60%, rgba(8, 24, 115, 0.55) 100%);"
        ></div>

        <div class="relative z-10">
          <div class="inline-flex items-center text-[11px] font-medium mb-3" style="background-color: rgba(255,255,255,0.14); color: #ffffff; border-radius: 2px; padding: 2px;">
            <span style="background-color: #dfd8c8; color: #0a0a0a; border-radius: 1px;" class="px-2 py-0.5 font-bold">✦</span>
            <span class="px-3 py-0.5">Verifikasi Klaim Insiden &amp; Pengaman Zero-Hallucination</span>
          </div>
          <h1 class="opero-h1 text-3xl sm:text-5xl" style="color: #ffffff;">
            Verifikator <span class="opero-serif" style="color: #dfd8c8;">Context Note</span> &amp; Framing
          </h1>
        </div>

        <div class="relative z-10 flex flex-wrap gap-2">
          {#each PRESETS as preset, idx}
            <button
              type="button"
              onclick={() => applyPreset(preset, idx, true)}
              style={activePresetIdx === idx
                ? 'background-color: #dfd8c8; color: #0a0a0a; border-radius: 3px; font-weight: 600;'
                : 'background-color: rgba(255, 255, 255, 0.14); color: #ffffff; border: 1px solid rgba(255, 255, 255, 0.25); border-radius: 3px;'}
              class="px-3.5 py-2 text-xs transition-colors cursor-pointer backdrop-blur-xs"
            >
              {preset.label}
            </button>
          {/each}
        </div>
      </div>
    </div>

    <!-- Main 2-Pane Split Ledger -->
    <div class="grid grid-cols-1 lg:grid-cols-12">

      <!-- Left Pane: Claim Input (4 cols) -->
      <div class="lg:col-span-4 p-6 space-y-6" style="background-color: #f2f0ea; border-right: 1px solid #c8c4ba;">
        <form onsubmit={handleSubmit} class="space-y-5">
          <div>
            <label for="post-content" class="block text-xs font-semibold mb-2" style="color: #0a0a0a;">
              Teks Unggahan atau Narasi Klaim Viral
            </label>
            <textarea
              id="post-content"
              bind:value={postContent}
              rows="6"
              placeholder="Tempel teks unggahan media sosial, keluhan warga, atau klaim pelanggaran aturan di sini..."
              style="background-color: #ffffff; color: #0a0a0a; border: 1px solid #c8c4ba; border-radius: 4px;"
              class="w-full p-3.5 text-xs sm:text-sm focus:outline-none leading-relaxed"
            ></textarea>
            <span class="block text-[11px] mt-1.5" style="color: #5e5d58;">
              Prinsip netralitas: sistem merujuk naskah undang-undang yang berlaku tanpa menghakimi individu.
            </span>
          </div>

          {#if errorMsg}
            <div class="p-3 bg-white text-xs font-medium" style="border-left: 3px solid #b91c1c; color: #b91c1c;">
              {errorMsg}
            </div>
          {/if}

          <div class="pt-2">
            <button
              type="submit"
              disabled={loading}
              style="background-color: #0c249c; color: #ffffff;"
              class="w-full inline-flex items-stretch justify-between text-xs font-medium hover:opacity-95 transition-opacity disabled:opacity-50"
            >
              <span class="px-4 py-3 flex items-center gap-2">
                <span>{loading ? 'Memverifikasi Korpus JDIH...' : 'Uji Klaim & Susun Catatan Konteks'}</span>
              </span>
              <span
                style="background-color: #e6e4de; color: #0a0a0a; margin: 3px;"
                class="w-9 flex items-center justify-center font-mono text-xs font-bold"
              >
                ↗
              </span>
            </button>
          </div>
        </form>

        <div class="pt-5 space-y-2 text-xs" style="border-top: 1px solid #c8c4ba; color: #333330;">
          <span class="font-mono text-[10px] uppercase tracking-wider font-semibold block" style="color: #0c249c;">
            Protokol Verifikasi Dua Lapis
          </span>
          <p class="leading-relaxed">
            <strong>Layer 1 (Exact Match):</strong> Setiap kutipan pasal divalidasi karakter-per-karakter terhadap naskah asli di JDIH Provinsi Bali.
          </p>
          <p class="leading-relaxed">
            <strong>Layer 2 (Abstain Guard):</strong> Apabila klaim berada di luar cakupan regulasi, sistem memblokir sintesis AI dan mengembalikan status <code class="font-mono text-[11px] bg-white px-1">TIDAK_DITEMUKAN</code>.
          </p>
        </div>
      </div>

      <!-- Right Pane: Legal Verification Dossier (8 cols) -->
      <div class="lg:col-span-8 min-w-0" style="background-color: #e6e4de;">
        {#if result}
          {#key result.masked_post_content}
            <div class="animate-brutal-stamp">
          <!-- Row 1: Telemetry & Copy Strip -->
          <div class="px-6 py-3.5 flex flex-wrap items-center justify-between gap-3" style="background-color: #dfd8c8; border-bottom: 1px solid #c8c4ba;">
            <div class="flex flex-wrap items-center gap-3 font-mono text-[11px]" style="color: #0a0a0a;">
              <span>ENGINE: <strong>{result.ai_engine || 'Strict-RAG'}</strong></span>
              <span>|</span>
              <span>LAYER-2 GUARD: <strong>{result.guard_status}</strong></span>
              <span>|</span>
              <span style="color: #0c249c;" class="font-bold">CONFIDENCE: {result.confidence}</span>
            </div>

            {#if result.copyable_comment}
              <button
                type="button"
                onclick={copyComment}
                style="background-color: #0c249c; color: #ffffff;"
                class="px-3.5 py-1.5 text-xs font-medium hover:opacity-90 transition-opacity"
              >
                {copySuccess ? 'Tersalin ke Clipboard' : 'Salin Komentar Konteks'}
              </button>
            {/if}
          </div>

          {#if result.status === 'TIDAK_DITEMUKAN'}
            <div class="p-8 sm:p-12 bg-white space-y-4" style="border-bottom: 1px solid #c8c4ba;">
              <div class="inline-flex items-stretch text-[10px] font-mono" style="background-color: #0a0a0a; color: #ffffff;">
                <span style="background-color: #0c249c;" class="px-2 py-0.5 font-bold">L2</span>
                <span class="px-2.5 py-0.5">STRICT-RAG ABSTAIN · ZERO HALLUCINATION</span>
              </div>
              <h2 class="text-2xl font-normal tracking-tight" style="color: #0a0a0a;">
                Dasar hukum tidak ditemukan di korpus resmi Provinsi Bali.
              </h2>
              <p class="text-sm leading-relaxed max-w-2xl" style="color: #333330;">
                {result.neutral_summary}
              </p>
              <div class="pt-4 font-mono text-[11px]" style="border-top: 1px solid #c8c4ba; color: #5e5d58;">
                Status: Pemanggilan sintesis LLM dibatalkan secara deterministik karena tidak ada instrumen di `corpus/bali_regulations.json` yang mengatur klaim tersebut.
              </div>
            </div>
          {:else}
            <!-- Row 2: Neutral Context Note Summary -->
            <div class="p-6 space-y-2.5 bg-white" style="border-bottom: 1px solid #c8c4ba;">
              <span class="font-mono text-[10px] uppercase tracking-wider font-semibold block" style="color: #0c249c;">
                Catatan Konteks Netral (Siap Publikasi)
              </span>
              <p class="text-base sm:text-lg leading-relaxed" style="color: #0a0a0a;">
                {result.neutral_summary}
              </p>
            </div>

            <!-- Row 3: Sensational Framing Ledger -->
            {#if result.framing_markers && result.framing_markers.length > 0}
              <div class="p-6 space-y-3" style="background-color: #f2f0ea; border-bottom: 1px solid #c8c4ba;">
                <span class="font-mono text-[10px] uppercase tracking-wider font-semibold block" style="color: #0a0a0a;">
                  Penanda Retorika Sensasional / Generalisasi Terdeteksi ({result.framing_markers.length})
                </span>
                <div>
                  {#each result.framing_markers as marker}
                    <div class="py-2.5 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs" style="border-top: 1px solid #c8c4ba;">
                      <span class="font-mono px-2 py-0.5 bg-white self-start font-semibold" style="color: #0c249c; border: 1px solid #c8c4ba;">
                        "{marker.phrase}"
                      </span>
                      <span style="color: #333330;">{marker.reason}</span>
                    </div>
                  {/each}
                </div>
              </div>
            {/if}

            <!-- Row 4: Verbatim Citations Table -->
            <div>
              <div class="px-6 py-3 flex items-center justify-between font-mono text-[10px] uppercase tracking-wider" style="background-color: #dfd8c8; color: #0a0a0a; border-bottom: 1px solid #c8c4ba;">
                <span class="font-semibold">Rujukan Pasal Verbatim ({result.citations.length} Dokumen)</span>
                <span>Layer-1 Exact Match Verified</span>
              </div>

              {#each result.citations as cite}
                <div class="p-6 grid grid-cols-1 md:grid-cols-12 gap-4 bg-white hover:bg-stone/40 transition-colors" style="border-bottom: 1px solid #c8c4ba;">
                  <div class="md:col-span-4 space-y-1.5">
                    <span class="font-mono text-[10px] px-2 py-0.5 inline-block font-semibold" style="background-color: #0c249c; color: #ffffff;">
                      Tingkat {cite.tier} · {cite.tier_label}
                    </span>
                    <h4 class="text-sm font-semibold pt-1" style="color: #0a0a0a;">{cite.pasal}</h4>
                    <p class="font-mono text-[10px] font-semibold" style="color: #0c249c;">TERVERIFIKASI LAYER-1</p>
                    <button
                      type="button"
                      onclick={() => onOpenDoc(cite)}
                      style="color: #0c249c;"
                      class="pt-2 inline-block font-mono text-[11px] font-semibold hover:underline"
                    >
                      Buka Naskah Asli →
                    </button>
                  </div>

                  <div class="md:col-span-8 space-y-3">
                    <p class="text-xs font-semibold" style="color: #0a0a0a;">{cite.official_doc_title}</p>
                    <blockquote class="p-3.5 font-mono text-xs leading-relaxed" style="background-color: #f2f0ea; border-left: 3px solid #0c249c; color: #0a0a0a;">
                      "{cite.quoted_text}"
                    </blockquote>
                    {#if cite.penalties}
                      <div class="text-xs flex items-baseline gap-2" style="color: #333330;">
                        <span class="font-mono text-[10px] uppercase font-semibold shrink-0" style="color: #0a0a0a;">Sanksi:</span>
                        <span>{cite.penalties}</span>
                      </div>
                    {/if}
                  </div>
                </div>
              {/each}
            </div>
          {/if}

          <div class="px-6 py-3.5 font-mono text-[11px]" style="background-color: #f2f0ea; color: #5e5d58;">
            {result.disclaimer}
          </div>
            </div>
          {/key}
        {/if}
      </div>

    </div>
  </div>
</div>
