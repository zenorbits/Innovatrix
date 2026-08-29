// Every function here hits a REST endpoint your backend should implement.
// If the call fails (backend not built yet, offline, etc.) it falls back to
// mock data so the UI keeps working. Remove the fallback once your backend
// is live, or keep it as a graceful-degradation layer — your call.

import { apiClient } from './client';
import {
  mockKpis,
  mockTrend,
  mockHeatmapCities,
  mockHeatmapRoutes,
  mockTopRoutes,
  mockAlerts
} from '../data/mockData';

async function safeFetch(path, fallback) {
  try {
    return await apiClient.get(path);
  } catch (err) {
    console.warn(`[dashboardService] falling back to mock data for ${path}:`, err.message);
    return fallback;
  }
}

// GET /kpis
// -> { airfareApix: {...}, weeklyInflationChange: {...}, routesMonitored: {...}, alertLevel: {...} }
export const getKpis = () => safeFetch('/kpis', mockKpis);

// GET /trend?range=5y
// -> { labels: string[], series: [{ key, name, data: number[] }] }
export const getTrend = () => safeFetch('/trend', mockTrend);

// GET /routes/heatmap
// -> { cities: [{ id, name, x, y }], routes: [{ from, to, tier }] }
export const getHeatmap = () =>
  safeFetch('/routes/heatmap', { cities: mockHeatmapCities, routes: mockHeatmapRoutes });

// GET /routes/top?limit=5
// -> [{ route, yoyPct, tier }]
export const getTopRoutes = () => safeFetch('/routes/top', mockTopRoutes);

// GET /alerts?limit=10
// -> [{ id, tier, message, time }]
export const getAlerts = () => safeFetch('/alerts', mockAlerts);
