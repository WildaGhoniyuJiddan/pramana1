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
      class="fixed inset-0 transition-opacity"
      style="background-color: rgba(10, 10, 10, 0.45); backdrop-filter: blur(2px);"
    ></button>

    <!-- Drawer panel (Sharp architectural lines, warm stone/paper palette) -->
    <div
      class="relative w-full max-w-xl h-full shadow-2xl border-l z-10 flex flex-col"
      style="background-color: #e6e4de; border-color: #c8c4ba; color: #0a0a0a;"
    >
      <!-- Drawer Header -->
      <div
        class="px-6 py-4 border-b flex items-center justify-between"
        style="background-color: #f2f0ea; border-color: #c8c4ba;"
      >
        <div>
          <span
            class="font-mono text-[10px] uppercase px-2 py-0.5 font-medium"
            style="background-color: #0c249c; color: #ffffff;"
          >
            Tingkat {item.tier || '1B'} · {item.tier_label || 'Regulasi'}
          </span>
          <h3 class="text-base font-medium mt-1.5" style="color: #0a0a0a;">
            {item.pasal || 'Naskah Regulasi'}
          </h3>
        </div>

        <button
          type="button"
          onclick={onClose}
          class="px-3 py-1 border font-mono text-xs transition-colors"
          style="background-color: #ffffff; border-color: #c8c4ba; color: #0a0a0a;"
        >
          TUTUP [ESC]
        </button>
      </div>

      <!-- Drawer Content -->
      <div class="p-6 overflow-y-auto flex-1 space-y-6" style="background-color: #ffffff;">
        <div class="pb-4 border-b" style="border-color: #c8c4ba;">
          <span class="font-mono text-[10px] uppercase tracking-wider block mb-1" style="color: #5c5b57;">
            Nomenklatur Peraturan Resmi
          </span>
          <p class="text-sm font-medium leading-snug" style="color: #0a0a0a;">
            {item.title || item.official_doc_title}
          </p>
        </div>

        <div>
          <span class="font-mono text-[10px] uppercase tracking-wider block mb-2" style="color: #5c5b57;">
            Batang Tubuh / Teks Verbatim
          </span>
          <div
            class="p-5 border text-xs sm:text-sm leading-relaxed font-mono whitespace-pre-line"
            style="background-color: #faf9f6; border: 1px solid #dcd7cb; color: #0a0a0a;"
          >
            {item.full_text || item.quoted_text}
          </div>
        </div>

        {#if item.penalties}
          <div class="pt-4 border-t" style="border-color: #c8c4ba;">
            <span class="font-mono text-[10px] uppercase tracking-wider block mb-1.5" style="color: #5c5b57;">
              Ketentuan Sanksi & Penegakan
            </span>
            <p class="text-xs leading-relaxed" style="color: #2b2b29;">
              {item.penalties}
            </p>
          </div>
        {/if}

        <div class="pt-4 border-t" style="border-color: #c8c4ba;">
          <span class="font-mono text-[10px] uppercase tracking-wider block mb-1.5" style="color: #5c5b57;">
            Tautan Portal JDIH / Sumber Resmi
          </span>
          <a
            href={item.source_url}
            target="_blank"
            rel="noopener noreferrer"
            class="inline-flex items-center gap-1.5 text-xs hover:underline font-mono break-all"
            style="color: #0c249c;"
          >
            <span>{item.source_url}</span>
            <span>↗</span>
          </a>
        </div>
      </div>

      <!-- Drawer Footer -->
      <div
        class="px-6 py-3.5 border-t font-mono text-[10px]"
        style="background-color: #f2f0ea; border-color: #c8c4ba; color: #5c5b57;"
      >
        Naskah peraturan perundang-undangan merupakan domain publik berdasarkan Pasal 42 huruf b UU No. 28 Tahun 2014.
      </div>
    </div>
  </div>
{/if}
