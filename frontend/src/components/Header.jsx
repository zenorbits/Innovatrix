export default function Header() {
  return (
    <header className="app-header">
      <div>
        <h1>AIRFARE INFLATION MONITORING DASHBOARD</h1>
        <p>Tracking airfare price inflation for India's Transport &amp; Communication CPI</p>
      </div>
      <div className="header-icons">
        <div className="icon-badge">🔔</div>
        <div className="icon-badge">👤</div>
      </div>
    </header>
  );
}
