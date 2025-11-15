import React from 'react';
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { DisclaimerBanner } from '../components/DisclaimerBanner';

describe('DisclaimerBanner Component', () => {
  it('renders regulatory notice clearly', () => {
    render(<DisclaimerBanner />);
    expect(screen.getByText(/Regulatory Notice:/i)).toBeDefined();
    expect(screen.getByText(/FinSight AI is a research and demonstration platform/i)).toBeDefined();
    expect(screen.getByText(/does not constitute financial advice/i)).toBeDefined();
  });
});
