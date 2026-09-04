import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { AuthProvider } from '../contexts/AuthContext';
import BiddingPage from '../pages/BiddingPage';

describe('Future Crop Lots Marketplace UI Test Suite', () => {
  it('renders BiddingPage with Future Crop Opportunity labels', () => {
    render(
      <AuthProvider>
        <BiddingPage />
      </AuthProvider>
    );

    expect(screen.getAllByText(/Farmer Marketplace|Bidding & Buyer Offers/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/Future Crop Opportunity/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/Indicative Asking Price/i).length).toBeGreaterThan(0);
  });

  it('allows opening the List Future Crop Availability modal for Farmers', () => {
    render(
      <AuthProvider>
        <BiddingPage />
      </AuthProvider>
    );

    const listBtn = screen.getAllByText(/\+ Add Crop to Marketplace|\+ List Crop Availability/i)[0];
    expect(listBtn).toBeInTheDocument();

    fireEvent.click(listBtn);
    expect(screen.getAllByText(/List Future Crop Availability|Plan New Crop|Add Crop to Marketplace/i).length).toBeGreaterThan(0);
  });
});
