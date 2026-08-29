// Minimal fetch wrapper. Swap this out for axios or your own client if you prefer —
// dashboardService.js is the only file that imports it.

const BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options
  });

  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`Request to ${path} failed: ${res.status} ${text}`);
  }

  return res.json();
}

export const apiClient = {
  get: (path) => request(path, { method: 'GET' })
};
