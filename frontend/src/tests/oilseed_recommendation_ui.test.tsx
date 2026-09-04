import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import React from 'react';
import { MemoryRouter } from 'react-router-dom';
import RecommendationPage from '../pages/RecommendationPage';
import * as storage from '../utils/storage';
import * as peerProofService from '../services/peerProofService';

vi.mock('../services/peerProofService');

describe('Oilseed Recommendation UI Integration Test Suite', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();

    vi.spyOn(peerProofService, 'getPeerProof').mockResolvedValue({
      available: true,
      crop_id: 2,
      crop_name: 'Groundnut',
      cohort_count: 12,
      geographic_scope: 'Your district',
      season: 'Kharif 2025',
      farm_size_range: '1.0 - 5.0 acres',
      average_yield_quintals_per_acre: 9.5,
      average_selling_price_per_quintal: 6000,
      average_net_realization_per_acre: 45000,
      data_source: 'CropShift verified farmer records',
      verification_status: 'Self-reported & Verified',
      peers: [],
    });
  });

  const mockRecommendation = {
    recommended_crop: 'Groundnut',
    suitability_score: 87,
    profitability_score: 82,
    market_score: 75,
    risk_score: 25,
    safety_score: 85,
    decision: 'SWITCH' as const,
    expected_profit: 48000,
    current_crop_profit: 18000,
    profit_difference: 30000,
    reasons: ['Excellent soil compatibility with Groundnut', 'High net profit gain per acre'],
    risks: ['Pest outbreak risk in monsoon season'],
    farm_suitability_score: 92,
    water_suitability_score: 88,
    economic_potential_score: 84,
    overall_score: 88,
    top_oilseeds: [
      {
        rank: 1,
        crop_id: 2,
        crop_name: 'Groundnut',
        farm_suitability_score: 92,
        water_suitability_score: 88,
        economic_potential_score: 84,
        overall_score: 88,
        decision: 'SWITCH' as const,
        expected_profit: 48000,
        profit_difference: 30000,
      },
      {
        rank: 2,
        crop_id: 3,
        crop_name: 'Sunflower',
        farm_suitability_score: 82,
        water_suitability_score: 80,
        economic_potential_score: 78,
        overall_score: 80,
        decision: 'SWITCH' as const,
        expected_profit: 40000,
        profit_difference: 22000,
      },
    ],
  };

  const mockFarm = {
    id: 1,
    land_area: 2.0,
    current_crop: 'Paddy',
    district: 'Tumkur',
    state: 'Karnataka',
    soil_type: 'red laterite',
    water_availability: true,
  };

  it('1. Renders #1 BEST MATCH Oilseed prominently with component scores', () => {
    vi.spyOn(storage, 'getRecommendation').mockReturnValue(mockRecommendation as any);
    vi.spyOn(storage, 'getFarmDetails').mockReturnValue(mockFarm as any);

    render(
      <MemoryRouter>
        <RecommendationPage />
      </MemoryRouter>
    );

    expect(screen.getByText(/BEST MATCH/i)).toBeInTheDocument();
    expect(screen.getByTestId('recommended-crop')).toHaveTextContent('Groundnut');
    expect(screen.getAllByText('Farm Suitability').length).toBeGreaterThan(0);
    expect(screen.getByText('Water / Resource Suitability')).toBeInTheDocument();
    expect(screen.getByText('Economic Potential')).toBeInTheDocument();
    expect(screen.getAllByText('92%').length).toBeGreaterThan(0);
    expect(screen.getAllByText('88%').length).toBeGreaterThan(0);
    expect(screen.getAllByText('84%').length).toBeGreaterThan(0);
  });

  it('2. Renders "Why This Recommendation?" explanation checklist', () => {
    vi.spyOn(storage, 'getRecommendation').mockReturnValue(mockRecommendation as any);
    vi.spyOn(storage, 'getFarmDetails').mockReturnValue(mockFarm as any);

    render(
      <MemoryRouter>
        <RecommendationPage />
      </MemoryRouter>
    );

    expect(screen.getByText('Excellent soil compatibility with Groundnut')).toBeInTheDocument();
  });

  it('3. Renders Top 10 Oilseeds list in ranked order', () => {
    vi.spyOn(storage, 'getRecommendation').mockReturnValue(mockRecommendation as any);
    vi.spyOn(storage, 'getFarmDetails').mockReturnValue(mockFarm as any);

    render(
      <MemoryRouter>
        <RecommendationPage />
      </MemoryRouter>
    );

    expect(screen.getByText(/Other Suitable Oilseed Candidates/i)).toBeInTheDocument();
    expect(screen.getByText('#1')).toBeInTheDocument();
    expect(screen.getByText('#2')).toBeInTheDocument();
    expect(screen.getByText('Sunflower')).toBeInTheDocument();
  });

  it('4. Navigation CTA to Explore Buyer Opportunities exists', () => {
    vi.spyOn(storage, 'getRecommendation').mockReturnValue(mockRecommendation as any);
    vi.spyOn(storage, 'getFarmDetails').mockReturnValue(mockFarm as any);

    render(
      <MemoryRouter>
        <RecommendationPage />
      </MemoryRouter>
    );

    expect(screen.getAllByText(/Explore Opportunities/i).length).toBeGreaterThan(0);
  });
});
