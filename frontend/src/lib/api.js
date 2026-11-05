/**
 * API client for Pramana backend.
 */

const ENV_BASE = (import.meta.env.VITE_API_BASE_URL || '').trim().replace(/\/+$/, '');
const API_BASE = `${ENV_BASE}/api/v1`;

export async function fetchHealth() {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error('Healthcheck failed');
  return res.json();
}

export async function fetchAiStatus() {
  const res = await fetch(`${API_BASE}/ai/status`);
  if (!res.ok) throw new Error('Failed to load AI status');
  return res.json();
}

export async function fetchCorpus() {
  const res = await fetch(`${API_BASE}/corpus`);
  if (!res.ok) throw new Error('Failed to load legal corpus');
  return res.json();
}

export async function requestTripBrief(payload) {
  const res = await fetch(`${API_BASE}/trip-brief`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to generate trip brief');
  }
  return res.json();
}

export async function requestContextNote(payload) {
  const res = await fetch(`${API_BASE}/context-note`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to generate context note');
  }
  return res.json();
}

export async function fetchZones() {
  const res = await fetch(`${API_BASE}/zones`);
  if (!res.ok) throw new Error('Failed to load Smart Gate zones');
  return res.json();
}

export async function fetchTotem(zoneId, lang = 'id') {
  const res = await fetch(
    `${API_BASE}/totem/${encodeURIComponent(zoneId)}?lang=${encodeURIComponent(lang)}`
  );
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to load Smart Gate card');
  }
  return res.json();
}

export async function requestTotemBrief(zoneId, lang = 'id') {
  const res = await fetch(
    `${API_BASE}/totem/${encodeURIComponent(zoneId)}/brief`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ lang })
    }
  );
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to generate Smart Gate brief');
  }
  return res.json();
}
