import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import SafetyScoreGauge from '../components/score/SafetyScoreGauge';
import ScoreBreakdown from '../components/score/ScoreBreakdown';
import IvrPage from '../pages/IvrPage';

// IvrPage needs API mock
vi.mock('../services/api', () => ({
  getIvrRecommendation: vi.fn(),
}));

// ============================================================================
// SafetyScoreGauge — ARIA
// ============================================================================
describe('SafetyScoreGauge — ARIA accessibility', () => {
  it('SVG has role="img" and descriptive aria-label for Low Safety', () => {
    render(<SafetyScoreGauge score={45} />);
    const svg = document.querySelector('svg[role="img"]');
    expect(svg).not.toBeNull();
    expect(svg!.getAttribute('aria-label')).toMatch(/Safety score 45 out of 100/i);
    expect(svg!.getAttribute('aria-label')).toMatch(/Low Safety/i);
  });

  it('SVG aria-label reflects Moderate Safety for score 70', () => {
    render(<SafetyScoreGauge score={70} />);
    const svg = document.querySelector('svg[role="img"]');
    expect(svg!.getAttribute('aria-label')).toMatch(/70 out of 100/i);
    expect(svg!.getAttribute('aria-label')).toMatch(/Moderate Safety/i);
  });

  it('SVG aria-label reflects High Safety for score 85', () => {
    render(<SafetyScoreGauge score={85} />);
    const svg = document.querySelector('svg[role="img"]');
    expect(svg!.getAttribute('aria-label')).toMatch(/85 out of 100/i);
    expect(svg!.getAttribute('aria-label')).toMatch(/High Safety/i);
  });

  it('amber score text uses text-amber-700 (WCAG AA contrast)', () => {
    render(<SafetyScoreGauge score={70} />);
    const scoreEl = screen.getByTestId('gauge-score-value');
    expect(scoreEl.className).toContain('text-amber-700');
    expect(scoreEl.className).not.toContain('text-amber-500');
  });
});

// ============================================================================
// ScoreBreakdown — progress bar ARIA
// ============================================================================
describe('ScoreBreakdown — progress bar ARIA attributes', () => {
  const props = {
    suitabilityScore: 87,
    profitabilityScore: 76,
    marketScore: 90,
    riskScore: 28,
  };

  it('all four progress bars have role="progressbar" and correct aria-valuenow', () => {
    render(<ScoreBreakdown {...props} />);
    const bars = screen.getAllByRole('progressbar');
    expect(bars).toHaveLength(4);
    const values = bars.map(b => b.getAttribute('aria-valuenow'));
    expect(values).toContain('87');
    expect(values).toContain('76');
    expect(values).toContain('90');
    expect(values).toContain('28');
  });

  it('progress bars have aria-valuemin="0" and aria-valuemax="100"', () => {
    render(<ScoreBreakdown {...props} />);
    const bars = screen.getAllByRole('progressbar');
    bars.forEach(bar => {
      expect(bar).toHaveAttribute('aria-valuemin', '0');
      expect(bar).toHaveAttribute('aria-valuemax', '100');
    });
  });
});

// ============================================================================
import { MemoryRouter } from 'react-router-dom';

// IvrPage — SlideToCall & Helpline accessibility
// ============================================================================
describe('IvrPage SlideToCall & controls — accessibility', () => {
  const renderIvr = () =>
    render(
      <MemoryRouter>
        <IvrPage />
      </MemoryRouter>
    );

  it('SlideToCall slider has role="slider" and ARIA attributes', () => {
    renderIvr();
    const slider = screen.getByRole('slider');
    expect(slider).toBeInTheDocument();
    expect(slider).toHaveAttribute('aria-valuemin', '0');
    expect(slider).toHaveAttribute('aria-valuemax', '100');
    expect(slider).toHaveAttribute('aria-label');
  });

  it('SlideToCall container has focus:ring-2 class for keyboard visibility', () => {
    renderIvr();
    const slider = screen.getByRole('slider');
    expect(slider.className).toContain('focus:ring-2');
  });

  it('SlideToCall has minimum height h-14 for touch target', () => {
    renderIvr();
    const slider = screen.getByRole('slider');
    expect(slider.className).toContain('h-14');
  });

  it('Direct helpline link has minimum touch target class min-h-[44px]', () => {
    renderIvr();
    const helplineLink = screen.getByRole('link', { name: /09513886363/i });
    expect(helplineLink.className).toContain('min-h-[44px]');
  });
});

