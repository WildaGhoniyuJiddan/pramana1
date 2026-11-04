<script>
  let { item = null, onClose = () => {} } = $props();
</script>

{#if item}
  <div class="fixed inset-0 z-50 overflow-hidden flex justify-end">
    <!-- Backdrop -->
    <button 
      type="button"
      aria-label="Tutup panel"
      onclick={onClose} 
      class="fixed inset-0 bg-black/40 backdrop-blur-sm transition-opacity"
    ></button>

    <!-- Drawer panel -->
    <div class="relative w-full max-w-xl bg-white h-full shadow-2xl border-l border-borderline z-10 flex flex-col animate-in slide-in-from-right duration-200">
      
      <!-- Drawer Header -->
      <div class="p-5 border-b border-borderline flex items-center justify-between bg-canvas/40">
        <div>
          <span class="text-[11px] font-mono uppercase bg-ink-900 text-white px-2 py-0.5 rounded font-bold">
            {item.tier_label || `Tingkat ${item.tier || '1B'}`}
          </span>
          <h3 class="text-base font-bold text-ink-900 mt-1.5">
            {item.pasal || 'Naskah Regulasi'}
          </h3>
        </div>

        <button 
          aria-label="Tutup"
          onclick={onClose}
          class="p-2 rounded-lg hover:bg-black/5 text-ink-500 hover:text-ink-900 transition-colors"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
        </button>
      </div>

      <!-- Drawer Content -->
      <div class="p-5 overflow-y-auto flex-1 space-y-4">
        <div>
          <span class="text-xs font-semibold text-ink-500 uppercase tracking-wider block mb-1">
            Judul Peraturan Resmi
          </span>
          <p class="text-sm font-bold text-ink-900 leading-snug">
            {item.title || item.official_doc_title}
          </p>
        </div>

        <div>
          <span class="text-xs font-semibold text-ink-500 uppercase tracking-wider block mb-1.5">
            Teks Asli Naskah Hukum (Verbatim)
          </span>
          <div class="p-4 bg-canvas/80 border border-borderline rounded-xl text-xs sm:text-sm text-ink-800 leading-relaxed font-serif whitespace-pre-line border-l-4 border-l-amber-500">
            {item.full_text || item.quoted_text}
          </div>
        </div>

        {#if item.penalties}
          <div>
            <span class="text-xs font-semibold text-red-700 uppercase tracking-wider block mb-1">
              Sanksi & Konsekuensi Hukum
            </span>
            <div class="p-3 bg-red-50 border border-red-200 rounded-lg text-xs text-red-900">
              {item.penalties}
            </div>
          </div>
        {/if}

        <div class="pt-2">
          <span class="text-xs font-semibold text-ink-500 uppercase tracking-wider block mb-1">
            Sumber Publikasi Resmi
          </span>
          <a
            href={item.source_url}
            target="_blank"
            rel="noopener noreferrer"
            class="inline-flex items-center gap-1.5 text-xs text-azure-700 hover:text-azure-900 font-medium underline break-all"
          >
            <span>{item.source_url}</span>
            <svg class="w-3.5 h-3.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path></svg>
          </a>
        </div>

      </div>

      <!-- Drawer Footer -->
      <div class="p-4 border-t border-borderline bg-canvas/30 text-center text-[11px] text-ink-500">
        Naskah peraturan perundang-undangan tidak dilindungi hak cipta menurut Pasal 42 huruf b UU No. 28 Tahun 2014.
      </div>

    </div>
  </div>
{/if}
