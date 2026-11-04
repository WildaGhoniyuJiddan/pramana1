/**
 * API client for Pramana backend.
 */

const API_BASE = '/api/v1';

export async function fetchHealth() {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error('Healthcheck failed');
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
