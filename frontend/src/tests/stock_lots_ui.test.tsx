import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import BiddingPage from '../pages/BiddingPage';
import { AuthProvider } from '../contexts/AuthContext';
import * as biddingService from '../services/biddingService';
import * as stockLotService from '../services/stockLotService';

vi.mock('../services/biddingService');
vi.mock('../services/stockLotService');

const mockFutureLot = {
  id: 10,
  farm_id: 1,
  farmer_id: 1,
  crop_id: 1,
  crop_name: 'Groundnut (Kadir-6)',
  variety: 'Kadir-6',
  planned_acres: 5.0,
  expected_quantity_quintals: 50.0,
  asking_price_per_quintal: 6000.0,
  expected_harvest_start: '2026-09-15',
  expected_harvest_end: '2026-09-30',
  quality_grade: 'FAQ',
  district: 'Dharwad',
  state: 'Karnataka',
  status: 'OPEN',
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString()
};

const mockStockLot = {
  id: 25,
  farmer_id: 1,
  farm_id: 1,
  future_crop_lot_id: 10,
  crop_id: 1,
  variety: 'Kadir-6',
  actual_quantity_quintals: 52.0,
  available_quantity_quintals: 52.0,
  actual_harvest_date: '2026-09-20',
  quality_grade: 'Grade A',
  asking_price_per_quintal: 6100.0,
  status: 'DRAFT',
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
  crop_name: 'Groundnut (Kadir-6)',
  district: 'Dharwad',
  state: 'Karnataka'
};

const mockOpenStockLot = {
  id: 25,
  crop_id: 1,
  crop_name: 'Groundnut (Kadir-6)',
  variety: 'Kadir-6',
  available_quantity_quintals: 52.0,
  actual_harvest_date: '2026-09-20',
  quality_grade: 'Grade A',
  asking_price_per_quintal: 6100.0,
  district: 'Dharwad',
  state: 'Karnataka',
  status: 'AVAILABLE'
};

describe('Phase 7B — StockLot & Harvest UI Integration Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    (biddingService.getFarmerFutureCropLotsMe as any).mockResolvedValue([mockFutureLot]);
    (biddingService.getBidsForFarmerLot as any).mockResolvedValue([]);
    (stockLotService.getFarmerStockLotsMe as any).mockResolvedValue([mockStockLot]);
    (stockLotService.getOpenStockLots as any).mockResolvedValue([mockOpenStockLot]);
    (biddingService.getOpenFutureCropLots as any).mockResolvedValue([]);
    (biddingService.getMyBids as any).mockResolvedValue([]);
  });

  it('1. Farmer view renders Mark as Harvested CTA on open future crop lot', async () => {
    render(
      <MemoryRouter>
        <AuthProvider>
          <BiddingPage />
        </AuthProvider>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Groundnut (Kadir-6)')).toBeInTheDocument();
      expect(screen.getByText('🌾 Mark as Harvested')).toBeInTheDocument();
    });
  });

  it('2. Clicking Mark as Harvested opens harvest recording modal', async () => {
    render(
      <MemoryRouter>
        <AuthProvider>
          <BiddingPage />
        </AuthProvider>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('🌾 Mark as Harvested')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('🌾 Mark as Harvested'));

    expect(screen.getByText(/Record Actual Harvest for LOT-10/i)).toBeInTheDocument();
    expect(screen.getByDisplayValue('50')).toBeInTheDocument();
  });

  it('3. Submitting harvest modal calls harvestFutureCropLot API', async () => {
    (stockLotService.harvestFutureCropLot as any).mockResolvedValue(mockStockLot);

    render(
      <MemoryRouter>
        <AuthProvider>
          <BiddingPage />
        </AuthProvider>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('🌾 Mark as Harvested')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('🌾 Mark as Harvested'));

    const submitBtn = screen.getByRole('button', { name: /Confirm Actual Harvest/i });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(stockLotService.harvestFutureCropLot).toHaveBeenCalledWith(
        10,
        expect.objectContaining({
          actual_quantity_quintals: 50,
          quality_grade: 'FAQ'
        })
      );
    });
  });

  it('4. Farmer can view Harvested Stock Inventory tab with draft stock lot', async () => {
    render(
      <MemoryRouter>
        <AuthProvider>
          <BiddingPage />
        </AuthProvider>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/Harvested Stock Inventory/i)).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText(/Harvested Stock Inventory/i));

    await waitFor(() => {
      expect(screen.getByText('Draft Harvested Stock')).toBeInTheDocument();
      expect(screen.getByText('📢 Publish Stock')).toBeInTheDocument();
    });
  });

  it('5. Clicking Publish Stock calls publishFarmerStockLot API', async () => {
    (stockLotService.publishFarmerStockLot as any).mockResolvedValue({
      ...mockStockLot,
      status: 'AVAILABLE'
    });

    render(
      <MemoryRouter>
        <AuthProvider>
          <BiddingPage />
        </AuthProvider>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/Harvested Stock Inventory/i)).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText(/Harvested Stock Inventory/i));

    await waitFor(() => {
      expect(screen.getByText('📢 Publish Stock')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('📢 Publish Stock'));

    await waitFor(() => {
      expect(stockLotService.publishFarmerStockLot).toHaveBeenCalledWith(25);
    });
  });
});
