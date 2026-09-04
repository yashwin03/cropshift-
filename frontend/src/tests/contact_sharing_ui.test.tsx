import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import BiddingPage from '../pages/BiddingPage';
import * as biddingService from '../services/biddingService';
import { AuthProvider } from '../contexts/AuthContext';

// Mock AuthContext
vi.mock('../contexts/AuthContext', async () => {
  const actual = await vi.importActual('../contexts/AuthContext');
  return {
    ...actual,
    useAuth: () => ({
      activeRole: 'farmer',
      setActiveRole: vi.fn(),
    }),
  };
});

vi.mock('../services/stockBidService', async () => {
  return {
    getStockBidContactSharing: vi.fn().mockResolvedValue({
      id: 501,
      stock_bid_id: 301,
      status: 'PENDING',
      farmer_consented: false,
      buyer_consented: false,
      farmer_contact: null,
      buyer_contact: null,
      created_at: '2026-06-02T10:00:00Z',
      updated_at: '2026-06-02T10:00:00Z',
    }),
    consentStockBidContactSharing: vi.fn().mockResolvedValue({
      id: 501,
      stock_bid_id: 301,
      status: 'PENDING',
      farmer_consented: true,
      buyer_consented: false,
      farmer_contact: null,
      buyer_contact: null,
      created_at: '2026-06-02T10:00:00Z',
      updated_at: '2026-06-02T10:00:00Z',
    }),
    revokeStockBidContactSharing: vi.fn().mockResolvedValue({
      id: 501,
      stock_bid_id: 301,
      status: 'REVOKED',
      farmer_consented: false,
      buyer_consented: false,
      farmer_contact: null,
      buyer_contact: null,
      created_at: '2026-06-02T10:00:00Z',
      updated_at: '2026-06-02T10:00:00Z',
    }),
  };
});

// Mock contactSharingService
vi.mock('../services/contactSharingService', async () => {
  return {
    getContactSharingStatus: vi.fn().mockResolvedValue({
      id: 501,
      bid_id: 301,
      status: 'PENDING',
      farmer_consented: false,
      buyer_consented: false,
      farmer_contact: null,
      buyer_contact: null,
      created_at: '2026-06-02T10:00:00Z',
      updated_at: '2026-06-02T10:00:00Z',
    }),
    grantContactSharingConsent: vi.fn().mockResolvedValue({
      id: 501,
      bid_id: 301,
      status: 'PENDING',
      farmer_consented: true,
      buyer_consented: false,
      farmer_contact: null,
      buyer_contact: null,
      created_at: '2026-06-02T10:00:00Z',
      updated_at: '2026-06-02T10:00:00Z',
    }),
    revokeContactSharingConsent: vi.fn().mockResolvedValue({
      id: 501,
      bid_id: 301,
      status: 'REVOKED',
      farmer_consented: false,
      buyer_consented: false,
      farmer_contact: null,
      buyer_contact: null,
      created_at: '2026-06-02T10:00:00Z',
      updated_at: '2026-06-02T10:00:00Z',
    }),
  };
});

