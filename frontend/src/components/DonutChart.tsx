import React from 'react';

interface DonutChartProps {
  data: Record<string, number>;
  size?: number;
}

export const DonutChart: React.FC<DonutChartProps> = ({ data, size = 200 }) => {
  const entries = Object.entries(data);
  const total = entries.reduce((acc, [_, val]) => acc + val, 0);

  const colors = [
    '#06b6d4',
    '#3b82f6',
    '#10b981',
    '#f59e0b',
    '#8b5cf6',
    '#f43f5e',
    '#64748b'
  ];

  let cumulativeAngle = 0;
  const radius = size * 0.38;
  const strokeWidth = size * 0.16;
  const center = size / 2;
  const circumference = 2 * Math.PI * radius;

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '24px', flexWrap: 'wrap' }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <circle
          cx={center}
          cy={center}
          r={radius}
          fill="none"
          stroke="rgba(255, 255, 255, 0.05)"
          strokeWidth={strokeWidth}
        />
        {entries.map(([label, val], idx) => {
          const pct = total > 0 ? val / total : 0;
          const strokeDasharray = `${pct * circumference} ${circumference}`;
          const strokeDashoffset = -cumulativeAngle * circumference;
          cumulativeAngle += pct;
          const color = colors[idx % colors.length];

          return (
            <circle
              key={label}
              cx={center}
              cy={center}
              r={radius}
              fill="none"
              stroke={color}
              strokeWidth={strokeWidth}
              strokeDasharray={strokeDasharray}
              strokeDashoffset={strokeDashoffset}
              transform={`rotate(-90 ${center} ${center})`}
              style={{ transition: 'stroke-dasharray 0.5s ease' }}
            />
          );
        })}
      </svg>


      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {entries.map(([label, val], idx) => {
          const color = colors[idx % colors.length];
          return (
            <div key={label} style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px' }}>
              <div style={{ width: '10px', height: '10px', borderRadius: '2px', backgroundColor: color }} />
              <span style={{ color: 'var(--text-secondary)' }}>{label}:</span>
              <strong style={{ color: 'var(--text-primary)' }}>{val.toFixed(1)}%</strong>
            </div>
          );
        })}
      </div>
    </div>
  );
};
