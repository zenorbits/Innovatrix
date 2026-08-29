// Fallback data so the dashboard renders even before a backend is connected.
// Shapes here define the CONTRACT your real API should return — see
// src/api/dashboardService.js for the endpoint each one maps to.

export const mockKpis = {
  airfareApix: { value: 118.5, changePct: 8.4, changeLabel: 'vs last month' },
  weeklyInflationChange: { changePct: 4.2, changeLabel: 'vs last month' },
  routesMonitored: { value: 25, label: 'Major city pairs' },
  alertLevel: { level: 'HIGH' } // 'LOW' | 'MEDIUM' | 'HIGH'
};

export const mockTrend = {
  labels: ['2021', '2022', '2023', '2024', '2025'],
  series: [
    { key: 'apix', name: 'APIx', data: [11, 13.5, 14.5, 17, 24] },
    { key: 'cpi', name: 'Transport & Communication CPI', data: [9.5, 12.5, 14.8, 16.8, 20] }
  ]
};

// x/y are plotted on a 0-300 x 0-320 viewBox as an evenly-spaced hexagon
// (no longer a geographic map) so the layout always looks balanced.
export const mockHeatmapCities = [
  { id: 'delhi', name: 'Delhi', x: 150, y: 55 },
  { id: 'kolkata', name: 'Kolkata', x: 250, y: 112 },
  { id: 'chennai', name: 'Chennai', x: 250, y: 228 },
  { id: 'bengaluru', name: 'Bengaluru', x: 150, y: 285 },
  { id: 'mumbai', name: 'Mumbai', x: 50, y: 228 },
  { id: 'hyderabad', name: 'Hyderabad', x: 50, y: 112 }
];

export const mockHeatmapRoutes = [
  { from: 'delhi', to: 'mumbai', tier: 'high' },
  { from: 'delhi', to: 'kolkata', tier: 'high' },
  { from: 'delhi', to: 'bengaluru', tier: 'medium' },
  { from: 'mumbai', to: 'bengaluru', tier: 'medium' },
  { from: 'bengaluru', to: 'kolkata', tier: 'low' },
  { from: 'mumbai', to: 'kolkata', tier: 'low' },
  { from: 'hyderabad', to: 'chennai', tier: 'low' },
  { from: 'delhi', to: 'hyderabad', tier: 'medium' }
];

export const mockTopRoutes = [
  { route: 'Delhi → Mumbai', yoyPct: 22.4, tier: 'high' },
  { route: 'Delhi → Bengaluru', yoyPct: 18.9, tier: 'high' },
  { route: 'Mumbai → Bengaluru', yoyPct: 11.2, tier: 'medium' },
  { route: 'Delhi → Kolkata', yoyPct: 9.6, tier: 'medium' },
  { route: 'Bengaluru → Kolkata', yoyPct: 3.8, tier: 'low' }
];

export const mockAlerts = [
  { id: 1, tier: 'high', message: 'Delhi–Mumbai fares up 6% in 7 days', time: '2 hours ago' },
  { id: 2, tier: 'medium', message: 'Fuel surcharge revised on 4 routes', time: 'Yesterday' },
  { id: 3, tier: 'high', message: 'APIx crossed 115 threshold', time: '2 days ago' }
];