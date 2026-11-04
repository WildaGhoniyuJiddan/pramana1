<script>
  import Header from './components/Header.svelte';
  import ModeTripBrief from './components/ModeTripBrief.svelte';
  import ModeContextNote from './components/ModeContextNote.svelte';
  import CorpusDrawer from './components/CorpusDrawer.svelte';
  import TransparencyModal from './components/TransparencyModal.svelte';

  let activeTab = $state('trip-brief');
  let selectedDoc = $state(null);
  let showTransparency = $state(false);

  function handleOpenDoc(item) {
    selectedDoc = item;
  }

  function handleCloseDoc() {
    selectedDoc = null;
  }
</script>

<div class="min-h-screen bg-[#f9f7f2] flex flex-col font-sans">
  <!-- Top Navigation & Hero Banner -->
  <Header 
    bind:activeTab 
    openTransparency={() => showTransparency = true} 
  />

  <!-- Main View Container -->
  <main class="flex-1 max-w-6xl w-full mx-auto px-4 sm:px-6 py-6 sm:py-8">
    {#if activeTab === 'trip-brief'}
      <ModeTripBrief onOpenDoc={handleOpenDoc} />
    {:else if activeTab === 'context-note'}
      <ModeContextNote onOpenDoc={handleOpenDoc} />
    {/if}
  </main>

  <!-- Footer -->
  <footer class="border-t border-borderline bg-white py-6 mt-12 text-center text-xs text-ink-500">
    <div class="max-w-6xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-3">
      <div class="flex items-center space-x-2">
        <span class="font-bold text-ink-900">Pramana</span>
        <span>•</span>
        <span>Bali DigiFest 2026 AI Web Innovation Challenge</span>
      </div>
      <div class="text-[11px] text-ink-400">
        Strict-RAG Legal Intelligence Engine • Tanpa Halusinasi
      </div>
    </div>
  </footer>

  <!-- Interactive PDF / Statute Drawer -->
  <CorpusDrawer 
    item={selectedDoc} 
    onClose={handleCloseDoc} 
  />

  <!-- Transparency & Evaluation Modal -->
  <TransparencyModal 
    isOpen={showTransparency} 
    onClose={() => showTransparency = false} 
  />
</div>
