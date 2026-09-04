import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import MainLayout from './layouts/MainLayout';
import HomePage from './pages/HomePage';
import FarmInfoPage from './pages/FarmInfoPage';
import RecommendationPage from './pages/RecommendationPage';
import ProfitAndMarketPage from './pages/ProfitAndMarketPage';
import MapPage from './pages/MapPage';
import SubsidiesPage from './pages/SubsidiesPage';
import RiskSimulationPage from './pages/RiskSimulationPage';
import IvrPage from './pages/IvrPage';
import BiddingPage from './pages/BiddingPage';
import BuyerPortalPage from './pages/BuyerPortalPage';
import NotFoundPage from './pages/NotFoundPage';
import LoginPage from './pages/LoginPage';
import { AuthProvider } from './contexts/AuthContext';
import { LanguageProvider } from './contexts/LanguageContext';

import ErrorBoundary from './components/common/ErrorBoundary';
import ProtectedRoute from './components/common/ProtectedRoute';

export default function App() {
  return (
    <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <AuthProvider>
        <LanguageProvider>
          <ErrorBoundary>
            <MainLayout>
              <Routes>
                <Route path="/login" element={<LoginPage />} />
                <Route
                  path="/"
                  element={
                    <ProtectedRoute allowedRoles={['FARMER']}>
                      <HomePage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/farm-info"
                  element={
                    <ProtectedRoute allowedRoles={['FARMER']}>
                      <FarmInfoPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/analyze"
                  element={
                    <ProtectedRoute allowedRoles={['FARMER']}>
                      <FarmInfoPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/recommendation"
                  element={
                    <ProtectedRoute allowedRoles={['FARMER']}>
                      <RecommendationPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/profit"
                  element={
                    <ProtectedRoute allowedRoles={['FARMER']}>
                      <ProfitAndMarketPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/market"
                  element={
                    <ProtectedRoute allowedRoles={['FARMER']}>
                      <ProfitAndMarketPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/map"
                  element={
                    <ProtectedRoute allowedRoles={['FARMER']}>
                      <MapPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/subsidies"
                  element={
                    <ProtectedRoute allowedRoles={['FARMER']}>
                      <SubsidiesPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/risk"
                  element={
                    <ProtectedRoute allowedRoles={['FARMER']}>
                      <RiskSimulationPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/ivr"
                  element={
                    <ProtectedRoute allowedRoles={['FARMER']}>
                      <IvrPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/bidding"
                  element={
                    <ProtectedRoute allowedRoles={['FARMER', 'BUYER']}>
                      <BiddingPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/buyer"
                  element={
                    <ProtectedRoute allowedRoles={['BUYER']}>
                      <BuyerPortalPage />
                    </ProtectedRoute>
                  }
                />
                <Route path="*" element={<NotFoundPage />} />
              </Routes>
            </MainLayout>
          </ErrorBoundary>
        </LanguageProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}
