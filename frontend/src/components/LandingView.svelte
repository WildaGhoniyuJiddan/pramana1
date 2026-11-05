<script>
  import AnatomyRig from './AnatomyRig.svelte';
  import { i18n, DICT } from '../lib/i18n.svelte.js';

  let { navigate = (path) => {}, onOpenDoc = (doc) => {} } = $props();

  let landing = $derived(DICT[i18n.lang].landing);

  // Distinct institutional & statutory wordmarks for the single-row Hero Ribbon
  let heroInstitutions = $derived([
    { id: 'jdih', name: i18n.lang === 'en' ? 'BPK JDIH & Official Sources' : 'JDIH BPK & Sumber Resmi', icon: 'gate' },
    { id: 'imigrasi', name: i18n.lang === 'en' ? 'Immigration Law Art. 75' : 'UU Imigrasi Pasal 75', icon: 'compass' },
    { id: 'perda5', name: i18n.lang === 'en' ? 'Bali Regional Reg 5/2020' : 'Perda Bali No. 5/2020', icon: 'dharma' },
    { id: 'segub4', name: i18n.lang === 'en' ? 'Governor Circular 4/2023 & 7/2025' : 'SE Gubernur 4/2023 & 7/2025', icon: 'scroll' },
    { id: 'phdi', name: i18n.lang === 'en' ? 'PHDI & Customary Village Council' : 'PHDI & Majelis Desa Adat', icon: 'lotus' },
    { id: 'lovebali', name: i18n.lang === 'en' ? 'Levy Bylaw 6/2023 jo. 2/2025' : 'Perda Pungutan 6/2023 jo. 2/2025', icon: 'diamond' },
    { id: 'uu28', name: i18n.lang === 'en' ? 'Public Domain Law 28/2014' : 'Domain Publik UU 28/2014', icon: 'book' }
  ]);
</script>

