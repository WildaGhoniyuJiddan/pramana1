<script>
  import { i18n } from '../lib/i18n.svelte.js';

  let { item = null, onClose = () => {} } = $props();

  const TEXT_STATUS_LABELS = {
    verbatim: 'VERBATIM',
    'verbatim-ocr-dibersihkan': 'VERBATIM (OCR)',
    'verbatim-teks-reproduksi-resmi': 'VERBATIM PORTAL',
    compilation: 'KOMPILASI',
    'non-verbatim': 'NON-VERBATIM',
    'belum-diambil': 'BELUM DIAMBIL'
  };

  function textStatusLabel(status, isVerbatim) {
    if (status && TEXT_STATUS_LABELS[status]) return TEXT_STATUS_LABELS[status];
    return isVerbatim === false ? 'NON-VERBATIM' : 'VERBATIM';
  }

  function textStatusStyle(status, isVerbatim) {
    if (status === 'verbatim' || status === 'verbatim-ocr-dibersihkan' || status === 'verbatim-teks-reproduksi-resmi') {
      return 'background-color: #e7f0ff; color: #0c249c; border: 1px solid #0c249c;';
    }
    if (status === 'compilation' || status === 'non-verbatim') {
      return 'background-color: #fff3cd; color: #8a3b00; border: 1px solid #8a3b00;';
    }
    if (status === 'belum-diambil') {
      return 'background-color: #ece9e2; color: #5c5952; border: 1px solid #8c877c;';
    }
    return isVerbatim === false
      ? 'background-color: #fff3cd; color: #8a3b00; border: 1px solid #8a3b00;'
      : 'background-color: #e7f0ff; color: #0c249c; border: 1px solid #0c249c;';
  }
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
            {i18n.lang === 'en' ? 'Tier' : 'Tingkat'} {item.tier || '1B'} · {item.tier_label || (i18n.lang === 'en' ? 'Statute' : 'Regulasi')}
          </span>
          <h3 class="text-base font-medium mt-1.5" style="color: #0a0a0a;">
            {item.pasal || (i18n.lang === 'en' ? 'Statutory Text' : 'Naskah Regulasi')}
          </h3>
        </div>

        <button
          type="button"
          onclick={onClose}
          class="px-3 py-1 border font-mono text-xs transition-colors cursor-pointer"
          style="background-color: #ffffff; border-color: #c8c4ba; color: #0a0a0a;"
        >
          {i18n.lang === 'en' ? 'CLOSE [ESC]' : 'TUTUP [ESC]'}
        </button>
      </div>

      <!-- Drawer Content -->
      <div class="p-6 overflow-y-auto flex-1 space-y-6" style="background-color: #ffffff;">
        <div class="pb-4 border-b space-y-2" style="border-color: #c8c4ba;">
          <span class="font-mono text-[10px] uppercase tracking-wider block" style="color: #5c5b57;">
            {i18n.lang === 'en' ? 'Official Statute Title' : 'Nomenklatur Peraturan Resmi'}
          </span>
          <p class="text-sm font-medium leading-snug" style="color: #0a0a0a;">
            {item.title || item.official_doc_title}
          </p>
          <div class="flex flex-wrap gap-1.5">
            {#if item.status}
              <span class="font-mono text-[10px] font-bold px-2 py-0.5" style="background-color: #f2f0ea; color: #0a0a0a; border: 1px solid #c8c4ba;">
                {i18n.lang === 'en' ? 'Status' : 'Status'}: {i18n.lang === 'en' ? (item.status === 'Berlaku' ? 'Active' : item.status === 'Disempurnakan' ? 'Superseded' : item.status === 'Berlaku Tahunan' ? 'Annual Observance' : item.status) : item.status}
              </span>
            {/if}
            <span
              class="font-mono text-[10px] font-bold px-2 py-0.5"
              style={textStatusStyle(item.text_status, item.is_verbatim)}
            >
              {textStatusLabel(item.text_status, item.is_verbatim)}
            </span>
            {#if item.document_id}
              <span class="font-mono text-[10px] font-bold px-2 py-0.5" style="background-color: #ffffff; color: #0c249c; border: 1px solid #0c249c;">
                DOC: {item.document_id}
              </span>
            {/if}
            {#if item.last_verified_date}
              <span class="font-mono text-[10px] font-bold px-2 py-0.5" style="background-color: #ffffff; color: #5c5952; border: 1px solid #cdc9be;">
                {i18n.lang === 'en' ? 'Verified' : 'Diverifikasi'} {item.last_verified_date}
              </span>
            {/if}
          </div>
          {#if item.status_note}
            <p class="text-[11px] leading-snug" style="color: #8a3b00;">{item.status_note}</p>
          {/if}
          {#if item.source_note}
            <p class="text-[11px] leading-snug" style="color: #5c5952;">{i18n.lang === 'en' ? 'Source note:' : 'Catatan sumber:'} {item.source_note}</p>
          {/if}
          {#if item.source_type}
            <p class="font-mono text-[10px] leading-snug" style="color: #5c5952;">
              {i18n.lang === 'en' ? 'Source type:' : 'Jenis sumber:'} {item.source_type}
            </p>
          {/if}
          {#if item.superseded_by}
            <p class="text-[11px] leading-snug" style="color: #5c5952;">
              {i18n.lang === 'en' ? 'Superseded by:' : 'Disempurnakan oleh:'}
              {#if item.superseded_by_url}
                <a href={item.superseded_by_url} target="_blank" rel="noopener noreferrer" class="underline" style="color: #0c249c;">
                  {item.superseded_by}
                </a>
              {:else}
                {item.superseded_by}
              {/if}
            </p>
          {/if}
        </div>

        <div>
          <span class="font-mono text-[10px] uppercase tracking-wider block mb-2" style="color: #5c5b57;">
            {item.is_verbatim === false 
              ? (i18n.lang === 'en' ? 'Stored Summary (Non-Verbatim Guidance)' : 'Ringkasan Tersimpan (Bukan Kutipan Verbatim)') 
              : (i18n.lang === 'en' ? 'Verified Stored Text (Layer-1 Corpus Reference)' : 'Teks Tersimpan (Rujukan Layer-1 Korpus)')}
          </span>
          <div
            class="p-5 border text-xs sm:text-sm leading-relaxed font-mono whitespace-pre-line"
            style="background-color: #faf9f6; border: 1px solid #dcd7cb; color: #0a0a0a;"
          >
            {item.full_text || item.quoted_text}
          </div>
          {#if item.is_verbatim === false}
            <p class="mt-2 text-[11px] leading-snug" style="color: #8a3b00;">
              {i18n.lang === 'en'
                ? 'This entry is a summary/compilation, not an official statutory transcript. Do not cite as verbatim text.'
                : 'Entri ini adalah ringkasan/kompilasi, bukan salinan pasal. Jangan dikutip sebagai bunyi pasal verbatim.'}
            </p>
          {/if}
          {#if item.quote_sha256}
            <p class="mt-2 font-mono text-[10px] break-all" style="color: #5c5952;">
              {i18n.lang === 'en' ? 'Quote SHA-256:' : 'SHA-256 kutipan:'} {item.quote_sha256}
            </p>
          {/if}
        </div>

        {#if item.penalties}
          <div class="pt-4 border-t" style="border-color: #c8c4ba;">
            <span class="font-mono text-[10px] uppercase tracking-wider block mb-1.5" style="color: #5c5b57;">
              {i18n.lang === 'en' ? 'Sanctions & Enforcement Provisions' : 'Ketentuan Sanksi & Penegakan'}
            </span>
            <p class="text-xs leading-relaxed" style="color: #2b2b29;">
              {item.penalties}
            </p>
          </div>
        {/if}

        <div class="pt-4 border-t space-y-2" style="border-color: #c8c4ba;">
          <span class="font-mono text-[10px] uppercase tracking-wider block" style="color: #5c5b57;">
            {i18n.lang === 'en' ? 'Official Source Links' : 'Tautan Sumber Resmi'}
          </span>
          {#if item.source_url}
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
          {/if}
          {#if item.source_pdf_url}
            <a
              href={item.source_pdf_url}
              target="_blank"
              rel="noopener noreferrer"
              class="inline-flex items-center gap-1.5 text-xs hover:underline font-mono break-all"
              style="color: #0c249c;"
            >
              <span>{i18n.lang === 'en' ? 'Official PDF:' : 'PDF resmi:'} {item.source_pdf_url}</span>
              <span>↗</span>
            </a>
          {/if}
          {#if item.source_pdf_sha256}
            <p class="font-mono text-[10px] break-all" style="color: #5c5952;">
              SHA-256 PDF: {item.source_pdf_sha256}
            </p>
          {/if}
          {#if item.related_document_ids?.length}
            <p class="font-mono text-[10px]" style="color: #5c5952;">
              {i18n.lang === 'en' ? 'Related documents:' : 'Dokumen terkait:'} {item.related_document_ids.join(', ')}
            </p>
          {/if}
        </div>
      </div>

      <!-- Drawer Footer -->
      <div
        class="px-6 py-3.5 border-t font-mono text-[10px]"
        style="background-color: #f2f0ea; border-color: #c8c4ba; color: #5c5b57;"
      >
        {i18n.lang === 'en'
          ? 'Statutory regulatory texts are in the public domain pursuant to Art. 42(b) of Law No. 28/2014. This display does not constitute official legal advice.'
          : 'Naskah peraturan perundang-undangan merupakan domain publik berdasarkan Pasal 42 huruf b UU No. 28 Tahun 2014. Tampilan ini bukan nasihat hukum.'}
      </div>
    </div>
  </div>
{/if}
