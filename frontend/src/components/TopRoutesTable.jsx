export default function TopRoutesTable({ topRoutes }) {
  return (
    <div className="mini-panel">
      <h3>TOP 5 ROUTES BY INFLATION</h3>
      <table className="routes">
        <thead>
          <tr>
            <th>Route</th>
            <th>YoY</th>
          </tr>
        </thead>
        <tbody>
          {topRoutes.map((r) => (
            <tr key={r.route}>
              <td>{r.route}</td>
              <td className={`pct tier-${r.tier}`}>+{r.yoyPct}%</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
