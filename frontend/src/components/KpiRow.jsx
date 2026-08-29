function KpiCard({ icon, label, value, sub, subMuted, alert }) {
  return (
    <div className={`kpi${alert ? ' alert' : ''}`}>
      <div className="icon">{icon}</div>
      <div>
        <div className="label">{label}</div>
        <div className="value">{value}</div>
        {sub && <div className={`sub${subMuted ? ' muted' : ''}`}>{sub}</div>}
      </div>
    </div>
  );
}

export default function KpiRow({ kpis }) {
  const { airfareApix, weeklyInflationChange, routesMonitored, alertLevel } = kpis;

  return (
    <div className="kpi-row">
      <KpiCard
        icon="✈️"
        label="Airfare APIx"
        value={airfareApix.value}
        sub={`▲ ${airfareApix.changePct}% ${airfareApix.changeLabel}`}
      />
      <KpiCard
        icon="📊"
        label="Weekly Inflation Change"
        value={`${weeklyInflationChange.changePct > 0 ? '+' : ''}${weeklyInflationChange.changePct}%`}
        sub={weeklyInflationChange.changeLabel}
        subMuted
      />
      <KpiCard
        icon="📍"
        label="Routes Monitored"
        value={routesMonitored.value}
        sub={routesMonitored.label}
        subMuted
      />
      <KpiCard icon="⚠️" label="Inflation Alert Level" value={`${alertLevel.level}!`} alert />
    </div>
  );
}
