<script>
  import { onMount } from 'svelte';
  import { i18n } from './lib/i18n.svelte.js';
  import Header from './components/Header.svelte';
  import LandingView from './components/LandingView.svelte';
  import ModeTripBrief from './components/ModeTripBrief.svelte';
  import ModeContextNote from './components/ModeContextNote.svelte';
  import CorpusExplorer from './components/CorpusExplorer.svelte';
  import CorpusDrawer from './components/CorpusDrawer.svelte';
  import SmartGateView from './components/SmartGateView.svelte';
  import SettingsView from './components/SettingsView.svelte';

  const STATIC_ROUTES = ['/', '/trip-brief', '/context-note', '/corpus', '/totem', '/settings'];
  const TOTEM_ROUTE = /^\/totem\/[a-z0-9]+(?:-[a-z0-9]+)*$/;

  function normalizePath(p) {
    const clean = (p || '/').replace(/\/+$/, '') || '/';
    if (STATIC_ROUTES.includes(clean) || TOTEM_ROUTE.test(clean)) return clean;
    return '/';
  }

  let currentPath = $state(normalizePath(typeof window !== 'undefined' ? window.location.pathname : '/'));
  let zoneId = $derived(
    currentPath.startsWith('/totem/') ? currentPath.split('/')[2] : null
  );
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

  <!-- Fixed Top Navbar (follows scroll on all pages) -->
  <Header {currentPath} {navigate} overlay={currentPath === '/'} />

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
        {:else if currentPath === '/totem' || currentPath.startsWith('/totem/')}
          <SmartGateView
            {zoneId}
            {navigate}
            onOpenDoc={handleOpenDoc}
          />
        {:else if currentPath === '/corpus'}
          <CorpusExplorer />
        {:else if currentPath === '/settings'}
          <SettingsView />
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
          src="/assets/pramana_logo.svg?v=6"
          alt="Pramana Logo"
          class="w-5 h-5 object-contain shrink-0"
        />
        <span class="font-semibold text-xs" style="color: #0a0a0a;">Pramana</span>
      </div>
      <div class="flex flex-wrap items-center justify-center sm:justify-start gap-x-4 gap-y-2 font-mono text-[11px]" style="color: #5c5b57;">
        <a href="/" onclick={(e) => { e.preventDefault(); navigate('/'); }} class="hover:underline">/</a>
        <a href="/trip-brief" onclick={(e) => { e.preventDefault(); navigate('/trip-brief'); }} class="hover:underline">/trip-brief</a>
        <a href="/context-note" onclick={(e) => { e.preventDefault(); navigate('/context-note'); }} class="hover:underline">/context-note</a>
        <a href="/totem" onclick={(e) => { e.preventDefault(); navigate('/totem'); }} class="hover:underline">/totem</a>
        <a href="/corpus" onclick={(e) => { e.preventDefault(); navigate('/corpus'); }} class="hover:underline">/corpus</a>
        <a href="/settings" onclick={(e) => { e.preventDefault(); navigate('/settings'); }} class="hover:underline">/settings</a>
      </div>
    </div>
    <div
      class="px-6 sm:px-10 pb-6 text-[11px] leading-relaxed"
      style="background-color: #e6e4de; color: #5c5b57;"
    >
      <strong>{i18n.lang === 'en' ? 'Note:' : 'Catatan:'}</strong> {i18n.lang === 'en'
        ? 'Pramana is an AI legal context assistance system based on a verified local corpus. System outputs do not constitute official legal advice and do not supersede statutory texts published on JDIH or official authorities. Citations are verified against the Pramana corpus, not re-verified real-time against JDIH servers.'
        : 'Pramana adalah sistem asistensi konteks aturan pariwisata berbasis korpus lokal. Keluaran sistem bukan nasihat hukum resmi dan tidak menggantikan teks peraturan pada JDIH atau instansi berwenang. Kutipan diverifikasi terhadap korpus Pramana, bukan verifikasi langsung real-time ke server JDIH.'}
    </div>
  </footer>

  <!-- Interactive Verbatim Statute Drawer -->
  <CorpusDrawer item={selectedDoc} onClose={handleCloseDoc} />
</div>
