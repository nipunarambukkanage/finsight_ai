import React from 'react';

interface CorrelationHeatmapProps {
  tickers: string[];
  matrix: number[][];
}

export const CorrelationHeatmap: React.FC<CorrelationHeatmapProps> = ({ tickers, matrix }) => {
  const getColor = (val: number) => {
    if (val === 1.0) return 'rgba(6, 182, 212, 0.9)'; // Diagonal cyan
    if (val > 0.6) return 'rgba(16, 185, 129, 0.7)'; // High pos green
    if (val > 0.3) return 'rgba(16, 185, 129, 0.4)';
    if (val > 0.0) return 'rgba(16, 185, 129, 0.15)';
    if (val > -0.3) return 'rgba(244, 63, 94, 0.15)';
    return 'rgba(244, 63, 94, 0.6)'; // High neg red
  };

  return (
    <div style={{ overflowX: 'auto' }}>
      <table
        id="correlation-heatmap-table"
        style={{
          width: '100%',
          borderCollapse: 'separate',
          borderSpacing: '4px',
          textAlign: 'center',
          fontSize: '12px'
        }}
      >
        <thead>
          <tr>
            <th style={{ padding: '8px', color: 'var(--text-muted)' }}>Ticker</th>
            {tickers.map((t) => (
              <th key={t} style={{ padding: '8px', color: 'var(--text-secondary)', fontWeight: 600 }}>
                {t}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {tickers.map((tRow, rIdx) => (
            <tr key={tRow}>
              <td style={{ padding: '8px', fontWeight: 600, color: 'var(--text-secondary)' }}>{tRow}</td>
              {matrix[rIdx]?.map((val, cIdx) => (
                <td
                  key={`${tRow}-${tickers[cIdx]}`}
                  style={{
                    padding: '12px 8px',
                    backgroundColor: getColor(val),
                    color: '#ffffff',
                    fontWeight: 600,
                    borderRadius: 'var(--radius-sm)',
                    fontFamily: 'var(--font-mono)'
                  }}
                  title={`Correlation between ${tRow} and ${tickers[cIdx]}: ${val}`}
                >
                  {val.toFixed(2)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
