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
  let activeRuleIdx = $state(0);

  const PRESETS = [
    {
      label: '01 // Nyepi (18-21 Mar)',
      start: '2026-03-18',
      end: '2026-03-21',
      origin: 'international',
      text: 'Tiba di Bandara Ngurah Rai, menginap di Ubud tanggal 18 Maret 2026 sampai 21 Maret 2026. Berencana jalan-jalan ke Pura Saraswati dan sewa motor di jalan raya. Kode booking: GA4521 email: alex@travel.com.'
    },
    {
      label: '02 // Kawasan Suci Pura',
      start: '2026-06-10',
      end: '2026-06-15',
      origin: 'international',
      text: 'Rencana tur spiritual mengunjungi Pura Besakih dan Pura Lempuyang, mendaki Gunung Agung, dan mengambil foto komersial menggunakan drone di area pelataran utama pura.'
    },
    {
      label: '03 // Sewa Motor & Remote',
      start: '2026-07-01',
      end: '2026-07-20',
      origin: 'international',
      text: 'Tinggal di Canggu selama 3 minggu, menyewa motor bulanan dari perorangan tanpa plat nomor resmi, dan bekerja lepas sebagai web designer untuk klien luar negeri dari kafe lokal.'
    }
  ];

  function getShortTabLabel(item, idx) {
    const cat = (item.category || '').toLowerCase();
    const num = `0${idx + 1}`;
    if (cat.includes('pungutan') || cat.includes('levy')) return `${num} · Retribusi Wisman`;
    if (cat.includes('kewajiban') || cat.includes("do's")) return `${num} · Etika Kawasan Suci`;
    if (cat.includes('larangan') || cat.includes("don'ts")) return `${num} · Larangan Wisatawan`;
    if (cat.includes('keimigrasian')) return `${num} · Izin Keimigrasian`;
    if (cat.includes('nyepi')) return `${num} · Catur Brata Nyepi`;
    if (cat.includes('lalu lintas') || cat.includes('angkutan')) return `${num} · Lalu Lintas & Motor`;
    return `${num} · ${item.category.split(' ')[0]}`;
  }

  function getHumanTitle(item) {
    const cat = (item.category || '').toLowerCase();
    if (cat.includes('pungutan') || cat.includes('levy')) {
      return 'Kewajiban Retribusi Wisatawan Asing Rp150.000 (Love Bali)';
    }
    if (cat.includes('kewajiban') || cat.includes("do's") || cat.includes('dos')) {
      return 'Kewajiban Berbusana Adat/Sopan & Menghormati Kesucian Pura';
    }
    if (cat.includes('larangan') || cat.includes("don'ts") || cat.includes('donts')) {
      return 'Larangan Memanjat Pohon Suci & Perilaku Menodai Kawasan Pura';
    }
    if (cat.includes('keimigrasian')) {
      return 'Larangan Bekerja atau Berbisnis Ilegal dengan Visa Kunjungan';
    }
    if (cat.includes('nyepi')) {
      return 'Kepatuhan Catur Brata Penyepian (Penghentian Aktivitas 24 Jam)';
    }
    return item.title;
  }

  function getCompactnyepiRule(ruleName) {
    const r = (ruleName || '').toLowerCase();
    if (r.includes('geni')) return 'Tanpa api & cahaya luar';
    if (r.includes('karya')) return 'Toko & kantor tutup total';
    if (r.includes('lelungan')) return 'Wajib di dalam penginapan';
    if (r.includes('lelanguan')) return 'Hening & tanpa hiburan';
    return ruleName;
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
      activeRuleIdx = 0;
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
            01
          </span>
          <span class="px-3 py-0.5 text-[11px] font-semibold">Preventive Trip Brief</span>
        </div>

        <h1 class="opero-h1 text-[30px] sm:text-[42px]">
          Panduan <span class="opero-serif">Kepatuhan Rute</span> &amp; Kalender Bali
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

  <!-- 2. WORKSPACE GRID (No internal scrollbar, balanced 2-column hierarchy) -->
  <section class="px-5 sm:px-10 py-6 sm:py-8">
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">

      <!-- LEFT COLUMN: INPUT CARD (5 cols) -->
      <div class="lg:col-span-5">
        <div class="brutal-card p-5 sm:p-6 space-y-5" style="background-color: #f3f1eb;">
          <div class="flex items-center justify-between pb-3" style="border-bottom: 1px solid #cdc9be;">
            <span class="font-mono text-[10px] font-bold px-2 py-0.5" style="background-color: #dfd6c3; color: #0a0a0a; border: 1px solid #0a0a0a;">
              PARAMETER RUTE
            </span>
            <span class="font-mono text-[11px]" style="color: #5c5952;">PII Auto-Masking</span>
          </div>

          <form onsubmit={handleSubmit} class="space-y-4">
            <div>
              <label for="itinerary" class="block text-xs font-semibold mb-1.5" style="color: #0a0a0a;">
                Rencana Aktivitas &amp; Tujuan Kunjungan
              </label>
              <textarea
                id="itinerary"
                bind:value={itineraryText}
                rows="4"
                placeholder="Tulis rencana perjalanan, destinasi pura, sewa kendaraan, atau jadwal tiba..."
                style="background-color: #ffffff; color: #0a0a0a; border: 1.5px solid #0a0a0a;"
                class="w-full p-3 text-xs sm:text-[13px] focus:outline-none leading-relaxed"
              ></textarea>
            </div>

            <div class="grid grid-cols-2 gap-3">
              <div>
                <label for="start-date" class="block text-xs font-semibold mb-1" style="color: #0a0a0a;">
                  Tanggal Tiba
                </label>
                <input
                  id="start-date"
                  type="date"
                  bind:value={startDate}
                  style="background-color: #ffffff; color: #0a0a0a; border: 1.5px solid #0a0a0a;"
                  class="w-full px-2.5 py-2 text-xs font-mono"
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
                  style="background-color: #ffffff; color: #0a0a0a; border: 1.5px solid #0a0a0a;"
                  class="w-full px-2.5 py-2 text-xs font-mono"
                />
              </div>
            </div>

            <div>
              <label for="traveler-origin" class="block text-xs font-semibold mb-1" style="color: #0a0a0a;">
                Kategori Wisatawan
              </label>
              <select
                id="traveler-origin"
                bind:value={travelerOrigin}
                style="background-color: #ffffff; color: #0a0a0a; border: 1.5px solid #0a0a0a;"
                class="w-full px-3 py-2 text-xs font-medium"
              >
                <option value="international">Wisatawan Mancanegara / WNA (Wajib Love Bali Rp150.000)</option>
                <option value="domestic">Wisatawan Nusantara / WNI (Bebas Pungutan Wisman)</option>
              </select>
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
                {loading ? 'Memeriksa Korpus JDIH...' : 'Susun Panduan Kepatuhan'}
              </span>
              <span
                style="background-color: #dfd8c8; color: #0a0a0a;"
                class="opero-arrow-box w-8 h-8 flex items-center justify-center font-mono text-xs font-bold"
              >
                ↗
              </span>
            </button>
          </form>

          <!-- Clean Architectural Privacy Footnote -->
          <div class="pt-3 flex items-start gap-2.5 text-[11px]" style="border-top: 1px solid #cdc9be; color: #4a4740;">
            <svg class="w-4 h-4 shrink-0 mt-0.5" viewBox="0 0 18 18" fill="none">
              <rect x="3.5" y="8" width="11" height="7.5" stroke="#0a0a0a" stroke-width="1.5" />
              <path d="M6 8V5.5a3 3 0 0 1 6 0V8" stroke="#0a0a0a" stroke-width="1.5" />
            </svg>
            <span class="leading-snug">
              Data reservasi (email, nomor paspor, kode booking) disamarkan otomatis sebelum analisis.
            </span>
          </div>
        </div>
      </div>

      <!-- RIGHT COLUMN: HIERARCHICAL DOSSIER (7 cols) -->
      <div class="lg:col-span-7 space-y-5">
        {#if result}
          <!-- STEP 1: PRIMARY ALERT / CALENDAR STATUS -->
          {#if result.calendar_conflicts && result.calendar_conflicts.has_nyepi}
            {@const nyepi = result.calendar_conflicts.nyepi_summary}
            <div class="brutal-card-cobalt p-5 sm:p-6 space-y-4">
              <div class="flex flex-wrap items-center justify-between gap-2">
                <span
                  class="font-mono text-[10px] font-bold px-2 py-0.5"
                  style="background-color: #dfd6c3; color: #0a0a0a; border: 1px solid #0a0a0a;"
                >
                  PRIORITAS 01 // PERINGATAN KALENDER SAKA 1948
                </span>
                <span class="font-mono text-[11px] font-bold" style="color: #dfd6c3;">
                  {nyepi.date} · TUTUP TOTAL 24 JAM
                </span>
              </div>

              <div class="space-y-1.5">
                <h2 class="opero-h1 text-xl sm:text-2xl" style="color: #ffffff;">
                  Jadwal Melewati <span class="opero-serif" style="color: #dfd6c3;">{nyepi.event_name}</span>
                </h2>
                <p class="text-xs leading-relaxed" style="color: rgba(255, 255, 255, 0.88);">
                  Operasional Bandara Ngurah Rai, pelabuhan, jalan raya, dan jaringan internet seluler dihentikan penuh mulai pukul 06.00 WITA hingga 06.00 WITA keesokan harinya.
                </p>
              </div>

              <!-- 4 Catur Brata Architectural Grid -->
              <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-1">
                {#each nyepi.restrictions as r, idx}
                  <div
                    class="p-2.5"
                    style="background-color: #f3f1eb; color: #0a0a0a; border: 1.5px solid #0a0a0a;"
                  >
                    <span class="font-mono text-[10px] font-bold block" style="color: #0c249c;">
                      0{idx + 1} // {r.rule.replace('Amati ', '')}
                    </span>
                    <span class="text-[11px] font-semibold block mt-0.5 leading-tight">
                      {getCompactnyepiRule(r.rule)}
                    </span>
                  </div>
                {/each}
              </div>
            </div>
          {:else}
            <div class="brutal-card p-5 flex items-center justify-between" style="background-color: #dfd6c3;">
              <div class="space-y-1">
                <span class="font-mono text-[10px] font-bold px-2 py-0.5" style="background-color: #0c249c; color: #ffffff; border: 1px solid #0a0a0a;">
                  STATUS KALENDER SAKA 1948
                </span>
                <h2 class="text-base font-medium pt-1" style="color: #0a0a0a;">
                  Jadwal Perjalanan Normal ({result.start_date} s/d {result.end_date})
                </h2>
              </div>
              <span class="font-mono text-xs font-bold" style="color: #0c249c;">TANPA PENUTUPAN</span>
            </div>
          {/if}

          <!-- STEP 2: INTERACTIVE REGULATION INSPECTOR (No wall of text, 1 focused card at a time) -->
          <div class="brutal-card p-5 sm:p-6 space-y-5" style="background-color: #f3f1eb;">
            <!-- Header & Export Actions -->
            <div class="flex flex-wrap items-center justify-between gap-3 pb-3.5" style="border-bottom: 1px solid #cdc9be;">
              <div>
                <span class="font-mono text-[10px] font-bold px-2 py-0.5" style="background-color: #dfd6c3; color: #0a0a0a; border: 1px solid #0a0a0a;">
                  02 // KETENTUAN HUKUM ({result.briefing_items.length} PASAL)
                </span>
              </div>

              <div class="flex flex-wrap items-center gap-2">
                <button
                  type="button"
                  onclick={copyWhatsApp}
                  style="background-color: #ffffff; color: #0a0a0a; border: 1.5px solid #0a0a0a; box-shadow: 2px 2px 0px #0a0a0a;"
                  class="brutal-press px-3 py-1.5 font-mono text-[11px] font-semibold inline-flex items-center gap-1.5 cursor-pointer"
                >
                  <svg class="w-3.5 h-3.5" viewBox="0 0 18 18" fill="none">
                    <rect x="5.5" y="5.5" width="9" height="9" stroke="#0a0a0a" stroke-width="1.5" />
                    <path d="M12.5 5.5V3.5h-9v9h2" stroke="#0a0a0a" stroke-width="1.5" />
                  </svg>
                  <span>{copySuccess ? 'Tersalin' : 'Salin Ringkasan'}</span>
                </button>

                {#if result.calendar_conflicts && result.calendar_conflicts.has_nyepi}
                  <button
                    type="button"
                    onclick={downloadIcs}
                    style="background-color: #0c249c; color: #ffffff; border: 1.5px solid #0a0a0a; box-shadow: 2px 2px 0px #0a0a0a;"
                    class="brutal-press px-3 py-1.5 font-mono text-[11px] font-semibold inline-flex items-center gap-1.5 cursor-pointer"
                  >
                    <svg class="w-3.5 h-3.5" viewBox="0 0 18 18" fill="none">
                      <rect x="2.5" y="3.5" width="13" height="11" stroke="#ffffff" stroke-width="1.5" />
                      <path d="M2.5 7.5h13M6 2v3M12 2v3" stroke="#ffffff" stroke-width="1.5" />
                    </svg>
                    <span>Unduh Kalender .ICS</span>
                  </button>
                {/if}
              </div>
            </div>

            <!-- Numbered Selector Tabs (Lets user scan all 5 rules immediately without scrolling) -->
            <div class="flex flex-wrap gap-2">
              {#each result.briefing_items as item, idx}
                <button
                  type="button"
                  onclick={() => (activeRuleIdx = idx)}
                  style={activeRuleIdx === idx
                    ? 'background-color: #0c249c; color: #ffffff; border: 1.5px solid #0a0a0a; box-shadow: 2px 2px 0px #0a0a0a;'
                    : 'background-color: #ffffff; color: #0a0a0a; border: 1.5px solid #0a0a0a;'}
                  class="brutal-press px-3 py-2 font-mono text-[11px] font-semibold cursor-pointer"
                >
                  {getShortTabLabel(item, idx)}
                </button>
              {/each}
            </div>

            <!-- Active Rule Detail Card -->
            {#if result.briefing_items[activeRuleIdx]}
              {@const activeItem = result.briefing_items[activeRuleIdx]}
              <div
                class="p-5 bg-white space-y-4"
                style="border: 1.5px solid #0a0a0a; box-shadow: 3px 3px 0px #0a0a0a;"
              >
                <div class="flex flex-wrap items-center justify-between gap-2 pb-3" style="border-bottom: 1px solid #e6e4de;">
                  <span
                    class="font-mono text-[10px] font-bold px-2 py-0.5"
                    style="background-color: #dfd6c3; color: #0a0a0a; border: 1px solid #0a0a0a;"
                  >
                    {activeItem.category}
                  </span>
                  <span class="font-mono text-xs font-bold" style="color: #0c249c;">
                    {activeItem.pasal}
                  </span>
                </div>

                <div class="space-y-2">
                  <h3 class="text-base sm:text-lg font-medium tracking-tight" style="color: #0a0a0a;">
                    {getHumanTitle(activeItem)}
                  </h3>
                  <p class="text-xs sm:text-[13px] leading-relaxed" style="color: #3a3935;">
                    {activeItem.summary}
                  </p>
                </div>

                {#if activeItem.penalties}
                  <div
                    class="p-3 text-xs space-y-1"
                    style="background-color: #dfd6c3; border: 1px solid #0a0a0a; color: #0a0a0a;"
                  >
                    <span class="font-mono text-[10px] font-bold uppercase block">
                      Ketentuan Sanksi &amp; Penegakan
                    </span>
                    <p class="leading-snug">{activeItem.penalties}</p>
                  </div>
                {/if}

                <div class="pt-1 flex flex-wrap items-center justify-between gap-2">
                  <span class="font-mono text-[10px] truncate max-w-md" style="color: #5c5952;">
                    Sumber: {activeItem.title}
                  </span>

                  <button
                    type="button"
                    onclick={() => onOpenDoc(activeItem)}
                    style="background-color: #0a0a0a; color: #ffffff; padding: 2px; border: 1.5px solid #0a0a0a;"
                    class="brutal-press inline-flex items-center gap-2 text-xs font-medium cursor-pointer"
                  >
                    <span class="px-2.5 py-1 font-mono text-[11px]">Buka Naskah Verbatim</span>
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
              <span>JDIH Provinsi Bali · Saka 1948</span>
            </div>

            {#if showTechAudit}
              <div class="p-3 bg-white font-mono text-[11px] space-y-1" style="border: 1px solid #0a0a0a;">
                <div>ENGINE: <strong>{result.ai_engine}</strong></div>
                <div>GUARD: <strong>{result.guard_status}</strong></div>
                <div>PII MASKED: <strong>{result.pii_redacted_count} entitas</strong></div>
              </div>
            {/if}
          </div>
        {/if}
      </div>

    </div>
  </section>
</div>