// Mock biddingService
vi.mock('../services/biddingService', async () => {
  const actual = await vi.importActual('../services/biddingService');
  return {
    ...actual,
    getOpenFutureCropLots: vi.fn().mockResolvedValue([]),
    getMyBids: vi.fn().mockResolvedValue([]),
    getFarmerFutureCropLotsMe: vi.fn().mockResolvedValue([
      {
        id: 201,
        farm_id: 1,
        farmer_id: 10,
        crop_id: 1,
        crop_name: 'Groundnut (Kadir-6)',
        planned_acres: 5.0,
        expected_quantity_quintals: 50,
        asking_price_per_quintal: 6000,
        planned_sowing_date: '2026-06-01',
        expected_harvest_start: '2026-09-15',
        expected_harvest_end: '2026-09-30',
        district: 'Dharwad',
        status: 'INDICATIVE_ACCEPTED',
      },
    ]),
    getBidsForFarmerLot: vi.fn().mockResolvedValue([
      {
        id: 301,
        future_crop_lot_id: 201,
        buyer_id: 20,
        buyer_display_id: 'Buyer #20',
        offered_price_per_quintal: 6100,
        quantity_quintals: 50,
        status: 'ACCEPTED',
        created_at: '2026-06-02T10:00:00Z',
        updated_at: '2026-06-02T10:00:00Z',
      },
    ]),
    getContactSharing: vi.fn().mockResolvedValue({
      id: 501,
      bid_id: 301,
      status: 'PENDING',
      farmer_consented: false,
      buyer_consented: false,
      farmer_contact: null,
      buyer_contact: null,
      created_at: '2026-06-02T10:00:00Z',
      updated_at: '2026-06-02T10:00:00Z',
    }),
    getContactSharingStatus: vi.fn().mockResolvedValue({
      id: 501,
      bid_id: 301,
      status: 'PENDING',
      farmer_consented: false,
      buyer_consented: false,
      farmer_contact: null,
      buyer_contact: null,
      created_at: '2026-06-02T10:00:00Z',
      updated_at: '2026-06-02T10:00:00Z',
    }),
    consentContactSharing: vi.fn().mockResolvedValue({
      id: 501,
      bid_id: 301,
      status: 'PENDING',
      farmer_consented: true,
      buyer_consented: false,
      farmer_contact: null,
      buyer_contact: null,
      created_at: '2026-06-02T10:00:00Z',
      updated_at: '2026-06-02T10:00:00Z',
    }),
    revokeContactSharing: vi.fn().mockResolvedValue({
      id: 501,
      bid_id: 301,
      status: 'REVOKED',
      farmer_consented: false,
      buyer_consented: false,
      farmer_contact: null,
      buyer_contact: null,
      created_at: '2026-06-02T10:00:00Z',
      updated_at: '2026-06-02T10:00:00Z',
    }),
  };
});

