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
import { TradeOrder } from '../types/api';

vi.mock('../services/biddingService');
vi.mock('../services/stockLotService');
vi.mock('../services/stockBidService');
vi.mock('../services/tradeOrderService');

const mockTradeOrder: TradeOrder = {
  id: 101,
  stock_bid_id: 5,
  stock_lot_id: 10,
  buyer_id: 2,
  farmer_id: 1,
  allocated_quantity_quintals: 40.0,
  agreed_price_per_quintal: 6200.0,
  status: 'CREATED',
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
  crop_name: 'Groundnut (Kadir-6)',
  district: 'Dharwad',
  state: 'Karnataka',
  buyer_display_id: 'Test Buyer',
  farmer_display_id: 'Test Farmer',
  contact_sharing_status: 'PENDING',
};

describe('Phase 8B Trade Order UI Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks();

    vi.mocked(biddingService.getOpenFutureCropLots).mockResolvedValue([]);
    vi.mocked(biddingService.getMyBids).mockResolvedValue([]);
    vi.mocked(stockLotService.getOpenStockLots).mockResolvedValue([]);
    vi.mocked(stockBidService.getMyStockBids).mockResolvedValue([]);
    vi.mocked(stockLotService.getFarmerStockLotsMe).mockResolvedValue([]);
    vi.mocked(biddingService.getFarmerFutureCropLotsMe).mockResolvedValue([]);
    vi.mocked(tradeOrderService.getMyTradeOrders).mockResolvedValue([mockTradeOrder]);

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
  });

  const renderWithAuth = (role: 'buyer' | 'farmer' = 'buyer') => {
    localStorage.setItem('user', JSON.stringify({ id: role === 'buyer' ? 2 : 1, email: `${role}@test.com`, role: role.toUpperCase() }));
    localStorage.setItem('cropshift_active_role', role);

    return render(
      <MemoryRouter>
        <AuthProvider>
          <BiddingPage />
        </AuthProvider>
      </MemoryRouter>
    );
  };

  it('1. Buyer can navigate to My Trade Orders tab', async () => {
    renderWithAuth('buyer');

    const tabBtn = await screen.findByRole('button', { name: /My Trade Orders/i });
    expect(tabBtn).toBeInTheDocument();

    fireEvent.click(tabBtn);

    expect(await screen.findByText(/Post-Harvest Fulfillment Tracking/i)).toBeInTheDocument();
    expect(screen.getByText(/TradeOrder tracks an accepted marketplace allocation/i)).toBeInTheDocument();
  });

  it('2. Display Trade Order card with correct price and quantity', async () => {
    renderWithAuth('buyer');

    const tabBtn = await screen.findByRole('button', { name: /My Trade Orders/i });
    fireEvent.click(tabBtn);

    expect(await screen.findByText('Order #101')).toBeInTheDocument();
    expect(screen.getByText('₹6200/Q')).toBeInTheDocument();
    expect(screen.getByText('40 Q')).toBeInTheDocument();
    expect(screen.getByText('Fulfillment Pending')).toBeInTheDocument();
  });

  it('3. Farmer can view Trade Orders tab', async () => {
    renderWithAuth('farmer');

    const tabBtn = await screen.findByRole('button', { name: /Trade Orders/i });
    expect(tabBtn).toBeInTheDocument();

    fireEvent.click(tabBtn);
    expect(await screen.findByText('Order #101')).toBeInTheDocument();
  });

  it('4. Clicking Mark Fulfilled calls fulfillTradeOrder service', async () => {
    window.confirm = vi.fn().mockReturnValue(true);
    vi.mocked(tradeOrderService.fulfillTradeOrder).mockResolvedValue({
      ...mockTradeOrder,
      status: 'FULFILLED',
      fulfilled_at: new Date().toISOString(),
    });

    renderWithAuth('buyer');
    const tabBtn = await screen.findByRole('button', { name: /My Trade Orders/i });
    fireEvent.click(tabBtn);

    const fulfillBtn = await screen.findByRole('button', { name: /Mark Fulfilled/i });
    fireEvent.click(fulfillBtn);

    expect(tradeOrderService.fulfillTradeOrder).toHaveBeenCalledWith(101);
  });

  it('5. Clicking Cancel Trade opens cancellation modal', async () => {
    renderWithAuth('buyer');
    const tabBtn = await screen.findByRole('button', { name: /My Trade Orders/i });
    fireEvent.click(tabBtn);

    const cancelBtn = await screen.findByRole('button', { name: /Cancel Trade/i });
    fireEvent.click(cancelBtn);

    expect(await screen.findByText(/Cancel Trade Order #101/i)).toBeInTheDocument();
    expect(screen.getByText(/Reason for Cancellation/i)).toBeInTheDocument();
    expect(screen.getByText(/Quantity Restoration:/i)).toBeInTheDocument();
  });

  it('6. Submitting cancellation modal calls cancelTradeOrder service', async () => {
    vi.mocked(tradeOrderService.cancelTradeOrder).mockResolvedValue({
      ...mockTradeOrder,
      status: 'CANCELLED',
      cancelled_at: new Date().toISOString(),
      cancellation_reason: 'BUYER_CANCELLED',
    });

    renderWithAuth('buyer');
    const tabBtn = await screen.findByRole('button', { name: /My Trade Orders/i });
    fireEvent.click(tabBtn);

    const cancelBtn = await screen.findByRole('button', { name: /Cancel Trade/i });
    fireEvent.click(cancelBtn);

    const submitBtn = await screen.findByRole('button', { name: /Confirm Cancellation/i });
    fireEvent.click(submitBtn);

    expect(tradeOrderService.cancelTradeOrder).toHaveBeenCalledWith(101, {
      cancellation_reason: 'BUYER_CANCELLED',
    });
  });

  it('7. Displays FULFILLED status badge and timestamp for fulfilled trade order', async () => {
    vi.mocked(tradeOrderService.getMyTradeOrders).mockResolvedValue([
      {
        ...mockTradeOrder,
        status: 'FULFILLED',
        fulfilled_at: '2026-09-20T10:00:00Z',
      },
    ]);

    renderWithAuth('buyer');
    const tabBtn = await screen.findByRole('button', { name: /My Trade Orders/i });
    fireEvent.click(tabBtn);

    expect(await screen.findByText('Trade Fulfilled')).toBeInTheDocument();
    expect(screen.getByText(/Fulfilled:/i)).toBeInTheDocument();
  });

  it('8. Displays CANCELLED status badge and reason for cancelled trade order', async () => {
    vi.mocked(tradeOrderService.getMyTradeOrders).mockResolvedValue([
      {
        ...mockTradeOrder,
        status: 'CANCELLED',
        cancelled_at: '2026-09-20T10:00:00Z',
        cancellation_reason: 'QUALITY_ISSUE',
      },
    ]);

    renderWithAuth('buyer');
    const tabBtn = await screen.findByRole('button', { name: /My Trade Orders/i });
    fireEvent.click(tabBtn);

    expect(await screen.findByText('Cancelled')).toBeInTheDocument();
    expect(screen.getByText(/QUALITY_ISSUE/i)).toBeInTheDocument();
  });

  it('9. Renders non-binding disclaimer message banner on Trade Orders tab', async () => {
    renderWithAuth('buyer');
    const tabBtn = await screen.findByRole('button', { name: /My Trade Orders/i });
    fireEvent.click(tabBtn);

    expect(await screen.findByText(/Non-Binding Marketplace Disclaimer:/i)).toBeInTheDocument();
  });

  it('10. Renders Contact Sharing Card inside Trade Order card', async () => {
    renderWithAuth('buyer');
    const tabBtn = await screen.findByRole('button', { name: /My Trade Orders/i });
    fireEvent.click(tabBtn);

    expect(await screen.findByText(/Mutual Contact Sharing/i)).toBeInTheDocument();
  });
});
