import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';

export default defineConfig({
  plugins: [svelte()],
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('CorpusExplorer') || id.includes('iso-kit')) {
            return 'corpus-explorer';
          }
          if (id.includes('SmartGateView') || id.includes('GateScannerModal') || id.includes('html5-qrcode') || id.includes('QrCode')) {
            return 'smart-gate';
          }
        }
      }
    }
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
});
