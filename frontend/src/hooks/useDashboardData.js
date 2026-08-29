import { useEffect, useState } from 'react';
import {
  getKpis,
  getTrend,
  getHeatmap,
  getTopRoutes,
  getAlerts
} from '../api/dashboardService';

// Loads everything the dashboard needs in parallel, once, on mount.
// Swap this for React Query / SWR later without touching any component —
// they only care about { data, loading, error }.
export function useDashboardData() {
  const [data, setData] = useState({
    kpis: null,
    trend: null,
    heatmap: null,
    topRoutes: null,
    alerts: null
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const [kpis, trend, heatmap, topRoutes, alerts] = await Promise.all([
          getKpis(),
          getTrend(),
          getHeatmap(),
          getTopRoutes(),
          getAlerts()
        ]);

        if (!cancelled) {
          setData({ kpis, trend, heatmap, topRoutes, alerts });
          setLoading(false);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err);
          setLoading(false);
        }
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, []);

  return { data, loading, error };
}
