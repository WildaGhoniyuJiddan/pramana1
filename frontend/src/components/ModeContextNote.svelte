<script>
  import { onMount } from 'svelte';
  import { requestContextNote } from '../lib/api.js';
  import { i18n, DICT } from '../lib/i18n.svelte.js';

  let { onOpenDoc = () => {} } = $props();

  let t = $derived(DICT[i18n.lang].context);
  let common = $derived(DICT[i18n.lang].common);
  let presets = $derived(t.presets);

  let postContent = $state('');
  let loading = $state(false);
  let errorMsg = $state('');
  let result = $state(null);
  let copySuccess = $state(false);
  let activePresetIdx = $state(0);
  let activeCiteIdx = $state(0);
  let showTechAudit = $state(false);
  let summaryLang = $derived(i18n.lang);

  onMount(() => {
    applyPreset(presets[0], 0, true);
  });

  // Keep preset text in sync if language switches while on a preset
  $effect(() => {
    const currPreset = presets[activePresetIdx];
    if (currPreset && (!postContent || presets.some(p => p.text === postContent))) {
      postContent = currPreset.text;
    }
  });

  function applyPreset(p, idx, autoRun = false) {
    activePresetIdx = idx;
    postContent = p.text;
    if (autoRun) handleSubmit();
  }

  async function handleSubmit(e) {
    if (e) e.preventDefault();
    if (!postContent.trim()) {
      errorMsg = i18n.lang === 'id' ? 'Masukkan teks klaim atau postingan untuk dianalisis.' : 'Please enter claim or incident text to analyze.';
      return;
    }
    loading = true;
    errorMsg = '';

    try {
      result = await requestContextNote({ post_content: postContent });
      activeCiteIdx = 0;
    } catch (err) {
      errorMsg = err.message || (i18n.lang === 'id' ? 'Gagal memproses catatan konteks.' : 'Failed to generate context note.');
    } finally {
      loading = false;
    }
  }

  async function copyComment() {
    if (!result || !result.copyable_comment) return;
    try {
      await navigator.clipboard.writeText(result.copyable_comment);
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
            02
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

  <!-- 2. WORKSPACE GRID -->
  <section class="px-5 sm:px-10 py-6 sm:py-8">
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">

      <!-- LEFT COLUMN: INPUT CARD (5 cols) -->
      <div class="lg:col-span-5">
        <div class="brutal-card p-5 sm:p-6 space-y-5" style="background-color: #f3f1eb;">
          <div class="flex items-center justify-between pb-3" style="border-bottom: 1px solid #cdc9be;">
            <span class="font-mono text-[10px] font-bold px-2 py-0.5" style="background-color: #dfd6c3; color: #0a0a0a; border: 1px solid #0a0a0a;">
              {t.claimNarrative}
            </span>
            <span class="font-mono text-[11px]" style="color: #5c5952;">{t.dualGuard}</span>
          </div>

          <form onsubmit={handleSubmit} class="space-y-4">
            <div>
              <label for="post-content" class="block text-xs font-semibold mb-1.5" style="color: #0a0a0a;">
                {t.inputLabel}
              </label>
              <textarea
                id="post-content"
                bind:value={postContent}
                rows="5"
                placeholder={t.placeholder}
                style="background-color: #ffffff; color: #0a0a0a; border: 1.5px solid #0a0a0a;"
                class="w-full p-3 text-xs sm:text-[13px] focus:outline-none leading-relaxed"
              ></textarea>
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

          <!-- Clean Architectural Protocol Footnote -->
          <div class="pt-3 space-y-2 text-[11px]" style="border-top: 1px solid #cdc9be; color: #4a4740;">
            <div class="flex items-start gap-2.5">
              <svg class="w-4 h-4 shrink-0 mt-0.5" viewBox="0 0 18 18" fill="none">
                <rect x="2.5" y="2.5" width="13" height="13" stroke="#0a0a0a" stroke-width="1.5" />
                <path d="M5.5 9l2.5 2.5 4.5-5" stroke="#0a0a0a" stroke-width="1.5" />
              </svg>
              <span class="leading-snug">
                {t.protocolL1}
              </span>
            </div>
            <div class="flex items-start gap-2.5">
              <svg class="w-4 h-4 shrink-0 mt-0.5" viewBox="0 0 18 18" fill="none">
                <circle cx="9" cy="9" r="6.5" stroke="#0a0a0a" stroke-width="1.5" />
                <path d="M5 5l8 8" stroke="#0a0a0a" stroke-width="1.5" />
              </svg>
              <span class="leading-snug">
                {t.protocolL2}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- RIGHT COLUMN: HIERARCHICAL VERIFICATION DOSSIER (7 cols) -->
      <div class="lg:col-span-7 space-y-5">
        {#if result}
          {#if result.status === 'TIDAK_DITEMUKAN'}
            <!-- ABSTAIN CARD -->
            <div class="brutal-card p-6 sm:p-8 space-y-4" style="background-color: #dfd6c3;">
              <div class="flex items-center justify-between">
                <span class="font-mono text-[10px] font-bold px-2 py-0.5" style="background-color: #0a0a0a; color: #ffffff;">
                  LAYER-2 ABSTAIN
                </span>
                <span class="font-mono text-xs font-bold" style="color: #0a0a0a;">ABSTAIN</span>
              </div>

              <h2 class="opero-h1 text-2xl sm:text-3xl">
                {t.abstainTitle}
              </h2>

              <p class="text-xs sm:text-sm leading-relaxed" style="color: #3a3935;">
                {result.neutral_summary}
              </p>

              <div class="p-3 bg-white font-mono text-[11px]" style="border: 1.5px solid #0a0a0a;">
                {t.abstainDesc}
              </div>

              {#if result.confidence_note}
                <p class="text-[11px] leading-snug" style="color: #5c5952;">{result.confidence_note}</p>
              {/if}

              <div class="p-3 text-[11px] leading-snug" style="background-color: #ffffff; border: 1px solid #0a0a0a; color: #3a3935;">
                <strong>{common.maskedText}</strong> {result.masked_post}
                <br />
                <strong>{common.piiRedacted}</strong> {result.pii_redacted_count ?? 0} {common.entities}
              </div>

              {#if result.disclaimer}
                <p class="text-[11px] leading-snug" style="color: #5c5952;">
                  <strong>{common.disclaimer}</strong> {result.disclaimer}
                </p>
              {/if}
            </div>
          {:else}
            <!-- STEP 1: PRIMARY FOCUS - CATATAN KONTEKS NETRAL -->
            <div class="brutal-card-cobalt p-5 sm:p-6 space-y-4">
              <div class="flex flex-wrap items-center justify-between gap-2">
                <span
                  class="font-mono text-[10px] font-bold px-2 py-0.5"
                  style="background-color: #dfd6c3; color: #0a0a0a; border: 1px solid #0a0a0a;"
                >
                  {t.readyBadge}
                </span>

                {#if result.copyable_comment}
                  <button
                    type="button"
                    onclick={copyComment}
                    style="background-color: #dfd6c3; color: #0a0a0a; border: 1.5px solid #0a0a0a; box-shadow: 2px 2px 0px #0a0a0a;"
                    class="brutal-press px-3 py-1 font-mono text-[11px] font-bold inline-flex items-center gap-1.5 cursor-pointer"
                  >
                    <svg class="w-3.5 h-3.5" viewBox="0 0 18 18" fill="none">
                      <rect x="5.5" y="5.5" width="9" height="9" stroke="#0a0a0a" stroke-width="1.5" />
                      <path d="M12.5 5.5V3.5h-9v9h2" stroke="#0a0a0a" stroke-width="1.5" />
                    </svg>
                    <span>{copySuccess ? common.copied : common.copy}</span>
                  </button>
                {/if}
              </div>

              <div>
                <p class="text-sm sm:text-base leading-relaxed font-normal" style="color: #ffffff;">
                  {summaryLang === 'en' && result.neutral_summary_en
                    ? result.neutral_summary_en
                    : result.neutral_summary}
                </p>
              </div>

              {#if result.ai_synthesis_status === 'llm'}
                <p class="text-[11px] font-mono" style="color: #dfd6c3;">
                  {common.llmNotice}
                </p>
              {:else if result.ai_synthesis_status === 'unavailable'}
                <p class="text-[11px] font-mono" style="color: #dfd6c3;">
                  {common.unavailableNotice}
                </p>
              {:else if result.ai_synthesis_status === 'abstain'}
                <p class="text-[11px] font-mono" style="color: #dfd6c3;">
                  {common.abstainNotice}
                </p>
              {:else}
                <p class="text-[11px] font-mono" style="color: #dfd6c3;">
                  {common.templateNotice}
                </p>
              {/if}

              {#if result.ai_claims?.length}
                <p class="font-mono text-[10px]" style="color: #dfd6c3;">
                  {result.ai_claims.length} claims verified against evidence span.
                </p>
              {/if}

              <div class="p-3 text-[11px] leading-snug" style="background-color: #f3f1eb; color: #3a3935; border: 1px solid #0a0a0a;">
                <strong>{common.maskedText}</strong> {result.masked_post}
                <br />
                <strong>{common.piiRedacted}</strong> {result.pii_redacted_count ?? 0} {common.entities}
              </div>

              {#if result.framing_markers && result.framing_markers.length > 0}
                <div class="p-3.5 space-y-2" style="background-color: #f3f1eb; color: #0a0a0a; border: 1.5px solid #0a0a0a;">
                  <span class="font-mono text-[10px] font-bold uppercase block" style="color: #0c249c;">
                    {t.framingTitle} ({result.framing_markers.length})
                  </span>
                  {#each result.framing_markers as marker}
                    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs pt-1" style="border-top: 1px solid #cdc9be;">
                      <span class="font-mono font-bold px-1.5 py-0.5 bg-white" style="border: 1px solid #0a0a0a;">
                        "{marker.phrase}"
                      </span>
                      <span style="color: #3a3935;">{marker.reason}</span>
                    </div>
                  {/each}
                </div>
              {/if}
            </div>

            <!-- STEP 2: SECONDARY FOCUS - VERBATIM CITATION INSPECTOR -->
            <div class="brutal-card p-5 sm:p-6 space-y-4" style="background-color: #f3f1eb;">
              <div class="flex flex-wrap items-center justify-between gap-2 pb-3" style="border-bottom: 1px solid #cdc9be;">
                <span class="font-mono text-[10px] font-bold px-2 py-0.5" style="background-color: #dfd6c3; color: #0a0a0a; border: 1px solid #0a0a0a;">
                  {t.citationsBadge} ({result.citations.length} {t.documentsLabel})
                </span>
                <span class="font-mono text-[11px] font-bold" style="color: #0c249c;">
                  {t.exactMatch}
                </span>
              </div>

              {#if result.citations.length > 1}
                <div class="flex flex-wrap gap-2">
                  {#each result.citations as cite, idx}
                    <button
                      type="button"
                      onclick={() => (activeCiteIdx = idx)}
                      style={activeCiteIdx === idx
                        ? 'background-color: #0c249c; color: #ffffff; border: 1.5px solid #0a0a0a; box-shadow: 2px 2px 0px #0a0a0a;'
                        : 'background-color: #ffffff; color: #0a0a0a; border: 1.5px solid #0a0a0a;'}
                      class="brutal-press px-3 py-1.5 font-mono text-[11px] font-semibold cursor-pointer"
                    >
                      0{idx + 1} · {cite.pasal}
                    </button>
                  {/each}
                </div>
              {/if}

              {#if result.citations[activeCiteIdx]}
                {@const activeCite = result.citations[activeCiteIdx]}
                <div
                  class="p-5 bg-white space-y-4"
                  style="border: 1.5px solid #0a0a0a; box-shadow: 3px 3px 0px #0a0a0a;"
                >
                  <div class="flex flex-wrap items-center justify-between gap-2 pb-2.5" style="border-bottom: 1px solid #e6e4de;">
                    <span class="font-mono text-[10px] font-bold px-2 py-0.5" style="background-color: #0c249c; color: #ffffff;">
                      {common.tierLabel} {activeCite.tier} · {activeCite.tier_label}
                    </span>
                    <span class="font-mono text-xs font-bold" style="color: #0a0a0a;">
                      {activeCite.pasal}
                    </span>
                  </div>

                  <h3 class="text-sm sm:text-base font-medium leading-snug" style="color: #0a0a0a;">
                    {activeCite.official_doc_title}
                  </h3>

                  <div class="flex flex-wrap gap-1.5">
                    <span class="font-mono text-[10px] font-bold px-2 py-0.5" style="background-color: #ffffff; color: #0a0a0a; border: 1px solid #0a0a0a;">
                      Status: {activeCite.status || '-'}
                    </span>
                    <span
                      class="font-mono text-[10px] font-bold px-2 py-0.5"
                      style={activeCite.is_verbatim
                        ? 'background-color: #e7f0ff; color: #0c249c; border: 1px solid #0c249c;'
                        : 'background-color: #fff3cd; color: #8a3b00; border: 1px solid #8a3b00;'}
                    >
                      {activeCite.text_status === 'compilation'
                        ? common.compilationNotice
                        : activeCite.is_verbatim ? common.verbatimNotice : common.summaryNotice}
                    </span>
                  </div>

                  <!-- Full-border architectural quote box (no cliché left stripe) -->
                  <div
                    class="p-4 text-xs sm:text-[13px] leading-relaxed"
                    style="background-color: #f3f1eb; border: 1.5px solid #0a0a0a; color: #0a0a0a;"
                  >
                    {#if activeCite.is_verbatim}
                      "{activeCite.quoted_text}"
                    {:else}
                      {activeCite.quoted_text}
                      <p class="mt-2 font-mono text-[10px] leading-snug" style="color: #8a3b00;">
                        {common.summaryNotice}
                      </p>
                    {/if}
                  </div>

                  {#if activeCite.status_note}
                    <p class="text-[11px] leading-snug" style="color: #8a3b00;">{activeCite.status_note}</p>
                  {/if}
                  {#if activeCite.source_note}
                    <p class="text-[11px] leading-snug" style="color: #5c5952;">{activeCite.source_note}</p>
                  {/if}
                  {#if activeCite.superseded_by}
                    <p class="text-[11px] leading-snug" style="color: #5c5952;">
                      {common.supersededBy}
                      {#if activeCite.superseded_by_url}
                        <a href={activeCite.superseded_by_url} target="_blank" rel="noopener noreferrer" class="underline" style="color: #0c249c;">
                          {activeCite.superseded_by}
                        </a>
                      {:else}
                        {activeCite.superseded_by}
                      {/if}
                    </p>
                  {/if}
                  {#if activeCite.quote_sha256}
                    <p class="font-mono text-[10px] break-all" style="color: #5c5952;">
                      SHA-256: {activeCite.quote_sha256}
                    </p>
                  {/if}

                  {#if activeCite.penalties}
                    <div
                      class="p-3 text-xs space-y-1"
                      style="background-color: #dfd6c3; border: 1px solid #0a0a0a; color: #0a0a0a;"
                    >
                      <span class="font-mono text-[10px] font-bold uppercase block">
                        {common.penaltiesTitle}
                      </span>
                      <p class="leading-snug">{activeCite.penalties}</p>
                    </div>
                  {/if}

                  <div class="pt-1 flex justify-end">
                    <button
                      type="button"
                      onclick={() => onOpenDoc(activeCite)}
                      style="background-color: #0a0a0a; color: #ffffff; padding: 2px; border: 1.5px solid #0a0a0a;"
                      class="brutal-press inline-flex items-center gap-2 text-xs font-medium cursor-pointer"
                    >
                      <span class="px-2.5 py-1 font-mono text-[11px]">
                        {activeCite.is_verbatim ? common.openOriginal : common.openSummary}
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
                  {showTechAudit ? common.hideAudit : common.showAudit}
                </button>
                <span>{common.confidence}: {result.confidence}</span>
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
                  <div>PII MASKED: <strong>{result.pii_redacted_count ?? 0} entitas</strong></div>
                </div>
              {/if}

              {#if result.confidence_note}
                <p class="text-[11px] leading-snug" style="color: #5c5952;">{result.confidence_note}</p>
              {/if}

              {#if result.disclaimer}
                <p class="text-[11px] leading-snug" style="color: #5c5952;">
                  <strong>Disclaimer:</strong> {result.disclaimer}
                </p>
              {/if}
            </div>
          {/if}
        {/if}
      </div>

    </div>
  </section>
</div>
