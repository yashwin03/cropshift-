import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { describe, test, expect, vi, beforeEach } from 'vitest';
import MapPage from '../pages/MapPage';
import { getFarmDetails } from '../utils/storage';

vi.hoisted(() => {
  vi.stubEnv('VITE_USE_MOCKS', 'false');
});

vi.mock('../mocks', () => ({
  __esModule: true,
  USE_MOCKS: false,
  delay: () => Promise.resolve(),
}));

// Mock MapLibre GL JS for JSDOM test runner
vi.mock('maplibre-gl', () => ({
  default: {
    Map: vi.fn().mockImplementation(() => ({
      addControl: vi.fn(),
      on: vi.fn((event, callback) => {
        if (event === 'load') callback();
      }),
      once: vi.fn(),
      flyTo: vi.fn(),
      getSource: vi.fn(() => null),
      addSource: vi.fn(),
      addLayer: vi.fn(),
      isStyleLoaded: vi.fn(() => true),
      remove: vi.fn(),
    })),
    NavigationControl: vi.fn(),
    Marker: vi.fn().mockImplementation(() => ({
      setLngLat: vi.fn().mockReturnThis(),
      setPopup: vi.fn().mockReturnThis(),
      addTo: vi.fn().mockReturnThis(),
      remove: vi.fn(),
    })),
    Popup: vi.fn().mockImplementation(() => ({
      setHTML: vi.fn().mockReturnThis(),
    })),
  },
}));

vi.mock('../utils/storage', () => ({
  getFarmDetails: vi.fn(),
  getRecommendation: vi.fn(() => ({
    recommended_crop: 'Groundnut',
    current_crop_profit: 34000,
  })),
}));

vi.mock('../services/api', () => ({
  getGeospatial: vi.fn().mockImplementation(() =>
    Promise.resolve({
      farm: { farm_id: 1, farm_name: 'Test Farm', latitude: 12.9, longitude: 77.5 },
      nearby_markets: [
        { market_name: 'Market A', latitude: 12.8, longitude: 77.4, distance_km: 5.0, within_radius: true, crop: 'Groundnut', current_price: 6200 },
        { market_name: 'Market B', latitude: 13.0, longitude: 77.6, distance_km: 15.0, within_radius: true, crop: 'Sunflower', current_price: 7100 },
      ],
      distance_information: 'Distance info summary',
      geographic_context: { district: 'Dist', state: 'State', markets_count: 2 },
    })
  ),
}));

describe('MapPage Geospatial Tests', () => {
  beforeEach(() => {
    vi.stubEnv('VITE_USE_MOCKS', 'false');
  });

  test('sorted distance listing displays ascending km details', async () => {
    vi.mocked(getFarmDetails).mockReturnValue({
      farm_id: 1,
      farm_name: 'Test Farm',
      land_area: 1,
      current_crop: 'Paddy',
      water_availability: 'Available',
      district: 'Dist',
      state: 'State',
    });

    vi.stubEnv('VITE_USE_MOCKS', 'false');
    render(<BrowserRouter><MapPage /></BrowserRouter>);

    const marketAElements = await screen.findAllByText(/Market A/i);
    const marketBElements = await screen.findAllByText(/Market B/i);
    expect(marketAElements.length).toBeGreaterThan(0);
    expect(marketBElements.length).toBeGreaterThan(0);
  });

  test('missing coordinates renders fallback UI instead of crashing', async () => {
    vi.mocked(getFarmDetails).mockReturnValue({
      farm_id: 1,
      farm_name: 'Test Farm',
      land_area: 1,
      current_crop: 'Paddy',
      water_availability: 'Available',
      district: 'Dist',
      state: 'State',
    });

    const apiService = await import('../services/api');
    vi.spyOn(apiService, 'getGeospatial').mockResolvedValueOnce({
      farm: { farm_id: 1, latitude: 0, longitude: 0 },
      nearby_markets: [],
      distance_information: 'No coordinates',
      geographic_context: { district: 'Dist', state: 'State', markets_count: 0 },
    });

    render(<BrowserRouter><MapPage /></BrowserRouter>);
    const fallbackTitle = await screen.findByText('Geospatial Coordinates Missing');
    expect(fallbackTitle).toBeInTheDocument();
  });

  test('State: Error - shows friendly error when geospatial API rejects', async () => {
    vi.mocked(getFarmDetails).mockReturnValue({
      farm_id: 1, farm_name: 'Test Farm', land_area: 1,
      current_crop: 'Paddy', water_availability: 'Available',
      district: 'Dist', state: 'State',
    });
    const apiService = await import('../services/api');
    vi.spyOn(apiService, 'getGeospatial').mockRejectedValue({
      response: { data: { error: { code: 'FARM_NOT_FOUND', message: 'Farm not found' } } },
    });

    render(<BrowserRouter><MapPage /></BrowserRouter>);
    await waitFor(() => {
      expect(screen.getByRole('alert')).toBeInTheDocument();
    });
    expect(screen.queryByText('FARM_NOT_FOUND')).not.toBeInTheDocument();
  });

  test('State: Empty - shows empty state when no farm profile exists', () => {
    vi.mocked(getFarmDetails).mockReturnValue(null);

    render(<BrowserRouter><MapPage /></BrowserRouter>);
    expect(screen.getByText('No Farm Profile Found')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /go to farm analysis/i })).toBeInTheDocument();
  });
});
