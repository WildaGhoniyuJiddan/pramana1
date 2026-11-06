<script>
  let { result = {} } = $props();

  const mode = $derived(result.resolution_mode || 'VERIFIED_GROUNDED');
  const modeLabel = $derived(
    mode === 'VERIFIED_GROUNDED'
      ? 'TERVERIFIKASI KORPUS'
      : mode === 'NEEDS_CLARIFICATION'
        ? 'PERLU DETAIL KONTEKS'
        : 'DI LUAR RANAH REGULASI'
  );
  const modeStyle = $derived(
    mode === 'VERIFIED_GROUNDED'
      ? 'background-color: #e7f0ff; color: #0c249c; border: 1.5px solid #0c249c;'
      : mode === 'NEEDS_CLARIFICATION'
        ? 'background-color: #fff3cd; color: #8a3b00; border: 1.5px solid #8a3b00;'
        : 'background-color: #e6e4de; color: #3a3935; border: 1.5px solid #3a3935;'
  );
  const claims = $derived(
    result.ai_claims?.length ?? result.claims?.length ?? 0
  );
  const model = $derived(
    result.ai_model || result.model || 'deterministic'
  );
  const score = $derived(
    result.retrieval_score === null || result.retrieval_score === undefined
      ? '-'
      : Number(result.retrieval_score).toFixed(3)
  );
</script>

<div
  class="flex flex-wrap items-center gap-2 p-2.5"
  style="background-color: #ffffff; border: 1.5px solid #0a0a0a;"
>
  <span
    class="font-mono text-[10px] font-bold px-2 py-0.5"
    style={modeStyle}
  >
    {modeLabel}
  </span>
  <span class="font-mono text-[10px]" style="color: #3a3935;">
    MODEL: <strong>{model || 'deterministic'}</strong>
  </span>
  <span class="font-mono text-[10px]" style="color: #3a3935;">
    SKOR: <strong>{score}</strong>
  </span>
  <span class="font-mono text-[10px]" style="color: #3a3935;">
    KLAIM: <strong>{claims}</strong>
  </span>
  <span class="font-mono text-[10px]" style="color: #3a3935;">
    LATENSI: <strong>{result.ai_latency_ms ?? 0} ms</strong>
  </span>
</div>
