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

  const PRESETS = [
    {
      label: '01 · Periode Nyepi 2026 (Ubud & Bandara)',
      text: 'Tiba di Bandara Ngurah Rai, menginap di Ubud tanggal 18 Maret 2026 sampai 21 Maret 2026. Berencana jalan-jalan ke Pura Saraswati dan sewa motor di jalan raya. Kode booking: GA4521 email: alex@travel.com.',
      start: '2026-03-18',
      end: '2026-03-21',
      origin: 'international'
    },
    {
      label: '02 · Kunjungan Pura & Kawasan Suci (Besakih)',
      text: 'Mengunjungi Pura Besakih dan Pura Uluwatu, menonton Tari Kecak, belanja suvenir di Sukawati dan makan malam di Seminyak.',
      start: '2026-05-10',
      end: '2026-05-15',
      origin: 'international'
    },
    {
      label: '03 · Sewa Kendaraan & Remote Work (Canggu)',
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
    if (!itineraryText.trim() || !startDate) {
      errorMsg = 'Masukkan rencana perjalanan dan tanggal keberangkatan.';
      return;
    }
    loading = true;
    errorMsg = '';

    try {
      result = await requestTripBrief({
        itinerary_text: itineraryText,
        start_date: startDate,
        end_date: endDate || startDate,
        traveler_origin: travelerOrigin
      });
    } catch (err) {
      errorMsg = err.message || 'Gagal memproses rencana perjalanan.';
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
    a.download = `pramana_trip_brief_${startDate}.ics`;
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
          style="object-position: center 20%;"
        />
        <div
          class="absolute inset-0 pointer-events-none"
          style="background: linear-gradient(90deg, rgba(8, 24, 115, 0.94) 0%, rgba(8, 24, 115, 0.72) 60%, rgba(8, 24, 115, 0.55) 100%);"
        ></div>

        <div class="relative z-10">
          <div class="inline-flex items-center text-[11px] font-medium mb-3" style="background-color: rgba(255,255,255,0.14); color: #ffffff; border-radius: 2px; padding: 2px;">
            <span style="background-color: #dfd8c8; color: #0a0a0a; border-radius: 1px;" class="px-2 py-0.5 font-bold">✦</span>
            <span class="px-3 py-0.5">Pencegahan Pra-Perjalanan &amp; Kalender Saka</span>
          </div>
          <h1 class="opero-h1 text-3xl sm:text-5xl" style="color: #ffffff;">
            Studio <span class="opero-serif" style="color: #dfd8c8;">Trip Brief</span> &amp; Konflik Nyepi
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

      <!-- Left Pane: Input Parameters (4 cols) -->
      <div class="lg:col-span-4 p-6 space-y-6" style="background-color: #f2f0ea; border-right: 1px solid #c8c4ba;">
        <form onsubmit={handleSubmit} class="space-y-5">
          <div>
            <label for="itinerary" class="block text-xs font-semibold mb-2" style="color: #0a0a0a;">
              Rincian Rute atau Catatan Reservasi
            </label>
            <textarea
              id="itinerary"
              bind:value={itineraryText}
              rows="5"
              placeholder="Masukkan rincian rute perjalanan, destinasi pura, atau catatan booking..."
              style="background-color: #ffffff; color: #0a0a0a; border: 1px solid #c8c4ba; border-radius: 4px;"
              class="w-full p-3.5 text-xs sm:text-sm focus:outline-none leading-relaxed"
            ></textarea>
            <span class="block text-[11px] mt-1.5" style="color: #5e5d58;">
              Penyaringan PII otomatis menyamarkan email, telepon, paspor, kartu, &amp; kode booking.
            </span>
          </div>

          <div class="grid grid-cols-2 gap-3 pt-4" style="border-top: 1px solid #c8c4ba;">
            <div>
              <label for="start-date" class="block text-xs font-semibold mb-1.5" style="color: #0a0a0a;">
                Tanggal Tiba
              </label>
              <input
                id="start-date"
                type="date"
                bind:value={startDate}
                style="background-color: #ffffff; color: #0a0a0a; border: 1px solid #c8c4ba; border-radius: 4px;"
                class="w-full px-3 py-2 text-xs"
              />
            </div>

            <div>
              <label for="end-date" class="block text-xs font-semibold mb-1.5" style="color: #0a0a0a;">
                Tanggal Pulang
              </label>
              <input
                id="end-date"
                type="date"
                bind:value={endDate}
                style="background-color: #ffffff; color: #0a0a0a; border: 1px solid #c8c4ba; border-radius: 4px;"
                class="w-full px-3 py-2 text-xs"
              />
            </div>
          </div>

          <div class="pt-4" style="border-top: 1px solid #c8c4ba;">
            <label for="traveler-origin" class="block text-xs font-semibold mb-1.5" style="color: #0a0a0a;">
              Kategori Yurisdiksi Wisatawan
            </label>
            <select
              id="traveler-origin"
              bind:value={travelerOrigin}
              style="background-color: #ffffff; color: #0a0a0a; border: 1px solid #c8c4ba; border-radius: 4px;"
              class="w-full px-3 py-2.5 text-xs"
            >
              <option value="international">Wisatawan Mancanegara (WNA, Wajib Pungutan Perda 6/2023)</option>
              <option value="domestic">Wisatawan Nusantara (WNI)</option>
            </select>
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
                <span>{loading ? 'Memeriksa Korpus JDIH...' : 'Susun Dokumen Trip Brief'}</span>
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
      </div>

      <!-- Right Pane: Editorial Legal Dossier (8 cols) -->
      <div class="lg:col-span-8 min-w-0" style="background-color: #e6e4de;">
        {#if result}
          {#key result.masked_itinerary}
            <div class="animate-brutal-stamp">
          <!-- Row 1: Telemetry & Export Strip -->
          <div class="px-6 py-3.5 flex flex-wrap items-center justify-between gap-3" style="background-color: #dfd8c8; border-bottom: 1px solid #c8c4ba;">
            <div class="flex flex-wrap items-center gap-3 font-mono text-[11px]" style="color: #0a0a0a;">
              <span>ENGINE: <strong>{result.ai_engine || 'Strict-RAG'}</strong></span>
              <span>|</span>
              <span>PII REDACTED: <strong>{result.pii_redacted_count}</strong></span>
              <span>|</span>
              <span style="color: #0c249c;" class="font-bold">{result.guard_status}</span>
            </div>

            <div class="flex items-center gap-2">
              <button
                type="button"
                onclick={copyWhatsApp}
                style="background-color: #ffffff; color: #0a0a0a; border: 1px solid #c8c4ba;"
                class="px-3.5 py-1.5 text-xs font-medium hover:bg-stone transition-colors"
              >
                {copySuccess ? 'Tersalin' : 'Salin Ringkasan WA'}
              </button>
              <button
                type="button"
                onclick={downloadIcs}
                style="background-color: #0c249c; color: #ffffff;"
                class="px-3.5 py-1.5 text-xs font-medium hover:opacity-90 transition-opacity"
              >
                Unduh Kalender (.ICS)
              </button>
            </div>
          </div>

          <!-- Row 2: Executive Synthesis & Masked Input -->
          {#if result.ai_synthesis}
            <div class="p-6 space-y-2.5 bg-white" style="border-bottom: 1px solid #c8c4ba;">
              <span class="font-mono text-[10px] uppercase tracking-wider block" style="color: #0c249c; font-weight: 600;">
                Ringkasan Kepatuhan Rute ({result.start_date} s/d {result.end_date})
              </span>
              <p class="text-base sm:text-lg leading-relaxed" style="color: #0a0a0a;">
                {result.ai_synthesis}
              </p>
              {#if result.pii_redacted_count > 0}
                <div class="pt-2 font-mono text-[11px]" style="color: #5e5d58;">
                  Log Masukan Terlindungi: <span style="color: #0a0a0a;">{result.masked_itinerary}</span>
                </div>
              {/if}
            </div>
          {/if}

          <!-- Row 3: Nyepi Critical Schedule Ledger -->
          {#if result.calendar_conflicts && result.calendar_conflicts.has_nyepi}
            {@const nyepi = result.calendar_conflicts.nyepi_summary}
            <div style="border-bottom: 1px solid #c8c4ba;">
              <div class="px-6 py-4 flex flex-wrap items-center justify-between gap-2" style="background-color: #0c249c; color: #ffffff;">
                <div>
                  <span class="font-mono text-[10px] uppercase tracking-wider block" style="color: #dfd8c8;">
                    Peringatan Kalender Kritis: Penghentian Aktivitas 24 Jam
                  </span>
                  <h3 class="text-base font-medium tracking-tight mt-0.5">
                    {nyepi.event_name} ({nyepi.date})
                  </h3>
                </div>
                <span class="font-mono text-[11px] px-2.5 py-1 font-semibold" style="background-color: #dfd8c8; color: #0a0a0a;">
                  06.00 WITA → 06.00 WITA (+1 Hari)
                </span>
              </div>

              <!-- 4 Catur Brata Columns -->
              <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 bg-white" style="border-bottom: 1px solid #c8c4ba;">
                {#each nyepi.restrictions as r, idx}
                  <div class="p-4 space-y-1.5" style="border-right: 1px solid #c8c4ba;">
                    <span class="font-mono text-[10px] font-bold block" style="color: #0c249c;">0{idx + 1} / {r.rule}</span>
                    <span class="text-xs font-semibold block" style="color: #0a0a0a;">{r.translation}</span>
                    <p class="text-[11px] leading-relaxed" style="color: #333330;">{r.instruction}</p>
                  </div>
                {/each}
              </div>

              <!-- Infrastructure Disruptions -->
              <div class="px-6 py-4 grid grid-cols-1 md:grid-cols-12 gap-4 text-xs" style="background-color: #f2f0ea;">
                <div class="md:col-span-3 font-mono text-[10px] uppercase font-semibold" style="color: #0a0a0a;">
                  Dampak Infrastruktur Publik
                </div>
                <ul class="md:col-span-9 space-y-1 list-disc list-inside" style="color: #333330;">
                  {#each nyepi.service_disruptions as d}
                    <li>{d}</li>
                  {/each}
                </ul>
              </div>
            </div>
          {/if}

          <!-- Row 4: Applicable Statutes Table -->
          <div>
            <div class="px-6 py-3 flex items-center justify-between font-mono text-[10px] uppercase tracking-wider" style="background-color: #dfd8c8; color: #0a0a0a; border-bottom: 1px solid #c8c4ba;">
              <span class="font-semibold">Instrumen Hukum Terverifikasi ({result.briefing_items.length} Pasal)</span>
              <span>Kutipan Verbatim JDIH Bali</span>
            </div>

            {#each result.briefing_items as item}
              <div class="p-6 grid grid-cols-1 md:grid-cols-12 gap-4 bg-white hover:bg-stone/40 transition-colors" style="border-bottom: 1px solid #c8c4ba;">
                <div class="md:col-span-4 space-y-1.5">
                  <span class="font-mono text-[10px] px-2 py-0.5 inline-block font-semibold" style="background-color: #0c249c; color: #ffffff;">
                    Tingkat {item.tier} · {item.tier_label}
                  </span>
                  <h4 class="text-sm font-semibold pt-1" style="color: #0a0a0a;">{item.category}</h4>
                  <p class="font-mono text-[11px]" style="color: #5e5d58;">{item.pasal}</p>
                  <button
                    type="button"
                    onclick={() => onOpenDoc(item)}
                    style="color: #0c249c;"
                    class="pt-2 inline-block font-mono text-[11px] font-semibold hover:underline"
                  >
                    Buka Naskah Penuh →
                  </button>
                </div>

                <div class="md:col-span-8 space-y-3">
                  <p class="text-xs font-semibold" style="color: #0a0a0a;">{item.title}</p>
                  <blockquote class="p-3.5 font-mono text-xs leading-relaxed" style="background-color: #f2f0ea; border-left: 3px solid #0c249c; color: #0a0a0a;">
                    "{item.summary}"
                  </blockquote>
                  <div class="text-xs flex items-baseline gap-2" style="color: #333330;">
                    <span class="font-mono text-[10px] uppercase font-semibold shrink-0" style="color: #0a0a0a;">Sanksi:</span>
                    <span>{item.penalties}</span>
                  </div>
                </div>
              </div>
            {/each}
          </div>

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
