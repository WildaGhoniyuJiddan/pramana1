<script>
  import { requestTripBrief, apiState } from '../lib/api.svelte.js';
  import { i18n, DICT } from '../lib/i18n.svelte.js';

  let { onOpenDoc = () => {} } = $props();

  let t = $derived(DICT[i18n.lang].trip);
  let common = $derived(DICT[i18n.lang].common);
  let presets = $derived(t.presets);

  let itineraryText = $state('');
  let startDate = $state('');
  let endDate = $state('');
  let travelerOrigin = $state('international');
  let loading = $state(false);
  let errorMsg = $state('');
  let result = $state(null);
  let copySuccess = $state(false);
  let showTechAudit = $state(false);
  let activePresetIdx = $state(-1);
  let lastPresetText = $state('');
  let activeRuleIdx = $state(0);
  let summaryLang = $derived(i18n.lang);

  const PRESET_DATES = [
    { start: '2026-03-18', end: '2026-03-21', origin: 'international' },
    { start: '2026-06-10', end: '2026-06-15', origin: 'international' },
    { start: '2026-07-01', end: '2026-07-20', origin: 'international' }
  ];

  $effect(() => {
    const curr = activePresetIdx >= 0 ? presets[activePresetIdx] : null;
    if (curr && itineraryText === lastPresetText && lastPresetText !== '') {
      itineraryText = curr.text;
      lastPresetText = curr.text;
    }
  });

  function getShortTabLabel(item, idx) {
    const isEn = i18n.lang === 'en';
    const num = `0${idx + 1}`;
    if (item.id === 'SE_GUB_04_2023_DO') return `${num} · ${isEn ? "Do's (Points 1-7)" : "Kewajiban (1-7)"}`;
    if (item.id === 'SE_GUB_04_2023_DONT') return `${num} · ${isEn ? "Don'ts (Points 2.a-2.h)" : "Larangan (2.a-2.h)"}`;
    if (item.id === 'PERDA_BALI_06_2023_LEVY') return `${num} · ${isEn ? 'Tourist Levy' : 'Pungutan Wisman'}`;
    if (item.id === 'PERDA_BALI_05_2020_PASAL_7') return `${num} · ${isEn ? 'Sacred Sites' : 'Perusakan DTW'}`;
    if (item.id === 'UU_22_2009_PASAL_77_281') return `${num} · ${isEn ? 'Driver License' : 'SIM Motor'}`;
    if (item.id === 'UU_22_2009_PASAL_291') return `${num} · ${isEn ? 'Helmet Mandate' : 'Kewajiban Helm'}`;
    if (item.display_title) {
      const clean = item.display_title.split('(')[0].trim();
      return `${num} · ${clean.slice(0, 18)}`;
    }
    return `${num} · ${item.category}`;
  }

  function getHumanTitle(item) {
    if (item.display_title) return item.display_title;
    if (i18n.lang === 'en' && item.title_en) return item.title_en;
    return item.title;
  }

  function getCompactnyepiRule(ruleName) {
    const isEn = i18n.lang === 'en';
    const r = (ruleName || '').toLowerCase();
    if (r.includes('geni')) return isEn ? 'No fire or outdoor light' : 'Tanpa api & cahaya luar';
    if (r.includes('karya')) return isEn ? 'All work and shops closed' : 'Toko & kantor tutup total';
    if (r.includes('lelungan')) return isEn ? 'Remain inside lodgings' : 'Wajib di dalam penginapan';
    if (r.includes('lelanguan')) return isEn ? 'Silence & no entertainment' : 'Hening & tanpa hiburan';
    return ruleName;
  }

  function applyPreset(p, idx) {
    activePresetIdx = idx;
    itineraryText = p.text;
    lastPresetText = p.text;
    const meta = PRESET_DATES[idx] || PRESET_DATES[0];
    startDate = meta.start;
    endDate = meta.end;
    travelerOrigin = meta.origin;
  }

  async function handleSubmit(e) {
    if (e) e.preventDefault();
    if (!itineraryText.trim()) {
      errorMsg = i18n.lang === 'en' ? 'Please enter your travel plans.' : 'Masukkan rencana perjalanan Anda terlebih dahulu.';
      return;
    }
    if (!startDate) {
      errorMsg = i18n.lang === 'en' ? 'Please select an arrival date.' : 'Tentukan tanggal tiba terlebih dahulu.';
      return;
    }
    if (endDate && endDate < startDate) {
      errorMsg = i18n.lang === 'en' ? 'Departure date cannot be earlier than arrival date.' : 'Tanggal pulang tidak boleh lebih awal dari tanggal tiba.';
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
      errorMsg = err.message || (i18n.lang === 'en' ? 'Failed to generate trip brief.' : 'Gagal menyusun panduan perjalanan.');
    } finally {
      loading = false;
    }
  }

  function downloadIcs() {
    if (!result || !result.ics_content) return;
    const blob = new Blob([result.ics_content], { type: 'text/calendar;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `panduan_bali_${result.start_date || startDate || 'trip'}.ics`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  function formatDate(value) {
    if (!value) return '-';
    const d = new Date(`${value}T00:00:00`);
    if (Number.isNaN(d.getTime())) return value;
    return new Intl.DateTimeFormat('id-ID', {
      day: 'numeric',
      month: 'short',
      year: 'numeric'
    }).format(d);
  }

  function sakaYearLabel() {
    const saka = result?.calendar_conflicts?.nyepi_summary?.saka_year;
    return saka ? `Saka ${saka}` : 'Kalender Saka';
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
          <span class="px-3 py-0.5 text-[11px] font-semibold">{t.badge}</span>
        </div>

        <h1 class="opero-h1 text-[30px] sm:text-[42px]">
          {t.title}
        </h1>
      </div>

      <!-- Preset Selector Buttons -->
      <div class="flex flex-wrap items-center gap-2">
        {#each presets as preset, idx}
          <button
            type="button"
            onclick={() => applyPreset(preset, idx)}
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
              {t.inputSection}
            </span>
            <span class="font-mono text-[11px]" style="color: #5c5952;">PII Auto-Masking</span>
          </div>

          <form onsubmit={handleSubmit} class="space-y-4">
            <div>
              <label for="itinerary" class="block text-xs font-semibold mb-1.5" style="color: #0a0a0a;">
                {t.inputLabel}
              </label>
              <textarea
                id="itinerary"
                bind:value={itineraryText}
                rows="4"
                placeholder={t.placeholder}
                style="background-color: #ffffff; color: #0a0a0a; border: 1.5px solid #0a0a0a;"
                class="w-full p-3 text-xs sm:text-[13px] focus:outline-none leading-relaxed"
              ></textarea>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label for="start-date" class="block text-xs font-semibold mb-1" style="color: #0a0a0a;">
                  {t.startDate}
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
                  {t.endDate}
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
                {t.travelerType}
              </label>
              <select
                id="traveler-origin"
                bind:value={travelerOrigin}
                style="background-color: #ffffff; color: #0a0a0a; border: 1.5px solid #0a0a0a;"
                class="w-full px-3 py-2 text-xs font-medium"
              >
                <option value="international">{t.typeInt}</option>
                <option value="domestic">{t.typeDom}</option>
              </select>
            </div>

            {#if apiState.isWakingUp}
          <div class="brutal-card p-4 flex items-center gap-3" style="background-color: #fff3cd; border-color: #8a3b00; color: #8a3b00;">
            <span class="animate-spin text-lg">⏳</span>
            <span class="font-mono text-xs font-bold">{apiState.message || common.serverWakingUp}</span>
          </div>
        {/if}

        {#if errorMsg}
              <div role="alert" aria-live="polite" class="p-3 text-xs font-medium" style="background-color: #ffffff; border: 1.5px solid #c92a2a; color: #c92a2a;">
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
                {loading ? t.loadingBtn : t.submitBtn}
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
              {t.privacyNote}
            </span>
          </div>
        </div>
      </div>

      <!-- RIGHT COLUMN: HIERARCHICAL DOSSIER (7 cols) -->
      <div class="lg:col-span-7 space-y-5">
        {#if result}
          <!-- RESULT SUMMARY / STATUS -->
          <div class="brutal-card p-5 sm:p-6 space-y-4" style="background-color: #f3f1eb;">
            <div class="flex flex-wrap items-center justify-between gap-2">
              <span
                class="font-mono text-[10px] font-bold px-2 py-0.5"
                style="background-color: #0c249c; color: #ffffff; border: 1px solid #0a0a0a;"
              >
                RINGKASAN &amp; STATUS VERIFIKASI
              </span>
              <span
                class="font-mono text-[11px] font-bold"
                style={result.status === 'SUCCESS' ? 'color: #0c249c;' : 'color: #8a3b00;'}
              >
                {result.status} · Keyakinan: {result.confidence}
              </span>
            </div>

            <div>
              <p class="text-xs sm:text-[13px] leading-relaxed" style="color: #0a0a0a;">
                {summaryLang === 'en' && result.ai_synthesis_en
                  ? result.ai_synthesis_en
                  : result.ai_synthesis}
              </p>
            </div>

            {#if result.ai_synthesis_status === 'llm'}
              <p class="text-[11px] font-mono" style="color: #8a3b00;">
                {common.llmNotice}
              </p>
            {:else if result.ai_synthesis_status === 'unavailable'}
              <p class="text-[11px] font-mono" style="color: #8a3b00;">
                {common.unavailableNotice}
              </p>
            {:else if result.ai_synthesis_status === 'abstain'}
              <p class="text-[11px] font-mono" style="color: #8a3b00;">
                {common.abstainNotice}
              </p>
            {:else}
              <p class="text-[11px] font-mono" style="color: #5c5952;">
                {common.templateNotice}
              </p>
            {/if}

            {#if result.ai_claims?.length}
              <p class="font-mono text-[10px]" style="color: #0c249c;">
                {result.ai_claims.length} claims verified against evidence span.
              </p>
            {/if}

            {#if result.confidence_note}
              <p class="text-[11px]" style="color: #5c5952;">{result.confidence_note}</p>
            {/if}

            {#if result.calendar_conflicts?.coverage_warning}
              <div
                class="p-3 text-xs leading-snug"
                style="background-color: #fff3cd; border: 1.5px solid #8a3b00; color: #5c2d00;"
              >
                {result.calendar_conflicts.coverage_warning}
              </div>
            {/if}

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11px]">
              <div class="p-3" style="background-color: #ffffff; border: 1px solid #0a0a0a;">
                <span class="font-mono font-bold block mb-1">{common.maskedText.toUpperCase()}</span>
                <span style="color: #3a3935;">{result.masked_itinerary}</span>
              </div>
              <div class="p-3" style="background-color: #ffffff; border: 1px solid #0a0a0a;">
                <span class="font-mono font-bold block mb-1">{common.piiRedacted.toUpperCase()}</span>
                <span style="color: #3a3935;">{result.pii_redacted_count} {common.entities}</span>
              </div>
            </div>

            <div class="flex flex-wrap items-center gap-2">
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
                <span>{t.downloadIcs}</span>
              </button>
              {#if travelerOrigin === 'international'}
                <a
                  href="https://lovebali.baliprov.go.id"
                  target="_blank"
                  rel="noopener noreferrer"
                  style="background-color: #dfd6c3; color: #0a0a0a; border: 1.5px solid #0a0a0a; box-shadow: 2px 2px 0px #0a0a0a;"
                  class="brutal-press px-3 py-1.5 font-mono text-[11px] font-bold inline-flex items-center gap-1.5 cursor-pointer"
                >
                  <span>{t.loveBaliLink}</span>
                </a>
              {/if}
            </div>
          </div>

          <!-- STEP 1: PRIMARY ALERT / CALENDAR STATUS -->
          {#if result.calendar_conflicts && result.calendar_conflicts.has_nyepi}
            {@const nyepi = result.calendar_conflicts.nyepi_summary}
            <div class="brutal-card-cobalt p-5 sm:p-6 space-y-4">
              <div class="flex flex-wrap items-center justify-between gap-2">
                <span
                  class="font-mono text-[10px] font-bold px-2 py-0.5"
                  style="background-color: #dfd6c3; color: #0a0a0a; border: 1px solid #0a0a0a;"
                >
                  {t.priorityCalendar} {sakaYearLabel().toUpperCase()}
                </span>
                <span class="font-mono text-[11px] font-bold" style="color: #dfd6c3;">
                  {nyepi.date} · 06.00 WITA – 06.00 WITA
                </span>
              </div>

              <div class="space-y-1.5">
                <h2 class="opero-h1 text-xl sm:text-2xl" style="color: #ffffff;">
                  {i18n.lang === 'en' ? 'Itinerary overlaps' : 'Jadwal Melewati'} <span class="opero-serif" style="color: #dfd6c3;">{nyepi.event_name}</span>
                </h2>
                <p class="text-xs leading-relaxed" style="color: rgba(255, 255, 255, 0.88);">
                  {nyepi.overlap_note}
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
            <div class="brutal-card p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-3" style="background-color: #dfd6c3;">
              <div class="space-y-1">
                <span class="font-mono text-[10px] font-bold px-2 py-0.5" style="background-color: #0c249c; color: #ffffff; border: 1px solid #0a0a0a;">
                  {i18n.lang === 'en' ? 'SAKA CALENDAR STATUS' : 'STATUS KALENDER SAKA'}
                </span>
                {#if result.calendar_conflicts?.events?.length}
                  <h2 class="text-base font-medium pt-1" style="color: #0a0a0a;">
                    {i18n.lang === 'en' ? `${result.calendar_conflicts.events.length} cultural advisories in this period` : `Ada ${result.calendar_conflicts.events.length} peringatan budaya pada rentang ini`}
                  </h2>
                  <p class="text-[11px] leading-snug" style="color: #3a3935;">
                    {result.calendar_conflicts.events.map((e) => e.name).join(' · ')}
                  </p>
                {:else}
                  <h2 class="text-base font-medium pt-1" style="color: #0a0a0a;">
                    {i18n.lang === 'en' ? `Normal Travel Schedule (${formatDate(result.start_date)} to ${formatDate(result.end_date)})` : `Jadwal Perjalanan Normal (${formatDate(result.start_date)} s/d ${formatDate(result.end_date)})`}
                  </h2>
                {/if}
              </div>
              <span class="font-mono text-xs font-bold shrink-0" style="color: #0c249c;">
                {result.calendar_conflicts?.events?.length ? (i18n.lang === 'en' ? 'CHECK CEREMONY' : 'CEK UPACARA') : (i18n.lang === 'en' ? 'NO CLOSURE' : 'TANPA PENUTUPAN')}
              </span>
            </div>
          {/if}

          {#if result.status !== 'TIDAK_DITEMUKAN'}
          <!-- STEP 2: INTERACTIVE REGULATION INSPECTOR (No wall of text, 1 focused card at a time) -->
          <div class="brutal-card p-5 sm:p-6 space-y-5" style="background-color: #f3f1eb;">
            <!-- Header & Export Actions -->
            <div class="flex flex-wrap items-center justify-between gap-3 pb-3.5" style="border-bottom: 1px solid #cdc9be;">
              <div>
                <span class="font-mono text-[10px] font-bold px-2 py-0.5" style="background-color: #dfd6c3; color: #0a0a0a; border: 1px solid #0a0a0a;">
                  {t.priorityLegal} ({result.briefing_items.length} {t.articlesLabel})
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
                  <span>{copySuccess ? common.copied : common.copySummary}</span>
                </button>
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
                    {i18n.lang === 'en' ? (activeItem.category_en || activeItem.category) : activeItem.category}
                  </span>
                  <span class="font-mono text-xs font-bold" style="color: #0c249c;">
                    {activeItem.pasal}
                  </span>
                </div>

                <!-- Superseded banner if status is Disempurnakan or superseded_by is present -->
                {#if activeItem.status === 'Disempurnakan' || activeItem.superseded_by}
                  <div
                    class="p-3 text-xs font-semibold flex items-center gap-2"
                    style="background-color: #fff3cd; border: 1.5px solid #8a3b00; color: #8a3b00;"
                  >
                    <span>⚠️</span>
                    <span>{common.supersededBanner}</span>
                  </div>
                {/if}

                <div class="flex flex-wrap gap-1.5">
                  <span
                    class="font-mono text-[10px] font-bold px-2 py-0.5"
                    style="background-color: #ffffff; color: #0a0a0a; border: 1px solid #0a0a0a;"
                  >
                    Status: {activeItem.status || '-'}
                  </span>
                  {#if i18n.lang === 'en'}
                    <span
                      class="font-mono text-[10px] font-bold px-2 py-0.5"
                      style="background-color: #fff3cd; color: #8a3b00; border: 1px solid #8a3b00;"
                    >
                      {activeItem.translation_status === 'human-reviewed' ? common.humanReviewedNotice : common.aiAssistedNotice}
                    </span>
                  {:else}
                    <span
                      class="font-mono text-[10px] font-bold px-2 py-0.5"
                      style={activeItem.is_verbatim
                        ? 'background-color: #e7f0ff; color: #0c249c; border: 1px solid #0c249c;'
                        : 'background-color: #fff3cd; color: #8a3b00; border: 1px solid #8a3b00;'}
                    >
                      {activeItem.text_status === 'compilation'
                        ? common.compilationNotice
                        : activeItem.is_verbatim ? common.verbatimNotice : common.summaryNotice}
                    </span>
                  {/if}
                </div>

                {#if activeItem.trigger_reason}
                  <div>
                    <span
                      class="font-mono text-[10px] font-bold px-2 py-0.5 inline-block"
                      style="background-color: #dfd6c3; color: #0a0a0a; border: 1px solid #0a0a0a;"
                    >
                      {i18n.lang === 'en' && activeItem.trigger_reason_en ? activeItem.trigger_reason_en : activeItem.trigger_reason}
                    </span>
                  </div>
                {/if}

                <div class="space-y-2">
                  <h3 class="text-base sm:text-lg font-medium tracking-tight" style="color: #0a0a0a;">
                    {getHumanTitle(activeItem)}
                  </h3>

                  {#if i18n.lang === 'en'}
                    <!-- Translation notice & English display text -->
                    <div class="p-2.5 bg-[#fbfaf8] border border-[#dcd7cb] text-[11px] text-[#8a3b00] font-mono">
                      ℹ️ {common.translationNotice}
                    </div>
                    <p class="text-xs sm:text-[13px] leading-relaxed font-sans" style="color: #2b2b29;">
                      {activeItem.display_text || activeItem.summary}
                    </p>

                    <!-- Open Collapsible Drawer for Verbatim Original Indonesian Statute Text -->
                    <details open class="mt-3 border border-[#0a0a0a] bg-[#faf9f6]">
                      <summary class="px-3 py-2 font-mono text-[10px] font-bold cursor-pointer uppercase bg-[#dfd6c3] flex items-center justify-between text-[#0c249c]">
                        <span>{common.originalAuthoritativeLabel}</span>
                        <span class="text-[9px] font-normal text-[#5c5952]">[KLIK UNTUK BUKA/TUTUP]</span>
                      </summary>
                      <div class="p-3.5 text-xs font-mono whitespace-pre-line leading-relaxed text-[#0a0a0a]">
                        {activeItem.text_original || activeItem.full_text}
                      </div>
                    </details>
                  {:else}
                    <p class="text-xs sm:text-[13px] leading-relaxed" style="color: #3a3935;">
                      {activeItem.summary}
                    </p>
                  {/if}

                  {#if activeItem.display_status_note || activeItem.status_note}
                    <p class="text-[11px] leading-snug" style="color: #8a3b00;">
                      {activeItem.display_status_note || activeItem.status_note}
                    </p>
                  {/if}
                  {#if activeItem.display_source_note || activeItem.source_note}
                    <p class="text-[11px] leading-snug" style="color: #5c5952;">
                      {activeItem.display_source_note || activeItem.source_note}
                    </p>
                  {/if}
                  {#if activeItem.superseded_by}
                    <p class="text-[11px] leading-snug" style="color: #5c5952;">
                      {common.supersededBy}
                      {#if activeItem.superseded_by_url}
                        <a href={activeItem.superseded_by_url} target="_blank" rel="noopener noreferrer" class="underline" style="color: #0c249c;">
                          {activeItem.superseded_by}
                        </a>
                      {:else}
                        {activeItem.superseded_by}
                      {/if}
                    </p>
                  {/if}
                </div>

                {#if activeItem.display_penalties || activeItem.penalties}
                  <div
                    class="p-3 text-xs space-y-1"
                    style="background-color: #dfd6c3; border: 1px solid #0a0a0a; color: #0a0a0a;"
                  >
                    <span class="font-mono text-[10px] font-bold uppercase block">
                      {common.penaltiesTitle}
                    </span>
                    <p class="leading-snug">{activeItem.display_penalties || activeItem.penalties}</p>
                  </div>
                {/if}

                <div class="pt-1 flex flex-wrap items-center justify-between gap-2">
                  <span class="font-mono text-[10px] truncate max-w-md" style="color: #5c5952;">
                    {i18n.lang === 'en' ? 'Source: ' : 'Sumber: '}{activeItem.display_title || activeItem.title}{#if activeItem.last_verified_date} · {formatDate(activeItem.last_verified_date)}{/if}
                  </span>

                  <button
                    type="button"
                    onclick={() => onOpenDoc(activeItem)}
                    style="background-color: #0a0a0a; color: #ffffff; padding: 2px; border: 1.5px solid #0a0a0a;"
                    class="brutal-press inline-flex items-center gap-2 text-xs font-medium cursor-pointer"
                  >
                    <span class="px-2.5 py-1 font-mono text-[11px]">
                      {activeItem.is_verbatim ? common.openOriginal : common.openSummary}
                    </span>
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
              <span>Korpus lokal Pramana · Kalender Saka 2025–2028</span>
            </div>

            {#if showTechAudit}
              <div class="p-3 bg-white font-mono text-[11px] space-y-1" style="border: 1px solid #0a0a0a;">
                <div>ENGINE: <strong>{result.ai_engine}</strong></div>
                <div>AI SYNTHESIS: <strong>{result.ai_synthesis_status || 'deterministic'}</strong></div>
                <div>AI GUARD: <strong>{result.ai_guard_status || '-'}</strong></div>
                <div>AI CLAIMS: <strong>{result.ai_claims?.length || 0}</strong></div>
                <div>AI MODEL: <strong>{result.ai_model || '-'}</strong></div>
                <div>GUARD: <strong>{result.guard_status}</strong></div>
                <div>CONFIDENCE: <strong>{result.confidence}</strong></div>
                <div>SCOPE: <strong>{result.verification_scope || 'corpus'}</strong></div>
                <div>PII MASKED: <strong>{result.pii_redacted_count} {common.entities}</strong></div>
              </div>
            {/if}
          </div>
          {:else}
            <!-- ABSTAIN CARD -->
            <div class="brutal-card p-6 sm:p-8 space-y-4" style="background-color: #dfd6c3;">
              <div class="flex flex-wrap items-center justify-between gap-2">
                <span class="font-mono text-[10px] font-bold px-2 py-0.5" style="background-color: #0a0a0a; color: #ffffff;">
                  LAYER-2 ABSTAIN
                </span>
                <span class="font-mono text-xs font-bold" style="color: #8a3b00;">
                  {result.guard_status}
                </span>
              </div>

              <h2 class="opero-h1 text-2xl sm:text-3xl">
                {t.abstainTitle}
              </h2>

              <p class="text-xs sm:text-sm leading-relaxed" style="color: #3a3935;">
                {result.ai_synthesis}
              </p>

              <div class="p-3 bg-white font-mono text-[11px] leading-relaxed" style="border: 1.5px solid #0a0a0a;">
                {t.abstainDesc}
              </div>
            </div>
          {/if}

          {#if result.disclaimer}
            <div
              class="p-3 text-[11px] leading-relaxed"
              style="background-color: #ffffff; border: 1px solid #0a0a0a; color: #3a3935;"
            >
              <strong>{common.disclaimer}</strong> {result.disclaimer}
            </div>
          {/if}
        {/if}
      </div>

    </div>
  </section>
</div>
