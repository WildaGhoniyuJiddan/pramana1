<script>
  import { onMount } from 'svelte';
  import { requestTripBrief } from '../lib/api.js';

  let { onOpenDoc = () => {} } = $props();

  let itineraryText = $state('');
  let startDate = $state('2026-03-18');
  let endDate = $state('2026-03-21');
  let travelerOrigin = $state('international');
  let loading = $state(false);
  let errorMsg = $state('');
  let result = $state(null);
  let copySuccess = $state(false);
  let activePresetIdx = $state(0);
  let showTechAudit = $state(false);

  const PRESETS = [
    {
      label: 'Periode Nyepi (18-21 Mar 2026)',
      text: 'Tiba di Bandara Ngurah Rai, menginap di Ubud tanggal 18 Maret 2026 sampai 21 Maret 2026. Berencana jalan-jalan ke Pura Saraswati dan sewa motor di jalan raya. Kode booking: GA4521 email: alex@travel.com.',
      start: '2026-03-18',
      end: '2026-03-21',
      origin: 'international'
    },
    {
      label: 'Kawasan Pura & Tempat Suci',
      text: 'Mengunjungi Pura Besakih dan Pura Uluwatu, menonton Tari Kecak, belanja suvenir di Sukawati dan makan malam di Seminyak.',
      start: '2026-05-10',
      end: '2026-05-15',
      origin: 'international'
    },
    {
      label: 'Sewa Motor & Kerja Remote',
      text: 'Sewa sepeda motor untuk mobilitas Canggu - Seminyak, bekerja dari kafe, dan kunjungan ke pantai.',
      start: '2026-06-01',
      end: '2026-06-08',
      origin: 'international'
    }
  ];

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
      errorMsg = 'Masukkan rute perjalanan atau catatan reservasi terlebih dahulu.';
      return;
    }
    loading = true;
    errorMsg = '';

    try {
      result = await requestTripBrief({
        itinerary_text: itineraryText,
        start_date: startDate,
        end_date: endDate,
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
</script>

<div class="mx-auto" style="max-width: 1360px; width: 100%; border-left: 1px solid #cdc9be; border-right: 1px solid #cdc9be; background-color: #e6e4de; color: #0a0a0a;">

  <!-- Clean Editorial Sub-header -->
  <div class="px-6 sm:px-10 py-7" style="border-bottom: 1px solid #cdc9be; background-color: #dfd8c8;">
    <div class="flex flex-col md:flex-row md:items-end justify-between gap-4">
      <div>
        <div class="inline-flex items-center gap-1.5 text-[11px] font-mono tracking-wider uppercase text-ink-600 mb-1.5">
          <span class="w-2 h-2 rounded-full" style="background-color: #0c249c;"></span>
          <span>Mode 1 · Pencegahan Pra-Perjalanan</span>
        </div>
        <h1 class="opero-h1 text-2xl sm:text-4xl">
          Panduan Perjalanan &amp; <span class="opero-serif">Aturan Bali</span>
        </h1>
        <p class="text-xs sm:text-[13px] text-ink-600 mt-1 max-w-xl">
          Masukkan rencana kunjungan untuk memeriksa kewajiban hukum resmi, larangan kawasan suci, serta jadwal penutupan Hari Suci Nyepi.
        </p>
      </div>

      <!-- Presets as quiet chips -->
      <div class="flex flex-wrap items-center gap-2">
        <span class="text-xs text-ink-500 font-mono">Contoh:</span>
        {#each PRESETS as preset, idx}
          <button
            type="button"
            onclick={() => applyPreset(preset, idx, true)}
            style={activePresetIdx === idx
              ? 'background-color: #0c249c; color: #ffffff; border: 1.5px solid #0a0a0a; box-shadow: 2px 2px 0px #0a0a0a;'
              : 'background-color: #ffffff; color: #0a0a0a; border: 1px solid #c8c4ba;'}
            class="brutal-press px-3 py-1.5 text-xs font-medium cursor-pointer"
          >
            {preset.label}
          </button>
        {/each}
      </div>
    </div>
  </div>

  <!-- 2-Pane Split: Left Input, Right Results -->
  <div class="grid grid-cols-1 lg:grid-cols-12 min-h-[600px]">

    <!-- Left Column: Input Form -->
    <div class="lg:col-span-5 p-6 sm:p-7 space-y-5" style="background-color: #f4f2ec; border-right: 1px solid #cdc9be;">
      <form onsubmit={handleSubmit} class="space-y-5">
        <div>
          <label for="itinerary" class="block text-xs font-semibold mb-1.5" style="color: #0a0a0a;">
            Rencana Perjalanan Anda
          </label>
          <textarea
            id="itinerary"
            bind:value={itineraryText}
            rows="5"
            placeholder="Contoh: Menginap di Ubud tanggal 18-21 Maret, sewa motor ke pantai, dan berkunjung ke Pura Besakih..."
            style="background-color: #ffffff; color: #0a0a0a; border: 1.5px solid #0a0a0a; box-shadow: 2px 2px 0px #0a0a0a;"
            class="w-full p-3.5 text-xs sm:text-sm focus:outline-none leading-relaxed"
          ></textarea>
          <div class="flex items-center gap-2 mt-2 text-[11px]" style="color: #5c5b57;">
            <svg class="w-3.5 h-3.5 shrink-0 text-emerald-700" viewBox="0 0 16 16" fill="currentColor">
              <path fill-rule="evenodd" d="M8 1a3.5 3.5 0 0 0-3.5 3.5V7A1.5 1.5 0 0 0 3 8.5v5A1.5 1.5 0 0 0 4.5 15h7a1.5 1.5 0 0 0 1.5-1.5v-5A1.5 1.5 0 0 0 11.5 7V4.5A3.5 3.5 0 0 0 8 1Zm2 6V4.5a2 2 0 1 0-4 0V7h4Z" clip-rule="evenodd" />
            </svg>
            <span>Privasi aman: email, paspor, telepon, &amp; kode booking disamarkan otomatis sebelum diproses.</span>
          </div>
        </div>

        <!-- Dates -->
        <div class="grid grid-cols-2 gap-3 pt-3" style="border-top: 1px solid #dcd7cb;">
          <div>
            <label for="start-date" class="block text-xs font-semibold mb-1" style="color: #0a0a0a;">
              Tanggal Tiba
            </label>
            <input
              id="start-date"
              type="date"
              bind:value={startDate}
              style="background-color: #ffffff; color: #0a0a0a; border: 1px solid #0a0a0a;"
              class="w-full px-3 py-2 text-xs"
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
              class="w-full px-3 py-2 text-xs"
            />
          </div>
        </div>

        <!-- Traveler Origin -->
        <div class="pt-3" style="border-top: 1px solid #dcd7cb;">
          <label for="traveler-origin" class="block text-xs font-semibold mb-1" style="color: #0a0a0a;">
            Kewarganegaraan Wisatawan
          </label>
          <select
            id="traveler-origin"
            bind:value={travelerOrigin}
            style="background-color: #ffffff; color: #0a0a0a; border: 1px solid #0a0a0a;"
            class="w-full px-3 py-2.5 text-xs font-medium"
          >
            <option value="international">Wisatawan Asing / WNA (Wajib Retribusi Love Bali Rp150.000)</option>
            <option value="domestic">Wisatawan Nusantara / WNI (Bebas Retribusi Love Bali)</option>
          </select>
        </div>

        {#if errorMsg}
          <div class="p-3 bg-red-50 text-xs font-medium text-red-700 border-l-4 border-red-700">
            {errorMsg}
          </div>
        {/if}

        <button
          type="submit"
          disabled={loading}
          style="background-color: #0c249c; color: #ffffff; padding: 2px; border: 1.5px solid #0a0a0a; box-shadow: 3px 3px 0px #0a0a0a;"
          class="opero-split-btn brutal-press w-full inline-flex items-center justify-between text-xs font-medium cursor-pointer disabled:opacity-50"
        >
          <span class="px-4 py-2.5 font-semibold">
            {loading ? 'Memeriksa Korpus Hukum...' : 'Periksa Rencana Perjalanan'}
          </span>
          <span
            style="background-color: #dfd8c8; color: #0a0a0a;"
            class="opero-arrow-box w-8 h-8 flex items-center justify-center font-mono text-xs font-bold"
          >
            ↗
          </span>
        </button>
      </form>
    </div>

    <!-- Right Column: Results Dossier -->
    <div class="lg:col-span-7 min-w-0" style="background-color: #e6e4de;">
      {#if result}
        <div class="animate-page-fade">

          <!-- Action bar -->
          <div class="px-6 py-4 flex flex-wrap items-center justify-between gap-3 bg-white" style="border-bottom: 1px solid #cdc9be;">
            <div>
              <span class="text-xs font-semibold" style="color: #0a0a0a;">
                Hasil Analisis Kepatuhan Rute
              </span>
              <span class="block text-[11px] text-ink-500 font-mono">
                {result.start_date} s/d {result.end_date}
              </span>
            </div>

            <div class="flex items-center gap-2">
              <button
                type="button"
                onclick={copyWhatsApp}
                style="background-color: #ffffff; color: #0a0a0a; border: 1.5px solid #0a0a0a; box-shadow: 2px 2px 0px #0a0a0a;"
                class="brutal-press px-3 py-1.5 text-xs font-medium cursor-pointer"
              >
                {copySuccess ? 'Tersalin' : 'Salin Ringkasan'}
              </button>

              {#if result.calendar_conflicts && result.calendar_conflicts.has_nyepi}
                <button
                  type="button"
                  onclick={downloadIcs}
                  style="background-color: #0c249c; color: #ffffff; border: 1.5px solid #0a0a0a; box-shadow: 2px 2px 0px #0a0a0a;"
                  class="brutal-press px-3 py-1.5 text-xs font-medium cursor-pointer"
                >
                  Unduh Kalender (.ICS)
                </button>
              {/if}
            </div>
          </div>

          <!-- Alert Banner if Nyepi is inside travel window -->
          {#if result.calendar_conflicts && result.calendar_conflicts.has_nyepi}
            {@const nyepi = result.calendar_conflicts.nyepi_summary}
            <div style="background-color: #0c249c; color: #ffffff; border-bottom: 2px solid #0a0a0a;" class="p-6">
              <div class="flex items-start gap-3">
                <span class="text-xl">⚠️</span>
                <div>
                  <div class="font-mono text-[10px] tracking-wider uppercase font-bold text-amber-200">
                    Perhatian Kritis · Penghentian Total 24 Jam
                  </div>
                  <h3 class="text-lg sm:text-xl font-bold tracking-tight mt-0.5">
                    {nyepi.event_name} ({nyepi.date})
                  </h3>
                  <p class="text-xs sm:text-sm mt-1.5 text-blue-100 leading-relaxed max-w-2xl">
                    Jadwal perjalanan Anda melewati Hari Suci Nyepi. Seluruh aktivitas publik, bandara, pelabuhan, jalan raya, dan data seluler dihentikan mulai pukul 06.00 WITA hingga 06.00 WITA keesokan harinya.
                  </p>
                </div>
              </div>

              <!-- 4 Catur Brata rules in 4 clean cards -->
              <div class="mt-5 grid grid-cols-2 sm:grid-cols-4 gap-2.5">
                {#each nyepi.restrictions as r, idx}
                  <div class="p-3 bg-white text-ink-900" style="border: 1.5px solid #0a0a0a;">
                    <span class="font-mono text-[10px] font-bold text-indigo-700 block">0{idx + 1} / {r.rule}</span>
                    <span class="text-xs font-bold block mt-0.5">{r.translation}</span>
                    <p class="text-[11px] text-ink-600 mt-1 leading-snug">{r.instruction}</p>
                  </div>
                {/each}
              </div>
            </div>
          {/if}

          <!-- Plain-Language Summary -->
          {#if result.ai_synthesis}
            <div class="p-6 bg-white" style="border-bottom: 1px solid #cdc9be;">
              <span class="text-[11px] font-mono font-semibold uppercase text-ink-500 block mb-1">
                Ikhtisar Regulasi
              </span>
              <p class="text-sm sm:text-base leading-relaxed text-ink-900">
                {result.ai_synthesis}
              </p>
            </div>
          {/if}

          <!-- Applicable Legal Rules (Cards with clear categories) -->
          <div class="p-6 space-y-4">
            <div class="flex items-center justify-between">
              <span class="text-xs font-bold uppercase tracking-wider font-mono text-ink-900">
                Aturan Hukum yang Berlaku ({result.briefing_items.length} Pasal)
              </span>
              <span class="text-[11px] text-ink-500">
                Berdasarkan JDIH Provinsi Bali
              </span>
            </div>

            <div class="space-y-3">
              {#each result.briefing_items as item}
                <div
                  class="p-4 bg-white space-y-2"
                  style="border: 1.5px solid #0a0a0a; box-shadow: 2px 2px 0px #0a0a0a;"
                >
                  <div class="flex items-center justify-between gap-2">
                    <span
                      class="px-2 py-0.5 font-mono text-[10px] font-bold"
                      style="background-color: #dfd8c8; color: #0a0a0a; border: 1px solid #0a0a0a;"
                    >
                      {item.category}
                    </span>
                    <span class="font-mono text-[11px] font-semibold text-ink-600">
                      {item.pasal}
                    </span>
                  </div>

                  <h4 class="text-xs sm:text-sm font-bold text-ink-900">
                    {item.title}
                  </h4>

                  <p class="text-xs text-ink-700 leading-relaxed font-sans">
                    {item.summary}
                  </p>

                  <div class="pt-2 flex flex-wrap items-center justify-between gap-2 text-[11px]" style="border-top: 1px dashed #cdc9be;">
                    <div class="text-ink-600">
                      <strong class="text-ink-900">Sanksi:</strong> {item.penalties}
                    </div>
                    <button
                      type="button"
                      onclick={() => onOpenDoc(item)}
                      class="text-indigo-800 font-semibold hover:underline cursor-pointer"
                    >
                      Lihat Teks Pasal Penuh →
                    </button>
                  </div>
                </div>
              {/each}
            </div>
          </div>

          <!-- Collapsible Audit/Technical Telemetry (Quiet, not screaming) -->
          <div class="px-6 pb-6">
            <button
              type="button"
              onclick={() => (showTechAudit = !showTechAudit)}
              class="text-[11px] font-mono text-ink-500 hover:text-ink-900 flex items-center gap-1.5 cursor-pointer"
            >
              <span>{showTechAudit ? '▼ Sembunyikan' : '▶ Tampilkan'} Detail Teknis Verifikasi</span>
            </button>

            {#if showTechAudit}
              <div class="mt-2.5 p-3 text-[11px] font-mono space-y-1 bg-stone/20" style="border: 1px solid #cdc9be;">
                <div>Engine: {result.ai_engine}</div>
                <div>Status Verifier: {result.guard_status}</div>
                <div>Data Pribadi Terlindungi: {result.pii_redacted_count} data</div>
                {#if result.pii_redacted_count > 0}
                  <div class="text-ink-600 truncate">Log Bersih: {result.masked_itinerary}</div>
                {/if}
              </div>
            {/if}
          </div>

        </div>
      {:else}
        <div class="h-full flex items-center justify-center p-12 text-center text-ink-400">
          <p class="text-sm max-w-xs">
            Isi rute perjalanan di sebelah kiri atau pilih salah satu contoh untuk melihat hasil analisis aturan.
          </p>
        </div>
      {/if}
    </div>

  </div>
</div>
