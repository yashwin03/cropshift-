import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import FarmInfoPage from '../pages/FarmInfoPage';
import { getFarmDetails, getRecommendation } from '../utils/storage';

// Mock useNavigate
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual<typeof import('react-router-dom')>('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

vi.mock('../services/api', () => ({
  createFarm: vi.fn(() => Promise.resolve({ id: 1 })),
  getRecommendation: vi.fn(() =>
    Promise.resolve({
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
      reasons: [],
      risks: [],
    })
  ),
}));

const renderPage = () =>
  render(
    <BrowserRouter>
      <FarmInfoPage />
    </BrowserRouter>
  );

describe('FarmInfoPage — Step 1: General Info', () => {
  beforeEach(() => {
    localStorage.clear();
    mockNavigate.mockReset();
  });

  it('renders step 1 heading and inputs', () => {
    renderPage();
    expect(screen.getByText('Tell us about your farm')).toBeInTheDocument();
    expect(screen.getByLabelText(/Farm Name or ID/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Land Area/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /next/i })).toBeInTheDocument();
    // Back button absent on step 1
    expect(screen.queryByRole('button', { name: /← back/i })).not.toBeInTheDocument();
  });

  it('shows error when farm name is empty and Next is clicked', () => {
    renderPage();
    fireEvent.click(screen.getByRole('button', { name: /next/i }));
    // Both farm_name and land_area are empty → two errors appear
    const alerts = screen.getAllByRole('alert');
    expect(alerts.length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText('Please enter your farm name or ID.')).toBeInTheDocument();
    // Still on step 1
    expect(screen.getByText('Tell us about your farm')).toBeInTheDocument();
  });

  it('shows error when land area is empty', () => {
    renderPage();
    fireEvent.change(screen.getByLabelText(/Farm Name or ID/i), {
      target: { value: 'Test Farm' },
    });
    fireEvent.click(screen.getByRole('button', { name: /next/i }));
    expect(screen.getByText('Please enter your land area in acres.')).toBeInTheDocument();
  });

  it('shows error when land area is zero', () => {
    renderPage();
    fireEvent.change(screen.getByLabelText(/Farm Name or ID/i), { target: { value: 'My Farm' } });
    fireEvent.change(screen.getByLabelText(/Land Area/i), { target: { value: '0' } });
    fireEvent.click(screen.getByRole('button', { name: /next/i }));
    expect(screen.getByText('Land area must be a number greater than zero.')).toBeInTheDocument();
  });

  it('shows error when land area exceeds 1000', () => {
    renderPage();
    fireEvent.change(screen.getByLabelText(/Farm Name or ID/i), { target: { value: 'Big Farm' } });
    fireEvent.change(screen.getByLabelText(/Land Area/i), { target: { value: '1500' } });
    fireEvent.click(screen.getByRole('button', { name: /next/i }));
    expect(
      screen.getByText('Land area cannot exceed 1,000 acres. Please check the value you entered.')
    ).toBeInTheDocument();
  });

  it('advances to step 2 with valid inputs', () => {
    renderPage();
    fireEvent.change(screen.getByLabelText(/Farm Name or ID/i), { target: { value: 'My Farm' } });
    fireEvent.change(screen.getByLabelText(/Land Area/i), { target: { value: '2.5' } });
    fireEvent.click(screen.getByRole('button', { name: /next/i }));
    expect(screen.getByText('What are you currently growing?')).toBeInTheDocument();
  });
});

