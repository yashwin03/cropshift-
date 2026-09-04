import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { describe, test, expect, vi, beforeEach } from 'vitest';
import RiskSimulationPage from '../pages/RiskSimulationPage';
import { getFarmDetails, getRecommendation } from '../utils/storage';

// Mock Storage helpers
vi.mock('../utils/storage', () => ({
  getFarmDetails: vi.fn(),
  getRecommendation: vi.fn(),
}));

vi.mock('../services/api', () => ({
  runRiskSimulation: vi.fn().mockImplementation(() =>
    Promise.resolve({
      baseline: { safety_score: 82, decision: 'SWITCH' },
      price_down: { safety_score: 69, decision: 'CAUTION' },
      yield_down: { safety_score: 63, decision: 'CAUTION' },
      water_risk: { safety_score: 48, decision: 'DONT_SWITCH' },
    })
  ),
}));

// Mock standard UI components
vi.mock('../components/score/DecisionBadge', () => ({
  default: ({ decision }: { decision: string }) => <div data-testid={`badge-${decision}`}>{decision}</div>,
}));

describe('RiskSimulationPage Unit & Integration Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  test('renders empty state when no recommendation exists in storage', async () => {
    vi.mocked(getFarmDetails).mockReturnValue(null);
    vi.mocked(getRecommendation).mockReturnValue(null);

    render(<BrowserRouter><RiskSimulationPage /></BrowserRouter>);

    const emptyTitle = await screen.findByText('No Active Recommendation');
    expect(emptyTitle).toBeInTheDocument();
  });

  test('renders scenarios and highlights decision changes', async () => {
    vi.mocked(getFarmDetails).mockReturnValue({
      farm_id: 1,
      farm_name: 'Test Farm',
      land_area: 2,
      current_crop: 'Paddy',
      water_availability: 'Available',
      district: 'Dist',
      state: 'State',
    });

    vi.mocked(getRecommendation).mockReturnValue({
      recommended_crop: 'Groundnut',
      suitability_score: 87,
      profitability_score: 76,
      market_score: 90,
      risk_score: 28,
      safety_score: 82,
      decision: 'SWITCH',
      expected_profit: 43000,
      current_crop_profit: 34000,
      profit_difference: 9000,
      reasons: [],
      risks: [],
    });

    render(<BrowserRouter><RiskSimulationPage /></BrowserRouter>);

    // Wait for the simulated scenarios to load
    const normalConditionsCard = await screen.findByTestId('scenario-card-baseline');
    expect(normalConditionsCard).toBeInTheDocument();

    // Verify all 4 scenarios render safety score text correctly
    expect(screen.getByTestId('safety-score-baseline')).toHaveTextContent('82');
    expect(screen.getByTestId('safety-score-price_down')).toHaveTextContent('69');
    expect(screen.getByTestId('safety-score-yield_down')).toHaveTextContent('63');
    expect(screen.getByTestId('safety-score-water_risk')).toHaveTextContent('48');

    // Verify decision changed alerts are highlighted for non-baseline changes
    const alerts = screen.getAllByTestId('decision-changed-alert');
    expect(alerts.length).toBe(3); // price_down (CAUTION), yield_down (CAUTION), water_risk (DONT_SWITCH) all differ from baseline (SWITCH)

    // Check chart bars represent correct dimensions
    expect(screen.getByTestId('bar-baseline')).toHaveStyle('width: 82%');
    expect(screen.getByTestId('bar-water_risk')).toHaveStyle('width: 48%');
  });
});
