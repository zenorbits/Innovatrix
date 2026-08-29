# Airfare Inflation Monitoring Dashboard

React + Vite implementation of the dashboard, structured so a real backend can
be dropped in without touching any UI component.

## Folder structure

```
airfare-dashboard/
├── index.html
├── package.json
├── vite.config.js
├── .env.example
└── src/
    ├── main.jsx              # React entry point
    ├── App.jsx               # Layout + top-level data loading
    ├── index.css             # All styling
    ├── api/
    │   ├── client.js         # Thin fetch wrapper (reads VITE_API_BASE_URL)
    │   └── dashboardService.js  # One function per endpoint, contract documented inline
    ├── hooks/
    │   └── useDashboardData.js  # Loads all dashboard data on mount
    ├── data/
    │   └── mockData.js       # Fallback data + the shape your API should return
    └── components/
        ├── Sidebar.jsx
        ├── Header.jsx
        ├── KpiRow.jsx
        ├── TrendChart.jsx
        ├── RouteHeatmap.jsx
        ├── TopRoutesTable.jsx
        └── RecentAlerts.jsx
```

## Run it

```bash
npm install
npm run dev
```

With no backend running, the dashboard uses the bundled mock data automatically
(see the console warnings from `dashboardService.js`), so the UI is fully
viewable standalone.

## Connecting a real backend

1. Copy `.env.example` to `.env` and set `VITE_API_BASE_URL` to your API's base
   URL (e.g. `https://api.yourteam.com/v1`).
2. Implement these endpoints — the exact shape each one must return is
   documented as a comment above each function in `src/api/dashboardService.js`:

   | Endpoint              | Returns                                              |
   |------------------------|-------------------------------------------------------|
   | `GET /kpis`            | APIx value, weekly change, routes monitored, alert level |
   | `GET /trend`           | Labels + one or more data series for the line chart   |
   | `GET /routes/heatmap`  | Cities (with x/y map coordinates) + routes with a severity tier |
   | `GET /routes/top`      | Top routes ranked by year-over-year inflation         |
   | `GET /alerts`          | Recent alert feed                                     |

3. That's it — `useDashboardData` calls all five in parallel and every
   component just renders whatever it receives, mock or real.

If your backend runs on a different host during local dev, edit the `proxy`
block in `vite.config.js` instead of hardcoding URLs in the app.

## Notes

- Charting: `chart.js` via `react-chartjs-2`.
- No state management library — data lives in `useDashboardData`'s state and
  flows down as props. Swap in React Query/SWR/Redux later by changing only
  that hook.
- The India map is a simplified illustrative SVG silhouette, not a
  geographically precise India map.
