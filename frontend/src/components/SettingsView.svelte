<script>
  import { i18n, setLanguage, DICT } from '../lib/i18n.svelte.js';

  let t = $derived(DICT[i18n.lang].settings);

  let ttsRate = $state(
    typeof localStorage !== 'undefined'
      ? parseFloat(localStorage.getItem('pramana_tts_rate') || '1.0')
      : 1.0
  );

  let ttsVoiceLang = $state(
    typeof localStorage !== 'undefined'
      ? localStorage.getItem('pramana_tts_voice_lang') || 'id'
      : 'id'
  );

  let isSpeaking = $state(false);

  function handleLanguageChange(lang) {
    setLanguage(lang);
    ttsVoiceLang = lang;
    if (typeof localStorage !== 'undefined') {
      localStorage.setItem('pramana_tts_voice_lang', lang);
    }
  }

  function handleTtsRateChange(rate) {
    ttsRate = rate;
    if (typeof localStorage !== 'undefined') {
      localStorage.setItem('pramana_tts_rate', String(rate));
    }
  }

  function handleVoiceLangChange(lang) {
    ttsVoiceLang = lang;
    if (typeof localStorage !== 'undefined') {
      localStorage.setItem('pramana_tts_voice_lang', lang);
    }
  }

  function testTts() {
    if (typeof window === 'undefined' || !('speechSynthesis' in window)) {
      alert('Browser ini tidak mendukung Web Speech API.');
      return;
    }

    window.speechSynthesis.cancel();
    const text =
      ttsVoiceLang === 'id'
        ? 'Selamat datang di Bali. Harap hormati kesucian tempat ibadah dan patuhi tata tertib berpakaian adat.'
        : 'Welcome to Bali. Please respect sacred temple regulations and dress with proper traditional sash and sarong.';

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = ttsVoiceLang === 'id' ? 'id-ID' : 'en-US';
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

  function clearUserData() {
    if (typeof localStorage !== 'undefined') {
      if (confirm(i18n.lang === 'id' ? 'Hapus riwayat gerbang dan setel ulang preferensi?' : 'Clear gate history and reset preferences?')) {
        localStorage.clear();
        setLanguage('id');
        window.location.reload();
      }
    }
  }
</script>

<div class="w-full mx-auto" style="max-width: 1040px;">
  <!-- Header Bar -->
  <section class="px-5 sm:px-10 py-6 sm:py-8 border-b" style="border-color: #cdc9be; background-color: #f3f1eb;">
    <div class="space-y-1">
      <span
        class="font-mono text-[10px] font-bold px-2 py-0.5 tracking-wider uppercase inline-block"
        style="background-color: #0c249c; color: #ffffff; border: 1px solid #0a0a0a;"
      >
        {t.badge}
      </span>
      <h1 class="text-2xl sm:text-3xl font-bold tracking-tight" style="color: #0a0a0a;">
        {t.title}
      </h1>
      <p class="text-xs sm:text-[13px] leading-relaxed max-w-2xl" style="color: #5c5952;">
        {t.subtitle}
      </p>
    </div>
  </section>

  <section class="px-5 sm:px-10 py-6 sm:py-8 space-y-6">
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">

      <!-- CARD 1: Bahasa Tampilan -->
      <div class="brutal-card p-5 sm:p-6 space-y-4" style="background-color: #ffffff;">
        <div class="border-b pb-2.5" style="border-color: #cdc9be;">
          <h2 class="font-mono text-[11px] font-bold uppercase tracking-wider text-[#0c249c]">
            {t.langCardTitle}
          </h2>
          <p class="text-[11px] text-[#5c5952] mt-0.5">{t.langCardSubtitle}</p>
        </div>

        <div class="space-y-3 pt-1">
          <button
            type="button"
            onclick={() => handleLanguageChange('id')}
            class="brutal-press w-full p-3.5 text-left border cursor-pointer flex items-center justify-between transition-all"
            style={i18n.lang === 'id'
              ? 'background-color: #0c249c; color: #ffffff; border: 1.5px solid #0a0a0a; box-shadow: 2px 2px 0px #0a0a0a;'
              : 'background-color: #f3f1eb; color: #0a0a0a; border: 1.5px solid #cdc9be;'}
          >
            <div class="space-y-0.5">
              <span class="font-bold text-xs block">🇮🇩 {t.idLabel}</span>
              <span class="text-[11px] opacity-80 block">{t.idDesc}</span>
            </div>
            {#if i18n.lang === 'id'}
              <span class="font-mono text-sm font-bold">✓</span>
            {/if}
          </button>

          <button
            type="button"
            onclick={() => handleLanguageChange('en')}
            class="brutal-press w-full p-3.5 text-left border cursor-pointer flex items-center justify-between transition-all"
            style={i18n.lang === 'en'
              ? 'background-color: #0c249c; color: #ffffff; border: 1.5px solid #0a0a0a; box-shadow: 2px 2px 0px #0a0a0a;'
              : 'background-color: #f3f1eb; color: #0a0a0a; border: 1.5px solid #cdc9be;'}
          >
            <div class="space-y-0.5">
              <span class="font-bold text-xs block">🇬🇧 {t.enLabel}</span>
              <span class="text-[11px] opacity-80 block">{t.enDesc}</span>
            </div>
            {#if i18n.lang === 'en'}
              <span class="font-mono text-sm font-bold">✓</span>
            {/if}
          </button>
        </div>
      </div>

      <!-- CARD 2: Audio Panduan Gerbang -->
      <div class="brutal-card p-5 sm:p-6 space-y-4" style="background-color: #ffffff;">
        <div class="border-b pb-2.5" style="border-color: #cdc9be;">
          <h2 class="font-mono text-[11px] font-bold uppercase tracking-wider text-[#0c249c]">
            {t.audioCardTitle}
          </h2>
          <p class="text-[11px] text-[#5c5952] mt-0.5">{t.audioCardSubtitle}</p>
        </div>

        <div class="space-y-3 pt-1">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
            <div>
              <label for="settings-voice-lang" class="font-mono text-[10px] font-bold text-[#5c5952] block mb-1">
                {t.voiceLang}
              </label>
              <select
                id="settings-voice-lang"
                value={ttsVoiceLang}
                onchange={(e) => handleVoiceLangChange(e.target.value)}
                class="w-full p-2.5 border border-[#0a0a0a] bg-[#f3f1eb] font-mono text-xs focus:outline-none"
              >
                <option value="id">Indonesia (id-ID)</option>
                <option value="en">English (en-US)</option>
              </select>
            </div>

            <div>
              <label for="settings-voice-speed" class="font-mono text-[10px] font-bold text-[#5c5952] block mb-1">
                {t.speed}
              </label>
              <select
                id="settings-voice-speed"
                value={ttsRate}
                onchange={(e) => handleTtsRateChange(parseFloat(e.target.value))}
                class="w-full p-2.5 border border-[#0a0a0a] bg-[#f3f1eb] font-mono text-xs focus:outline-none"
              >
                <option value="0.85">{t.speedSlow}</option>
                <option value="1.0">{t.speedNormal}</option>
                <option value="1.15">{t.speedFast}</option>
              </select>
            </div>
          </div>

          <div class="pt-1">
            <button
              type="button"
              onclick={isSpeaking ? stopTts : testTts}
              class="brutal-press w-full py-2.5 font-mono text-xs font-bold cursor-pointer"
              style={isSpeaking
                ? 'background-color: #8a3b00; color: #ffffff; border: 1.5px solid #0a0a0a;'
                : 'background-color: #0c249c; color: #ffffff; border: 1.5px solid #0a0a0a; box-shadow: 2px 2px 0px #0a0a0a;'}
            >
              {isSpeaking ? t.stopVoiceBtn : t.testVoiceBtn}
            </button>
          </div>
        </div>
      </div>

    </div>

    <!-- CARD 3: Storage & Privacy -->
    <div class="brutal-card p-5 sm:p-6 space-y-3" style="background-color: #f3f1eb;">
      <div class="flex flex-wrap items-center justify-between gap-2 border-b pb-2.5" style="border-color: #cdc9be;">
        <div>
          <h2 class="font-mono text-[11px] font-bold uppercase tracking-wider text-[#0a0a0a]">
            {t.storageCardTitle}
          </h2>
          <p class="text-[11px] text-[#5c5952]">{t.storageCardSubtitle}</p>
        </div>
        <button
          type="button"
          onclick={clearUserData}
          class="font-mono text-[11px] font-bold px-3 py-1.5 border border-[#c92a2a] text-[#c92a2a] bg-[#ffffff] hover:bg-[#fff0f0] cursor-pointer"
        >
          {t.clearDataBtn}
        </button>
      </div>
      <p class="text-[11px] text-[#5c5952] leading-relaxed">
        {t.storageDesc}
      </p>
    </div>
  </section>
</div>
