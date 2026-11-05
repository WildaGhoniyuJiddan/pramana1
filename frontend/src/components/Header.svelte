<script>
  let { currentPath = '/', navigate = (p) => {}, overlay = false } = $props();

  let scrollY = $state(0);
  let isScrolled = $derived(scrollY > 15);

  const NAV_ITEMS = [
    { path: '/', label: 'Home' },
    { path: '/trip-brief', label: 'Trip Brief' },
    { path: '/context-note', label: 'Context Note' },
    { path: '/totem', label: 'Gate' },
    { path: '/corpus', label: 'Korpus Pramana' }
  ];

  function isActive(item) {
    if (item.path === '/totem') {
      return currentPath === '/totem' || currentPath.startsWith('/totem/');
    }
    return currentPath === item.path;
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
      {#each NAV_ITEMS as item}
        <a
          href={item.path}
          onclick={(e) => { e.preventDefault(); navigate(item.path); }}
          style={isActive(item) ? 'color: #0c249c; font-weight: 600;' : 'color: #3a3935;'}
          class="hover:opacity-70 transition-opacity whitespace-nowrap"
        >
          {item.label}
        </a>
      {/each}
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
