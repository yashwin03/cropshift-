import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import BiddingPage from '../pages/BiddingPage';
import { AuthProvider } from '../contexts/AuthContext';
import * as biddingService from '../services/biddingService';
import * as stockLotService from '../services/stockLotService';
import * as stockBidService from '../services/stockBidService';
import * as tradeOrderService from '../services/tradeOrderService';

vi.mock('../services/biddingService');
vi.mock('../services/stockLotService');
vi.mock('../services/stockBidService');
vi.mock('../services/tradeOrderService');

const mockOpenStockLot = {
  id: 10,
  crop_id: 1,
  crop_name: 'Groundnut (Kadir-6)',
  variety: 'Kadir-6',
  available_quantity_quintals: 100.0,
  actual_harvest_date: '2026-09-20',
  quality_grade: 'Grade A',
  asking_price_per_quintal: 6000.0,
  district: 'Dharwad',
  state: 'Karnataka',
  status: 'AVAILABLE',
};

const mockStockBid = {
  id: 5,
  stock_lot_id: 10,
  buyer_id: 2,
  offered_price_per_quintal: 6200.0,
  requested_quantity_quintals: 40.0,
  allocated_quantity_quintals: 0.0,
  conditions: 'Moisture < 8%',
  status: 'SUBMITTED',
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
  crop_name: 'Groundnut (Kadir-6)',
  district: 'Dharwad',
  buyer_display_id: 'Buyer #2',
  effective_offer_per_quintal: 6150.0,
};

const mockStockBidFarmerView = {
  id: 5,
  stock_lot_id: 10,
  offered_price_per_quintal: 6200.0,
  requested_quantity_quintals: 40.0,
  allocated_quantity_quintals: 0.0,
  conditions: 'Moisture < 8%',
  status: 'SUBMITTED',
  created_at: new Date().toISOString(),
  buyer_display_id: 'Buyer #2',
  effective_offer_per_quintal: 6150.0,
};

