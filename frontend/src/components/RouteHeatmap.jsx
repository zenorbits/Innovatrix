const TIER_COLOR = {
  high: '#d64545',
  medium: '#e0a12c',
  low: '#1f9d55'
};

const CENTER = { x: 150, y: 170 };

export default function RouteHeatmap({ heatmap }) {
  const { cities, routes } = heatmap;
  const cityById = Object.fromEntries(cities.map((c) => [c.id, c]));

  return (
    <div className="panel">
      <h2>ROUTE HEATMAP</h2>
      <div className="legend">
        <span className="tier-high">
          <span className="dot" style={{ background: TIER_COLOR.high }}></span>High (&gt;15%)
        </span>
        <span className="tier-medium">
          <span className="dot" style={{ background: TIER_COLOR.medium }}></span>Medium (5% - 15%)
        </span>
        <span className="tier-low">
          <span className="dot" style={{ background: TIER_COLOR.low }}></span>Low (&lt;5%)
        </span>
      </div>
      <div id="mapWrap">
        <svg viewBox="0 0 300 320" width="100%" height="100%">
          <defs>
            <pattern id="gridDots" width="24" height="24" patternUnits="userSpaceOnUse">
              <circle cx="2" cy="2" r="1.4" fill="#dce6f4" />
            </pattern>
            <filter id="nodeShadow" x="-50%" y="-50%" width="200%" height="200%">
              <feDropShadow dx="0" dy="1" stdDeviation="1.5" floodColor="#1c2b52" floodOpacity="0.25" />
            </filter>
          </defs>

          <rect x="8" y="8" width="284" height="304" rx="16" fill="#f6f9fd" stroke="#e3ebf5" strokeWidth="1.5" />
          <rect x="8" y="8" width="284" height="304" rx="16" fill="url(#gridDots)" />

          {routes.map((r, i) => {
            const from = cityById[r.from];
            const to = cityById[r.to];
            if (!from || !to) return null;
            return (
              <line
                key={i}
                x1={from.x}
                y1={from.y}
                x2={to.x}
                y2={to.y}
                stroke={TIER_COLOR[r.tier] || '#999'}
                strokeWidth="2.5"
                strokeLinecap="round"
                strokeOpacity="0.85"
                fill="none"
              />
            );
          })}

          {cities.map((c) => {
            // color a city marker by its worst (highest-severity) connected route
            const tiers = routes
              .filter((r) => r.from === c.id || r.to === c.id)
              .map((r) => r.tier);
            const worst = tiers.includes('high')
              ? 'high'
              : tiers.includes('medium')
              ? 'medium'
              : 'low';

            // push the label outward, away from the panel center, so it
            // never collides with the connecting lines or the node itself
            const dx = c.x - CENTER.x;
            const dy = c.y - CENTER.y;
            const dist = Math.sqrt(dx * dx + dy * dy) || 1;
            const labelX = c.x + (dx / dist) * 20;
            const labelY = c.y + (dy / dist) * 20;

            return (
              <g key={c.id}>
                <circle
                  cx={c.x}
                  cy={c.y}
                  r="7"
                  fill={TIER_COLOR[worst]}
                  stroke="#fff"
                  strokeWidth="2"
                  filter="url(#nodeShadow)"
                />
                <text
                  x={labelX}
                  y={labelY}
                  fontSize="11"
                  textAnchor="middle"
                  dominantBaseline="middle"
                  fill="#1c2b52"
                  fontWeight="700"
                >
                  {c.name}
                </text>
              </g>
            );
          })}
        </svg>
      </div>
    </div>
  );
}