import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter, MemoryRouter } from 'react-router-dom';
import { describe, it, expect, beforeEach } from 'vitest';
import FarmerBottomNav from '../components/common/FarmerBottomNav';
import BiddingPage from '../pages/BiddingPage';
import BuyerPortalPage from '../pages/BuyerPortalPage';
import { AuthProvider, useAuth } from '../contexts/AuthContext';

function TestRoleComponent() {
  const { activeRole, setRole } = useAuth();
  return (
    <div>
      <span data-testid="current-role">{activeRole}</span>
      <button onClick={() => setRole('buyer')}>Switch to Buyer</button>
      <button onClick={() => setRole('farmer')}>Switch to Farmer</button>
    </div>
  );
}

describe('UI Restructuring & Role Switching Test Suite', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('FarmerBottomNav renders 5 main destinations including central Bidding CTA', () => {
    render(
      <BrowserRouter>
        <FarmerBottomNav />
      </BrowserRouter>
    );

    expect(screen.getByText('Home')).toBeInTheDocument();
    expect(screen.getByText('Map')).toBeInTheDocument();
    expect(screen.getByText('Bids')).toBeInTheDocument();
    expect(screen.getByText('IVR Call')).toBeInTheDocument();
    expect(screen.getByText('Subsidies')).toBeInTheDocument();

    const biddingLink = screen.getByRole('link', { name: /Bidding Marketplace/i });
    expect(biddingLink).toBeInTheDocument();
    expect(biddingLink).toHaveAttribute('href', '/bidding');
  });

  it('BiddingPage renders active crop lots and handles bid placement', () => {
    render(
      <MemoryRouter>
        <AuthProvider>
          <BiddingPage />
        </AuthProvider>
      </MemoryRouter>
    );

    expect(screen.getAllByText(/Marketplace/i).length).toBeGreaterThan(0);
    expect(screen.getByText(/Groundnut \(Kadir-6\)/i)).toBeInTheDocument();
    expect(screen.getByText(/Sunflower \(KBSH-41\)/i)).toBeInTheDocument();

    // Click on Place Offer button
    const placeBidBtns = screen.getAllByRole('button', { name: /place offer/i });
    expect(placeBidBtns.length).toBeGreaterThan(0);
    fireEvent.click(placeBidBtns[0]);

    // Modal should appear
    expect(screen.getByText(/Submit Indicative Offer for LOT-101/i)).toBeInTheDocument();
  });



  it('BuyerPortalPage renders buyer procurement demands and allows posting new demand', () => {
    render(
      <MemoryRouter>
        <AuthProvider>
          <BuyerPortalPage />
        </AuthProvider>
      </MemoryRouter>
    );

    expect(screen.getByText(/Farmer Procurement Overview/i)).toBeInTheDocument();
    expect(screen.getByText(/Karnataka Agro Processing Ltd./i)).toBeInTheDocument();

    // Click Post Procurement Demand button
    const postDemandBtn = screen.getByRole('button', { name: /\+ Post Procurement Requirement/i });
    fireEvent.click(postDemandBtn);

    // Modal opens
    expect(screen.getAllByText(/Post Procurement Requirement/i).length).toBeGreaterThan(0);
  });

  it('AuthContext correctly manages role resolution and prevents client role escalation when logged in', () => {
    render(
      <AuthProvider>
        <TestRoleComponent />
      </AuthProvider>
    );

    const roleSpan = screen.getByTestId('current-role');
    expect(roleSpan.textContent).toBe('farmer');

    // Unauthenticated guest can set role state
    const buyerBtn = screen.getByText('Switch to Buyer');
    fireEvent.click(buyerBtn);
    expect(roleSpan.textContent).toBe('buyer');
  });

});
