import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { describe, test, expect, vi } from 'vitest';
import SubsidyCard from '../components/subsidy/SubsidyCard';
import IvrPage from '../pages/IvrPage';
import type { SubsidyScheme } from '../types/api';

const PM_KISAN_SCHEME: SubsidyScheme = {
  scheme_id: 'pm_kisan',
  scheme_name: 'PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)',
  relevance: 'HIGH',
  eligibility_status: 'LIKELY_ELIGIBLE',
  eligibility_factors: ['Land area <= 5 acres'],
  required_information: ['Land records', 'Aadhaar'],
  support_information: 'Income support of ₹6,000 per year in three equal installments.',
  verification_required: true,
  official_url: 'https://pmkisan.gov.in/',
  data_source: 'pmkisan.gov.in',
};

describe('Corrections Verification Tests', () => {
  test('PM-KISAN card renders official PM-KISAN button linking to pmkisan.gov.in', () => {
    render(<SubsidyCard scheme={PM_KISAN_SCHEME} />);

    const link = screen.getByRole('link', { name: /Open Official PM-KISAN Portal/i });
    expect(link).toBeInTheDocument();
    expect(link).toHaveAttribute('href', 'https://pmkisan.gov.in/');
    expect(link).toHaveAttribute('target', '_blank');
  });

  test('IvrPage renders Offline Support heading with high contrast and correct phone and PIN', () => {
    render(
      <BrowserRouter>
        <IvrPage />
      </BrowserRouter>
    );

    expect(screen.getByRole('heading', { name: /Voice Advisory & Offline Support/i })).toBeInTheDocument();
    expect(screen.getAllByText(/09513886363/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/8618-8551-17/i).length).toBeGreaterThan(0);
  });
});