describe('Phase 7C StockBid UI Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.spyOn(window, 'confirm').mockImplementation(() => true);

    vi.mocked(biddingService.getOpenFutureCropLots).mockResolvedValue([]);
    vi.mocked(biddingService.getMyBids).mockResolvedValue([]);
    vi.mocked(biddingService.getFarmerFutureCropLotsMe).mockResolvedValue([]);
    vi.mocked(biddingService.getBidsForFarmerLot).mockResolvedValue([]);

    vi.mocked(stockLotService.getOpenStockLots).mockResolvedValue([mockOpenStockLot as any]);
    vi.mocked(stockLotService.getFarmerStockLotsMe).mockResolvedValue([{ ...mockOpenStockLot, farmer_id: 1, farm_id: 1 } as any]);

    vi.mocked(stockBidService.getMyStockBids).mockResolvedValue([mockStockBid as any]);
    vi.mocked(stockBidService.getFarmerStockLotBids).mockResolvedValue([mockStockBidFarmerView as any]);
    vi.mocked(stockBidService.getStockBidContactSharing).mockResolvedValue({
      id: 1,
      bid_id: 0,
      stock_bid_id: 5,
      farmer_id: 1,
      buyer_id: 2,
      farmer_consented: false,
      buyer_consented: false,
      status: 'PENDING',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    } as any);

    vi.mocked(tradeOrderService.getMyTradeOrders).mockResolvedValue([]);
  });

  const renderPageAsBuyer = () => {
    localStorage.setItem('user', JSON.stringify({ id: 2, email: 'buyer@test.com', role: 'BUYER' }));
    localStorage.setItem('cropshift_active_role', 'buyer');
    return render(
      <MemoryRouter>
        <AuthProvider>
          <BiddingPage />
        </AuthProvider>
      </MemoryRouter>
    );
  };

  const renderPageAsFarmer = () => {
    localStorage.setItem('user', JSON.stringify({ id: 1, email: 'farmer@test.com', role: 'FARMER' }));
    localStorage.setItem('cropshift_active_role', 'farmer');
    return render(
      <MemoryRouter>
        <AuthProvider>
          <BiddingPage />
        </AuthProvider>
      </MemoryRouter>
    );
  };

  it('1. Buyer sees Available Harvested Stock tab and Submit Stock Offer button', async () => {
    renderPageAsBuyer();
    const stockTab = await screen.findByRole('button', { name: /Available Harvested Stock/i });
    fireEvent.click(stockTab);

    expect(await screen.findByText('Submit Stock Offer')).toBeInTheDocument();
  });

  it('2. Buyer can open Submit Stock Offer modal and submit offer', async () => {
    vi.mocked(stockBidService.createStockBid).mockResolvedValue(mockStockBid as any);
    renderPageAsBuyer();
    const stockTab = await screen.findByRole('button', { name: /Available Harvested Stock/i });
    fireEvent.click(stockTab);

    const offerBtn = await screen.findByText('Submit Stock Offer');
    fireEvent.click(offerBtn);

    expect(await screen.findByText(/Submit Offer for Stock Lot #10/i)).toBeInTheDocument();

    const priceInput = screen.getByLabelText(/Offered Price/i);
    fireEvent.change(priceInput, { target: { value: '6200' } });

    const submitBtns = screen.getAllByRole('button', { name: 'Submit Stock Offer' });
    fireEvent.click(submitBtns[submitBtns.length - 1]);

    await waitFor(() => {
      expect(stockBidService.createStockBid).toHaveBeenCalledWith(10, expect.objectContaining({
        offered_price_per_quintal: 6200,
        requested_quantity_quintals: 100,
      }));
    });
  });

  it('3. Buyer sees My Post-Harvest Stock Offers section', async () => {
    renderPageAsBuyer();
    const bidsTab = await screen.findByRole('button', { name: /My Indicative Bids/i });
    fireEvent.click(bidsTab);

    expect(await screen.findByText(/My Post-Harvest Stock Offers/i)).toBeInTheDocument();
    expect(screen.getByText('Offer #5')).toBeInTheDocument();
  });

  it('4. Buyer can withdraw submitted stock offer', async () => {
    vi.mocked(stockBidService.withdrawStockBid).mockResolvedValue({ ...mockStockBid, status: 'WITHDRAWN' } as any);
    renderPageAsBuyer();
    const bidsTab = await screen.findByRole('button', { name: /My Indicative Bids/i });
    fireEvent.click(bidsTab);

    const withdrawBtn = await screen.findByRole('button', { name: 'Withdraw Offer' });
    fireEvent.click(withdrawBtn);

    await waitFor(() => {
      expect(stockBidService.withdrawStockBid).toHaveBeenCalledWith(5);
    });
  });

  it('5. Farmer sees incoming stock offers on harvested stock inventory', async () => {
    renderPageAsFarmer();
    const stockTab = await screen.findByRole('button', { name: /Harvested Stock Inventory/i });
    fireEvent.click(stockTab);

    expect(await screen.findByText(/Incoming Stock Offers/i)).toBeInTheDocument();
    expect(screen.getByText('Buyer #2')).toBeInTheDocument();
  });

  it('6. Farmer can open Accept Offer modal and allocate quantity', async () => {
    vi.mocked(stockBidService.acceptStockBid).mockResolvedValue({ ...mockStockBid, status: 'ACCEPTED', allocated_quantity_quintals: 40.0 } as any);
    renderPageAsFarmer();
    const stockTab = await screen.findByRole('button', { name: /Harvested Stock Inventory/i });
    fireEvent.click(stockTab);

    const acceptBtn = await screen.findByRole('button', { name: 'Accept Offer' });
    fireEvent.click(acceptBtn);

    expect(await screen.findByText(/Allocate Harvested Stock & Accept Offer/i)).toBeInTheDocument();

    const qtyInput = screen.getByLabelText(/How many quintals do you want to allocate?/i);
    expect(qtyInput).toHaveValue(40);

    const confirmBtn = screen.getByRole('button', { name: 'Confirm Allocation' });
    fireEvent.click(confirmBtn);

    await waitFor(() => {
      expect(stockBidService.acceptStockBid).toHaveBeenCalledWith(5, { allocated_quantity_quintals: 40 });
    });
  });

  it('7. Farmer can reject incoming stock offer', async () => {
    vi.mocked(stockBidService.rejectStockBid).mockResolvedValue({ ...mockStockBid, status: 'REJECTED' } as any);
    renderPageAsFarmer();
    const stockTab = await screen.findByRole('button', { name: /Harvested Stock Inventory/i });
    fireEvent.click(stockTab);

    const rejectBtn = await screen.findByRole('button', { name: 'Reject' });
    fireEvent.click(rejectBtn);

    await waitFor(() => {
      expect(stockBidService.rejectStockBid).toHaveBeenCalledWith(5);
    });
  });

  it('8. Contact sharing card is rendered for accepted stock bids', async () => {
    vi.mocked(stockBidService.getFarmerStockLotBids).mockResolvedValue([{ ...mockStockBidFarmerView, status: 'ACCEPTED', allocated_quantity_quintals: 40.0 } as any]);
    renderPageAsFarmer();
    const stockTab = await screen.findByRole('button', { name: /Harvested Stock Inventory/i });
    fireEvent.click(stockTab);

    expect(await screen.findByText(/Mutual Contact Sharing/i)).toBeInTheDocument();
  });
});
