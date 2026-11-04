<script>
  import { onMount } from 'svelte';
  import Header from './components/Header.svelte';
  import LandingView from './components/LandingView.svelte';
  import ModeTripBrief from './components/ModeTripBrief.svelte';
  import ModeContextNote from './components/ModeContextNote.svelte';
  import CorpusExplorer from './components/CorpusExplorer.svelte';
  import CorpusDrawer from './components/CorpusDrawer.svelte';

  const VALID_ROUTES = ['/', '/trip-brief', '/context-note', '/corpus'];

  function normalizePath(p) {
    const clean = (p || '/').replace(/\/+$/, '') || '/';
    return VALID_ROUTES.includes(clean) ? clean : '/';
  }

  let currentPath = $state(normalizePath(typeof window !== 'undefined' ? window.location.pathname : '/'));
  let selectedDoc = $state(null);
  let routeTransitionKey = $state(0);
  let showShutter = $state(false);

  function navigate(path) {
    const next = normalizePath(path);
    if (next !== currentPath) {
      showShutter = true;
      window.history.pushState({}, '', next);
      currentPath = next;
      routeTransitionKey += 1;
      window.scrollTo({ top: 0, behavior: 'instant' });
      setTimeout(() => {
        showShutter = false;
      }, 240);
    }
  }

  onMount(() => {
    const onPopState = () => {
      currentPath = normalizePath(window.location.pathname);
      routeTransitionKey += 1;
    };
    const onKeyDown = (e) => {
      if (e.key === 'Escape' && selectedDoc) selectedDoc = null;
    };
    window.addEventListener('popstate', onPopState);
    window.addEventListener('keydown', onKeyDown);
    return () => {
      window.removeEventListener('popstate', onPopState);
      window.removeEventListener('keydown', onKeyDown);
    };
  });

  function handleOpenDoc(item) {
    selectedDoc = item;
  }

  function handleCloseDoc() {
    selectedDoc = null;
  }
</script>

<div class="min-h-screen flex flex-col font-sans" style="background-color: #e6e4de; color: #0a0a0a; width: 100%; max-width: 100vw; overflow-x: hidden;">
  <!-- Hairline Indicator on Page Switch (Zero screen shake) -->
  {#if showShutter}
    <div class="fixed top-0 inset-x-0 z-50 pointer-events-none">
      <div class="h-[2px] w-full animate-shutter-bar" style="background-color: #0c249c;"></div>
    </div>
  {/if}

  <!-- On '/' the compact nav bar floats directly inside the hero artwork; on workspace routes it docks at top -->
  {#if currentPath !== '/'}
    <Header {currentPath} {navigate} overlay={false} />
  {/if}

  <!-- Route Views with smooth opacity fade (No translateY jump) -->
  <main class="flex-1 w-full" style="max-width: 100vw; overflow-x: hidden;">
    {#key routeTransitionKey}
      <div class="animate-page-fade w-full">
        {#if currentPath === '/'}
          <LandingView {navigate} onOpenDoc={handleOpenDoc} />
        {:else if currentPath === '/trip-brief'}
          <ModeTripBrief onOpenDoc={handleOpenDoc} />
        {:else if currentPath === '/context-note'}
          <ModeContextNote onOpenDoc={handleOpenDoc} />
        {:else if currentPath === '/corpus'}
          <CorpusExplorer />
        {/if}
      </div>
    {/key}
  </main>

  <!-- Architectural Footer -->
  <footer
    class="w-full mx-auto text-xs"
    style="max-w-[1360px]; color: #5c5b57; border-left: 1px solid #cdc9be; border-right: 1px solid #cdc9be; border-top: 1px solid #cdc9be;"
  >
    <div
      class="px-6 sm:px-10 py-6 flex flex-col sm:flex-row items-center justify-between gap-4"
      style="background-color: #e6e4de;"
    >
      <div class="flex items-center gap-3">
        <!-- Clean Sketchy Scissor-Cut Swirl Logo -->
        <img
          src="/assets/pramana_logo.svg?v=5"
          alt="Pramana Logo"
          class="w-4 h-4 object-contain shrink-0"
        />
        <span class="font-semibold text-xs" style="color: #0a0a0a;">Pramana</span>
        <span style="color: #cdc9be;">|</span>
        <span>Bali DigiFest 2026 — AI Web Innovation Challenge</span>
      </div>
      <div class="flex items-center gap-5 font-mono text-[11px]" style="color: #5c5b57;">
        <a href="/" onclick={(e) => { e.preventDefault(); navigate('/'); }} class="hover:underline">/</a>
        <a href="/trip-brief" onclick={(e) => { e.preventDefault(); navigate('/trip-brief'); }} class="hover:underline">/trip-brief</a>
        <a href="/context-note" onclick={(e) => { e.preventDefault(); navigate('/context-note'); }} class="hover:underline">/context-note</a>
        <a href="/corpus" onclick={(e) => { e.preventDefault(); navigate('/corpus'); }} class="hover:underline">/corpus</a>
      </div>
    </div>
  </footer>

  <!-- Interactive Verbatim Statute Drawer -->
  <CorpusDrawer item={selectedDoc} onClose={handleCloseDoc} />
</div>
