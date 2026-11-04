<script>
  import { onMount } from 'svelte';
  import { requestTripBrief } from '../lib/api.js';

  let { onOpenDoc = () => {} } = $props();

  let itineraryText = $state('');
  let startDate = $state('');
  let endDate = $state('');
  let travelerOrigin = $state('international');
  let loading = $state(false);
  let errorMsg = $state('');
  let result = $state(null);
  let copySuccess = $state(false);
  let showTechAudit = $state(false);
  let activePresetIdx = $state(0);
  let expandedItemId = $state(null);

  const PRESETS = [
    {
      label: 'Periode Nyepi (18-21 Mar 2026)',
      start: '2026-03-18',
      end: '2026-03-21',
      origin: 'international',
      text: 'Tiba di Bandara Ngurah Rai, menginap di Ubud tanggal 18 Maret 2026 sampai 21 Maret 2026. Berencana jalan-jalan ke Pura Saraswati dan sewa motor di jalan raya. Kode booking: GA4521 email: alex@travel.com.'
    },
    {
      label: 'Kawasan Pura & Tempat Suci',
      start: '2026-06-10',
      end: '2026-06-15',
      origin: 'international',
      text: 'Rencana tur spiritual mengunjungi Pura Besakih dan Pura Lempuyang, mendaki Gunung Agung, dan mengambil foto komersial menggunakan drone di area pelataran utama pura.'
    },
    {
      label: 'Sewa Motor & Kerja Remote',
      start: '2026-07-01',
      end: '2026-07-20',
      origin: 'international',
      text: 'Tinggal di Canggu selama 3 minggu, menyewa motor bulanan dari perorangan tanpa plat nomor resmi, dan bekerja lepas sebagai web designer untuk klien luar negeri dari kafe lokal.'
    }
  ];

  function getHumanTitle(item) {
    const cat = (item.category || '').toLowerCase();
    if (cat.includes('pungutan') || cat.includes('levy')) {
      return 'Kewajiban Pembayaran Retribusi Rp150.000 via Love Bali';
    }
    if (cat.includes('kewajiban') || cat.includes("do's") || cat.includes('dos')) {
      return 'Kewajiban Berbusana Sopan & Menghormati Kawasan Suci';
    }
    if (cat.includes('larangan') || cat.includes("don'ts") || cat.includes('donts')) {
      return 'Larangan Memanjat Pohon Suci & Perilaku Tidak Pantas';
    }
    if (cat.includes('keimigrasian')) {
      return 'Larangan Bekerja atau Bisnis Ilegal dengan Visa Wisata';
    }
    if (cat.includes('nyepi')) {
      return 'Kepatuhan Catur Brata Penyepian (Penghentian 24 Jam)';
    }
    return item.title;
  }

  onMount(() => {
    applyPreset(PRESETS[0], 0, true);
  });

  function applyPreset(p, idx, autoRun = false) {
    activePresetIdx = idx;
    itineraryText = p.text;
    startDate = p.start;
    endDate = p.end;
    travelerOrigin = p.origin;
    if (autoRun) handleSubmit();
  }

  async function handleSubmit(e) {
    if (e) e.preventDefault();
    if (!itineraryText.trim()) {
      errorMsg = 'Masukkan rencana perjalanan Anda terlebih dahulu.';
      return;
    }
    loading = true;
    errorMsg = '';

    try {
      result = await requestTripBrief({
        itinerary_text: itineraryText,
        start_date: startDate || undefined,
        end_date: endDate || undefined,
        traveler_origin: travelerOrigin
      });
    } catch (err) {
      errorMsg = err.message || 'Gagal menyusun panduan perjalanan.';
    } finally {
      loading = false;
    }
  }

  function downloadIcs() {
    if (!result || !result.ics_calendar) return;
    const blob = new Blob([result.ics_calendar], { type: 'text/calendar;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `panduan_bali_${startDate}.ics`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  async function copyWhatsApp() {
    if (!result || !result.whatsapp_text) return;
    try {
      await navigator.clipboard.writeText(result.whatsapp_text);
      copySuccess = true;
      setTimeout(() => (copySuccess = false), 2500);
    } catch (e) {
      console.error(e);
    }
  }

  function toggleExpand(id) {
    expandedItemId = expandedItemId === id ? null : id;
  }
</script>

<div class="mx-auto" style="max-width: 1360px; width: 100%; border-left: 1px solid #cdc9be; border-right: 1px solid #cdc9be; background-color: #e6e4de; color: #0a0a0a;">

  <!-- Compact Top Bar -->
  <div class="px-5 sm:px-8 py-4" style="border-bottom: 1px solid #cdc9be; background-color: #dfd8c8;">
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-3">
      <div>
        <h1 class="opero-h1 text-xl sm:text-2xl font-bold">
          Panduan Perjalanan &amp; <span class="opero-serif font-normal">Aturan Wisata Bali</span>
        </h1>
        <p class="text-xs text-ink-600 mt-0.5">
          Verifikasi rute terhadap naskah JDIH Bali, kalender Hari Suci Nyepi, dan kewajiban hukum resmi.
        </p>
      </div>

      <!-- Presets as neat pills -->
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

  <!-- Main 2-Pane Layout (Synchronized Viewport Height, No Orphan Blank Space) -->
  <div class="grid grid-cols-1 lg:grid-cols-12 items-stretch min-h-[calc(100vh-155px)]">

    <!-- Left Column: Input Panel -->
    <div
      class="lg:col-span-5 p-5 sm:p-6 space-y-4 flex flex-col justify-between"
      style="background-color: #f4f2ec; border-right: 1px solid #cdc9be;"
    >
      <form onsubmit={handleSubmit} class="space-y-3.5">
        <div>
          <label for="itinerary" class="block text-xs font-semibold mb-1" style="color: #0a0a0a;">
            Rencana Perjalanan Anda
          </label>
          <textarea
            id="itinerary"
            bind:value={itineraryText}
            rows="4"
            placeholder="Contoh: Menginap di Ubud tanggal 18-21 Maret, sewa motor ke pantai, dan berkunjung ke Pura Besakih..."
            style="background-color: #ffffff; color: #0a0a0a; border: 1.5px solid #0a0a0a;"
            class="w-full p-3 text-xs sm:text-sm focus:outline-none leading-relaxed"
          ></textarea>
          <div class="flex items-center gap-1.5 mt-1.5 text-[11px]" style="color: #5c5b57;">
            <svg class="w-3.5 h-3.5 shrink-0" viewBox="0 0 16 16" fill="currentColor">
              <path fill-rule="evenodd" d="M8 1a3.5 3.5 0 0 0-3.5 3.5V7A1.5 1.5 0 0 0 3 8.5v5A1.5 1.5 0 0 0 4.5 15h7a1.5 1.5 0 0 0 1.5-1.5v-5A1.5 1.5 0 0 0 11.5 7V4.5A3.5 3.5 0 0 0 8 1Zm2 6V4.5a2 2 0 1 0-4 0V7h4Z" clip-rule="evenodd" />
            </svg>
            <span>Data sensitif disamarkan otomatis sebelum analisis.</span>
          </div>
        </div>

        <!-- Dates in 1 clean compact row -->
        <div class="grid grid-cols-2 gap-2.5 pt-1" style="border-top: 1px solid #dcd7cb;">
          <div>
            <label for="start-date" class="block text-xs font-semibold mb-1" style="color: #0a0a0a;">
              Tanggal Tiba
            </label>
            <input
              id="start-date"
              type="date"
              bind:value={startDate}
              style="background-color: #ffffff; color: #0a0a0a; border: 1px solid #0a0a0a;"
              class="w-full px-2.5 py-1.5 text-xs"
            />
          </div>

          <div>
            <label for="end-date" class="block text-xs font-semibold mb-1" style="color: #0a0a0a;">
              Tanggal Pulang
            </label>
            <input
              id="end-date"
              type="date"
              bind:value={endDate}
              style="background-color: #ffffff; color: #0a0a0a; border: 1px solid #0a0a0a;"
              class="w-full px-2.5 py-1.5 text-xs"
            />
          </div>
        </div>

        <!-- Traveler Origin -->
        <div class="pt-1" style="border-top: 1px solid #dcd7cb;">
          <label for="traveler-origin" class="block text-xs font-semibold mb-1" style="color: #0a0a0a;">
            Kewarganegaraan
          </label>
          <select
            id="traveler-origin"
            bind:value={travelerOrigin}
            style="background-color: #ffffff; color: #0a0a0a; border: 1px solid #0a0a0a;"
            class="w-full px-2.5 py-1.5 text-xs font-medium"
          >
            <option value="international">Wisatawan Asing / WNA (Wajib Love Bali Rp150.000)</option>
            <option value="domestic">Wisatawan Nusantara / WNI (Bebas Pungutan)</option>
          </select>
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
          <span>{loading ? 'Memeriksa Korpus Hukum...' : 'Periksa Rencana Perjalanan'}</span>
          <span class="font-mono text-xs">→</span>
        </button>
      </form>

      <!-- Subtitle helper note -->
      <div class="pt-3 text-[11px] text-ink-500 space-y-1" style="border-top: 1px solid #dcd7cb;">
        <div>Korpus hukum terindeks: Perda No. 6/2023, SE Gubernur No. 4/2023, UU Keimigrasian No. 6/2011, dan Kalender Nyepi Saka 1948.</div>
      </div>
    </div>

    <!-- Right Column: Results Dossier (Scrollable Pane) -->
    <div
      class="lg:col-span-7 flex flex-col lg:max-h-[calc(100vh-155px)] overflow-hidden"
      style="background-color: #e6e4de;"
    >
      {#if result}
        <!-- Fixed Action Bar -->
        <div class="px-5 py-3 flex flex-wrap items-center justify-between gap-2 bg-white shrink-0" style="border-bottom: 1px solid #cdc9be;">
          <div class="text-xs">
            <span class="font-bold" style="color: #0a0a0a;">Hasil Kepatuhan Rute</span>
            <span class="text-ink-500 font-mono text-[11px] ml-1.5">({result.start_date} s/d {result.end_date})</span>
          </div>

          <div class="flex items-center gap-2">
            <button
              type="button"
              onclick={copyWhatsApp}
              style="background-color: #ffffff; color: #0a0a0a; border: 1px solid #0a0a0a;"
              class="px-2.5 py-1 text-xs font-medium hover:bg-stone/30 transition-colors cursor-pointer"
            >
              {copySuccess ? 'Tersalin' : 'Salin Ringkasan'}
            </button>

            {#if result.calendar_conflicts && result.calendar_conflicts.has_nyepi}
              <button
                type="button"
                onclick={downloadIcs}
                style="background-color: #0c249c; color: #ffffff;"
                class="px-2.5 py-1 text-xs font-medium hover:opacity-90 transition-opacity cursor-pointer"
              >
                Unduh .ICS
              </button>
            {/if}
          </div>
        </div>

        <!-- Scrollable Result Body -->
        <div class="flex-1 overflow-y-auto p-4 sm:p-5 space-y-3.5">

          <!-- Nyepi Notice Banner (Compact & High Impact) -->
          {#if result.calendar_conflicts && result.calendar_conflicts.has_nyepi}
            {@const nyepi = result.calendar_conflicts.nyepi_summary}
            <div style="background-color: #0c249c; color: #ffffff; border: 1px solid #0a0a0a;" class="p-4 space-y-2.5">
              <div class="flex items-start gap-2.5">
                <svg class="w-4 h-4 shrink-0 mt-0.5" viewBox="0 0 20 20" fill="#dfd8c8">
                  <path fill-rule="evenodd" d="M8.485 2.495c.673-1.167 2.357-1.167 3.03 0l6.28 10.875c.673 1.167-.17 2.625-1.516 2.625H3.72c-1.347 0-2.189-1.458-1.515-2.625L8.485 2.495zM10 5a.75.75 0 01.75.75v3.5a.75.75 0 01-1.5 0v-3.5A.75.75 0 0110 5zm0 9a1 1 0 100-2 1 1 0 000 2z" clip-rule="evenodd" />
                </svg>
                <div class="flex-1 min-w-0">
                  <div class="flex flex-wrap items-baseline justify-between gap-1">
                    <h3 class="text-xs sm:text-sm font-bold tracking-tight">
                      Peringatan: Jadwal Melewati {nyepi.event_name} ({nyepi.date})
                    </h3>
                    <span class="font-mono text-[10px] text-amber-200 uppercase font-semibold">Penghentian 24 Jam</span>
                  </div>
                  <p class="text-[11.5px] mt-1 text-blue-100 leading-snug">
                    Seluruh aktivitas publik, operasional bandara, pelabuhan, jalan raya, dan koneksi internet seluler dihentikan mulai pukul 06.00 WITA hingga 06.00 WITA keesokan harinya.
                  </p>
                </div>
              </div>

              <!-- 4 Catur Brata rules in compact horizontal chips -->
              <div class="grid grid-cols-2 sm:grid-cols-4 gap-1.5 pt-1" style="border-top: 1px solid rgba(255,255,255,0.2);">
                {#each nyepi.restrictions as r, idx}
                  <div class="p-1.5 bg-white text-ink-900 text-[10.5px]" style="border: 1px solid #0a0a0a;">
                    <span class="font-bold text-indigo-800 block text-[9.5px]">0{idx + 1} · {r.translation}</span>
                    <span class="text-ink-600 block line-clamp-1">{r.rule}</span>
                  </div>
                {/each}
              </div>
            </div>
          {/if}

          <!-- Plain-Language Itinerary Synthesis -->
          {#if result.ai_synthesis}
            <div class="p-4 bg-white space-y-1" style="border: 1px solid #c8c4ba;">
              <span class="text-[10px] font-mono font-semibold uppercase text-ink-500 block">
                Ringkasan Kepatuhan Wisatawan
              </span>
              <p class="text-xs sm:text-[13px] leading-relaxed text-ink-900">
                {result.ai_synthesis}
              </p>
            </div>
          {/if}

          <!-- Actionable Legal Rules (Clean Accordion List) -->
          <div class="space-y-2">
            <div class="flex items-center justify-between text-xs px-1">
              <span class="font-bold uppercase tracking-wider font-mono text-ink-900 text-[11px]">
                Ketentuan Terkait ({result.briefing_items.length} Regulasi)
              </span>
              <span class="text-[11px] text-ink-500">Klik item untuk detail sanksi &amp; naskah</span>
            </div>

            <div class="space-y-2">
              {#each result.briefing_items as item, idx}
                {@const isExpanded = expandedItemId === (item.id || idx)}
                <div
                  class="bg-white border transition-colors"
                  style="border-color: #c8c4ba;"
                >
                  <!-- Card Header Bar -->
                  <button
                    type="button"
                    onclick={() => toggleExpand(item.id || idx)}
                    class="w-full p-3.5 text-left flex items-start justify-between gap-3 hover:bg-stone/20 transition-colors cursor-pointer"
                  >
                    <div class="space-y-1 min-w-0">
                      <div class="flex items-center gap-2">
                        <span
                          class="px-1.5 py-0.5 font-mono text-[9.5px] font-bold shrink-0"
                          style="background-color: #dfd8c8; color: #0a0a0a; border: 1px solid #c8c4ba;"
                        >
                          {item.category}
                        </span>
                        <span class="font-mono text-[10.5px] text-ink-500 shrink-0">
                          {item.pasal}
                        </span>
                      </div>
                      <h4 class="text-xs sm:text-sm font-semibold text-ink-900 leading-snug">
                        {getHumanTitle(item)}
                      </h4>
                    </div>

                    <span class="text-xs text-ink-500 font-mono font-bold shrink-0 mt-1">
                      {isExpanded ? '▲' : '▼'}
                    </span>
                  </button>

                  <!-- Card Core Summary -->
                  <div class="px-3.5 pb-3 pt-0">
                    <p class="text-xs text-ink-700 leading-relaxed font-sans">
                      {item.summary}
                    </p>
                  </div>

                  <!-- Expandable Legal Details Drawer -->
                  {#if isExpanded}
                    <div
                      class="px-3.5 py-3 text-xs space-y-2 bg-[#faf9f6]"
                      style="border-top: 1px dashed #cdc9be;"
                    >
                      <div class="text-[11px] text-ink-500 font-mono">
                        Nomenklatur: <strong class="text-ink-900">{item.title}</strong>
                      </div>

                      {#if item.penalties}
                        <div class="p-2 bg-white text-xs border" style="border-color: #dcd7cb;">
                          <strong class="text-ink-900 text-[11px]">Ketentuan Sanksi:</strong>
                          <span class="text-ink-700 ml-1">{item.penalties}</span>
                        </div>
                      {/if}

                      <div class="pt-1 flex justify-end">
                        <button
                          type="button"
                          onclick={() => onOpenDoc(item)}
                          style="color: #0c249c;"
                          class="font-mono text-[11px] font-semibold hover:underline cursor-pointer"
                        >
                          Buka Naskah Lengkap di Korpus →
                        </button>
                      </div>
                    </div>
                  {/if}
                </div>
              {/each}
            </div>
          </div>

          <!-- Quiet Diagnostic Button -->
          <div class="pt-2 pb-4">
            <button
              type="button"
              onclick={() => (showTechAudit = !showTechAudit)}
              class="text-[11px] font-mono text-ink-500 hover:text-ink-900 flex items-center gap-1 cursor-pointer"
            >
              <span>{showTechAudit ? 'Tutup Diagnostik' : 'Lihat Diagnostik Mesin Verifikasi'}</span>
            </button>

            {#if showTechAudit}
              <div class="mt-2 p-2.5 text-[11px] font-mono space-y-1 bg-white border" style="border-color: #cdc9be;">
                <div>Engine: {result.ai_engine}</div>
                <div>Status Guard: {result.guard_status}</div>
                <div>PII Masked: {result.pii_redacted_count} entitas</div>
              </div>
            {/if}
          </div>

        </div>
      {:else}
        <div class="h-full flex items-center justify-center p-10 text-center text-ink-400">
          <p class="text-xs sm:text-sm max-w-xs">
            Isi rute perjalanan di sebelah kiri atau pilih salah satu contoh untuk melihat panduan aturan.
          </p>
        </div>
      {/if}
    </div>

  </div>
</div>
