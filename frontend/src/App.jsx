import Sidebar from './components/Sidebar';
import Header from './components/Header';
import KpiRow from './components/KpiRow';
import TrendChart from './components/TrendChart';
import RouteHeatmap from './components/RouteHeatmap';
import TopRoutesTable from './components/TopRoutesTable';
import RecentAlerts from './components/RecentAlerts';
import { useDashboardData } from './hooks/useDashboardData';

export default function App() {
  const { data, loading, error } = useDashboardData();

  return (
    <div className="app">
      <Sidebar />
      <div className="main">
        <Header />
        <div className="content">
          {loading && <div className="state-message">Loading dashboard data…</div>}

          {error && (
            <div className="state-message">
              Couldn't load live data ({error.message}). Check your backend connection.
            </div>
          )}

          {!loading && !error && (
            <>
              <KpiRow kpis={data.kpis} />
              <div className="panels">
                <TrendChart trend={data.trend} />
                <RouteHeatmap heatmap={data.heatmap} />
                <div className="side-panels">
                  <TopRoutesTable topRoutes={data.topRoutes} />
                  <RecentAlerts alerts={data.alerts} />
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
