import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend);

const COLORS = {
  apix: { border: '#3f6fd6', fill: 'rgba(63,111,214,0.08)' },
  cpi: { border: '#3fa15a', fill: 'rgba(63,161,90,0.08)' }
};

export default function TrendChart({ trend }) {
  const data = {
    labels: trend.labels,
    datasets: trend.series.map((s) => {
      const palette = COLORS[s.key] || { border: '#888', fill: 'rgba(0,0,0,0.05)' };
      return {
        label: s.name,
        data: s.data,
        borderColor: palette.border,
        backgroundColor: palette.fill,
        borderWidth: 2.5,
        tension: 0.35,
        pointRadius: 3,
        fill: true
      };
    })
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        align: 'start',
        labels: { boxWidth: 10, font: { size: 11 } }
      }
    },
    scales: {
      y: { beginAtZero: true, grid: { color: '#eef2f8' } },
      x: { grid: { display: false } }
    }
  };

  return (
    <div className="panel">
      <h2>AIRFARE INFLATION TREND</h2>
      <div className="chart-wrap">
        <Line data={data} options={options} />
      </div>
    </div>
  );
}
