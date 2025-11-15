import React from 'react';
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { CorrelationHeatmap } from '../components/CorrelationHeatmap';

describe('CorrelationHeatmap Component', () => {
  it('renders table headers and cells correctly', () => {
    const tickers = ['AAPL', 'MSFT'];
    const matrix = [
      [1.0, 0.65],
      [0.65, 1.0]
    ];

    render(<CorrelationHeatmap tickers={tickers} matrix={matrix} />);

    expect(screen.getAllByText('AAPL').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('MSFT').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('1.00').length).toBe(2);
    expect(screen.getAllByText('0.65').length).toBe(2);
  });
});
