<script>
  let { currentPath = '/', navigate = (p) => {}, overlay = false } = $props();

  const NAV_ITEMS = [
    { path: '/', label: 'Home' },
    { path: '/trip-brief', label: 'Trip Brief' },
    { path: '/context-note', label: 'Context Note' },
    { path: '/corpus', label: 'Korpus JDIH' }
  ];
</script>

{#if overlay}
  <!-- Floating Top Navbar inside Hero Artwork -->
  <div class="absolute top-4 sm:top-5 inset-x-0 z-30 flex justify-center px-4 pointer-events-none">
    <nav
      style="background-color: #ffffff; color: #0a0a0a; max-width: 580px; width: 100%; border: 1px solid #d4d0c5; border-radius: 4px;"
      class="pointer-events-auto flex items-center justify-between pl-4 pr-1.5 py-1.5"
    >
      <a
        href="/"
        onclick={(e) => { e.preventDefault(); navigate('/'); }}
        class="flex items-center gap-2 font-semibold text-[13px] tracking-tight pr-4"
        style="color: #0a0a0a;"
      >
        <!-- Clean Sketchy Scissor-Cut Swirl Logo -->
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
        onclick={() => navigate('/trip-brief')}
        aria-label="Buka Trip Brief"
        style="background-color: #0c249c; color: #ffffff; border-radius: 2px;"
        class="opero-arrow-btn ml-4 w-7 h-7 flex items-center justify-center text-xs hover:opacity-90 transition-all cursor-pointer"
      >
        →
      </button>
    </nav>
  </div>
{:else}
  <!-- Centered Navbar on Workspace Routes -->
  <header
    style="background-color: #e6e4de; border-bottom: 1px solid #cdc9be;"
    class="sticky top-0 z-40 w-full"
  >
    <div
      class="mx-auto px-4 py-3 flex items-center justify-center"
      style="max-width: 1360px; width: 100%; border-left: 1px solid #cdc9be; border-right: 1px solid #cdc9be;"
    >
      <nav
        style="background-color: #ffffff; color: #0a0a0a; max-width: 580px; width: 100%; border: 1px solid #d4d0c5; border-radius: 4px;"
        class="flex items-center justify-between pl-4 pr-1.5 py-1.5"
      >
        <a
          href="/"
          onclick={(e) => { e.preventDefault(); navigate('/'); }}
          style="color: #0a0a0a;"
          class="flex items-center gap-2 font-semibold text-[13px] tracking-tight pr-4"
        >
          <!-- Clean Sketchy Scissor-Cut Swirl Logo -->
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
              class="py-1 transition-opacity hover:opacity-70"
            >
              {item.label}
            </a>
          {/each}
        </div>

        <button
          type="button"
          onclick={() => navigate(currentPath === '/trip-brief' ? '/context-note' : '/trip-brief')}
          style="background-color: #0c249c; color: #ffffff; border-radius: 2px;"
          class="opero-arrow-btn ml-4 w-7 h-7 flex items-center justify-center text-xs cursor-pointer"
          title={currentPath === '/trip-brief' ? 'Buka Context Note' : 'Buka Trip Brief'}
        >
          →
        </button>
      </nav>
    </div>
  </header>
{/if}
