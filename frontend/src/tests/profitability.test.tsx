import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import ProfitabilityPage from '../pages/ProfitabilityPage';
import ProfitComparison, { formatINR } from '../components/profit/ProfitComparison';
import {
  GOLDEN_DEMO_PROFITABILITY,
  DONT_SWITCH_PROFITABILITY,
} from '../mocks/fixtures';
import * as apiService from '../services/api';
import * as storage from '../utils/storage';

// Mock storage so ProfitabilityPage has a farm to load data for
vi.mock('../utils/storage', async () => {
  const actual = await vi.importActual<typeof import('../utils/storage')>('../utils/storage');
  return {
    ...actual,
    getFarmDetails: vi.fn(() => ({ farm_id: 1, farm_name: 'Test Farm', land_area: 1, current_crop: 'Paddy', water_availability: 'Available', district: 'Test', state: 'Test' })),
    getRecommendation: vi.fn(() => null),
  };
});

// Mock recharts ResponsiveContainer to work properly in jsdom environment
vi.mock('recharts', async () => {
  const actual = await vi.importActual<typeof import('recharts')>('recharts');
  return {
    ...actual,
    ResponsiveContainer: ({ children }: { children: React.ReactNode }) => (
      <div style={{ width: 500, height: 300 }}>{children}</div>
    ),
  };
});

const renderPage = () =>
  render(
    <BrowserRouter>
      <ProfitabilityPage />
    </BrowserRouter>
  );

describe('Profitability — Component Unit Tests', () => {
  it('formats currency correctly in Indian grouping (formatINR)', () => {
    expect(formatINR(43000)).toBe('₹43,000');
    expect(formatINR(28000)).toBe('₹28,000');
    expect(formatINR(1000000)).toBe('₹10,00,000');
    expect(formatINR(-2000)).toBe('₹2,000');
  });

  it('renders persistent estimation disclaimer in the DOM', () => {
    render(<ProfitComparison data={GOLDEN_DEMO_PROFITABILITY} />);
    const disclaimer = screen.getByTestId('profitability-disclaimer');
    expect(disclaimer).toBeInTheDocument();
    expect(disclaimer).toHaveTextContent(
      'These are estimates based on regional data. Actual results depend on weather, prices, and farming practices.'
    );
  });

  it('renders all six comparison metrics for both crops in positive difference scenario', () => {
    render(<ProfitComparison data={GOLDEN_DEMO_PROFITABILITY} />);

    // Crop names
    expect(screen.getByTestId('current-crop-name')).toHaveTextContent('Paddy');
    expect(screen.getByTestId('recommended-crop-name')).toHaveTextContent('Groundnut');

    // 1. Expected Yield
    expect(screen.getAllByText(/20 Quintal \/ acre/i).length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText(/10 Quintal \/ acre/i).length).toBeGreaterThanOrEqual(1);

    // 2. Production Cost
    expect(screen.getAllByText(/₹18,000/i).length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText(/₹12,000/i).length).toBeGreaterThanOrEqual(1);

    // 3. Expected Revenue
    expect(screen.getAllByText(/₹52,000/i).length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText(/₹55,000/i).length).toBeGreaterThanOrEqual(1);

    // 4. Estimated Profit
    expect(screen.getAllByText(/₹34,000/i).length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText(/₹43,000/i).length).toBeGreaterThanOrEqual(1);

    // 5. Highlighted Profit Difference (+₹9,000)
    const diffBanner = screen.getByTestId('profit-diff-banner');
    expect(diffBanner).toHaveTextContent('+₹9,000');

    // 6. Data Status Badges
    expect(screen.getByText('Reference Data')).toBeInTheDocument();
    expect(screen.getAllByText(/Estimated/i).length).toBeGreaterThanOrEqual(1);
  });

  it('renders negative profit difference correctly (-₹2,000)', () => {
    render(<ProfitComparison data={DONT_SWITCH_PROFITABILITY} />);
    const diffBanner = screen.getByTestId('profit-diff-banner');
    expect(diffBanner).toHaveTextContent('-₹2,000');
  });
});

describe('ProfitabilityPage — Integration Flow', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    // Re-apply storage mock after restoreAllMocks
    vi.spyOn(storage, 'getFarmDetails').mockReturnValue({ farm_id: 1, farm_name: 'Test Farm', land_area: 1, current_crop: 'Paddy', water_availability: 'Available', district: 'Test', state: 'Test' });
  });

  it('loads and renders profitability metrics and visual chart', async () => {
    vi.spyOn(apiService, 'getProfitability').mockResolvedValue(GOLDEN_DEMO_PROFITABILITY);

    renderPage();

    // Shows loading briefly after useEffect fires
    await screen.findByTestId('profitability-loading');

    // Resolves content
    await waitFor(() => {
      expect(screen.getByText('Profitability Comparison')).toBeInTheDocument();
      expect(screen.getByTestId('current-crop-name')).toHaveTextContent('Paddy');
      expect(screen.getByTestId('recommended-crop-name')).toHaveTextContent('Groundnut');
    });

    // Chart container rendered
    expect(screen.getByTestId('profit-chart-container')).toBeInTheDocument();

    // Navigation buttons present
    expect(screen.getByRole('button', { name: /view market intelligence/i })).toBeInTheDocument();
  });

  it('handles error state gracefully with retry button', async () => {
    vi.spyOn(apiService, 'getProfitability').mockRejectedValue(new Error('Network error'));

    renderPage();

    await waitFor(() => {
      // useApiState maps unknown errors to a generic friendly message
      expect(screen.getByRole('alert')).toBeInTheDocument();
    });

    expect(screen.getByRole('button', { name: /try again/i })).toBeInTheDocument();
  });
});
