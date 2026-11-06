/**
 * API client for Pramana backend with timeout, 429 backoff, 422 array formatting,
 * cold-start 5s wake-up detection with automatic retry, and HTML fallback detection.
 */

import { i18n } from './i18n.svelte.js';

const DEFAULT_REMOTE_BACKEND = 'https://pramana1.onrender.com';
const RESOLVED_BASE = (
  import.meta.env.VITE_API_BASE_URL ||
  (typeof window !== 'undefined' &&
  (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
    ? 'http://127.0.0.1:8000'
    : DEFAULT_REMOTE_BACKEND)
).trim().replace(/\/+$/, '');

const API_BASE = `${RESOLVED_BASE}/api/v1`;
const DEFAULT_TIMEOUT_MS = 25000;

export const apiState = $state({
  isWakingUp: false,
  message: ''
});

function formatDetail(detail) {
  if (!detail) return '';
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        if (typeof item === 'string') return item;
        return item.msg || JSON.stringify(item);
      })
      .join('; ');
  }
  if (typeof detail === 'object') return detail.msg || JSON.stringify(detail);
  return String(detail);
}

async function apiFetch(endpoint, options = {}, isRetry = false) {
  const url = `${API_BASE}${endpoint}`;
  const controller = new AbortController();
  const timeoutId = setTimeout(
    () => controller.abort(),
    options.timeoutMs || DEFAULT_TIMEOUT_MS
  );

  const wakeTimer = setTimeout(() => {
    apiState.isWakingUp = true;
    apiState.message =
      i18n.lang === 'en'
        ? 'Server is waking up, please wait...'
        : 'Server sedang bangun, harap tunggu...';
  }, 5000);

  try {
    const res = await fetch(url, {
      ...options,
      signal: controller.signal
    });

    const contentType = res.headers.get('content-type') || '';

    // If server returned HTML (e.g., Vercel SPA rewrite when backend unreachable or VITE_API_BASE_URL empty)
    if (contentType.includes('text/html')) {
      const isEn = i18n.lang === 'en';
      throw new Error(
        isEn
          ? 'Backend unreachable (received HTML instead of API response). Check server status or VITE_API_BASE_URL.'
          : 'Backend tidak terjangkau (menerima HTML bukan respons API). Periksa status server atau VITE_API_BASE_URL.'
      );
    }

    if (res.status === 429) {
      const retryAfter = res.headers.get('retry-after');
      const isEn = i18n.lang === 'en';
      const suffix = retryAfter ? ` (${retryAfter}s)` : '';
      throw new Error(
        isEn
          ? `Rate limit reached. Please wait a moment${suffix}.`
          : `Terlalu banyak permintaan. Silakan tunggu beberapa saat${suffix}.`
      );
    }

    if (!res.ok) {
      let detail = '';
      try {
        const errJson = await res.json();
        detail = formatDetail(errJson.detail);
      } catch {
        detail = res.statusText;
      }
      throw new Error(detail || `Request failed with HTTP ${res.status}`);
    }

    return await res.json();
  } catch (err) {
    // Cold start auto-retry once after 1.5s
    if (!isRetry && (err.name === 'AbortError' || err.name === 'TypeError')) {
      apiState.isWakingUp = true;
      apiState.message =
        i18n.lang === 'en'
          ? 'Server is waking up, retrying once...'
          : 'Server sedang bangun, mencoba ulang sekali...';
      await new Promise((r) => setTimeout(r, 1500));
      return apiFetch(endpoint, options, true);
    }

    if (err.name === 'AbortError') {
      const isEn = i18n.lang === 'en';
      throw new Error(
        isEn
          ? 'Connection timed out. Server backend may still be starting up from cold sleep, please retry.'
          : 'Koneksi timeout. Server backend mungkin sedang cold start, silakan coba lagi.'
      );
    }
    throw err;
  } finally {
    clearTimeout(timeoutId);
    clearTimeout(wakeTimer);
    apiState.isWakingUp = false;
    apiState.message = '';
  }
}

export async function fetchHealth() {
  return apiFetch('/health');
}

export async function fetchAiStatus() {
  return apiFetch('/ai/status');
}

export async function fetchCorpus() {
  return apiFetch('/corpus');
}

export async function requestTripBrief(payload) {
  const body = { lang: i18n.lang, ...payload };
  return apiFetch('/trip-brief', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
}

export async function requestContextNote(payload) {
  const body = { lang: i18n.lang, ...payload };
  return apiFetch('/context-note', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
}

export async function fetchZones() {
  return apiFetch('/zones');
}

export async function fetchTotem(zoneId, lang = 'id') {
  return apiFetch(
    `/totem/${encodeURIComponent(zoneId)}?lang=${encodeURIComponent(lang)}`
  );
}

export async function requestTotemBrief(zoneId, lang = 'id') {
  return apiFetch(
    `/totem/${encodeURIComponent(zoneId)}/brief`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ lang })
    }
  );
}
