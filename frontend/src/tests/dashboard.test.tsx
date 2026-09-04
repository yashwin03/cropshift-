import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { describe, it, expect, beforeEach } from 'vitest';
import HomePage from '../pages/HomePage';
import { saveFarmDetails, saveRecommendation } from '../utils/storage';

describe('HomePage Dashboard Test Suite', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  const renderComponent = () => {
    return render(
      <BrowserRouter>
        <HomePage />
      </BrowserRouter>
    );
  };

  it('renders greetings and empty state when no farm profile exists', () => {
    renderComponent();
    expect(screen.getByText('WELCOME BACK')).toBeInTheDocument();
    expect(screen.getByText(/No farm profile recorded yet/i)).toBeInTheDocument();

    // Metric cards and tools links should be visible
    expect(screen.getAllByText(/Farm Advisory/i).length).toBeGreaterThan(0);
    expect(screen.getByText(/Weather Advisory/i)).toBeInTheDocument();
    expect(screen.getByText(/Mandi Market Price/i)).toBeInTheDocument();
    expect(screen.getByText(/Buyer Opportunities/i)).toBeInTheDocument();
  });

  it('renders farm summary and latest analysis details when profile exists', () => {
    // Seed localStorage manually
    const farmMock = {
      farm_id: 1,
      farm_name: 'Test Farm Profile',
      land_area: 5,
      current_crop: 'Paddy',
      water_availability: 'Limited',
      district: 'Guntur',
      state: 'Andhra Pradesh'
    };
    const recMock = {
      recommended_crop: 'Groundnut',
      suitability_score: 90,
      profitability_score: 85,
      market_score: 75,
      risk_score: 80,
      safety_score: 83,
      decision: 'SWITCH',
      expected_profit: 45000,
      current_crop_profit: 35000,
      profit_difference: 10000,
      reasons: ['Reason A'],
      risks: ['Risk A']
    };

    saveFarmDetails(farmMock);
    saveRecommendation(recMock);

    renderComponent();

    // Welcome back is visible
    expect(screen.getByText('WELCOME BACK')).toBeInTheDocument();

    // Farm Summary Card content
    expect(screen.getByText('Test Farm Profile')).toBeInTheDocument();
    expect(screen.getByText('5 Acre')).toBeInTheDocument();
    expect(screen.getByText(/Guntur, Andhra Pradesh/i)).toBeInTheDocument();

    // Recommendation card details
    expect(screen.getByText('Good to Switch')).toBeInTheDocument();
    expect(screen.getByText('83')).toBeInTheDocument();
    expect(screen.getAllByText(/Groundnut/i).length).toBeGreaterThan(0);
    expect(screen.getByText('+₹10,000/acre')).toBeInTheDocument();
  });

  it('resets details when clicking Reset button', () => {
    // Seed first
    saveFarmDetails({ farm_name: 'Reset Farm' } as any);
    renderComponent();
    expect(screen.getByText('Reset Farm')).toBeInTheDocument();

    const resetBtn = screen.getByRole('button', { name: /reset/i });
    fireEvent.click(resetBtn);

    // Should return back to empty state
    expect(screen.getByText(/No farm profile recorded yet/i)).toBeInTheDocument();
  });
});


