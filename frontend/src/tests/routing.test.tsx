import React from 'react';
import { render, screen } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { describe, it, expect, vi } from 'vitest';

// --- Mock all API services used by pages ---
vi.mock('../services/api', () => ({
  getFarmRecommendation: vi.fn(),
  getProfitability: vi.fn(),
  getMarketData: vi.fn(),
  getMapData: vi.fn(),
  getSubsidies: vi.fn(),
  runRiskSimulation: vi.fn(),
  getIvrRecommendation: vi.fn(),
}));

// Mock storage helpers used by pages that read from localStorage
vi.mock('../utils/storage', () => ({
  getFarmDetails: vi.fn(() => null),
  getRecommendation: vi.fn(() => null),
  saveFarmDetails: vi.fn(),
  saveRecommendation: vi.fn(),
  clearAllData: vi.fn(),
}));

// Import page components (after mocks are hoisted)
import HomePage from '../pages/HomePage';
import FarmInfoPage from '../pages/FarmInfoPage';
import RecommendationPage from '../pages/RecommendationPage';
import ProfitabilityPage from '../pages/ProfitabilityPage';
import MarketPage from '../pages/MarketPage';
import MapPage from '../pages/MapPage';
import SubsidiesPage from '../pages/SubsidiesPage';
import RiskSimulationPage from '../pages/RiskSimulationPage';
import IvrPage from '../pages/IvrPage';
import LoginPage from '../pages/LoginPage';
import NotFoundPage from '../pages/NotFoundPage';

import { AuthProvider } from '../contexts/AuthContext';

// Helper: render a single page at a given path using MemoryRouter
function renderRoute(path: string, element: React.ReactElement) {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <AuthProvider>
        <Routes>
          <Route path={path === '/404-nonexistent' ? '*' : path} element={element} />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </AuthProvider>
    </MemoryRouter>
  );
}

describe('Routing — all named routes resolve without crashing', () => {
  it('/ — HomePage renders', () => {
    renderRoute('/', <HomePage />);
    // HomePage shows a heading or CTA
    expect(document.body).toBeTruthy();
  });

  it('/login — LoginPage renders', () => {
    renderRoute('/login', <LoginPage />);
    expect(screen.getByText(/Choose your portal/i)).toBeInTheDocument();
  });

  it('/analyze — FarmInfoPage renders', () => {
    renderRoute('/analyze', <FarmInfoPage />);
    expect(document.body).toBeTruthy();
  });

  it('/recommendation — RecommendationPage renders (no data → empty state)', () => {
    renderRoute('/recommendation', <RecommendationPage />);
    expect(document.body).toBeTruthy();
  });

  it('/profit — ProfitabilityPage renders', () => {
    renderRoute('/profit', <ProfitabilityPage />);
    expect(document.body).toBeTruthy();
  });

  it('/market — MarketPage renders', () => {
    renderRoute('/market', <MarketPage />);
    expect(document.body).toBeTruthy();
  });

  it('/map — MapPage renders', () => {
    renderRoute('/map', <MapPage />);
    expect(document.body).toBeTruthy();
  });

  it('/subsidies — SubsidiesPage renders', () => {
    renderRoute('/subsidies', <SubsidiesPage />);
    expect(document.body).toBeTruthy();
  });

  it('/risk — RiskSimulationPage renders', () => {
    renderRoute('/risk', <RiskSimulationPage />);
    expect(document.body).toBeTruthy();
  });

  it('/ivr — IvrPage renders', () => {
    renderRoute('/ivr', <IvrPage />);
    expect(document.body).toBeTruthy();
  });
});

describe('Routing — unknown routes render NotFoundPage', () => {
  it('renders 404 page for /this-does-not-exist', () => {
    render(
      <MemoryRouter initialEntries={['/this-does-not-exist']}>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </MemoryRouter>
    );
    expect(screen.getByText(/404/i)).toBeInTheDocument();
    expect(screen.getByText(/Page Not Found/i)).toBeInTheDocument();
  });

  it('renders 404 page for /totally/unknown/path', () => {
    render(
      <MemoryRouter initialEntries={['/totally/unknown/path']}>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </MemoryRouter>
    );
    expect(screen.getByText(/404/i)).toBeInTheDocument();
    expect(screen.getByText(/Go Back Home/i)).toBeInTheDocument();
  });

  it('NotFoundPage contains a link back to /', () => {
    render(
      <MemoryRouter initialEntries={['/nonexistent']}>
        <Routes>
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </MemoryRouter>
    );
    const homeLink = screen.getByRole('link', { name: /Go Back Home/i });
    expect(homeLink).toBeInTheDocument();
    expect(homeLink).toHaveAttribute('href', '/');
  });
});
