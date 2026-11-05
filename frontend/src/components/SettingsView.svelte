<script>
  import { onMount } from 'svelte';
  import { fetchHealth, fetchAiStatus } from '../lib/api.js';

  let currentLang = $state(
    typeof localStorage !== 'undefined'
      ? localStorage.getItem('pramana_language') || 'id'
      : 'id'
  );

  let ttsRate = $state(
    typeof localStorage !== 'undefined'
      ? parseFloat(localStorage.getItem('pramana_tts_rate') || '1.0')
      : 1.0
  );

  let ttsLang = $state(
    typeof localStorage !== 'undefined'
      ? localStorage.getItem('pramana_tts_lang') || 'id'
      : 'id'
  );

  let isSpeaking = $state(false);
  let healthData = $state(null);
  let aiData = $state(null);
  let pingMs = $state(null);
  let isCheckingApi = $state(false);
  let apiError = $state('');

  // PII Playground
  let samplePiiInput = $state(
    'Tamu: John Doe (email: john@travel.com, telp: +6281234567890). Booking Code: BK9942, Paspor: A12345678.'
  );

  function maskClientSide(text) {
    if (!text) return '';
    return text
      .replace(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g, '[EMAIL]')
      .replace(/(\+?\d[\d\s-]{8,}\d)/g, '[TELEPON]')
      .replace(/\b[A-PR-WY][0-9]{7,8}\b/gi, '[PASPOR]')
      .replace(/\b[A-Z0-9]{6,8}\b/g, (match) => {
        if (/^[0-9]+$/.test(match)) return match;
        return '[KODE_BOOKING]';
      });
  }

  let maskedPreview = $derived(maskClientSide(samplePiiInput));

  function setLanguage(lang) {
    currentLang = lang;
    if (typeof localStorage !== 'undefined') {
      localStorage.setItem('pramana_language', lang);
      window.dispatchEvent(new CustomEvent('pramana_language_changed', { detail: lang }));
    }
  }

  function setTtsRate(rate) {
    ttsRate = rate;
    if (typeof localStorage !== 'undefined') {
      localStorage.setItem('pramana_tts_rate', String(rate));
    }
  }

  function setTtsLang(lang) {
    ttsLang = lang;
    if (typeof localStorage !== 'undefined') {
      localStorage.setItem('pramana_tts_lang', lang);
    }
  }

  function testTts() {
    if (typeof window === 'undefined' || !('speechSynthesis' in window)) {
      alert('Browser ini tidak mendukung Web Speech API.');
      return;
    }

    window.speechSynthesis.cancel();
    const text =
      ttsLang === 'id'
        ? 'Selamat datang di Bali. Harap patuhi tata tertib kawasan suci dan kenakan pakaian adat yang pantas.'
        : 'Welcome to Bali. Please respect sacred temple regulations and wear proper traditional attire.';

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = ttsLang === 'id' ? 'id-ID' : 'en-US';
    utterance.rate = ttsRate;

    isSpeaking = true;
    utterance.onend = () => { isSpeaking = false; };
    utterance.onerror = () => { isSpeaking = false; };

    window.speechSynthesis.speak(utterance);
  }

  function stopTts() {
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      isSpeaking = false;
    }
  }

  async function checkConnection() {
    isCheckingApi = true;
    apiError = '';
    const started = performance.now();
    try {
      const [h, a] = await Promise.all([fetchHealth(), fetchAiStatus()]);
      pingMs = Math.round(performance.now() - started);
      healthData = h;
      aiData = a;
    } catch (err) {
      apiError = err.message || 'Gagal menghubungi backend API.';
    } finally {
      isCheckingApi = false;
    }
  }

  function clearLocalStorage() {
    if (typeof localStorage !== 'undefined') {
      if (confirm('Bersihkan riwayat gerbang dan setelan lokal?')) {
        localStorage.clear();
        alert('Penyimpanan lokal berhasil dibersihkan.');
        window.location.reload();
      }
    }
  }

  onMount(() => {
    checkConnection();
  });
</script>

