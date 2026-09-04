import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import SafetyScoreGauge from '../components/score/SafetyScoreGauge';
import ScoreBreakdown from '../components/score/ScoreBreakdown';

describe('SafetyScoreGauge — Threshold color bands & accessible text', () => {
  it('renders score 0 with red band and Low Safety rating', () => {
    render(<SafetyScoreGauge score={0} />);
    expect(screen.getByTestId('gauge-score-value')).toHaveTextContent('0');
    expect(screen.getByTestId('gauge-rating-label')).toHaveTextContent('Low Safety');
    expect(screen.getByTestId('gauge-progress-circle')).toHaveAttribute('stroke', '#ef4444');
  });

  it('renders boundary score 59 with red band and Low Safety rating', () => {
    render(<SafetyScoreGauge score={59} />);
    expect(screen.getByTestId('gauge-score-value')).toHaveTextContent('59');
    expect(screen.getByTestId('gauge-rating-label')).toHaveTextContent('Low Safety');
    expect(screen.getByTestId('gauge-progress-circle')).toHaveAttribute('stroke', '#ef4444');
  });

  it('renders boundary score 60 with amber band and Moderate Safety rating', () => {
    render(<SafetyScoreGauge score={60} />);
    expect(screen.getByTestId('gauge-score-value')).toHaveTextContent('60');
    expect(screen.getByTestId('gauge-rating-label')).toHaveTextContent('Moderate Safety');
    expect(screen.getByTestId('gauge-progress-circle')).toHaveAttribute('stroke', '#f59e0b');
  });

  it('renders boundary score 79 with amber band and Moderate Safety rating', () => {
    render(<SafetyScoreGauge score={79} />);
    expect(screen.getByTestId('gauge-score-value')).toHaveTextContent('79');
    expect(screen.getByTestId('gauge-rating-label')).toHaveTextContent('Moderate Safety');
    expect(screen.getByTestId('gauge-progress-circle')).toHaveAttribute('stroke', '#f59e0b');
  });

  it('renders boundary score 80 with green band and High Safety rating', () => {
    render(<SafetyScoreGauge score={80} />);
    expect(screen.getByTestId('gauge-score-value')).toHaveTextContent('80');
    expect(screen.getByTestId('gauge-rating-label')).toHaveTextContent('High Safety');
    expect(screen.getByTestId('gauge-progress-circle')).toHaveAttribute('stroke', '#16a34a');
  });

  it('renders top score 100 with green band and High Safety rating', () => {
    render(<SafetyScoreGauge score={100} />);
    expect(screen.getByTestId('gauge-score-value')).toHaveTextContent('100');
    expect(screen.getByTestId('gauge-rating-label')).toHaveTextContent('High Safety');
    expect(screen.getByTestId('gauge-progress-circle')).toHaveAttribute('stroke', '#16a34a');
  });
});

describe('ScoreBreakdown — 4 component factors & explainability', () => {
  const defaultProps = {
    suitabilityScore: 87,
    profitabilityScore: 76,
    marketScore: 90,
    riskScore: 28,
  };

  it('renders all four factor components with their respective scores and weights', () => {
    render(<ScoreBreakdown {...defaultProps} />);

    // Suitability
    expect(screen.getByText('Suitability')).toBeInTheDocument();
    expect(screen.getByText('35% of score')).toBeInTheDocument();
    expect(screen.getByTestId('score-value-suitability')).toHaveTextContent('87 / 100');
    expect(screen.getByText(/fits your land, soil type, and water availability/i)).toBeInTheDocument();

    // Profitability
    expect(screen.getByText('Profitability')).toBeInTheDocument();
    expect(screen.getByText('30% of score')).toBeInTheDocument();
    expect(screen.getByTestId('score-value-profitability')).toHaveTextContent('76 / 100');
    expect(screen.getByText(/more or less profit you could earn/i)).toBeInTheDocument();

    // Market
    expect(screen.getByText('Market')).toBeInTheDocument();
    expect(screen.getByText('20% of score')).toBeInTheDocument();
    expect(screen.getByTestId('score-value-market')).toHaveTextContent('90 / 100');
    expect(screen.getByText(/local market prices and buyer access/i)).toBeInTheDocument();

    // Risk
    expect(screen.getByText('Risk')).toBeInTheDocument();
    expect(screen.getByText('15% of score')).toBeInTheDocument();
    expect(screen.getByTestId('score-value-risk')).toHaveTextContent('28 / 100');
    expect(screen.getByText(/price fluctuation, drought vulnerability/i)).toBeInTheDocument();
  });

  it('renders progress bars with correct aria attributes', () => {
    render(<ScoreBreakdown {...defaultProps} />);
    const progressBars = screen.getAllByRole('progressbar');
    expect(progressBars).toHaveLength(4);
    expect(progressBars[0]).toHaveAttribute('aria-valuenow', '87');
    expect(progressBars[1]).toHaveAttribute('aria-valuenow', '76');
    expect(progressBars[2]).toHaveAttribute('aria-valuenow', '90');
    expect(progressBars[3]).toHaveAttribute('aria-valuenow', '28');
  });

  it('expands and collapses the calculation methodology accordion', () => {
    render(<ScoreBreakdown {...defaultProps} />);

    const toggleBtn = screen.getByTestId('toggle-calculation-details');
    expect(screen.queryByTestId('calculation-details-panel')).not.toBeInTheDocument();

    // Expand
    fireEvent.click(toggleBtn);
    expect(screen.getByTestId('calculation-details-panel')).toBeInTheDocument();
    expect(screen.getByText(/Standard Decision Weights/i)).toBeInTheDocument();

    // Collapse
    fireEvent.click(toggleBtn);
    expect(screen.queryByTestId('calculation-details-panel')).not.toBeInTheDocument();
  });
});