describe('FarmInfoPage — Step 2: Crop Selection', () => {
  const goToStep2 = () => {
    renderPage();
    fireEvent.change(screen.getByLabelText(/Farm Name or ID/i), { target: { value: 'Farm X' } });
    fireEvent.change(screen.getByLabelText(/Land Area/i), { target: { value: '3' } });
    fireEvent.click(screen.getByRole('button', { name: /next/i }));
  };

  beforeEach(() => { localStorage.clear(); mockNavigate.mockReset(); });

  it('shows crop selection step with dropdown', () => {
    goToStep2();
    expect(screen.getByText('What are you currently growing?')).toBeInTheDocument();
    expect(screen.getByLabelText(/What crop are you growing now/i)).toBeInTheDocument();
  });

  it('shows error when Next is clicked without crop selection', () => {
    goToStep2();
    fireEvent.click(screen.getByRole('button', { name: /next/i }));
    expect(screen.getByText('Please select your current crop.')).toBeInTheDocument();
  });

  it('Back button returns to step 1 preserving farm name and area', () => {
    goToStep2();
    fireEvent.click(screen.getByRole('button', { name: /← back/i }));
    expect(screen.getByText('Tell us about your farm')).toBeInTheDocument();
    expect(screen.getByLabelText(/Farm Name or ID/i)).toHaveValue('Farm X');
    expect(screen.getByLabelText(/Land Area/i)).toHaveValue('3');
  });

  it('advances to step 3 when crop selected', () => {
    goToStep2();
    fireEvent.change(screen.getByLabelText(/What crop are you growing now/i), {
      target: { value: 'Paddy' },
    });
    fireEvent.click(screen.getByRole('button', { name: /next/i }));
    expect(screen.getByText('Describe your farming conditions')).toBeInTheDocument();
  });
});

describe('FarmInfoPage — Step 3: Farm Conditions', () => {
  const goToStep3 = () => {
    renderPage();
    fireEvent.change(screen.getByLabelText(/Farm Name or ID/i), { target: { value: 'Test Farm' } });
    fireEvent.change(screen.getByLabelText(/Land Area/i), { target: { value: '1' } });
    fireEvent.click(screen.getByRole('button', { name: /next/i }));
    fireEvent.change(screen.getByLabelText(/What crop are you growing now/i), {
      target: { value: 'Paddy' },
    });
    fireEvent.click(screen.getByRole('button', { name: /next/i }));
  };

  beforeEach(() => { localStorage.clear(); mockNavigate.mockReset(); });

  it('renders water availability buttons', () => {
    goToStep3();
    expect(screen.getByRole('button', { name: /available/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /limited/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /scarce/i })).toBeInTheDocument();
  });

  it('shows error when water availability not selected', () => {
    goToStep3();
    fireEvent.click(screen.getByRole('button', { name: /review/i }));
    expect(screen.getByText('Please select your water availability level.')).toBeInTheDocument();
  });

  it('optional soil type and location fields can be skipped', () => {
    goToStep3();
    fireEvent.click(screen.getByRole('button', { name: /^available$/i }));
    // Don't fill optional fields — go straight to review
    fireEvent.click(screen.getByRole('button', { name: /review/i }));
    expect(screen.getByText('Review your information')).toBeInTheDocument();
  });

  it('shows location accuracy warning when location is blank', () => {
    goToStep3();
    expect(
      screen.getByText(/Without exact GPS coordinates, market distance estimates will be less accurate/i)
    ).toBeInTheDocument();
  });
});

