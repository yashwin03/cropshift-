import React from 'react';
import { render, screen, within } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import RecommendationPage from '../pages/RecommendationPage';
import type { RecommendationResponse } from '../types/api';

/* ─── Mocks ───────────────────────────────────────────────────────────────── */

const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual<typeof import('react-router-dom')>('react-router-dom');
  return { ...actual, useNavigate: () => mockNavigate };
});

/* ─── Fixtures ────────────────────────────────────────────────────────────── */

const SWITCH_REC: RecommendationResponse = {
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
  reasons: ['Suitable for your farm', 'Higher expected profit', 'Favorable market conditions'],
  risks: ['Market price may fluctuate'],
};

const CAUTION_REC: RecommendationResponse = {
  ...SWITCH_REC,
  safety_score: 72,
  decision: 'CAUTION',
  profit_difference: 6000,
  recommended_crop: 'Cotton',
  reasons: ['Moderate suitability'],
  risks: ['Requires more water monitoring'],
};

const DONT_SWITCH_REC: RecommendationResponse = {
  ...SWITCH_REC,
  safety_score: 90,
  decision: 'DONT_SWITCH',
  profit_difference: -2000,
  recommended_crop: 'Paddy',
  reasons: ['Highly suitable for current water availability'],
  risks: [],
};

/* ─── Helpers ─────────────────────────────────────────────────────────────── */

import { saveRecommendation } from '../utils/storage';

const seedStorage = (rec: RecommendationResponse) => {
  saveRecommendation(rec);
};

const renderPage = () =>
  render(
    <BrowserRouter>
      <RecommendationPage />
    </BrowserRouter>
  );

/* ─── Tests ───────────────────────────────────────────────────────────────── */

describe('RecommendationPage — null guard', () => {
  beforeEach(() => { localStorage.clear(); mockNavigate.mockReset(); });

  it('renders EmptyState with CTA when no recommendation in storage', () => {
    renderPage();
    expect(screen.getByText('No Recommendation Yet')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /start analysis/i })).toBeInTheDocument();
  });
});

describe('RecommendationPage — SWITCH decision', () => {
  beforeEach(() => { localStorage.clear(); mockNavigate.mockReset(); seedStorage(SWITCH_REC); });

  it('renders recommended crop name prominently', () => {
    renderPage();
    expect(screen.getByTestId('recommended-crop')).toHaveTextContent('Groundnut');
  });

  it('renders safety score as received — no arithmetic', () => {
    renderPage();
    expect(screen.getByTestId('safety-score')).toHaveTextContent('82');
  });

  it('renders SWITCH decision badge with correct label', () => {
    renderPage();
    const badge = screen.getByText('Good to Switch');
    expect(badge).toBeInTheDocument();
    expect(badge.closest('[data-decision="SWITCH"]')).toBeTruthy();
  });

  it('renders positive profit difference with + sign and green styling', () => {
    renderPage();
    const profitEl = screen.getByTestId('profit-difference');
    expect(profitEl).toHaveTextContent('+');
    expect(profitEl).toHaveTextContent('9,000');
    expect(profitEl.className).toMatch(/green/);
  });

  it('renders all three reasons as a checklist', () => {
    renderPage();
    expect(screen.getByText('Suitable for your farm')).toBeInTheDocument();
    expect(screen.getByText('Higher expected profit')).toBeInTheDocument();
    expect(screen.getByText('Favorable market conditions')).toBeInTheDocument();
  });

  it('renders risks card when risks array is non-empty', () => {
    renderPage();
    expect(screen.getByText('Market price may fluctuate')).toBeInTheDocument();
  });

  it('renders all five onward navigation links', () => {
    renderPage();
    expect(screen.getByRole('button', { name: /compare money earned/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /prices & market access/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /nearby markets & distance/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /schemes you may qualify for/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /what-if scenarios/i })).toBeInTheDocument();
  });

  it('renders safety score gauge and factor score breakdown', () => {
    renderPage();
    expect(screen.getByTestId('safety-score-gauge')).toBeInTheDocument();
    expect(screen.getByText('Score Breakdown & Factors')).toBeInTheDocument();
    expect(screen.getByTestId('score-item-suitability')).toBeInTheDocument();
  });
});

describe('RecommendationPage — CAUTION decision', () => {
  beforeEach(() => { localStorage.clear(); mockNavigate.mockReset(); seedStorage(CAUTION_REC); });

  it('renders CAUTION badge with amber styling', () => {
    renderPage();
    const badge = screen.getByText('Proceed with Caution');
    expect(badge).toBeInTheDocument();
    const container = badge.closest('[data-decision="CAUTION"]');
    expect(container).toBeTruthy();
    expect(container!.className).toMatch(/amber/);
  });
});

describe('RecommendationPage — DONT_SWITCH decision', () => {
  beforeEach(() => { localStorage.clear(); mockNavigate.mockReset(); seedStorage(DONT_SWITCH_REC); });

  it('renders DONT_SWITCH badge with red styling', () => {
    renderPage();
    const badge = screen.getByText('Stay with Current Crop');
    expect(badge).toBeInTheDocument();
    const container = badge.closest('[data-decision="DONT_SWITCH"]');
    expect(container).toBeTruthy();
    expect(container!.className).toMatch(/red/);
  });

  it('renders negative profit difference with - sign and red styling', () => {
    renderPage();
    const profitEl = screen.getByTestId('profit-difference');
    expect(profitEl).toHaveTextContent('-');
    expect(profitEl).toHaveTextContent('2,000');
    expect(profitEl.className).toMatch(/red/);
  });

  it('does NOT render risks card when risks array is empty', () => {
    renderPage();
    expect(screen.queryByText('Risks to Be Aware Of')).not.toBeInTheDocument();
  });
});

describe('RecommendationPage — six required elements present', () => {
  beforeEach(() => { localStorage.clear(); seedStorage(SWITCH_REC); });

  it('all six required elements are present for a SWITCH response', () => {
    renderPage();
    // 1. Recommended crop
    expect(screen.getByTestId('recommended-crop')).toBeInTheDocument();
    // 2. Safety score
    expect(screen.getByTestId('safety-score')).toBeInTheDocument();
    // 3. Decision badge
    expect(screen.getByText('Good to Switch')).toBeInTheDocument();
    // 4. Profit difference
    expect(screen.getByTestId('profit-difference')).toBeInTheDocument();
    // 5. Reasons section
    expect(screen.getByText('Why This Recommendation?')).toBeInTheDocument();
    // 6. Risks section
    expect(screen.getByText('Risks to Be Aware Of')).toBeInTheDocument();
  });
});
