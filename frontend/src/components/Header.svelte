<script>
  let { currentPath = '/', navigate = (p) => {}, overlay = false } = $props();

  let scrollY = $state(0);
  let lastScrollY = $state(0);
  let scrollDelta = $state(0);
  let isScrollingDown = $state(false);
  let isScrolled = $derived(scrollY > 15);

  const NAV_ITEMS = [
    { path: '/', label: 'Home' },
    { path: '/trip-brief', label: 'Trip Brief' },
    { path: '/context-note', label: 'Context Note' },
    { path: '/corpus', label: 'Korpus JDIH' }
  ];

  let scrollTimeout;
  function onScroll() {
    const current = window.scrollY;
    const diff = current - lastScrollY;
    if (Math.abs(diff) > 2) {
      isScrollingDown = diff > 0;
      scrollDelta = Math.max(-8, Math.min(8, diff * 0.25));
    }
    lastScrollY = current;

    clearTimeout(scrollTimeout);
    scrollTimeout = setTimeout(() => {
      scrollDelta = 0;
    }, 140);
  }
</script>

<svelte:window bind:scrollY={scrollY} onscroll={onScroll} />

{#if !overlay}
  <!-- Structural Top Spacer in document flow for workspace routes -->
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

<!-- Smooth Floating Following Navbar -->
<div
  class="fixed top-0 inset-x-0 z-40 flex justify-center px-4 pointer-events-none transition-all duration-300 ease-out"
  style={overlay
    ? `padding-top: ${isScrolled ? '14px' : '26px'};`
    : `padding-top: ${isScrolled ? '10px' : '15px'};`}
>
  <nav
    style="background-color: rgba(255, 255, 255, 0.94); backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px); color: #0a0a0a; max-width: 580px; width: 100%; border: 1.5px solid #0a0a0a; border-radius: 4px; box-shadow: {isScrolled ? '4px 4px 0px #0a0a0a' : '2.5px 2.5px 0px #0a0a0a'}; transform: translateY({scrollDelta}px);"
    class="pointer-events-auto flex items-center justify-between pl-4 pr-1.5 py-1.5 transition-all duration-200 ease-out"
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

    <div class="flex items-center gap-5 sm:gap-7 text-[12px] font-medium">
      {#each NAV_ITEMS as item}
        <a
          href={item.path}
          onclick={(e) => { e.preventDefault(); navigate(item.path); }}
          style={currentPath === item.path ? 'color: #0c249c; font-weight: 600;' : 'color: #3a3935;'}
          class="hover:opacity-70 transition-opacity"
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