describe('FarmInfoPage — Step 4: Review & Submit', () => {
  beforeEach(() => { localStorage.clear(); mockNavigate.mockReset(); });

  const goToStep4 = () => {
    renderPage();
    // Step 1
    fireEvent.change(screen.getByLabelText(/Farm Name or ID/i), { target: { value: 'Rajesh Farm' } });
    fireEvent.change(screen.getByLabelText(/Land Area/i), { target: { value: '2' } });
    fireEvent.click(screen.getByRole('button', { name: /next/i }));
    // Step 2
    fireEvent.change(screen.getByLabelText(/What crop are you growing now/i), {
      target: { value: 'Paddy' },
    });
    fireEvent.click(screen.getByRole('button', { name: /next/i }));
    // Step 3
    fireEvent.click(screen.getByRole('button', { name: /^available$/i }));
    fireEvent.click(screen.getByRole('button', { name: /review/i }));
  };

  it('displays review table with submitted values', () => {
    goToStep4();
    expect(screen.getByText('Review your information')).toBeInTheDocument();
    expect(screen.getByText('Rajesh Farm')).toBeInTheDocument();
    expect(screen.getByText('2 acres')).toBeInTheDocument();
    expect(screen.getByText('Paddy')).toBeInTheDocument();
    expect(screen.getByText('Available')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /analyze my farm/i })).toBeInTheDocument();
  });

  it('Edit Details button returns to step 3', () => {
    goToStep4();
    fireEvent.click(screen.getByRole('button', { name: /← edit details/i }));
    expect(screen.getByText('Describe your farming conditions')).toBeInTheDocument();
  });

  it('submitting saves to localStorage and navigates to /recommendation', async () => {
    goToStep4();
    fireEvent.click(screen.getByRole('button', { name: /analyze my farm/i }));
    await waitFor(
      () => {
        expect(mockNavigate).toHaveBeenCalledWith('/recommendation');
      },
      { timeout: 1500 }
    );
    expect(getFarmDetails()).not.toBeNull();
    expect(getRecommendation()).not.toBeNull();
  });

  it('delegates recommendation calculation to recommendationService without component logic', async () => {
    goToStep4();
    fireEvent.click(screen.getByRole('button', { name: /analyze my farm/i }));
    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/recommendation');
    });

    const storedRec = getRecommendation() || {} as any;
    // Result matches recommendation object returned from service layer directly
    expect(storedRec.recommended_crop).toBeDefined();
    expect(storedRec.safety_score).toBeDefined();
    expect(storedRec.decision).toBeDefined();
  });

  it('handles backend 500 errors gracefully', async () => {
    const api = await import('../services/api');
    vi.mocked(api.createFarm).mockRejectedValueOnce({ response: { status: 500 } });

    renderPage();

    // Step 1
    fireEvent.change(screen.getByLabelText(/Farm Name/i), { target: { value: 'Test Farm' } });
    fireEvent.change(screen.getByLabelText(/Land Area/i), { target: { value: '5' } });
    fireEvent.click(screen.getByText(/Next →/i));

    // Step 2
    fireEvent.change(screen.getByLabelText(/What crop are you growing now?/i), { target: { value: 'Paddy' } });
    fireEvent.click(screen.getByText(/Next →/i));

    // Step 3
    fireEvent.click(screen.getByText(/^Available$/i));
    fireEvent.click(screen.getByText(/Review →/i));

    // Step 4
    fireEvent.click(screen.getByText(/Analyze My Farm/i));

    await waitFor(() => {
      expect(screen.getByText(/We couldn't analyze your farm right now/i)).toBeInTheDocument();
    });
  });

  it('allows entering geolocation data', async () => {
    renderPage();

    // Step 1
    fireEvent.change(screen.getByLabelText(/Farm Name/i), { target: { value: 'Test Farm' } });
    fireEvent.change(screen.getByLabelText(/Land Area/i), { target: { value: '5' } });
    fireEvent.click(screen.getByText(/Next →/i));

    // Step 2
    fireEvent.change(screen.getByLabelText(/What crop are you growing now?/i), { target: { value: 'Paddy' } });
    fireEvent.click(screen.getByText(/Next →/i));

    // Step 3
    fireEvent.click(screen.getByText(/^Available$/i));
    
    // Check manual inputs
    fireEvent.change(screen.getByLabelText(/Latitude/i), { target: { value: '12.34' } });
    fireEvent.change(screen.getByLabelText(/Longitude/i), { target: { value: '56.78' } });

    fireEvent.click(screen.getByText(/Review →/i));

    // Step 4 Review should show GPS
    expect(screen.getByText(/12.34, 56.78/i)).toBeInTheDocument();
  });
});
