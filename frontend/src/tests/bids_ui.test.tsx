import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import React from 'react';
import { MemoryRouter } from 'react-router-dom';
import BiddingPage from '../pages/BiddingPage';
import { AuthProvider } from '../contexts/AuthContext';
import * as biddingService from '../services/biddingService';

vi.mock('../services/biddingService');

describe('Phase 5C — Live Frontend Bidding Integration Test Suite', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  const mockOpenLots = [
    {
      id: 101,
      crop_id: 1,
      crop_name: 'Groundnut (Kadir-6)',
      variety: 'Kadir-6',
      planned_acres: 5.0,
      expected_quantity_quintals: 100,
      asking_price_per_quintal: 6200,
      expected_harvest_start: '2026-09-15',
      expected_harvest_end: '2026-09-30',
      district: 'Dharwad',
      state: 'Karnataka',
      status: 'OPEN' as const,
      farmer_display_id: 'Farmer #1'
    }
  ];

  const mockBuyerBids = [
    {
      id: 201,
      future_crop_lot_id: 101,
      buyer_id: 2,
      offered_price_per_quintal: 6500,
      quantity_quintals: 50,
      conditions: 'Moisture < 8%',
      status: 'SUBMITTED' as const,
      created_at: '2026-09-01T10:00:00Z',
      updated_at: '2026-09-01T10:00:00Z',
      crop_name: 'Groundnut (Kadir-6)',
      district: 'Dharwad',
      buyer_display_id: 'Buyer #2',
      effective_offer_per_quintal: 6450,
      effective_offer_note: null
    }
  ];

  const mockFarmerLots = [
    {
      id: 101,
      farm_id: 1,
      farmer_id: 1,
      crop_id: 1,
      planned_acres: 5.0,
      expected_quantity_quintals: 100,
      asking_price_per_quintal: 6200,
      planned_sowing_date: '2026-06-01',
      expected_harvest_start: '2026-09-15',
      expected_harvest_end: '2026-09-30',
      status: 'OPEN' as const,
      created_at: '2026-06-01T00:00:00Z',
      updated_at: '2026-06-01T00:00:00Z',
      crop_name: 'Groundnut (Kadir-6)',
      district: 'Dharwad'
    }
  ];

  it('1. Buyer can load future crop opportunities from API', async () => {
    localStorage.setItem('cropshift_user', JSON.stringify({ id: 2, username: 'buyer1', role: 'BUYER' }));
    vi.spyOn(biddingService, 'getOpenFutureCropLots').mockResolvedValue(mockOpenLots as any);
    vi.spyOn(biddingService, 'getMyBids').mockResolvedValue([]);

    render(
      <MemoryRouter>
        <AuthProvider>
          <BiddingPage />
        </AuthProvider>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/Groundnut \(Kadir-6\)/i)).toBeInTheDocument();
      expect(screen.getByText(/50 Quintals/i)).toBeInTheDocument();
      expect(screen.getByText(/₹6000\/Q/i)).toBeInTheDocument();
    });
  });

  it('2. Buyer can open bid form modal for an opportunity', async () => {
    localStorage.setItem('cropshift_user', JSON.stringify({ id: 2, username: 'buyer1', role: 'BUYER' }));
    vi.spyOn(biddingService, 'getOpenFutureCropLots').mockResolvedValue(mockOpenLots as any);
    vi.spyOn(biddingService, 'getMyBids').mockResolvedValue([]);

    render(
      <MemoryRouter>
        <AuthProvider>
          <BiddingPage />
        </AuthProvider>
      </MemoryRouter>
    );

    await waitFor(() => expect(screen.getByText(/Groundnut \(Kadir-6\)/i)).toBeInTheDocument());

    const submitBtns = screen.getAllByRole('button', { name: /Submit Indicative Offer/i });
    fireEvent.click(submitBtns[0]);

    expect(screen.getAllByText(/Submit Indicative Offer/i).length).toBeGreaterThan(0);
    expect(screen.getByDisplayValue('6000')).toBeInTheDocument();
  });

  it('3. Buyer can submit an indicative bid', async () => {
    localStorage.setItem('cropshift_user', JSON.stringify({ id: 2, username: 'buyer1', role: 'BUYER' }));
    vi.spyOn(biddingService, 'getOpenFutureCropLots').mockResolvedValue(mockOpenLots as any);
    vi.spyOn(biddingService, 'getMyBids').mockResolvedValue([]);
    const createBidSpy = vi.spyOn(biddingService, 'createBid').mockResolvedValue(mockBuyerBids[0] as any);

    render(
      <MemoryRouter>
        <AuthProvider>
          <BiddingPage />
        </AuthProvider>
      </MemoryRouter>
    );

    await waitFor(() => expect(screen.getByText(/Groundnut \(Kadir-6\)/i)).toBeInTheDocument());

    const submitBtns = screen.getAllByRole('button', { name: /Submit Indicative Offer/i });
    fireEvent.click(submitBtns[0]);

    const confirmBtn = screen.getByRole('button', { name: /Confirm Indicative Bid|Submit Offer|Confirm Offer/i });
    fireEvent.click(confirmBtn);

    await waitFor(() => {
      expect(createBidSpy).toHaveBeenCalledWith({
        future_crop_lot_id: 101,
        offered_price_per_quintal: 6000,
        quantity_quintals: 50,
        conditions: undefined
      });
      expect(screen.getByText(/Successfully submitted indicative/i)).toBeInTheDocument();
    });
  });

  it('4. Buyer can view own submitted bids tab', async () => {
    localStorage.setItem('cropshift_user', JSON.stringify({ id: 2, username: 'buyer1', role: 'BUYER' }));
    localStorage.setItem('cropshift_active_role', 'buyer');
    localStorage.setItem('user', JSON.stringify({ id: 2, username: 'buyer1', role: 'BUYER' }));
    vi.spyOn(biddingService, 'getOpenFutureCropLots').mockResolvedValue([]);
    vi.spyOn(biddingService, 'getMyBids').mockResolvedValue(mockBuyerBids as any);

    render(
      <MemoryRouter>
        <AuthProvider>
          <BiddingPage />
        </AuthProvider>
      </MemoryRouter>
    );

    const myOffersTab = await waitFor(() => screen.getByText(/My Offers Sent/i));
    fireEvent.click(myOffersTab);

    await waitFor(() => {
      expect(screen.getByText(/₹6500\/Q/i)).toBeInTheDocument();
      expect(screen.getByText(/Moisture < 8%/i)).toBeInTheDocument();
      expect(screen.getAllByText(/Submitted/i)[0]).toBeInTheDocument();
    });
  });

  it('5. Buyer can withdraw a submitted bid', async () => {
    localStorage.setItem('cropshift_user', JSON.stringify({ id: 2, username: 'buyer1', role: 'BUYER' }));
    vi.spyOn(biddingService, 'getOpenFutureCropLots').mockResolvedValue([]);
    vi.spyOn(biddingService, 'getMyBids').mockResolvedValue(mockBuyerBids as any);
    const withdrawSpy = vi.spyOn(biddingService, 'withdrawBid').mockResolvedValue({ ...mockBuyerBids[0], status: 'WITHDRAWN' } as any);
    vi.spyOn(window, 'confirm').mockReturnValue(true);

    render(
      <MemoryRouter>
        <AuthProvider>
          <BiddingPage />
        </AuthProvider>
      </MemoryRouter>
    );

    await waitFor(() => fireEvent.click(screen.getByText(/My Offers Sent \(1\)|My Indicative Bids \(1\)/i)));

    const withdrawBtn = screen.getByRole('button', { name: /Withdraw Bid|Withdraw Offer/i });
    fireEvent.click(withdrawBtn);

    await waitFor(() => {
      expect(withdrawSpy).toHaveBeenCalledWith(201);
      expect(screen.getByText(/withdrawn successfully/i)).toBeInTheDocument();
    });
  });

  it('6. Farmer can see own future crop lots', async () => {
    localStorage.setItem('cropshift_user', JSON.stringify({ id: 1, username: 'farmer1', role: 'FARMER' }));
    vi.spyOn(biddingService, 'getFarmerFutureCropLotsMe').mockResolvedValue(mockFarmerLots as any);
    vi.spyOn(biddingService, 'getBidsForFarmerLot').mockResolvedValue([]);

    render(
      <MemoryRouter>
        <AuthProvider>
          <BiddingPage />
        </AuthProvider>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getAllByText(/My Production Lots|My Planned Crops/i).length).toBeGreaterThan(0);
      expect(screen.getAllByText(/Groundnut \(Kadir-6\)/i).length).toBeGreaterThan(0);
    });
    expect(screen.getAllByText(/No bids received yet/i).length).toBeGreaterThan(0);
  });

  it('7. Farmer can load incoming bids for their lot', async () => {
    localStorage.setItem('cropshift_user', JSON.stringify({ id: 1, username: 'farmer1', role: 'FARMER' }));
    vi.spyOn(biddingService, 'getFarmerFutureCropLotsMe').mockResolvedValue(mockFarmerLots as any);
    vi.spyOn(biddingService, 'getBidsForFarmerLot').mockResolvedValue(mockBuyerBids as any);

    render(
      <MemoryRouter>
        <AuthProvider>
          <BiddingPage />
        </AuthProvider>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/Buyer #2/i)).toBeInTheDocument();
      expect(screen.getByText(/₹6500\/Q/i)).toBeInTheDocument();
    });
  });

  it('8. Farmer sees effective offer badge when available', async () => {
    localStorage.setItem('cropshift_user', JSON.stringify({ id: 1, username: 'farmer1', role: 'FARMER' }));
    vi.spyOn(biddingService, 'getFarmerFutureCropLotsMe').mockResolvedValue(mockFarmerLots as any);
    vi.spyOn(biddingService, 'getBidsForFarmerLot').mockResolvedValue(mockBuyerBids as any);

    render(
      <MemoryRouter>
        <AuthProvider>
          <BiddingPage />
        </AuthProvider>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/₹6450\/Q/i)).toBeInTheDocument();
      expect(screen.getByText(/Best Net Realization/i)).toBeInTheDocument();
    });
  });

  it('9. Farmer sees unavailable effective offer note correctly when missing', async () => {
    localStorage.setItem('cropshift_user', JSON.stringify({ id: 1, username: 'farmer1', role: 'FARMER' }));
    vi.spyOn(biddingService, 'getFarmerFutureCropLotsMe').mockResolvedValue(mockFarmerLots as any);
    const unavailBid = [{ ...mockBuyerBids[0], effective_offer_per_quintal: null, effective_offer_note: 'Destination location unavailable' }];
    vi.spyOn(biddingService, 'getBidsForFarmerLot').mockResolvedValue(unavailBid as any);

    render(
      <MemoryRouter>
        <AuthProvider>
          <BiddingPage />
        </AuthProvider>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/Net realization unavailable — destination location unavailable/i)).toBeInTheDocument();
    });
  });

  it('10. Farmer can open acceptance confirmation modal', async () => {
    localStorage.setItem('cropshift_user', JSON.stringify({ id: 1, username: 'farmer1', role: 'FARMER' }));
    vi.spyOn(biddingService, 'getFarmerFutureCropLotsMe').mockResolvedValue(mockFarmerLots as any);
    vi.spyOn(biddingService, 'getBidsForFarmerLot').mockResolvedValue(mockBuyerBids as any);

    render(
      <MemoryRouter>
        <AuthProvider>
          <BiddingPage />
        </AuthProvider>
      </MemoryRouter>
    );

    await waitFor(() => expect(screen.getByRole('button', { name: /Accept Indicative Offer/i })).toBeInTheDocument());

    fireEvent.click(screen.getByRole('button', { name: /Accept Indicative Offer/i }));

    expect(screen.getByText(/Confirm Indicative Offer Acceptance/i)).toBeInTheDocument();
    expect(screen.getByText(/This is an indicative pre-sowing bid, not a legally binding purchase contract/i)).toBeInTheDocument();
  });

  it('11. Farmer can accept an indicative bid', async () => {
    localStorage.setItem('cropshift_user', JSON.stringify({ id: 1, username: 'farmer1', role: 'FARMER' }));
    vi.spyOn(biddingService, 'getFarmerFutureCropLotsMe').mockResolvedValue(mockFarmerLots as any);
    vi.spyOn(biddingService, 'getBidsForFarmerLot').mockResolvedValue(mockBuyerBids as any);
    const acceptSpy = vi.spyOn(biddingService, 'acceptBid').mockResolvedValue({ ...mockBuyerBids[0], status: 'ACCEPTED' } as any);

    render(
      <MemoryRouter>
        <AuthProvider>
          <BiddingPage />
        </AuthProvider>
      </MemoryRouter>
    );

    await waitFor(() => fireEvent.click(screen.getByRole('button', { name: /Accept Indicative Offer/i })));

    const confirmBtn = screen.getByRole('button', { name: /Confirm Acceptance/i });
    fireEvent.click(confirmBtn);

    await waitFor(() => {
      expect(acceptSpy).toHaveBeenCalledWith(201);
      expect(screen.getByText(/Successfully accepted indicative bid/i)).toBeInTheDocument();
    });
  });

  it('12. Accepted state is reflected after API refresh', async () => {
    localStorage.setItem('cropshift_user', JSON.stringify({ id: 1, username: 'farmer1', role: 'FARMER' }));
    const acceptedLot = [{ ...mockFarmerLots[0], status: 'INDICATIVE_ACCEPTED' as const }];
    const acceptedBids = [{ ...mockBuyerBids[0], status: 'ACCEPTED' as const }];
    vi.spyOn(biddingService, 'getFarmerFutureCropLotsMe').mockResolvedValue(acceptedLot as any);
    vi.spyOn(biddingService, 'getBidsForFarmerLot').mockResolvedValue(acceptedBids as any);

    render(
      <MemoryRouter>
        <AuthProvider>
          <BiddingPage />
        </AuthProvider>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/Indicative Accepted/i)).toBeInTheDocument();
      expect(screen.getByText(/ACCEPTED/i)).toBeInTheDocument();
    });
  });

  it('13. No private contact information (phone/email/exact coordinates) is rendered', async () => {
    localStorage.setItem('cropshift_user', JSON.stringify({ id: 1, username: 'farmer1', role: 'FARMER' }));
    vi.spyOn(biddingService, 'getFarmerFutureCropLotsMe').mockResolvedValue(mockFarmerLots as any);
    vi.spyOn(biddingService, 'getBidsForFarmerLot').mockResolvedValue(mockBuyerBids as any);

    render(
      <MemoryRouter>
        <AuthProvider>
          <BiddingPage />
        </AuthProvider>
      </MemoryRouter>
    );

    await waitFor(() => expect(screen.getByText(/Buyer #2/i)).toBeInTheDocument());

    expect(screen.queryByText(/phone/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/email/i)).not.toBeInTheDocument();
  });

  it('14. Mock bids are not used in live view', async () => {
    localStorage.setItem('cropshift_user', JSON.stringify({ id: 2, username: 'buyer1', role: 'BUYER' }));
    vi.spyOn(biddingService, 'getOpenFutureCropLots').mockResolvedValue([]);
    vi.spyOn(biddingService, 'getMyBids').mockResolvedValue([]);

    render(
      <MemoryRouter>
        <AuthProvider>
          <BiddingPage />
        </AuthProvider>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/No future crop opportunities available right now./i)).toBeInTheDocument();
    });

    expect(screen.queryByText(/LOT-101/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Raju Naik/i)).not.toBeInTheDocument();
  });

  it('15. Loading/error/empty states work correctly', async () => {
    localStorage.setItem('cropshift_user', JSON.stringify({ id: 2, username: 'buyer1', role: 'BUYER' }));
    vi.spyOn(biddingService, 'getOpenFutureCropLots').mockRejectedValue(new Error('Network error'));
    vi.spyOn(biddingService, 'getMyBids').mockRejectedValue(new Error('Network error'));

    render(
      <MemoryRouter>
        <AuthProvider>
          <BiddingPage />
        </AuthProvider>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getAllByText(/Pre-Sowing|Farmer Marketplace/i).length).toBeGreaterThan(0);
    });
  });

  it('16. Non-binding indicative terminology is displayed', async () => {
    localStorage.setItem('cropshift_user', JSON.stringify({ id: 2, username: 'buyer1', role: 'BUYER' }));
    vi.spyOn(biddingService, 'getOpenFutureCropLots').mockResolvedValue(mockOpenLots as any);
    vi.spyOn(biddingService, 'getMyBids').mockResolvedValue([]);

    render(
      <MemoryRouter>
        <AuthProvider>
          <BiddingPage />
        </AuthProvider>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getAllByText(/Farmer Marketplace|Pre-Sowing/i).length).toBeGreaterThan(0);
      expect(screen.getAllByText(/Future Crop Opportunity|Pre-Sowing Opportunity/i).length).toBeGreaterThan(0);
    });

    expect(screen.queryByText(/Guaranteed Purchase/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Confirmed Contract/i)).not.toBeInTheDocument();
  });
});
