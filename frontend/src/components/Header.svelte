<script>
  let { activeTab = $bindable('trip-brief'), openTransparency = () => {} } = $props();
</script>

<header class="relative overflow-hidden border-b border-borderline bg-white">
  <!-- Hero background painting container with subtle overlay -->
  <div class="relative w-full h-64 md:h-80 overflow-hidden">
    <img 
      src="/assets/balinese_gate_hero.png" 
      alt="Balinese Candi Bentar Landscape" 
      class="w-full h-full object-cover object-center filter saturate-[1.05] contrast-[1.02]"
    />
    <!-- Subtle gradient overlay so text remains razor-sharp -->
    <div class="absolute inset-0 bg-gradient-to-t from-black/75 via-black/30 to-black/10"></div>

    <!-- Top floating nav bar -->
    <div class="absolute top-4 inset-x-0 max-w-6xl mx-auto px-4 sm:px-6 flex items-center justify-between">
      <div class="flex items-center space-x-3 bg-white/95 backdrop-blur-md px-3.5 py-1.5 rounded-full border border-white/60 shadow-sm">
        <span class="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></span>
        <span class="font-bold tracking-tight text-ink-900 text-sm">PRAMANA</span>
        <span class="text-[11px] font-mono uppercase bg-amber-100 text-amber-800 px-2 py-0.5 rounded-full font-medium">Bali DigiFest 2026</span>
      </div>

      <button 
        onclick={openTransparency}
        class="text-xs font-medium text-white/95 hover:text-white bg-black/40 hover:bg-black/60 backdrop-blur-md px-3.5 py-1.5 rounded-full border border-white/20 transition-all flex items-center gap-1.5"
      >
        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
        <span>Transparansi Korpus & Evaluasi</span>
      </button>
    </div>

    <!-- Hero Titles -->
    <div class="absolute bottom-6 inset-x-0 max-w-6xl mx-auto px-4 sm:px-6 text-white">
      <div class="inline-flex items-center gap-2 px-2.5 py-1 rounded-md bg-white/20 backdrop-blur-sm border border-white/30 text-xs font-mono text-white mb-2">
        <span>Dual-Layer Strict-RAG</span>
        <span>•</span>
        <span>Pasal Resmi JDIH Bali</span>
      </div>
      <h1 class="font-serif text-3xl sm:text-4xl md:text-5xl font-bold tracking-tight text-white drop-shadow-sm">
        Pramana
      </h1>
      <p class="text-sm sm:text-base text-white/90 max-w-2xl font-normal leading-relaxed mt-1 drop-shadow-sm">
        Platform AI kepatuhan hukum dan pemahaman konteks aturan lokal pariwisata Bali dengan kutipan pasal verbatim tanpa halusinasi.
      </p>
    </div>
  </div>

  <!-- Mode Switcher Tabs -->
  <div class="max-w-6xl mx-auto px-4 sm:px-6">
    <div class="flex space-x-2 py-3 border-t border-borderline/60">
      <button
        onclick={() => activeTab = 'trip-brief'}
        class={`px-4 py-2 rounded-lg text-sm font-medium transition-all flex items-center gap-2 ${
          activeTab === 'trip-brief'
            ? 'bg-ink-900 text-white shadow-sm'
            : 'text-ink-700 hover:text-ink-900 hover:bg-black/5'
        }`}
      >
        <span class="w-2 h-2 rounded-full {activeTab === 'trip-brief' ? 'bg-amber-400' : 'bg-transparent'}"></span>
        Mode 1: Trip Brief (Pencegahan)
      </button>

      <button
        onclick={() => activeTab = 'context-note'}
        class={`px-4 py-2 rounded-lg text-sm font-medium transition-all flex items-center gap-2 ${
          activeTab === 'context-note'
            ? 'bg-ink-900 text-white shadow-sm'
            : 'text-ink-700 hover:text-ink-900 hover:bg-black/5'
        }`}
      >
        <span class="w-2 h-2 rounded-full {activeTab === 'context-note' ? 'bg-emerald-400' : 'bg-transparent'}"></span>
        Mode 2: Analisis Postingan Viral
      </button>
    </div>
  </div>
</header>