<div class="w-full mx-auto" style="max-width: 1360px;">
  <!-- Header Bar -->
  <section class="px-5 sm:px-10 py-6 sm:py-8 border-b" style="border-color: #cdc9be; background-color: #f3f1eb;">
    <div class="flex flex-wrap items-center justify-between gap-4">
      <div class="space-y-1">
        <span
          class="font-mono text-[10px] font-bold px-2 py-0.5 tracking-wider uppercase inline-block"
          style="background-color: #0c249c; color: #ffffff; border: 1px solid #0a0a0a;"
        >
          05 // KONFIGURASI SISTEM
        </span>
        <h1 class="text-2xl sm:text-3xl font-bold tracking-tight" style="color: #0a0a0a;">
          Pengaturan &amp; Diagnostik
        </h1>
        <p class="text-xs sm:text-[13px] leading-relaxed max-w-2xl" style="color: #5c5952;">
          Preferensi antarmuka bahasa, konfigurasi audio panduan gerbang, sandbox privasi PII, dan telemetri koneksi backend.
        </p>
      </div>

      <button
        type="button"
        onclick={checkConnection}
        disabled={isCheckingApi}
        class="brutal-press px-4 py-2 font-mono text-xs font-bold cursor-pointer inline-flex items-center gap-1.5"
        style="background-color: #0c249c; color: #ffffff; border: 1.5px solid #0a0a0a; box-shadow: 2px 2px 0px #0a0a0a;"
      >
        <span>🔄</span>
        <span>{isCheckingApi ? 'Memeriksa...' : 'Cek Status API'}</span>
      </button>
    </div>
  </section>

  <section class="px-5 sm:px-10 py-6 sm:py-8 space-y-6">
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">

      <!-- PANEL 1: Preferensi Bahasa -->
      <div class="brutal-card p-5 sm:p-6 space-y-4" style="background-color: #ffffff;">
        <div class="flex items-center justify-between border-b pb-3" style="border-color: #cdc9be;">
          <span class="font-mono text-[10px] font-bold uppercase tracking-wider text-[#0c249c]">
            PREFERENSI BAHASA (GLOBAL)
          </span>
          <span class="font-mono text-[11px] text-[#5c5952]">Aktif: {currentLang.toUpperCase()}</span>
        </div>

        <p class="text-xs leading-relaxed text-[#3a3935]">
          Pilih bahasa baku untuk ringkasan kepatuhan, instruksi gerbang pintar, dan penjelasan korpus.
        </p>

        <div class="grid grid-cols-2 gap-3 pt-1">
          <button
            type="button"
            onclick={() => setLanguage('id')}
            class="brutal-press p-3 text-left border cursor-pointer transition-all"
            style={currentLang === 'id'
              ? 'background-color: #0c249c; color: #ffffff; border: 1.5px solid #0a0a0a; box-shadow: 2px 2px 0px #0a0a0a;'
              : 'background-color: #f3f1eb; color: #0a0a0a; border: 1px solid #cdc9be;'}
          >
            <span class="font-mono text-xs font-bold block mb-0.5">🇮🇩 Bahasa Indonesia</span>
            <span class="text-[11px] opacity-80 block">Bahasa rujukan hukum resmi naskah perundang-undangan Bali.</span>
          </button>

          <button
            type="button"
            onclick={() => setLanguage('en')}
            class="brutal-press p-3 text-left border cursor-pointer transition-all"
            style={currentLang === 'en'
              ? 'background-color: #0c249c; color: #ffffff; border: 1.5px solid #0a0a0a; box-shadow: 2px 2px 0px #0a0a0a;'
              : 'background-color: #f3f1eb; color: #0a0a0a; border: 1px solid #cdc9be;'}
          >
            <span class="font-mono text-xs font-bold block mb-0.5">🇬🇧 English</span>
            <span class="text-[11px] opacity-80 block">International traveler guidance with original legal citations.</span>
          </button>
        </div>
      </div>

      <!-- PANEL 2: Audio & TTS Panduan Gerbang -->
      <div class="brutal-card p-5 sm:p-6 space-y-4" style="background-color: #ffffff;">
        <div class="flex items-center justify-between border-b pb-3" style="border-color: #cdc9be;">
          <span class="font-mono text-[10px] font-bold uppercase tracking-wider text-[#0c249c]">
            AUDIO PANDUAN GERBANG (TTS)
          </span>
          <span class="font-mono text-[11px] text-[#5c5952]">Web Speech API</span>
        </div>

        <p class="text-xs leading-relaxed text-[#3a3935]">
          Atur aksen bahasa dan kecepatan suara panduan saat wisatawan tap NFC atau scan QR di gerbang masuk pura/bandara.
        </p>

        <div class="space-y-3">
          <div class="grid grid-cols-2 gap-3 text-xs">
            <div>
              <label for="tts-lang" class="font-mono text-[10px] font-bold text-[#5c5952] block mb-1">
                BAHASA SUARA
              </label>
              <select
                id="tts-lang"
                value={ttsLang}
                onchange={(e) => setTtsLang(e.target.value)}
                class="w-full p-2 border border-[#0a0a0a] bg-[#f3f1eb] font-mono text-xs"
              >
                <option value="id">Indonesia (id-ID)</option>
                <option value="en">English (en-US)</option>
              </select>
            </div>

            <div>
              <label for="tts-rate" class="font-mono text-[10px] font-bold text-[#5c5952] block mb-1">
                KECEPATAN BICARA ({ttsRate}x)
              </label>
              <select
                id="tts-rate"
                value={ttsRate}
                onchange={(e) => setTtsRate(parseFloat(e.target.value))}
                class="w-full p-2 border border-[#0a0a0a] bg-[#f3f1eb] font-mono text-xs"
              >
                <option value="0.85">0.85x (Lambat &amp; Jelas)</option>
                <option value="1.0">1.0x (Normal)</option>
                <option value="1.15">1.15x (Cepat)</option>
              </select>
            </div>
          </div>

          <div class="flex items-center gap-2 pt-1">
            <button
              type="button"
              onclick={isSpeaking ? stopTts : testTts}
              class="brutal-press w-full py-2 font-mono text-xs font-bold cursor-pointer"
              style={isSpeaking
                ? 'background-color: #8a3b00; color: #ffffff; border: 1.5px solid #0a0a0a;'
                : 'background-color: #0c249c; color: #ffffff; border: 1.5px solid #0a0a0a; box-shadow: 2px 2px 0px #0a0a0a;'}
            >
              {isSpeaking ? '⏹ Hentikan Suara' : '🔊 Uji Putar Suara Narasi'}
            </button>
          </div>
        </div>
      </div>

      <!-- PANEL 3: Sandbox Penyamaran PII -->
      <div class="brutal-card p-5 sm:p-6 space-y-4" style="background-color: #ffffff;">
        <div class="flex items-center justify-between border-b pb-3" style="border-color: #cdc9be;">
          <span class="font-mono text-[10px] font-bold uppercase tracking-wider text-[#0c249c]">
            SANDBOX PRIVASI &amp; PII MASKING
          </span>
          <span class="font-mono text-[10px] font-bold px-2 py-0.5 bg-[#dfd6c3] border border-[#0a0a0a]">
            ZERO-LEAK PREVIEW
          </span>
        </div>

        <p class="text-xs leading-relaxed text-[#3a3935]">
          Uji langsung bagaimana data sensitif wisatawan (email, telepon, paspor, kode booking) disamarkan di sisi browser sebelum dikirim ke API backend atau model AI.
        </p>

        <div class="space-y-2">
          <label for="pii-input" class="font-mono text-[10px] font-bold text-[#5c5952] block">
            INPUT TEKS SIMULASI:
          </label>
          <textarea
            id="pii-input"
            bind:value={samplePiiInput}
            rows="2"
            class="w-full p-2.5 text-xs font-mono border border-[#0a0a0a] bg-[#fcfbf9] focus:outline-none"
          ></textarea>
        </div>

        <div class="space-y-1.5 pt-1">
          <span class="font-mono text-[10px] font-bold text-[#5c5952] block">
            HASIL PENYAMARAN AMAN:
          </span>
          <div class="p-2.5 bg-[#f3f1eb] border border-[#cdc9be] font-mono text-xs text-[#0a0a0a] leading-relaxed break-words">
            {maskedPreview}
          </div>
        </div>
      </div>

      <!-- PANEL 4: Diagnostik Koneksi & AI Backend -->
      <div class="brutal-card p-5 sm:p-6 space-y-4" style="background-color: #ffffff;">
        <div class="flex items-center justify-between border-b pb-3" style="border-color: #cdc9be;">
          <span class="font-mono text-[10px] font-bold uppercase tracking-wider text-[#0c249c]">
            STATUS LIVE BACKEND &amp; AI
          </span>
          {#if pingMs !== null}
            <span class="font-mono text-[10px] font-bold px-2 py-0.5 bg-[#e7f0ff] border border-[#0c249c] text-[#0c249c]">
              PING: {pingMs} ms
            </span>
          {/if}
        </div>

        {#if apiError}
          <div class="p-3 bg-[#fff0f0] border border-[#c92a2a] text-[#c92a2a] font-mono text-xs leading-relaxed">
            {apiError}
          </div>
        {:else if healthData}
          <div class="font-mono text-xs space-y-2 text-[#3a3935]">
            <div class="flex justify-between border-b pb-1 border-[#f3f1eb]">
              <span>Status Servis:</span>
              <span class="font-bold text-[#0c249c]">ONLINE ({healthData.status})</span>
            </div>
            <div class="flex justify-between border-b pb-1 border-[#f3f1eb]">
              <span>Model AI:</span>
              <span class="font-bold">{healthData.ai_model}</span>
            </div>
            <div class="flex justify-between border-b pb-1 border-[#f3f1eb]">
              <span>AI Mode / Status:</span>
              <span>{healthData.ai_mode} (Aktif: {healthData.ai_enabled ? 'Ya' : 'Fallback'})</span>
            </div>
            <div class="flex justify-between border-b pb-1 border-[#f3f1eb]">
              <span>Chunk Korpus Hukum:</span>
              <span>{healthData.total_regulations_indexed} pasal terindeks</span>
            </div>
            <div class="flex justify-between border-b pb-1 border-[#f3f1eb]">
              <span>Embeddings Dimuat:</span>
              <span>{aiData?.embedding_vectors_loaded || 40} vektor</span>
            </div>
            <div class="flex justify-between">
              <span>Cakupan Kalender:</span>
              <span>{healthData.calendar_coverage}</span>
            </div>
          </div>
        {:else}
          <p class="font-mono text-xs text-[#5c5952]">Memeriksa koneksi ke backend...</p>
        {/if}

        <div class="pt-2 border-t border-[#cdc9be] flex items-center justify-between">
          <span class="font-mono text-[10px] text-[#5c5952]">Penyimpanan Lokal:</span>
          <button
            type="button"
            onclick={clearLocalStorage}
            class="font-mono text-[10px] text-[#c92a2a] underline cursor-pointer hover:opacity-80"
          >
            Hapus Cache &amp; Reset Lokal
          </button>
        </div>
      </div>

    </div>
  </section>
</div>
