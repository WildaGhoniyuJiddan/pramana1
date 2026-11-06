<script>
  import { onMount, onDestroy } from 'svelte';
  import { Html5Qrcode } from 'html5-qrcode';

  let { isOpen = false, onClose = () => {}, onScan = (zoneId) => {} } = $props();

  let scannerMode = $state('camera'); // 'camera' | 'nfc' | 'file'
  let scannerError = $state('');
  let isScanning = $state(false);
  let nfcSimulating = $state(false);
  let nfcProgressZone = $state(null);
  let html5QrCode = null;
  const SCANNER_ELEMENT_ID = 'pramana-qr-reader';

  const SAMPLE_ZONES = [
    { id: 'pura-besakih', name: 'Pura Besakih (Kawasan Suci)', tagUid: '04:7B:3A:92:1C:60:80' },
    { id: 'bandara-ngurah-rai', name: 'Bandara Ngurah Rai (Pintu Masuk)', tagUid: '04:1A:8F:22:90:4B:81' },
    { id: 'pantai-melasti', name: 'Pantai Melasti (Kawasan Wisata Pesisir)', tagUid: '04:4C:E1:5D:88:31:80' }
  ];

  function extractZoneId(decodedText) {
    if (!decodedText) return null;
    const clean = decodedText.trim();
    // Case 1: direct URL containing /totem/{zoneId}
    const match = clean.match(/\/totem\/([a-z0-9-]+)/i);
    if (match) return match[1].toLowerCase();
    // Case 2: raw zone id
    const known = ['pura-besakih', 'bandara-ngurah-rai', 'pantai-melasti'];
    if (known.includes(clean.toLowerCase())) return clean.toLowerCase();
    return null;
  }

  async function startCamera() {
    scannerError = '';
    try {
      if (!html5QrCode) {
        html5QrCode = new Html5Qrcode(SCANNER_ELEMENT_ID);
      }
      isScanning = true;
      await html5QrCode.start(
        { facingMode: 'environment' },
        {
          fps: 10,
          qrbox: { width: 220, height: 220 }
        },
        (decodedText) => {
          const zoneId = extractZoneId(decodedText);
          if (zoneId) {
            stopCamera();
            onScan(zoneId);
            onClose();
          } else {
            scannerError = `QR terdeteksi tetapi bukan gerbang Pramana: "${decodedText.slice(0, 40)}..."`;
          }
        },
        () => {
          // Ignore transient frame parse failures
        }
      );
    } catch (err) {
      isScanning = false;
      scannerError = 'Kamera tidak dapat diakses atau izin ditolak. Anda dapat menggunakan Simulasi Tap NFC atau Unggah Foto QR.';
    }
  }

  async function stopCamera() {
    if (html5QrCode && isScanning) {
      try {
        await html5QrCode.stop();
      } catch (e) {
        // Ignore stop error
      }
      isScanning = false;
    }
  }

  async function handleFileUpload(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    scannerError = '';
    try {
      if (!html5QrCode) {
        html5QrCode = new Html5Qrcode(SCANNER_ELEMENT_ID);
      }
      const decodedText = await html5QrCode.scanFile(file, true);
      const zoneId = extractZoneId(decodedText);
      if (zoneId) {
        onScan(zoneId);
        onClose();
      } else {
        scannerError = `QR terdeteksi tetapi bukan gerbang Pramana: "${decodedText}"`;
      }
    } catch (err) {
      scannerError = 'Gagal membaca kode QR dari gambar. Pastikan gambar tajam dan pencahayaan cukup.';
    }
  }

  function simulateNfcTap(zone) {
    nfcSimulating = true;
    nfcProgressZone = zone;
    scannerError = '';
    setTimeout(() => {
      nfcSimulating = false;
      onScan(zone.id);
      onClose();
    }, 1100);
  }

  $effect(() => {
    if (isOpen) {
      if (scannerMode === 'camera') {
        // Small delay to ensure modal element is in DOM
        setTimeout(() => startCamera(), 100);
      }
    } else {
      stopCamera();
    }
  });

  onDestroy(() => {
    stopCamera();
  });
</script>