<div class="w-full" style="background-color: #e6e4de; color: #0a0a0a; width: 100%; max-width: 100vw; overflow-x: hidden;">
  <div
    class="w-full mx-auto"
    style="max-width: 1360px; width: 100%; border-left: 1px solid #cdc9be; border-right: 1px solid #cdc9be; overflow: hidden;"
  >
    <!-- 1. HERO ARTWORK SECTION -->
    <section class="p-3 sm:p-4">
      <div
        class="relative w-full h-[540px] sm:h-[640px] lg:h-[700px] overflow-hidden"
        style="border-radius: 8px; background-color: #091e8a; border: 1px solid #b8b3a6;"
      >
        <img
          src="/assets/opero_bali_hero.jpg"
          alt="Pointillist Candi Bentar Bali Night Sky"
          class="w-full h-full object-cover block"
          style="object-position: center 26%; transform: scale(1.02);"
        />

        <div
          class="absolute inset-x-0 bottom-0 h-28 pointer-events-none"
          style="background: linear-gradient(to top, rgba(226, 219, 203, 0.86) 0%, rgba(226, 219, 203, 0.32) 55%, rgba(226, 219, 203, 0) 100%);"
        ></div>

        <div
          class="absolute bottom-4 left-0 right-0 z-20 px-2"
          style="width: 100%; max-width: 100%; overflow: hidden;"
        >
          <div class="opero-marquee-track gap-3.5">
            {#each [...heroInstitutions, ...heroInstitutions] as item}
              <button
                type="button"
                onclick={() => navigate('/corpus')}
                style="background-color: rgba(233, 228, 216, 0.92); backdrop-filter: blur(8px); color: #0a0a0a; border-radius: 2px; border: 1px solid rgba(10, 10, 10, 0.2);"
                class="h-11 px-5 shrink-0 flex items-center justify-center gap-2.5 hover:bg-white transition-colors cursor-pointer"
              >
                {#if item.icon === 'gate'}
                  <svg class="w-4 h-4 shrink-0" viewBox="0 0 18 18" fill="none">
                    <path d="M3 15V5l4 3v7H3zm12 0V5l-4 3v7h4z" fill="#0a0a0a" />
                  </svg>
                {:else if item.icon === 'compass'}
                  <svg class="w-4 h-4 shrink-0" viewBox="0 0 18 18" fill="none">
                    <circle cx="9" cy="9" r="6.5" stroke="#0a0a0a" stroke-width="1.6" />
                    <polygon points="9,4.5 11,9 9,13.5 7,9" fill="#0a0a0a" />
                  </svg>
                {:else if item.icon === 'dharma'}
                  <svg class="w-4 h-4 shrink-0" viewBox="0 0 18 18" fill="none">
                    <circle cx="9" cy="9" r="5.5" stroke="#0a0a0a" stroke-width="1.6" />
                    <path d="M9 2v14M2 9h14M4 4l10 10M14 4L4 14" stroke="#0a0a0a" stroke-width="1.2" />
                  </svg>
                {:else if item.icon === 'scroll'}
                  <svg class="w-4 h-4 shrink-0" viewBox="0 0 18 18" fill="none">
                    <rect x="3.5" y="3" width="11" height="12" stroke="#0a0a0a" stroke-width="1.6" />
                    <path d="M6.5 7h5M6.5 10.5h3.5" stroke="#0a0a0a" stroke-width="1.5" />
                  </svg>
                {:else if item.icon === 'lotus'}
                  <svg class="w-4 h-4 shrink-0" viewBox="0 0 18 18" fill="none">
                    <path d="M9 3C6.5 6.5 6.5 11 9 14c2.5-3 2.5-7.5 0-11z" stroke="#0a0a0a" stroke-width="1.5" />
                    <path d="M3.5 8c2 0 4.5 2 5.5 6-3-0.5-5.5-2.5-5.5-6zm11 0c-2 0-4.5 2-5.5 6 3-0.5 5.5-2.5 5.5-6z" stroke="#0a0a0a" stroke-width="1.4" />
                  </svg>
                {:else if item.icon === 'diamond'}
                  <svg class="w-4 h-4 shrink-0" viewBox="0 0 18 18" fill="none">
                    <rect x="9" y="2.5" width="9.2" height="9.2" transform="rotate(45 9 2.5)" stroke="#0a0a0a" stroke-width="1.6" />
                  </svg>
                {:else}
                  <svg class="w-4 h-4 shrink-0" viewBox="0 0 18 18" fill="none">
                    <path d="M3 4.5h5a2 2 0 0 1 2 2v8a1.5 1.5 0 0 0-1.5-1.5H3v-8.5zm12 0h-5a2 2 0 0 0-2 2v8a1.5 1.5 0 0 1 1.5-1.5H15v-8.5z" stroke="#0a0a0a" stroke-width="1.5" />
                  </svg>
                {/if}
                <span class="text-[12.5px] font-semibold tracking-tight whitespace-nowrap" style="color: #0a0a0a;">
                  {item.name}
                </span>
              </button>
            {/each}
          </div>
        </div>
      </div>
    </section>

    <!-- 2. HEADLINE SECTION -->
    <section
      class="px-5 sm:px-10 pt-8 sm:pt-11 pb-12 sm:pb-16"
      style="border-bottom: 1px solid #cdc9be;"
    >
      <h1 class="opero-h1 text-[38px] sm:text-[56px] lg:text-[66px] max-w-4xl">
        The AI <span class="opero-serif">legal context</span> layer<br />
        for Bali tourism &amp; governance.
      </h1>

      <div class="mt-8 sm:mt-10 flex flex-wrap items-center gap-4">
        <button
          type="button"
          onclick={() => navigate('/trip-brief')}
          style="background-color: #0c249c; color: #ffffff; padding: 3px; border: 1.5px solid #0a0a0a; box-shadow: 3px 3px 0px #0a0a0a;"
          class="opero-split-btn brutal-press inline-flex items-center text-xs font-medium cursor-pointer"
        >
          <span class="px-5 py-2.5">{landing.tripBtn}</span>
          <span
            style="background-color: #dfd8c8; color: #0a0a0a;"
            class="opero-arrow-box w-8 h-8 flex items-center justify-center font-mono text-xs font-bold"
          >
            ↗
          </span>
        </button>

        <button
          type="button"
          onclick={() => navigate('/context-note')}
          style="background-color: #ffffff; color: #0a0a0a; padding: 3px; border: 1.5px solid #0a0a0a; box-shadow: 3px 3px 0px #0a0a0a;"
          class="opero-split-btn brutal-press inline-flex items-center text-xs font-medium cursor-pointer"
        >
          <span class="px-5 py-2.5">{landing.contextBtn}</span>
          <span
            style="background-color: #0c249c; color: #ffffff;"
            class="opero-arrow-box w-8 h-8 flex items-center justify-center font-mono text-xs font-bold"
          >
            ↗
          </span>
        </button>
      </div>
    </section>

    <!-- 3. ANATOMY ISOMETRIC ARCHITECTURAL STAGE -->
    <section class="p-3 sm:p-5" style="border-bottom: 1px solid #cdc9be;">
      <div
        class="relative w-full p-4 sm:p-7 overflow-hidden"
        style="background-color: #0b2299; color: #ffffff; border: 1.5px solid #0a0a0a; box-shadow: 5px 5px 0px #0a0a0a;"
      >
        <svg
          class="absolute inset-0 w-full h-full pointer-events-none opacity-15"
          viewBox="0 0 1200 600"
          preserveAspectRatio="xMidYMid slice"
          fill="none"
        >
          <g stroke="#dfd6c3" stroke-width="1">
            <line x1="0" y1="120" x2="1200" y2="120" />
            <line x1="0" y1="300" x2="1200" y2="300" />
            <line x1="0" y1="480" x2="1200" y2="480" />
            <line x1="300" y1="0" x2="300" y2="600" />
            <line x1="600" y1="0" x2="600" y2="600" />
            <line x1="900" y1="0" x2="900" y2="600" />
            <line x1="450" y1="0" x2="1200" y2="450" />
            <line x1="1200" y1="150" x2="450" y2="600" />
          </g>
        </svg>

        <div class="relative z-10 opero-cobalt-grid">
          <!-- LEFT: ANATOMY INTERACTIVE ISOMETRIC COMPARATOR RIG -->
          <div class="min-w-0 w-full">
            <AnatomyRig />
          </div>

          <!-- RIGHT: EDITORIAL COPY INSIDE COBALT STAGE -->
          <div class="min-w-0 w-full space-y-5 px-1 sm:px-2">
            <div
              class="w-11 h-11 flex items-center justify-center"
              style="background-color: #dfd6c3; color: #0a0a0a; border: 1.5px solid #0a0a0a; box-shadow: 3px 3px 0px #0a0a0a;"
            >
              <svg class="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="#0a0a0a" stroke-width="2">
                <polygon points="12,3 20,7.5 12,12 4,7.5" fill="#ffffff" />
                <polyline points="4,12 12,16.5 20,12" />
                <polyline points="4,16.5 12,21 20,16.5" />
              </svg>
            </div>

            <h2
              class="text-2xl sm:text-3xl font-normal tracking-tight leading-tight break-words"
              style="color: #ffffff; letter-spacing: -0.03em;"
            >
              {landing.archTitle}
            </h2>

            <p
              class="text-xs sm:text-[13.5px] leading-relaxed break-words"
              style="color: rgba(255, 255, 255, 0.88);"
            >
              {landing.archDesc}
            </p>

            <div class="pt-1 flex flex-wrap gap-3">
              <button
                type="button"
                onclick={() => navigate('/corpus')}
                style="background-color: #dfd6c3; color: #0a0a0a; border: 1.5px solid #0a0a0a; box-shadow: 3px 3px 0px #0a0a0a;"
                class="brutal-press px-4 py-2.5 text-xs font-semibold hover:bg-white transition-colors cursor-pointer"
              >
                {landing.openCorpusBtn}
              </button>
              <button
                type="button"
                onclick={() => navigate('/trip-brief')}
                style="background-color: #ffffff; color: #0a0a0a; border: 1.5px solid #0a0a0a; box-shadow: 3px 3px 0px #0a0a0a;"
                class="brutal-press px-4 py-2.5 text-xs font-semibold hover:bg-stone transition-colors cursor-pointer"
              >
                {i18n.lang === 'en' ? 'Open Simulator →' : 'Buka Simulasi →'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 4. CAPABILITIES SECTION -->
    <section class="px-5 sm:px-10 py-12 sm:py-16">
      <div
        class="inline-flex items-center text-xs font-medium mb-5"
        style="background-color: #0c249c; color: #ffffff; padding: 2px; border: 1.5px solid #0a0a0a; box-shadow: 2px 2px 0px #0a0a0a;"
      >
        <span
          style="background-color: #dfd6c3; color: #0a0a0a;"
          class="w-5 h-5 flex items-center justify-center text-[10px] font-bold"
        >
          ✦
        </span>
        <span class="px-3 py-0.5 text-[11px] font-semibold">Capabilities</span>
      </div>

      <h2 class="opero-h1 text-[32px] sm:text-[48px] lg:text-[56px] max-w-2xl">
        Build <span class="opero-serif">Workflows</span> That<br />
        Match Real Regulations
      </h2>

      <div class="mt-10 grid grid-cols-1 md:grid-cols-3 gap-6">
        <!-- Card 1: Trip Brief -->
        <div
          class="brutal-card p-6 flex flex-col justify-between space-y-6"
          style="background-color: #f3f1eb;"
        >
          <div class="space-y-3">
            <div class="flex items-center justify-between">
              <span class="font-mono text-[10px] font-bold px-2 py-0.5" style="background-color: #dfd6c3; color: #0a0a0a; border: 1px solid #0a0a0a;">
                01 // PREVENTIVE BRIEF
              </span>
              <span class="font-mono text-xs font-bold" style="color: #0c249c;">/trip-brief</span>
            </div>
            <h3 class="text-lg font-medium tracking-tight pt-1" style="color: #0a0a0a;">
              {landing.card1Title}
            </h3>
            <p class="text-xs leading-relaxed" style="color: #3a3935;">
              {landing.card1Desc}
            </p>
          </div>

          <button
            type="button"
            onclick={() => navigate('/trip-brief')}
            style="background-color: #0c249c; color: #ffffff; padding: 2px; border: 1.5px solid #0a0a0a; box-shadow: 3px 3px 0px #0a0a0a;"
            class="opero-split-btn brutal-press w-full inline-flex items-center justify-between text-xs font-medium cursor-pointer"
          >
            <span class="px-3.5 py-2">{landing.card1Btn}</span>
            <span
              style="background-color: #dfd8c8; color: #0a0a0a;"
              class="opero-arrow-box w-7 h-7 flex items-center justify-center font-mono text-xs font-bold"
            >
              ↗
            </span>
          </button>
        </div>

        <!-- Card 2: Context Note -->
        <div
          class="brutal-card p-6 flex flex-col justify-between space-y-6"
          style="background-color: #f3f1eb;"
        >
          <div class="space-y-3">
            <div class="flex items-center justify-between">
              <span class="font-mono text-[10px] font-bold px-2 py-0.5" style="background-color: #dfd6c3; color: #0a0a0a; border: 1px solid #0a0a0a;">
                02 // PUBLIC CONTEXT
              </span>
              <span class="font-mono text-xs font-bold" style="color: #0c249c;">/context-note</span>
            </div>
            <h3 class="text-lg font-medium tracking-tight pt-1" style="color: #0a0a0a;">
              {landing.card2Title}
            </h3>
            <p class="text-xs leading-relaxed" style="color: #3a3935;">
              {landing.card2Desc}
            </p>
          </div>

          <button
            type="button"
            onclick={() => navigate('/context-note')}
            style="background-color: #ffffff; color: #0a0a0a; padding: 2px; border: 1.5px solid #0a0a0a; box-shadow: 3px 3px 0px #0a0a0a;"
            class="opero-split-btn brutal-press w-full inline-flex items-center justify-between text-xs font-medium cursor-pointer"
          >
            <span class="px-3.5 py-2">{landing.card2Btn}</span>
            <span
              style="background-color: #0c249c; color: #ffffff;"
              class="opero-arrow-box w-7 h-7 flex items-center justify-center font-mono text-xs font-bold"
            >
              ↗
            </span>
          </button>
        </div>

        <!-- Card 3: Deterministic Calendar Saka 1948 -->
        <div
          class="brutal-card p-6 flex flex-col justify-between space-y-6"
          style="background-color: #dfd6c3;"
        >
          <div class="space-y-3">
            <div class="flex items-center justify-between">
              <span class="font-mono text-[10px] font-bold px-2 py-0.5" style="background-color: #0c249c; color: #ffffff; border: 1px solid #0a0a0a;">
                03 // KALENDER SAKA
              </span>
              <span class="font-mono text-xs font-bold" style="color: #0a0a0a;">2026</span>
            </div>
            <h3 class="text-lg font-medium tracking-tight pt-1" style="color: #0a0a0a;">
              {landing.card3Title}
            </h3>
            <div class="space-y-1.5 pt-1 text-xs" style="color: #0a0a0a;">
              <div class="flex justify-between py-1 px-2.5 bg-white" style="border: 1px solid #0a0a0a;">
                <span class="font-mono font-bold">18 Mar</span>
                <span>{landing.ogoh}</span>
              </div>
              <div class="flex justify-between py-1 px-2.5 font-semibold" style="background-color: #0c249c; color: #ffffff; border: 1px solid #0a0a0a;">
                <span class="font-mono">19 Mar</span>
                <span>{landing.nyepi}</span>
              </div>
              <div class="flex justify-between py-1 px-2.5 bg-white" style="border: 1px solid #0a0a0a;">
                <span class="font-mono font-bold">17 Jun</span>
                <span>{landing.galungan}</span>
              </div>
              <div class="flex justify-between py-1 px-2.5 bg-white" style="border: 1px solid #0a0a0a;">
                <span class="font-mono font-bold">27 Jun</span>
                <span>{landing.kuningan}</span>
              </div>
            </div>
          </div>

          <button
            type="button"
            onclick={() => navigate('/corpus')}
            style="background-color: #0a0a0a; color: #ffffff; padding: 2px; border: 1.5px solid #0a0a0a; box-shadow: 3px 3px 0px #0c249c;"
            class="opero-split-btn brutal-press w-full inline-flex items-center justify-between text-xs font-medium cursor-pointer"
          >
            <span class="px-3.5 py-2">{landing.card3Btn}</span>
            <span
              style="background-color: #dfd8c8; color: #0a0a0a;"
              class="opero-arrow-box w-7 h-7 flex items-center justify-center font-mono text-xs font-bold"
            >
              ↗
            </span>
          </button>
        </div>
      </div>
    </section>
  </div>
</div>
