<script>
  let {
    guidance = null,
    mode = 'NEEDS_CLARIFICATION',
    onSelectRewrite = () => {}
  } = $props();

  const isOutOfScope = $derived(mode === 'OUT_OF_SCOPE_GUIDANCE');
  const title = $derived(
    isOutOfScope
      ? 'Di Luar Ranah Regulasi — Saran Praktis'
      : 'Lengkapi Konteks Anda — Triase Hukum Aktif'
  );
  const accent = $derived(
    isOutOfScope
      ? 'background-color: #e6e4de; color: #0a0a0a; border: 1.5px solid #0a0a0a;'
      : 'background-color: #fff3cd; color: #5c2d00; border: 1.5px solid #8a3b00;'
  );
  const diagnosis = $derived(guidance?.missing_context_diagnosis || []);
  const nextSteps = $derived(guidance?.what_user_should_do_next || []);
  const rewrites = $derived(guidance?.suggested_query_rewrites || []);
  const authority = $derived(guidance?.relevant_authority_or_channel || '');
</script>

{#if diagnosis.length || nextSteps.length || rewrites.length || authority}
  <div class="brutal-card p-5 sm:p-6 space-y-4" style={accent}>
    <div class="flex flex-wrap items-center justify-between gap-2">
      <span class="font-mono text-[10px] font-bold px-2 py-0.5 bg-white" style="border: 1px solid #0a0a0a; color: #0a0a0a;">
        {title}
      </span>
      <span class="font-mono text-[10px] font-bold" style="color: #0a0a0a;">
        SITASI PASAL DIKUNCI KOSONG
      </span>
    </div>

    {#if diagnosis.length}
      <div class="space-y-1.5">
        <h3 class="font-mono text-[11px] font-bold uppercase" style="color: #0a0a0a;">
          01 // Diagnosis Unsur yang Kurang
        </h3>
        <ul class="space-y-1.5 text-xs sm:text-[13px] leading-relaxed" style="color: #3a3935;">
          {#each diagnosis as item, idx}
            <li class="flex items-start gap-2">
              <span class="font-mono text-[10px] font-bold shrink-0">{idx + 1}.</span>
              <span>{item}</span>
            </li>
          {/each}
        </ul>
      </div>
    {/if}

    {#if nextSteps.length}
      <div class="space-y-1.5 pt-2" style="border-top: 1px solid rgba(10, 10, 10, 0.25);">
        <h3 class="font-mono text-[11px] font-bold uppercase" style="color: #0a0a0a;">
          02 // Langkah yang Disarankan
        </h3>
        <ul class="space-y-1.5 text-xs sm:text-[13px] leading-relaxed" style="color: #3a3935;">
          {#each nextSteps as item, idx}
            <li class="flex items-start gap-2">
              <span class="font-mono text-[10px] font-bold shrink-0">{idx + 1}.</span>
              <span>{item}</span>
            </li>
          {/each}
        </ul>
      </div>
    {/if}

    {#if authority}
      <div class="p-3 text-xs leading-snug" style="background-color: #ffffff; border: 1px solid #0a0a0a; color: #0a0a0a;">
        <span class="font-mono text-[10px] font-bold uppercase block mb-1">
          03 // Kanal Resmi
        </span>
        {authority}
      </div>
    {/if}

    {#if rewrites.length}
      <div class="space-y-2 pt-2" style="border-top: 1px solid rgba(10, 10, 10, 0.25);">
        <h3 class="font-mono text-[11px] font-bold uppercase" style="color: #0a0a0a;">
          04 // Klik untuk Memperjelas Konteks
        </h3>
        <p class="text-[11px] leading-snug" style="color: #3a3935;">
          Pilih salah satu kalimat lengkap di bawah untuk menjalankan ulang analisis dengan unsur lokasi, tindakan, dan pihak yang lebih jelas.
        </p>
        <div class="grid grid-cols-1 gap-2">
          {#each rewrites as rewrite, idx}
            <button
              type="button"
              onclick={() => onSelectRewrite(rewrite)}
              class="brutal-press text-left px-3 py-2 text-xs sm:text-[13px] leading-snug cursor-pointer"
              style="background-color: #ffffff; color: #0a0a0a; border: 1.5px solid #0a0a0a; box-shadow: 2px 2px 0px #0a0a0a;"
            >
              <span class="font-mono text-[10px] font-bold block mb-1" style="color: #0c249c;">
                SKENARIO 0{idx + 1}
              </span>
              {rewrite}
            </button>
          {/each}
        </div>
      </div>
    {/if}
  </div>
{/if}
