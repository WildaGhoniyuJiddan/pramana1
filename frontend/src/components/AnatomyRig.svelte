<script>
  import { onMount } from 'svelte';
  import * as k from '../lib/iso-kit.js';

  const WIDTH = 640;
  const HEIGHT = 220;

  let activeIdx = $state(0);

  // Straightforward 3-Step Scenarios (1. Input -> 2. Filter -> 3. Output)
  const CASES = [
    {
      id: 'sacred',
      tab: '1. Kawasan Suci Pura',
      isAbstain: false,
      step1: {
        tag: '01 // INPUT PENGGUNA',
        title: 'Klaim / Rencana Wisata',
        desc: '"Wisatawan memanjat pohon keramat di kawasan Pura Tabanan (Booking: alex@mail.com)"',
        pill: 'PII Disamarkan Otomatis'
      },
      step2: {
        tag: '02 // FILTER PRAMANA',
        title: 'Cek Aturan Adat & Korpus',
        desc: 'Mencocokkan lokasi kawasan suci Utama Mandala dengan SE Gubernur & UU Imigrasi.',
        pill: 'Gerbang Candi Bentar: LOLOS'
      },
      step3: {
        tag: '03 // OUTPUT KORPUS',
        title: 'Kutipan dari Korpus',
        desc: 'Merujuk Pasal 75 UU No. 6/2011 & larangan SE Gub No. 4/2023 (disempurnakan SE 7/2025).',
        pill: 'Layer-1 exact match (korpus)'
      }
    },
    {
      id: 'nyepi',
      tab: '2. Hari Suci Nyepi',
      isAbstain: false,
      step1: {
        tag: '01 // INPUT PENGGUNA',
        title: 'Jadwal Rute Perjalanan',
        desc: '"Tiba di Bandara Ngurah Rai & menginap di Ubud tanggal 18 – 21 Maret 2026."',
        pill: 'Rentang 4 Hari Terdeteksi'
      },
      step2: {
        tag: '02 // FILTER PRAMANA',
        title: 'Kalender Saka',
        desc: 'Mendeteksi irisan Hari Suci Nyepi pada 19 Maret 2026 (06.00 WITA – 20 Mar 06.00 WITA).',
        pill: 'Catur Brata Penyepian 24 Jam'
      },
      step3: {
        tag: '03 // OUTPUT KORPUS',
        title: 'Panduan & Kalender .ICS',
        desc: 'Notifikasi penutupan bandara/jalan raya + unduh jadwal pengingat .ICS (RFC 5545).',
        pill: 'Siap Impor ke Google/Apple Cal'
      }
    },
    {
      id: 'abstain',
      tab: '3. Klaim Hoaks / Di Luar Hukum',
      isAbstain: true,
      step1: {
        tag: '01 // INPUT PENGGUNA',
        title: 'Klaim di Luar Regulasi',
        desc: '"Kucing oranye meminta ikan goreng di meja kasir restoran pantai."',
        pill: 'Topik Non-Hukum'
      },
      step2: {
        tag: '02 // FILTER PRAMANA',
        title: 'Skor di Bawah Ambang Relevansi',
        desc: 'Tidak ditemukan kecocokan yang melewati ambang 0,50 di korpus lokal Pramana.',
        pill: 'Gerbang Candi Bentar: DITUTUP'
      },
      step3: {
        tag: '03 // OUTPUT KORPUS',
        title: 'Menolak Mengarang Pasal',
        desc: 'Mesin menghentikan sintesis AI (Abstain) agar tidak mengarang nomor Perda fiktif.',
        pill: 'Abstain Guard Aktif'
      }
    }
  ];

  const P = {
    origin: [WIDTH / 2, 134],
    scale: 1.72,
    azimuth: 54,
    elevation: 28
  };

  const at = (point) => k.iso(point, P);
  const S = (paths, style) => k.solidSvg(paths, style);
  const L = (d, style) => k.lineSvg(d, style);
  const D = (points, style) => k.dotsSvg(points, style);

  const X1 = -96;
  const X2 = 0;
  const X3 = 96;

  // 1. Static Pedestal 01 (Left: Input & PII Scanner Base)
  function buildPedestal1Base() {
    const out = [];
    const base = { x: X1 - 26, y: -24, w: 52, d: 48, r: 4 };
    out.push(`<path class="iso-halo" d="${k.haloOf(base, -8, 8, P)}"/>`);
    out.push(S(k.slabOf(base, -8, 8, P, 5, 1.0), { tone: 'mid' }));
    out.push(L(k.planOutline(k.insetPlan(base, 3.5), 0, P), { tone: 'lo' }));

    // Recessed Scanner Platen at z = 0..1.8
    const platen = { x: X1 - 17, y: -14, w: 34, d: 28, r: 2 };
    out.push(S(k.slabOf(platen, 0, 1.8, P, 4, 0.4), { tone: 'lo' }));
    out.push(D(k.dotGrid(X1 - 12, 17, 5, 1, 6, 0, P), { size: 0.55, tone: 'mid' }));
    return out.join('');
  }

  // Animated 3D PII Scanner Bridge that sweeps back and forth above the document packet on Pedestal 01
  function buildScannerBar() {
    const bar = { x: X1 - 19, y: -2.5, w: 38, d: 5, r: 1 };
    return S(k.slabOf(bar, 6.2, 3.2, P, 3, 0.4), { tone: 'hi', lit: true });
  }

  // 2. Solid 3D Conveyor Bridge Segment (Zero dotted lines)
  function buildBridgeSegment(xFrom, xTo) {
    const out = [];
    const deck = { x: xFrom, y: -7.5, w: xTo - xFrom, d: 15, r: 1 };
    out.push(S(k.slabOf(deck, -3.5, 5.3, P, 3, 0.4), { tone: 'lo' }));
    const railBack = { x: xFrom, y: -7.5, w: xTo - xFrom, d: 2.2, r: 0.5 };
    const railFront = { x: xFrom, y: 5.3, w: xTo - xFrom, d: 2.2, r: 0.5 };
    out.push(S(k.slabOf(railBack, 1.8, 1.8, P, 2, 0.3), { tone: 'mid' }));
    out.push(S(k.slabOf(railFront, 1.8, 1.8, P, 2, 0.3), { tone: 'mid' }));
    return out.join('');
  }

  // Animated 3D Document Packet that glides at z = 1.9..5.1 from X1 (-96) -> X2 (0) -> X3 (+96)
  function buildMovingPacket() {
    const out = [];
    const tray = { x: -11, y: -4.6, w: 22, d: 9.2, r: 1.2 };
    out.push(S(k.slabOf(tray, 1.9, 3.2, P, 3, 0.4), { tone: 'hi', lit: true }));
    out.push(L(k.lineOnTop([-6.5, -1.5], [6.5, -1.5], 5.1, P), { tone: 'lit', free: true }));
    out.push(L(k.lineOnTop([-6.5, 1.5], [4.0, 1.5], 5.1, P), { tone: 'lo', free: true }));
    return out.join('');
  }

  // 3. Pedestal 02 (Center: Candi Bentar Base & Saka 1948 Ring at z = 0..1.8)
  function buildPedestal2Base() {
    const out = [];
    const base = { x: X2 - 28, y: -26, w: 56, d: 52, r: 4 };
    out.push(`<path class="iso-halo" d="${k.haloOf(base, -8, 8, P)}"/>`);
    out.push(S(k.slabOf(base, -8, 8, P, 5, 1.0), { tone: 'mid' }));
    out.push(S(k.cylinder(X2, 0, 19, 0, 1.8, P, 48, 0.4), { tone: 'lo' }));
    const ticks = k.radialTicks(X2, 0, 17, 36, 3, 1.8, [1.2, 2.4], P);
    out.push(L(ticks.minor, { tone: 'lo' }), L(ticks.major, { tone: 'mid' }));
    return out.join('');
  }

  // Animated 3D Candi Bentar Half-Tower (Back tower & Front tower slide apart/together in 3D!)
  function buildCandiTowerHalf(isFront) {
    const out = [];
    const innerY = isFront ? 2.2 : -2.2;
    const tiers = [
      [1.8, 7, 13, 11, 'mid', false],
      [8.8, 10, 10.5, 9, 'hi', false],
      [18.8, 8, 8, 7, 'hi', false],
      [26.8, 6, 5.2, 4.5, 'hi', true]
    ];
    for (const [z0, h, w, d, tone, lit] of tiers) {
      const y0 = isFront ? innerY : innerY - d;
      const plan = { x: X2 - w / 2, y: y0, w, d, r: 0.8 };
      out.push(S(k.slabOf(plan, z0, h, P, 3, 0.4), { tone, lit }));
    }
    return out.join('');
  }

  // 4. Pedestal 03 (Right: Pramana Corpus Anvil Base at z = 0..1.8 so packet glides right onto it!)
  function buildPedestal3Base() {
    const out = [];
    const base = { x: X3 - 26, y: -24, w: 52, d: 48, r: 4 };
    out.push(`<path class="iso-halo" d="${k.haloOf(base, -8, 8, P)}"/>`);
    out.push(S(k.slabOf(base, -8, 8, P, 5, 1.0), { tone: 'mid' }));
    out.push(L(k.planOutline(k.insetPlan(base, 3.5), 0, P), { tone: 'lo' }));

    const anvil = { x: X3 - 17, y: -14, w: 34, d: 28, r: 2 };
    out.push(S(k.slabOf(anvil, 0, 1.8, P, 4, 0.5), { tone: 'lo' }));
    out.push(L(k.planOutline(k.insetPlan(anvil, 2.5), 1.8, P), { tone: 'faint' }));
    return out.join('');
  }

  // Animated 3D Pramana Corpus Seal Cylinder (Suspended at z = 6..16, stamps down onto the packet at X3!)
  function buildStampHead() {
    const out = [];
    const pad = { x: X3 - 12, y: -8, w: 24, d: 16, r: 1.5 };
    out.push(S(k.slabOf(pad, 5.2, 3.0, P, 3, 0.4), { tone: 'hi', lit: true }));
    out.push(S(k.cylinder(X3, 0, 9.5, 8.2, 5.5, P, 36, 0.5), { tone: 'hi', lit: true }));
    out.push(L(k.knurl(X3, 0, 9.5, 8.2, 13.7, 28, P), { tone: 'lo' }));
    out.push(L(k.ring(X3, 0, 6.2, 13.7, P, 24), { tone: 'lo' }));
    out.push(S(k.cylinder(X3, 0, 3.5, 13.7, 4.5, P, 20, 0.3), { tone: 'mid' }));
    return out.join('');
  }

  // Solid Callout Badges (Zero dotted/dashed lines!)
  function buildCalloutBadge(pt, num, text, active) {
    const [sx, sy] = pt;
    const bw = 136;
    const bh = 22;
    const bx = sx - bw / 2;
    const by = sy - 30;
    const bg = active ? '#0c249c' : '#262522';
    return `
      <line x1="${sx.toFixed(1)}" y1="${sy.toFixed(1)}" x2="${sx.toFixed(1)}" y2="${(by + bh).toFixed(1)}" stroke="#0a0a0a" stroke-width="1.5"/>
      <circle cx="${sx.toFixed(1)}" cy="${sy.toFixed(1)}" r="2.8" fill="#0c249c" stroke="#ffffff" stroke-width="1"/>
      <rect x="${(bx + 2).toFixed(1)}" y="${(by + 2).toFixed(1)}" width="${bw}" height="${bh}" fill="#0a0a0a"/>
      <rect x="${bx.toFixed(1)}" y="${by.toFixed(1)}" width="${bw}" height="${bh}" fill="#ffffff" stroke="#0a0a0a" stroke-width="1.5"/>
      <rect x="${bx.toFixed(1)}" y="${by.toFixed(1)}" width="24" height="${bh}" fill="${bg}"/>
      <text x="${(bx + 12).toFixed(1)}" y="${(by + 14.5).toFixed(1)}" text-anchor="middle" fill="#ffffff" font-family="IBM Plex Mono, monospace" font-size="9.5" font-weight="700">${num}</text>
      <text x="${(bx + 24 + (bw - 24) / 2).toFixed(1)}" y="${(by + 14.5).toFixed(1)}" text-anchor="middle" fill="#0a0a0a" font-family="IBM Plex Mono, monospace" font-size="9" font-weight="700">${text}</text>
    `;
  }

  const staticPed1 = buildPedestal1Base();
  const staticScanner = buildScannerBar();
  const staticBridge12 = buildBridgeSegment(X1 + 26, X2 - 28);
  const staticBridge23 = buildBridgeSegment(X2 + 28, X3 - 26);
  const staticPed2 = buildPedestal2Base();
  const staticBackTower = buildCandiTowerHalf(false);
  const staticFrontTower = buildCandiTowerHalf(true);
  const staticPed3 = buildPedestal3Base();
  const staticStampHead = buildStampHead();
  const staticPacket = buildMovingPacket();

  const pointerPathAt = (angle) =>
    k.lineOnTop(
      [X2 - Math.sin(angle) * 4, Math.cos(angle) * 4],
      [X2 + Math.sin(angle) * 15.5, -Math.cos(angle) * 15.5],
      2.0,
      P
    );

  let scannerEl = $state(null);
  let packetEl = $state(null);
  let backTowerEl = $state(null);
  let frontTowerEl = $state(null);
  let stampHeadEl = $state(null);
  let sakaHandEl = $state(null);

  let currentCase = $derived(CASES[activeIdx]);

  onMount(() => {
    let frame = 0;
    let start = performance.now();
    let gateGap = 6.0;
    const still = window.matchMedia('(prefers-reduced-motion: reduce)');

    function tick(now) {
      const t = (now - start) / 1000;
      const isAbstain = CASES[activeIdx].isAbstain;

      // 1. 3D PII Scanner Bar sweeps smoothly across Pedestal 01 (y = -8..+8)
      const scanY = still.matches ? 0 : Math.sin(t * 2.8) * 8.5;
      if (scannerEl) {
        scannerEl.setAttribute('transform', k.translateAlong(P, [0, scanY, 0]));
      }

      // 2. 3D Candi Bentar Split-Gate Towers part open (gap = 6.0) or clamp shut on Abstain (gap = 0.0)
      const targetGap = isAbstain ? 0.0 : 6.0 + (still.matches ? 0 : Math.sin(t * 2.2) * 0.6);
      gateGap += (targetGap - gateGap) * 0.12;
      if (backTowerEl && frontTowerEl) {
        backTowerEl.setAttribute('transform', k.translateAlong(P, [0, -gateGap, 0]));
        frontTowerEl.setAttribute('transform', k.translateAlong(P, [0, gateGap, 0]));
      }

      // 3. Saka 1948 Calendar Hand rotates smoothly on Pedestal 02
      if (sakaHandEl) {
        const ang = isAbstain ? 0 : t * 0.95;
        sakaHandEl.setAttribute('d', pointerPathAt(ang));
      }

      // 4. 3D Document Packet glides all the way from Pedestal 01 (X1 = -96) -> Pedestal 02 (0) -> Pedestal 03 (X3 = +96)!
      const cycle = (t * 0.48) % 1;
      let packetX = 0;
      let stampZ = 5.5;

      if (isAbstain) {
        // Starts at X1 (-96), travels toward X2 (-20), bounces off the locked Candi Bentar gate, and returns to X1
        const u = cycle < 0.5 ? cycle * 2 : (1 - cycle) * 2;
        const eased = 1 - Math.pow(1 - u, 2.2);
        packetX = X1 + eased * 74;
        stampZ = 5.5;
      } else {
        // Travels from X1 (-96) through Candi Bentar (0) right onto Pedestal 03 (X3 = +96)
        if (cycle < 0.72) {
          const u = cycle / 0.72;
          const eased = u < 0.5 ? 2 * u * u : 1 - Math.pow(-2 * u + 2, 2) / 2;
          packetX = X1 + eased * (X3 - X1);
          stampZ = 5.5;
        } else {
          // Packet rests on Pedestal 03 (X3 = +96) while the 3D corpus seal stamps down onto it!
          packetX = X3;
          const stampPhase = (cycle - 0.72) / 0.28;
          stampZ = 5.5 - Math.sin(stampPhase * Math.PI) * 5.5;
        }
      }

      if (packetEl) {
        packetEl.setAttribute('transform', k.translateAlong(P, [packetX, 0, 0]));
      }
      if (stampHeadEl) {
        stampHeadEl.setAttribute('transform', k.translateAlong(P, [0, 0, stampZ]));
      }

      frame = requestAnimationFrame(tick);
    }

    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  });
