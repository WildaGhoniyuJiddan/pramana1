<script>
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

  const PRESETS = [
    {
      label: '⚠️ Periode Nyepi 2026 (Ubud & Bandara)',
      text: 'Tiba di Bandara Ngurah Rai, menginap di Ubud tanggal 18 Maret 2026 sampai 21 Maret 2026. Berencana jalan-jalan ke Pura Saraswati dan sewa motor di jalan raya. Kode booking: GA4521 email: alex@travel.com.',
      start: '2026-03-18',
      end: '2026-03-21',
      origin: 'international'
    },
    {
      label: '🏖️ Wisata Budaya & Pura (Kuta & Besakih)',
      text: 'Mengunjungi Pura Besakih dan Pura Uluwatu, menonton Tari Kecak, belanja suvenir di Sukawati dan nongkrong di beach club Seminyak.',
      start: '2026-05-10',
      end: '2026-05-15',
      origin: 'international'
    },
    {
      label: '🛵 Sewa Motor & Villa Canggu',
      text: 'Sewa skuter matik untuk mobilitas Canggu - Seminyak, bekerja remote dari cafe, dan surf trip ke Pantai Echo.',
      start: '2026-06-01',
      end: '2026-06-08',
      origin: 'international'
    }
  ];

  function applyPreset(p) {
    itineraryText = p.text;
    startDate = p.start;
    endDate = p.end;
    travelerOrigin = p.origin;
  }

  async function handleSubmit(e) {
    if (e) e.preventDefault();
    if (!itineraryText.trim() || !startDate) {
      errorMsg = 'Harap masukkan itinerary dan tanggal perjalanan.';
      return;
    }
    loading = true;
    errorMsg = '';
    result = null;

    try {
      result = await requestTripBrief({
        itinerary_text: itineraryText,
        start_date: startDate,
        end_date: endDate || startDate,
        traveler_origin: travelerOrigin
      });
    } catch (err) {
      errorMsg = err.message || 'Gagal memproses itinerary.';
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
        <h2 class="text-lg font-bold text-ink-900">Input Rencana Perjalanan (Trip Brief)</h2>
        <p class="text-xs text-ink-500 mt-0.5">Analisis aturan adat, bentrok hari raya Nyepi, dan kewajiban hukum Bali.</p>
      </div>
      <span class="text-xs font-mono bg-azure-50 text-azure-700 border border-azure-100 px-2.5 py-1 rounded-md">
        Mode Pencegahan
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
        <label for="itinerary" class="block text-xs font-semibold text-ink-700 uppercase tracking-wider mb-1.5">
          Rencana Rute / Catatan Booking / Aktivitas
        </label>
        <textarea
          id="itinerary"
          bind:value={itineraryText}
          rows="3"
          placeholder="Contoh: Menginap di Ubud, jalan-jalan ke Pura Uluwatu, sewa motor di Denpasar... (Data nama, email, dan kode booking disamarkan otomatis oleh sistem)."
          class="w-full px-3.5 py-2.5 text-sm rounded-lg border border-borderline focus:outline-none focus:ring-2 focus:ring-ink-900 focus:border-transparent font-sans"
        ></textarea>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <div>
          <label for="start-date" class="block text-xs font-semibold text-ink-700 uppercase tracking-wider mb-1">
            Tanggal Tiba / Mulai
          </label>
          <input
            id="start-date"
            type="date"
            bind:value={startDate}
            class="w-full px-3 py-2 text-sm rounded-lg border border-borderline focus:outline-none focus:ring-2 focus:ring-ink-900 bg-white"
          />
        </div>

        <div>
          <label for="end-date" class="block text-xs font-semibold text-ink-700 uppercase tracking-wider mb-1">
            Tanggal Selesai
          </label>
          <input
            id="end-date"
            type="date"
            bind:value={endDate}
            class="w-full px-3 py-2 text-sm rounded-lg border border-borderline focus:outline-none focus:ring-2 focus:ring-ink-900 bg-white"
          />
        </div>

        <div>
          <label for="traveler-origin" class="block text-xs font-semibold text-ink-700 uppercase tracking-wider mb-1">
            Status Wisatawan
          </label>
          <select
            id="traveler-origin"
            bind:value={travelerOrigin}
            class="w-full px-3 py-2 text-sm rounded-lg border border-borderline focus:outline-none focus:ring-2 focus:ring-ink-900 bg-white"
          >
            <option value="international">Wisatawan Mancanegara (WNA)</option>
            <option value="domestic">Wisatawan Nusantara (WNI)</option>
          </select>
        </div>
      </div>

      {#if errorMsg}
        <div class="p-3 bg-red-50 text-red-700 rounded-lg text-xs border border-red-200">
          {errorMsg}
        </div>
      {/if}

      <div class="flex items-center justify-between pt-2">
        <span class="text-[11px] text-ink-400">
          *PII Masking aktif: nama, kontak, dan nomor booking tidak disimpan.
        </span>
        <button
          type="submit"
          disabled={loading}
          class="px-5 py-2.5 bg-ink-900 hover:bg-black text-white text-sm font-semibold rounded-lg shadow transition-all flex items-center gap-2 disabled:opacity-50"
        >
          {#if loading}
            <span class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
            <span>Mengekstrak Aturan...</span>
          {:else}
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path></svg>
            <span>Hasilkan Trip Brief</span>
          {/if}
        </button>
      </div>
    </form>
  </div>

  <!-- Results Section -->
  {#if result}
    <div class="space-y-5 animate-in fade-in duration-300">
      
      <!-- PII Masking Feedback -->
      {#if result.pii_redacted_count > 0}
        <div class="p-3 bg-amber-50/80 border border-amber-200/80 rounded-lg flex items-center justify-between text-xs text-amber-900">
          <div class="flex items-center gap-2">
            <span class="font-bold">🔒 PII Masking Aktif:</span>
            <span>{result.pii_redacted_count} data pribadi/booking code disamarkan otomatis sebelum diproses.</span>
          </div>
          <span class="font-mono text-[11px] bg-amber-200/60 px-2 py-0.5 rounded">Aman & Teruji</span>
        </div>
      {/if}

      <!-- Nyepi / Holiday Conflict Banner -->
      {#if result.calendar_conflicts && result.calendar_conflicts.has_nyepi}
        {@const nyepi = result.calendar_conflicts.nyepi_summary}
        <div class="bg-red-50/90 border-2 border-red-400 rounded-xl p-5 shadow-sm">
          <div class="flex items-start justify-between">
            <div class="flex items-center gap-2.5">
              <span class="w-3 h-3 rounded-full bg-red-600 animate-ping"></span>
              <h3 class="font-bold text-red-950 text-base">
                PERINGATAN KRITIS: {nyepi.event_name} ({nyepi.date})
              </h3>
            </div>
            <span class="px-2.5 py-0.5 bg-red-600 text-white font-mono text-[11px] font-bold rounded-full uppercase">
              Total Silence 24 Jam
            </span>
          </div>
          
          <p class="text-xs text-red-900 mt-2 leading-relaxed">
            Jadwal perjalanan Anda bersinggungan dengan Hari Suci Nyepi. Pada hari ini seluruh aktivitas umum di Pulau Bali dihentikan total (pukul 06.00 s/d 06.00 WITA keesokan harinya).
          </p>

          <!-- 4 Catur Brata Rules -->
          <div class="mt-3.5 grid grid-cols-1 sm:grid-cols-2 gap-2.5">
            {#each nyepi.restrictions as r}
              <div class="bg-white/90 p-3 rounded-lg border border-red-200 text-xs">
                <span class="font-bold text-red-950">{r.rule} ({r.translation})</span>
                <p class="text-ink-700 mt-1 leading-normal">{r.instruction}</p>
              </div>
            {/each}
          </div>

          <!-- Service Disruptions -->
          <div class="mt-3.5 p-3 bg-red-100/70 rounded-lg text-xs text-red-950">
            <span class="font-bold block mb-1">Dampak Layanan Transportasi & Komunikasi:</span>
            <ul class="list-disc list-inside space-y-0.5 text-red-900 text-[11px]">
              {#each nyepi.service_disruptions as d}
                <li>{d}</li>
              {/each}
            </ul>
          </div>
        </div>
      {/if}

      <!-- Other Holiday Conflicts (Pengerupukan, Galungan) -->
      {#if result.calendar_conflicts && result.calendar_conflicts.events}
        {#each result.calendar_conflicts.events as ev}
          {#if ev.severity !== 'CRITICAL'}
            <div class="bg-amber-50 border border-amber-200 rounded-lg p-3.5 flex items-start justify-between text-xs">
              <div>
                <span class="font-bold text-amber-950">{ev.name} ({ev.date})</span>
                <p class="text-amber-900 mt-0.5">{ev.details.service_disruptions?.[0] || 'Perayaan upacara adat Bali.'}</p>
              </div>
              <span class="px-2 py-0.5 bg-amber-200 text-amber-900 font-mono text-[10px] rounded font-semibold">
                Info Upacara
              </span>
            </div>
          {/if}
        {/each}
      {/if}

      <!-- Briefing Cards Header & Quick Actions -->
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-2">
        <div>
          <h3 class="text-base font-bold text-ink-900">
            Aturan Hukum Terverifikasi ({result.briefing_items.length} Pasal Relevan)
          </h3>
          <p class="text-xs text-ink-500">Kutipan resmi dari JDIH Provinsi Bali dan Hukum Nasional.</p>
        </div>

        <div class="flex items-center gap-2">
          <button
            onclick={copyWhatsApp}
            class="px-3 py-1.5 bg-white hover:bg-canvas border border-borderline text-ink-800 text-xs font-medium rounded-lg shadow-sm transition-all flex items-center gap-1.5"
          >
            {#if copySuccess}
              <span class="text-emerald-600 font-bold">✓ Tersalin!</span>
            {:else}
              <svg class="w-3.5 h-3.5 text-emerald-600" fill="currentColor" viewBox="0 0 24 24"><path d="M12.031 6.172c-3.181 0-5.767 2.586-5.768 5.766-.001 1.298.38 2.27 1.019 3.287l-.582 2.128 2.182-.573c.978.58 1.911.928 3.145.929 3.178 0 5.767-2.587 5.768-5.766.001-3.187-2.575-5.77-5.764-5.771zm3.392 8.244c-.144.405-.837.774-1.17.824-.299.045-.677.063-1.092-.069-.252-.08-.575-.187-.988-.365-1.739-.751-2.874-2.502-2.961-2.617-.087-.116-.708-.94-.708-1.793s.448-1.273.607-1.446c.159-.173.346-.217.462-.217l.332.006c.106.005.249-.04.39.298.144.347.491 1.2.534 1.287.043.087.072.188.014.303-.058.116-.087.188-.173.289l-.26.302c-.087.087-.178.182-.077.355.101.173.449.741.963 1.2.662.591 1.221.774 1.394.86.173.086.275.072.376-.044.101-.116.433-.506.549-.679.116-.173.231-.145.39-.087s1.011.477 1.184.564.289.13.332.202c.043.072.043.419-.101.824z"/></svg>
              <span>Salin WhatsApp</span>
            {/if}
          </button>

          <button
            onclick={downloadIcs}
            class="px-3 py-1.5 bg-ink-900 hover:bg-black text-white text-xs font-medium rounded-lg shadow-sm transition-all flex items-center gap-1.5"
          >
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
            <span>Unduh Kalender (.ics)</span>
          </button>
        </div>
      </div>

      <!-- Regulation Cards Grid -->
      <div class="grid grid-cols-1 gap-4">
        {#each result.briefing_items as item}
          <div class="bg-white rounded-xl border border-borderline p-5 shadow-sm hover:border-ink-400 transition-all">
            <div class="flex items-center justify-between flex-wrap gap-2 pb-3 border-b border-borderline/60">
              <div class="flex items-center gap-2">
                <span class={`text-[11px] font-mono px-2.5 py-0.5 rounded-full font-bold ${
                  item.tier === '1A' ? 'bg-indigo-100 text-indigo-800' :
                  item.tier === '1B' ? 'bg-emerald-100 text-emerald-800' :
                  'bg-amber-100 text-amber-800'
                }`}>
                  {item.tier_label}
                </span>
                <span class="text-xs font-semibold text-ink-900">{item.category}</span>
                <span class="text-xs font-mono text-ink-400">({item.pasal})</span>
              </div>

              <button
                onclick={() => onOpenDoc(item)}
                class="text-xs text-azure-700 hover:text-azure-900 font-medium flex items-center gap-1"
              >
                <span>Lihat Teks Pasal Penuh</span>
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
              </button>
            </div>

            <h4 class="text-sm font-bold text-ink-900 mt-3">{item.title}</h4>
            
            <p class="text-xs text-ink-700 mt-2 leading-relaxed bg-canvas/70 p-3 rounded-lg border border-borderline/50">
              "{item.summary}"
            </p>

            <div class="mt-3 flex items-start gap-2 text-xs text-red-700 bg-red-50/60 p-2.5 rounded-lg border border-red-100">
              <span class="font-bold shrink-0">⚠️ Konsekuensi/Sanksi:</span>
              <span>{item.penalties}</span>
            </div>
          </div>
        {/each}
      </div>

      <!-- Disclaimer -->
      <div class="p-3 bg-canvas border border-borderline rounded-lg text-center text-[11px] text-ink-500">
        {result.disclaimer}
      </div>

    </div>
  {/if}
</div>
