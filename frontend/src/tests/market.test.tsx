import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { describe, test, expect, vi, beforeEach } from 'vitest';
import TrendIndicator from '../components/market/TrendIndicator';
import MarketCard from '../components/market/MarketCard';
import MarketPage from '../pages/MarketPage';
import type { MarketItem } from '../types/api';
import * as storage from '../utils/storage';
import * as apiService from '../services/api';

const PADDY_MARKET: MarketItem = {
  crop_id: 1, crop_name: 'Paddy', price: 2000, price_unit: 'Quintal',
  market_name: 'Test Market', market_location: 'Location', distance_km: 10,
  trend: 'STABLE', market_score: 80, data_status: 'REAL', data_source: 'Source',
};

vi.mock('../utils/storage', () => ({
  getRecommendation: vi.fn(),
  getFarmDetails: vi.fn(),
}));

vi.mock('../services/api', () => ({
  getMarkets: vi.fn(),
}));

describe('Market Components Tests', () => {
  test('all three trends render distinct indicators', () => {
    const { rerender } = render(<TrendIndicator trend="RISING" />);
    expect(screen.getByText('Prices Rising')).toBeInTheDocument();
    expect(screen.getByTestId('trend-indicator-rising')).toHaveClass('text-green-700');
    rerender(<TrendIndicator trend="STABLE" />);
    expect(screen.getByText('Prices Steady')).toBeInTheDocument();
    expect(screen.getByTestId('trend-indicator-stable')).toHaveClass('text-blue-700');
    rerender(<TrendIndicator trend="FALLING" />);
    expect(screen.getByText('Prices Falling')).toBeInTheDocument();
    expect(screen.getByTestId('trend-indicator-falling')).toHaveClass('text-red-700');
  });

  test('all four data_status values render the correct badge text', () => {
    const baseMarket: MarketItem = {
      crop_id: 1, crop_name: 'Paddy', price: 2000, price_unit: 'Quintal',
      market_name: 'Test Market', market_location: 'Location', distance_km: 10,
      trend: 'STABLE', market_score: 80, data_status: 'REAL', data_source: 'Source',
    };
    const { rerender } = render(<MarketCard market={baseMarket} title="Test Title" />);
    expect(screen.getByText('Live Data')).toBeInTheDocument();
    rerender(<MarketCard market={{ ...baseMarket, data_status: 'STATIC' }} title="Test Title" />);
    expect(screen.getByText('Reference Data')).toBeInTheDocument();
    rerender(<MarketCard market={{ ...baseMarket, data_status: 'ESTIMATED' }} title="Test Title" />);
    expect(screen.getByText('Estimated')).toBeInTheDocument();
    rerender(<MarketCard market={{ ...baseMarket, data_status: 'DEMO' }} title="Test Title" />);
    expect(screen.getByText('Demo Data')).toBeInTheDocument();
  });

  test('missing price renders the unavailable state', () => {
    const mockMarket: MarketItem = {
      crop_id: 99, crop_name: 'Unknown Crop', price: 0, price_unit: 'Quintal',
      market_name: 'Market Hub', market_location: 'Location', distance_km: 30,
      trend: 'STABLE', market_score: 50, data_status: 'DEMO', data_source: 'Source',
    };
    render(<MarketCard market={mockMarket} title="Test Title" />);
    expect(screen.getByText('Price unavailable')).toBeInTheDocument();
    expect(screen.queryByText('per Quintal')).not.toBeInTheDocument();
  });
});

describe('MarketPage - B14 State Coverage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });
  const renderPage = () => render(<BrowserRouter><MarketPage /></BrowserRouter>);

  test('State: Empty - shows EmptyState when no recommendation exists', () => {
    vi.mocked(storage.getRecommendation).mockReturnValue(null);
    renderPage();
    expect(screen.getByText('No Farm Analysis Found')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /go to farm analysis/i })).toBeInTheDocument();
  });

  test('State: Loading - shows spinner while API is fetching', async () => {
    vi.mocked(storage.getRecommendation).mockReturnValue({
      recommended_crop: 'Groundnut', suitability_score: 87, profitability_score: 76,
      market_score: 90, risk_score: 28, safety_score: 82, decision: 'SWITCH',
      expected_profit: 43000, current_crop_profit: 34000, profit_difference: 9000,
      reasons: [], risks: [],
    });
    vi.mocked(apiService.getMarkets).mockImplementation(
      () => new Promise(resolve => setTimeout(() => resolve(PADDY_MARKET), 2000))
    );
    renderPage();
    const spinner = await screen.findByRole('status');
    expect(spinner).toBeInTheDocument();
  });

  test('State: Error - shows friendly error when API rejects with known code', async () => {
    vi.mocked(storage.getRecommendation).mockReturnValue({
      recommended_crop: 'Groundnut', suitability_score: 87, profitability_score: 76,
      market_score: 90, risk_score: 28, safety_score: 82, decision: 'SWITCH',
      expected_profit: 43000, current_crop_profit: 34000, profit_difference: 9000,
      reasons: [], risks: [],
    });
    vi.mocked(apiService.getMarkets).mockRejectedValue({
      response: { data: { error: { code: 'DATA_UNAVAILABLE', message: 'No market data' } } },
    });
    renderPage();
    await waitFor(() => { expect(screen.getByRole('alert')).toBeInTheDocument(); });
    expect(screen.queryByText('DATA_UNAVAILABLE')).not.toBeInTheDocument();
  });

  test('State: Backend Unavailable - maps NETWORK_ERROR to friendly message', async () => {
    vi.mocked(storage.getRecommendation).mockReturnValue({
      recommended_crop: 'Groundnut', suitability_score: 87, profitability_score: 76,
      market_score: 90, risk_score: 28, safety_score: 82, decision: 'SWITCH',
      expected_profit: 43000, current_crop_profit: 34000, profit_difference: 9000,
      reasons: [], risks: [],
    });
    vi.mocked(apiService.getMarkets).mockRejectedValue({ code: 'NETWORK_ERROR' });
    renderPage();
    await waitFor(() => {
      const alert = screen.getByRole('alert');
      expect(alert).toHaveTextContent(/reach the server/i);
    });
  });
});
