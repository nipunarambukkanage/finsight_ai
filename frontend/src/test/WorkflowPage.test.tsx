import React from 'react';
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { WorkflowPage } from '../pages/WorkflowPage';

describe('WorkflowPage Component', () => {
  it('renders institutional workflow header and regulatory disclaimer', () => {
    render(<WorkflowPage />);


    expect(screen.getByText(/Autonomous Research & Strategy Workflow Hub/i)).toBeDefined();
    expect(screen.getAllByText(/LangGraph/i).length).toBeGreaterThan(0);


    expect(screen.getByText(/Regulatory Notice:/i)).toBeDefined();
    expect(screen.getByText(/No live money trading is executed/i)).toBeDefined();


    expect(screen.getByText(/1. Market Data/i)).toBeDefined();
    expect(screen.getByText(/4. Dev Agent/i)).toBeDefined();
    expect(screen.getByText(/5. QA Agent/i)).toBeDefined();
    expect(screen.getByText(/6. Backtest/i)).toBeDefined();
    expect(screen.getByText(/7. Approval Gate/i)).toBeDefined();
    expect(screen.getByText(/8. Shadow Mode/i)).toBeDefined();


    expect(screen.getByText(/Initiate Autonomous Workflow/i)).toBeDefined();
  });
});
