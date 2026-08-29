export default function RecentAlerts({ alerts }) {
  return (
    <div className="mini-panel">
      <h3>RECENT ALERTS</h3>
      <ul className="alert-list">
        {alerts.map((a) => (
          <li key={a.id}>
            <span className={`alert-dot tier-${a.tier}`} style={{ background: 'currentColor' }}></span>
            <div>
              {a.message}
              <span className="alert-time">{a.time}</span>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
