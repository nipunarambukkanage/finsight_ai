import React from 'react';
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { DonutChart } from '../components/DonutChart';

describe('DonutChart Component', () => {
  it('renders sector labels and percentages in legend', () => {
    const data = { Technology: 70.0, Healthcare: 20.0, Cash: 10.0 };
    render(<DonutChart data={data} />);

    expect(screen.getByText(/Technology:/i)).toBeDefined();
    expect(screen.getByText(/70.0%/i)).toBeDefined();
    expect(screen.getByText(/Healthcare:/i)).toBeDefined();
    expect(screen.getByText(/20.0%/i)).toBeDefined();
    expect(screen.getByText(/Cash:/i)).toBeDefined();
    expect(screen.getByText(/10.0%/i)).toBeDefined();
  });
});
