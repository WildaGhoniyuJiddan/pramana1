<script>
  import { i18n, DICT } from '../lib/i18n.svelte.js';

  let { currentPath = '/', navigate = (p) => {}, overlay = false } = $props();

  let scrollY = $state(0);
  let isScrolled = $derived(scrollY > 15);

  let nav = $derived(DICT[i18n.lang].nav);

  let navItems = $derived([
    { path: '/', label: nav.home },
    { path: '/trip-brief', label: nav.tripBrief },
    { path: '/context-note', label: nav.contextNote },
    { path: '/totem', label: nav.gate },
    { path: '/corpus', label: nav.corpus }
  ]);

  function isActive(path) {
    if (path === '/totem') {
      return currentPath === '/totem' || currentPath.startsWith('/totem/');
    }
    return currentPath === path;
  }
</script>

<svelte:window bind:scrollY={scrollY} />

{#if !overlay}
  <!-- Structural Spacer in document flow so top content is never clipped -->
  <div
    class="w-full"
    style="background-color: #e6e4de; border-bottom: 1px solid #cdc9be; height: 62px;"
  >
    <div
      class="mx-auto h-full"
      style="max-width: 1360px; width: 100%; border-left: 1px solid #cdc9be; border-right: 1px solid #cdc9be;"
    ></div>
  </div>
{/if}

<!-- Smooth Floating Navbar (Rock-solid, zero jitter, pure CSS transition) -->
<div
  class="fixed inset-x-0 z-40 flex justify-center px-4 pointer-events-none transition-all duration-300 ease-out"
  style="top: {overlay ? (isScrolled ? '12px' : '22px') : '12px'};"
>
  <nav
    style="background-color: rgba(255, 255, 255, {isScrolled ? '0.96' : '0.92'}); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); color: #0a0a0a; max-width: 680px; width: 100%; border: 1.5px solid #0a0a0a; border-radius: 4px; box-shadow: {isScrolled ? '4px 4px 0px #0a0a0a' : '3px 3px 0px #0a0a0a'};"
    class="pointer-events-auto flex items-center justify-between pl-4 pr-1.5 py-1.5 transition-all duration-300 ease-out"
  >
    <a
      href="/"
      onclick={(e) => { e.preventDefault(); navigate('/'); }}
      class="flex items-center gap-2 font-semibold text-[13px] tracking-tight pr-4"
      style="color: #0a0a0a;"
    >
      <img
        src="/assets/pramana_logo.svg?v=5"
        alt="Pramana Logo"
        class="w-4 h-4 object-contain shrink-0"
      />
      <span>Pramana</span>
    </a>

    <div class="flex items-center gap-3 sm:gap-5 text-[11px] sm:text-[12px] font-medium">
      {#each navItems as item}
        <a
          href={item.path}
          onclick={(e) => { e.preventDefault(); navigate(item.path); }}
          style={isActive(item.path) ? 'color: #0c249c; font-weight: 600;' : 'color: #3a3935;'}
          class="hover:opacity-70 transition-opacity whitespace-nowrap"
        >
          {item.label}
        </a>
      {/each}

      <a
        href="/settings"
        onclick={(e) => { e.preventDefault(); navigate('/settings'); }}
        style={currentPath === '/settings' ? 'color: #0c249c;' : 'color: #5c5952;'}
        class="hover:opacity-70 transition-opacity p-1 flex items-center justify-center cursor-pointer"
        title={nav.settings}
        aria-label="Settings"
      >
        <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="3"></circle>
          <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
        </svg>
      </a>
    </div>

    <button
      type="button"
      onclick={() => navigate(currentPath === '/trip-brief' ? '/context-note' : '/trip-brief')}
      aria-label="Navigasi mode"
      style="background-color: #0c249c; color: #ffffff; border-radius: 2px;"
      class="opero-arrow-btn ml-4 w-7 h-7 flex items-center justify-center text-xs hover:opacity-90 transition-all cursor-pointer"
      title={currentPath === '/trip-brief' ? 'Buka Context Note' : 'Buka Trip Brief'}
    >
      →
    </button>
  </nav>
</div>