</script>

<div
  class="iso w-full p-3.5 sm:p-5"
  data-theme="opero"
  style="background-color: #dfd6c3; color: #0a0a0a; border: 2px solid #0a0a0a; box-shadow: 6px 6px 0px #0a0a0a;"
>
  <!-- 1. Top Bar: Simple Scenario Picker -->
  <div
    class="px-3.5 py-2.5 flex flex-wrap items-center justify-between gap-2 mb-3.5"
    style="background-color: #ffffff; border: 1.5px solid #0a0a0a; box-shadow: 3px 3px 0px #0a0a0a;"
  >
    <div class="flex items-center gap-2">
      <span
        class="px-2 py-0.5 font-mono text-[10px] font-bold"
        style="background-color: #0a0a0a; color: #dfd6c3;"
      >
        ALUR KERJA 3-TAHAP
      </span>
      <span
        class="px-1.5 py-0.5 font-mono text-[9px] font-bold"
        style="background-color: #dfd6c3; color: #0a0a0a; border: 1px solid #0a0a0a;"
      >
        Ilustrasi alur (contoh statis)
      </span>
      <span class="text-xs font-bold tracking-tight hidden sm:inline" style="color: #0a0a0a;">
        Pilih contoh kasus:
      </span>
    </div>

    <div class="flex flex-wrap items-center gap-1.5">
      {#each CASES as c, idx}
        <button
          type="button"
          onclick={() => (activeIdx = idx)}
          style={activeIdx === idx
            ? 'background-color: #0c249c; color: #ffffff; border: 1.5px solid #0a0a0a; box-shadow: 2px 2px 0px #0a0a0a;'
            : 'background-color: #f4f1ea; color: #0a0a0a; border: 1px solid #0a0a0a;'}
          class="brutal-press px-2.5 py-1 font-mono text-[10.5px] font-bold transition-all cursor-pointer"
        >
          {c.tab}
        </button>
      {/each}
    </div>
  </div>

  <!-- 2. Middle Visual: Animated 3-Stage Isometric Pipeline with Solid 3D Conveyor Bridge -->
  <div
    class="iso-plate select-none"
    style="background-color: #ebe5d8; border: 1.5px solid #0a0a0a; padding: 14px 10px 8px; border-radius: 0;"
  >
    <svg
      xmlns="http://www.w3.org/2000/svg"
      class="iso-svg"
      viewBox="0 0 {WIDTH} {HEIGHT}"
      role="img"
      aria-label="Simulasi 3D Tiga Tahap Pramana: Input dan Redaksi PII, Gerbang Candi Bentar, dan Segel Korpus Pramana"
    >
      <!-- Back-to-Front Painter's Order along X1 (-96) -> X2 (0) -> X3 (+96) -->
      <!-- 1. Base Pedestals & Solid 3D Conveyor Bridges -->
      {@html staticPed1}
      {@html staticBridge12}
      {@html staticPed2}
      <path
        bind:this={sakaHandEl}
        class="iso-line"
        data-tone="lit"
        data-free="start"
        d={pointerPathAt(0.4)}
        style="stroke-width: 1.4;"
      />
      {@html staticBridge23}
      {@html staticPed3}

      <!-- 2. Back Candi Bentar Half-Tower (Painted BEFORE the moving packet) -->
      <g bind:this={backTowerEl} transform={k.translateAlong(P, [0, -6.0, 0])}>
        {@html staticBackTower}
      </g>

      <!-- 3. Animated 3D Document Packet Gliding from X1 (-96) -> X2 (0) -> X3 (+96) -->
      <g bind:this={packetEl} transform={k.translateAlong(P, [0, 0, 0])}>
        {@html staticPacket}
      </g>

      <!-- 4. Animated 3D PII Scanner Bar on Pedestal 01 (Painted AFTER packet so packet passes underneath it!) -->
      <g bind:this={scannerEl} transform={k.translateAlong(P, [0, 0, 0])}>
        {@html staticScanner}
      </g>

      <!-- 5. Front Candi Bentar Half-Tower (Painted AFTER packet so packet passes between the towers!) -->
      <g bind:this={frontTowerEl} transform={k.translateAlong(P, [0, 6.0, 0])}>
        {@html staticFrontTower}
      </g>

      <!-- 6. Animated 3D Pramana Corpus Seal Cylinder on Pedestal 03 (Stamps down onto packet!) -->
      <g bind:this={stampHeadEl} transform={k.translateAlong(P, [0, 0, 5.5])}>
        {@html staticStampHead}
      </g>

      <!-- 7. Crisp Solid Callout Badges above Pedestals 01, 02, 03 -->
      {@html buildCalloutBadge(at([X1, 0, 18]), '01', 'INPUT & PRIVASI', true)}
      {@html buildCalloutBadge(
        at([X2, 0, 42]),
        '02',
        currentCase.isAbstain ? 'GERBANG DITUTUP' : 'GERBANG CANDI BENTAR',
        true
      )}
      {@html buildCalloutBadge(
        at([X3, 0, 28]),
        '03',
        currentCase.isAbstain ? 'ABSTAIN (TOLAK)' : 'SEGEL KORPUS PRAMANA',
        !currentCase.isAbstain
      )}
    </svg>
  </div>

  <!-- 3. Bottom 3-Column Step-by-Step Cards (Solid borders, zero dashed/dotted lines) -->
  <div
    class="mt-3.5 grid gap-3"
    style="display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));"
  >
    <!-- Step 01 Card -->
    <div
      class="p-3 flex flex-col justify-between"
      style="background-color: #ffffff; border: 1.5px solid #0a0a0a; box-shadow: 3px 3px 0px #0a0a0a;"
    >
      <div>
        <div class="font-mono text-[9.5px] font-bold" style="color: #0c249c;">
          {currentCase.step1.tag}
        </div>
        <div class="text-xs font-bold mt-1" style="color: #0a0a0a;">
          {currentCase.step1.title}
        </div>
        <p class="text-[11px] mt-1 leading-snug" style="color: #3a3935;">
          {currentCase.step1.desc}
        </p>
      </div>
      <div class="mt-2.5 pt-2" style="border-top: 1px solid #d4d0c5;">
        <span
          class="inline-block px-2 py-0.5 font-mono text-[9.5px] font-bold"
          style="background-color: #ebe5d8; color: #0a0a0a; border: 1px solid #0a0a0a;"
        >
          {currentCase.step1.pill}
        </span>
      </div>
    </div>

    <!-- Step 02 Card -->
    <div
      class="p-3 flex flex-col justify-between"
      style="background-color: #ffffff; border: 1.5px solid #0a0a0a; box-shadow: 3px 3px 0px #0a0a0a;"
    >
      <div>
        <div class="font-mono text-[9.5px] font-bold" style="color: #0c249c;">
          {currentCase.step2.tag}
        </div>
        <div class="text-xs font-bold mt-1" style="color: #0a0a0a;">
          {currentCase.step2.title}
        </div>
        <p class="text-[11px] mt-1 leading-snug" style="color: #3a3935;">
          {currentCase.step2.desc}
        </p>
      </div>
      <div class="mt-2.5 pt-2" style="border-top: 1px solid #d4d0c5;">
        <span
          class="inline-block px-2 py-0.5 font-mono text-[9.5px] font-bold"
          style={currentCase.isAbstain
            ? 'background-color: #0a0a0a; color: #dfd6c3;'
            : 'background-color: #ebe5d8; color: #0a0a0a; border: 1px solid #0a0a0a;'}
        >
          {currentCase.step2.pill}
        </span>
      </div>
    </div>

    <!-- Step 03 Card -->
    <div
      class="p-3 flex flex-col justify-between"
      style={currentCase.isAbstain
        ? 'background-color: #262522; color: #ffffff; border: 1.5px solid #0a0a0a; box-shadow: 3px 3px 0px #0a0a0a;'
        : 'background-color: #0c249c; color: #ffffff; border: 1.5px solid #0a0a0a; box-shadow: 3px 3px 0px #0a0a0a;'}
    >
      <div>
        <div class="font-mono text-[9.5px] font-bold" style="color: #dfd6c3;">
          {currentCase.step3.tag}
        </div>
        <div class="text-xs font-bold mt-1" style="color: #ffffff;">
          {currentCase.step3.title}
        </div>
        <p class="text-[11px] mt-1 leading-snug" style="color: rgba(255, 255, 255, 0.9);">
          {currentCase.step3.desc}
        </p>
      </div>
      <div class="mt-2.5 pt-2" style="border-top: 1px solid rgba(255, 255, 255, 0.25);">
        <span
          class="inline-block px-2 py-0.5 font-mono text-[9.5px] font-bold"
          style="background-color: #dfd6c3; color: #0a0a0a;"
        >
          {currentCase.step3.pill}
        </span>
      </div>
    </div>
  </div>
</div>