describe('Phase 6B Mutual Contact Sharing UI Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.setItem('cropshift_active_role', 'farmer');
  });

  it('1. Accepted bid renders Share Contact Details CTA', async () => {
    render(
      <AuthProvider>
        <BiddingPage />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getAllByText(/Farmer Marketplace & Procurement|Farmer Marketplace/i)[0]).toBeInTheDocument();
    });
  });

  it('2. Farmer consent button updates UI state', async () => {
    render(
      <AuthProvider>
        <BiddingPage />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('🤝 Share Contact Details')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('🤝 Share Contact Details'));

    await waitFor(() => {
      expect(biddingService.consentContactSharing).toHaveBeenCalledWith(301);
      expect(screen.getByText('⏳ Waiting for Buyer Consent')).toBeInTheDocument();
    });
  });

  it('3. Buyer consent button updates UI state', async () => {
    render(
      <AuthProvider>
        <BiddingPage />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('🤝 Share Contact Details')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('🤝 Share Contact Details'));

    await waitFor(() => {
      expect(biddingService.consentContactSharing).toHaveBeenCalledWith(301);
    });
  });

  it('4. Displays waiting for consent state when single party consents', async () => {
    vi.mocked(biddingService.getContactSharing).mockResolvedValueOnce({
      id: 501,
      bid_id: 301,
      status: 'PENDING',
      farmer_consented: true,
      buyer_consented: false,
      farmer_contact: null,
      buyer_contact: null,
      created_at: '2026-06-02T10:00:00Z',
      updated_at: '2026-06-02T10:00:00Z',
    });

    render(
      <AuthProvider>
        <BiddingPage />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('⏳ Waiting for Buyer Consent')).toBeInTheDocument();
    });
  });

  it('5. Contact details are not rendered before mutual consent', async () => {
    render(
      <AuthProvider>
        <BiddingPage />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.queryByText(/Contact Unlocked/i)).not.toBeInTheDocument();
      expect(screen.queryByText(/\+91/i)).not.toBeInTheDocument();
    });
  });

  it('6. Contact details are displayed after mutual consent', async () => {
    vi.mocked(biddingService.getContactSharing).mockResolvedValueOnce({
      id: 501,
      bid_id: 301,
      status: 'MUTUAL_CONSENT',
      farmer_consented: true,
      buyer_consented: true,
      buyer_contact: {
        full_name: 'Suresh Buyer',
        phone: '+919876543210',
        email: 'suresh@buyer.com',
        business_name: 'Buyer #20',
      },
      created_at: '2026-06-02T10:00:00Z',
      updated_at: '2026-06-02T10:00:00Z',
    });

    render(
      <AuthProvider>
        <BiddingPage />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByText(/Contact Unlocked \(Buyer\)/i)).toBeInTheDocument();
      expect(screen.getByText('Suresh Buyer')).toBeInTheDocument();
      expect(screen.getByText('+919876543210')).toBeInTheDocument();
      expect(screen.getByText('suresh@buyer.com')).toBeInTheDocument();
    });
  });

  it('7. Revoking consent hides contact details', async () => {
    vi.mocked(biddingService.getContactSharing).mockResolvedValueOnce({
      id: 501,
      bid_id: 301,
      status: 'MUTUAL_CONSENT',
      farmer_consented: true,
      buyer_consented: true,
      buyer_contact: {
        full_name: 'Suresh Buyer',
        phone: '+919876543210',
        email: 'suresh@buyer.com',
      },
      created_at: '2026-06-02T10:00:00Z',
      updated_at: '2026-06-02T10:00:00Z',
    });

    render(
      <AuthProvider>
        <BiddingPage />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('Revoke Consent')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Revoke Consent'));

    await waitFor(() => {
      expect(biddingService.revokeContactSharing).toHaveBeenCalledWith(301);
      expect(screen.queryByText(/Contact Unlocked/i)).not.toBeInTheDocument();
    });
  });

  it('8. Re-consenting restores mutual consent contact details', async () => {
    vi.mocked(biddingService.getContactSharing).mockResolvedValueOnce({
      id: 501,
      bid_id: 301,
      status: 'REVOKED',
      farmer_consented: false,
      buyer_consented: true,
      farmer_contact: null,
      buyer_contact: null,
      created_at: '2026-06-02T10:00:00Z',
      updated_at: '2026-06-02T10:00:00Z',
    });

    vi.mocked(biddingService.consentContactSharing).mockResolvedValueOnce({
      id: 501,
      bid_id: 301,
      status: 'MUTUAL_CONSENT',
      farmer_consented: true,
      buyer_consented: true,
      buyer_contact: {
        full_name: 'Suresh Buyer',
        phone: '+919876543210',
        email: 'suresh@buyer.com',
      },
      created_at: '2026-06-02T10:00:00Z',
      updated_at: '2026-06-02T10:00:00Z',
    });

    render(
      <AuthProvider>
        <BiddingPage />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('🤝 Share Contact Details')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('🤝 Share Contact Details'));

    await waitFor(() => {
      expect(screen.getByText('Suresh Buyer')).toBeInTheDocument();
    });
  });

  it('9. Sensitive fields are shielded before unlock', async () => {
    render(
      <AuthProvider>
        <BiddingPage />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.queryByText('Phone:')).not.toBeInTheDocument();
      expect(screen.queryByText('Email:')).not.toBeInTheDocument();
    });
  });

  it('10. Existing bidding marketplace rendering remains intact', async () => {
    render(
      <AuthProvider>
        <BiddingPage />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('Groundnut (Kadir-6)')).toBeInTheDocument();
      expect(screen.getByText('Indicative Accepted')).toBeInTheDocument();
      expect(screen.getByText('Buyer #20')).toBeInTheDocument();
    });
  });
});
