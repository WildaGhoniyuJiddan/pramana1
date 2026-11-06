<script>
  import QRCode from 'qrcode';

  let { value = '', size = 160, alt = 'QR code' } = $props();
  let dataUrl = $state('');
  let errorMsg = $state('');

  $effect(() => {
    let cancelled = false;
    const current = value;
    dataUrl = '';
    errorMsg = '';

    if (!current) return;

    QRCode.toDataURL(current, {
      margin: 4,
      width: size,
      errorCorrectionLevel: 'H',
      color: { dark: '#0a0a0a', light: '#ffffff' }
    })
      .then((url) => {
        if (!cancelled) dataUrl = url;
      })
      .catch(() => {
        if (!cancelled) errorMsg = 'QR gagal dibuat.';
      });

    return () => {
      cancelled = true;
    };
  });
</script>

{#if dataUrl}
  <img
    src={dataUrl}
    {alt}
    width={size}
    height={size}
    style="image-rendering: pixelated; border: 1px solid #0a0a0a; background-color: #ffffff;"
  />
{:else if errorMsg}
  <span class="font-mono text-[10px]" style="color: #c92a2a;">{errorMsg}</span>
{:else}
  <div
    class="font-mono text-[10px] flex items-center justify-center"
    style="width: {size}px; height: {size}px; background-color: #f3f1eb; border: 1px dashed #8c877c; color: #5c5952;"
  >
    QR...
  </div>
{/if}
