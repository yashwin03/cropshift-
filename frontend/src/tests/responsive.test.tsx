import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import ProfitComparison from '../components/profit/ProfitComparison';
import type { ProfitabilityResponse } from '../types/api';

const mockProfitData: ProfitabilityResponse = {
  current_crop: {
    crop_name: 'Cotton',
    expected_yield: 8,
    yield_unit: 'Quintal',
    production_cost: 25000,
    expected_revenue: 60000,
    estimated_profit: 35000,
    data_status: 'MOCK',
  },
  recommended_crop: {
    crop_name: 'Groundnut',
    expected_yield: 10,
    yield_unit: 'Quintal',
    production_cost: 22000,
    expected_revenue: 75000,
    estimated_profit: 53000,
    data_status: 'MOCK',
  },
  profit_difference: 18000,
};

describe('ProfitComparison Responsive Visibility', () => {
  it('renders both mobile and desktop structures for responsive visibility', () => {
    render(
      <BrowserRouter>
        <ProfitComparison data={mockProfitData} />
      </BrowserRouter>
    );

    // Assert that the responsive container elements are present in the DOM
    const mobileContainer = screen.getByTestId('comparison-table-mobile');
    const desktopContainer = screen.getByTestId('comparison-table-desktop');

    expect(mobileContainer).toBeInTheDocument();
    expect(desktopContainer).toBeInTheDocument();

    // Verify Tailwind classes are applied correctly for breakpoint behavior
    expect(mobileContainer.className).toContain('block md:hidden');
    expect(desktopContainer.className).toContain('hidden md:block');
  });
});
