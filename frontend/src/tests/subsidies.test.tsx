import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { describe, test, expect, vi, beforeEach } from 'vitest';
import SubsidyCard from '../components/subsidy/SubsidyCard';
import SubsidiesPage from '../pages/SubsidiesPage';
import type { SubsidyScheme } from '../types/api';
import * as storage from '../utils/storage';
import * as apiService from '../services/api';

vi.mock('../utils/storage', () => ({
  getFarmDetails: vi.fn(),
}));

vi.mock('../services/api', () => ({
  getSubsidies: vi.fn(),
}));

const MOCK_FARM = {
  farm_id: 1, farm_name: 'Test Farm', land_area: 1,
  current_crop: 'Paddy', water_availability: 'Available',
  district: 'Test', state: 'Test',
};

const BASE_SCHEME: SubsidyScheme = {
  scheme_id: 'test_1', scheme_name: 'Test Scheme', relevance: 'HIGH',
  eligibility_status: 'LIKELY_ELIGIBLE', eligibility_factors: ['Factor 1'],
  required_information: ['Doc 1'], support_information: 'Support detail',
  verification_required: false, data_source: 'Source gov',
};

describe('Subsidy Matcher Tests', () => {
  test('all three eligibility statuses render correct wording', () => {
    const { rerender } = render(<SubsidyCard scheme={BASE_SCHEME} />);
    expect(screen.getByTestId('eligibility-status-banner')).toHaveTextContent('Match Status: You may qualify');
    rerender(<SubsidyCard scheme={{ ...BASE_SCHEME, eligibility_status: 'VERIFICATION_REQUIRED' }} />);
    expect(screen.getByTestId('eligibility-status-banner')).toHaveTextContent('Match Status: Land Ownership & Aadhaar Verification Required');
    rerender(<SubsidyCard scheme={{ ...BASE_SCHEME, eligibility_status: 'LIKELY_NOT_ELIGIBLE' }} />);
    expect(screen.getByTestId('eligibility-status-banner')).toHaveTextContent('Likely not applicable');
  });

  test('verification notice shows final eligibility confirmation notice', () => {
    render(<SubsidyCard scheme={BASE_SCHEME} />);
    expect(screen.getByTestId('verification-notice')).toBeInTheDocument();
    expect(screen.getByText(/Final eligibility must be confirmed/i)).toBeInTheDocument();
  });
});

describe('SubsidiesPage - B14 State Coverage', () => {
  beforeEach(() => { vi.clearAllMocks(); });
  const renderPage = () => render(<BrowserRouter><SubsidiesPage /></BrowserRouter>);

  test('State: Empty (no farm) - shows EmptyState with profile CTA', () => {
    vi.mocked(storage.getFarmDetails).mockReturnValue(null);
    renderPage();
    expect(screen.getByText('No Farm Profile Found')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /go to farm analysis/i })).toBeInTheDocument();
  });

  test('State: Loading - shows spinner while subsidies fetch', async () => {
    vi.mocked(storage.getFarmDetails).mockReturnValue(MOCK_FARM);
    vi.mocked(apiService.getSubsidies).mockImplementation(
      () => new Promise(resolve => setTimeout(() => resolve([BASE_SCHEME]), 2000))
    );
    renderPage();
    const spinner = await screen.findByRole('status');
    expect(spinner).toBeInTheDocument();
  });

  test('State: Error - shows friendly alert when API rejects', async () => {
    vi.mocked(storage.getFarmDetails).mockReturnValue(MOCK_FARM);
    vi.mocked(apiService.getSubsidies).mockRejectedValue({
      response: { data: { error: { code: 'INTERNAL_ERROR', message: 'Server error' } } },
    });
    renderPage();
    await waitFor(() => { expect(screen.getByRole('alert')).toBeInTheDocument(); });
    expect(screen.queryByText('INTERNAL_ERROR')).not.toBeInTheDocument();
  });

  test('State: Empty list - shows EmptyState when API returns no schemes', async () => {
    vi.mocked(storage.getFarmDetails).mockReturnValue(MOCK_FARM);
    vi.mocked(apiService.getSubsidies).mockResolvedValue([]);
    renderPage();
    await waitFor(() => {
      expect(screen.getByText('No Matching Schemes')).toBeInTheDocument();
    });
  });

  test('State: Backend Unavailable - NETWORK_ERROR shows friendly message', async () => {
    vi.mocked(storage.getFarmDetails).mockReturnValue(MOCK_FARM);
    vi.mocked(apiService.getSubsidies).mockRejectedValue({ code: 'NETWORK_ERROR' });
    renderPage();
    await waitFor(() => {
      const alert = screen.getByRole('alert');
      expect(alert).toHaveTextContent(/reach the server/i);
    });
  });

  test('State: Data loaded - renders scheme cards successfully', async () => {
    vi.mocked(storage.getFarmDetails).mockReturnValue(MOCK_FARM);
    vi.mocked(apiService.getSubsidies).mockResolvedValue([BASE_SCHEME]);
    renderPage();
    await waitFor(() => {
      expect(screen.getByText('Test Scheme')).toBeInTheDocument();
    });
    expect(screen.getByText('Smart Subsidy Matcher')).toBeInTheDocument();
  });
});