{#if isOpen}
  <div
    class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs"
    role="dialog"
    aria-modal="true"
  >
    <div
      class="w-full max-w-lg bg-[#ffffff] border-2 border-[#0a0a0a] shadow-[6px_6px_0px_#0a0a0a] p-5 sm:p-6 space-y-4 max-h-[90vh] overflow-y-auto"
    >
      <div class="flex items-center justify-between border-b-2 border-[#0a0a0a] pb-3">
        <div class="space-y-0.5">
          <span class="font-mono text-[10px] font-bold text-[#0c249c] uppercase tracking-wider block">
            PHYGITAL GATEWAY INTERACTION
          </span>
          <h3 class="text-lg font-bold text-[#0a0a0a]">Pindai QR / Tap NFC Gerbang</h3>
        </div>
        <button
          type="button"
          onclick={() => { stopCamera(); onClose(); }}
          class="font-mono text-sm font-bold px-2 py-1 border border-[#0a0a0a] bg-[#f3f1eb] hover:bg-[#dfd6c3] cursor-pointer"
        >
          ✕
        </button>
      </div>

      <!-- Mode Selector -->
      <div class="grid grid-cols-2 gap-2 text-xs font-mono font-bold">
        <button
          type="button"
          onclick={() => { scannerMode = 'camera'; startCamera(); }}
          class="p-2 text-center border border-[#0a0a0a] cursor-pointer"
          style={scannerMode === 'camera'
            ? 'background-color: #0c249c; color: #ffffff;'
            : 'background-color: #f3f1eb; color: #0a0a0a;'}
        >
          📷 Kamera / Scan QR
        </button>
        <button
          type="button"
          onclick={() => { stopCamera(); scannerMode = 'nfc'; }}
          class="p-2 text-center border border-[#0a0a0a] cursor-pointer"
          style={scannerMode === 'nfc'
            ? 'background-color: #0c249c; color: #ffffff;'
            : 'background-color: #f3f1eb; color: #0a0a0a;'}
        >
          📡 Simulasi NFC (Tanpa Tag Fisik)
        </button>
      </div>

      {#if scannerError}
        <div class="p-3 text-xs bg-[#fff0f0] border border-[#c92a2a] text-[#c92a2a] font-mono leading-relaxed">
          {scannerError}
        </div>
      {/if}

      {#if scannerMode === 'camera'}
        <div class="space-y-3">
          <div
            id={SCANNER_ELEMENT_ID}
            class="w-full bg-[#0a0a0a] border border-[#0a0a0a] min-h-[240px] flex items-center justify-center overflow-hidden"
          >
            {#if !isScanning}
              <span class="font-mono text-xs text-[#dfd6c3]">Menyiapkan kamera...</span>
            {/if}
          </div>

          <div class="flex items-center justify-between text-xs pt-1">
            <span class="font-mono text-[11px] text-[#5c5952]">Arahkan ke plang QR gerbang wisata.</span>
            <label
              class="font-mono text-[10px] font-bold px-2.5 py-1.5 border border-[#0a0a0a] bg-[#f3f1eb] hover:bg-[#dfd6c3] cursor-pointer"
            >
              Unggah Foto QR
              <input type="file" accept="image/*" onchange={handleFileUpload} class="hidden" />
            </label>
          </div>
        </div>
      {:else}
        <!-- NFC Simulation View -->
        <div class="space-y-3">
          <div class="p-3 bg-[#f3f1eb] border border-[#cdc9be] text-xs space-y-1">
            <div class="flex items-center gap-2">
              <span class="px-1.5 py-0.5 font-mono text-[9px] font-bold bg-[#dfd6c3] text-[#0a0a0a] border border-[#0a0a0a]">SIMULASI PROTOTIPE</span>
              <p class="font-bold text-[#0a0a0a]">Tanpa Perangkat Keras Fisik</p>
            </div>
            <p class="text-[#5c5952] text-[11px] leading-relaxed">
              Tombol di bawah mensimulasikan event sentuhan NFC ponsel ke stiker NTAG213 di totem gerbang fisik secara perangkat lunak tanpa tag fisik nyata. Pada deployment fisik, stiker berisi tautan NDEF URI standar (<code class="bg-[#e8dfc8] px-1 py-0.5">https://.../totem/[zona]</code>).
            </p>
          </div>

          {#if nfcSimulating}
            <div class="p-6 bg-[#0c249c] text-white border-2 border-[#0a0a0a] text-center space-y-2 animate-pulse">
              <span class="font-mono text-[10px] uppercase font-bold tracking-widest text-[#dfd6c3]">
                NFC TAG TOUCH DETECTED
              </span>
              <p class="text-sm font-bold">Membaca NDEF Tag: {nfcProgressZone?.name}</p>
              <p class="font-mono text-[11px] text-[#dfd6c3]">UID: {nfcProgressZone?.tagUid}</p>
            </div>
          {:else}
            <div class="space-y-2">
              <span class="font-mono text-[10px] uppercase font-bold text-[#5c5952] block">
                PILIH GERBANG FISIK UNTUK SIMULASI TAP:
              </span>
              {#each SAMPLE_ZONES as zone}
                <button
                  type="button"
                  onclick={() => simulateNfcTap(zone)}
                  class="w-full text-left p-3 border border-[#0a0a0a] bg-[#ffffff] hover:bg-[#f3f1eb] cursor-pointer flex items-center justify-between group transition-colors"
                >
                  <div class="space-y-0.5">
                    <p class="text-xs font-bold text-[#0a0a0a] group-hover:text-[#0c249c]">{zone.name}</p>
                    <p class="font-mono text-[10px] text-[#5c5952]">Tag UID: {zone.tagUid}</p>
                  </div>
                  <span class="font-mono text-[11px] font-bold text-[#0c249c]">TAP HP 📱 ➔</span>
                </button>
              {/each}
            </div>
          {/if}
        </div>
      {/if}
    </div>
  </div>
{/if}
