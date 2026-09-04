import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import React from 'react';
import PeerProofCard from '../components/recommendation/PeerProofCard';
import * as peerProofService from '../services/peerProofService';

vi.mock('../services/peerProofService');

describe('PeerProofCard UI Unit Test Suite', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('1. Displays peer proof evidence when available', async () => {
    vi.spyOn(peerProofService, 'getPeerProof').mockResolvedValue({
      available: true,
      crop_id: 2,
      crop_name: 'Groundnut',
      cohort_count: 12,
      geographic_scope: 'Your district',
      season: 'Kharif 2025',
      farm_size_range: '1.0 - 5.0 acres',
      average_yield_quintals_per_acre: 9.5,
      average_selling_price_per_quintal: 6000,
      average_net_realization_per_acre: 45000,
      data_source: 'CropShift demo dataset',
      verification_status: 'Demo data — not real farmer verification',
      peers: [
        {
          id: 1,
          peer_display_id: 'Basavaraj Patil',
          district: 'Tumkur',
          acres: 2.0,
          yield_per_acre: 9.5,
          contactable: true,
          verification_status: 'Verified',
        },
      ],
    });

    render(<PeerProofCard cropId={2} cropName="Groundnut" district="Tumkur" />);

    expect(await screen.findByText(/Farmers Growing.*Groundnut.*Near You/i)).toBeInTheDocument();
    expect(screen.getAllByText(/9.5/i).length).toBeGreaterThan(0);
    expect(screen.getByText(/Basavaraj Patil/i)).toBeInTheDocument();
    expect(screen.getByText(/Request Contact/i)).toBeInTheDocument();
  });

  it('2. Displays unavailable state when cohort is small or unavailable', async () => {
    vi.spyOn(peerProofService, 'getPeerProof').mockResolvedValue({
      available: false,
      crop_id: 99,
      crop_name: 'Rare Crop',
      cohort_count: 1,
      geographic_scope: 'Your district',
      message: 'Peer proof unavailable yet. Not enough verified peer records in your district.',
      data_source: 'CropShift demo dataset',
      verification_status: 'Demo data — not real farmer verification',
      peers: [],
    });

    render(<PeerProofCard cropId={99} cropName="Rare Crop" district="Tumkur" />);

    expect(await screen.findByText(/No demo farmer records for Rare Crop yet/i)).toBeInTheDocument();
  });

  it('3. Contact request unlocks peer phone and email', async () => {
    vi.spyOn(peerProofService, 'getPeerProof').mockResolvedValue({
      available: true,
      crop_id: 2,
      crop_name: 'Groundnut',
      cohort_count: 12,
      geographic_scope: 'Your district',
      data_source: 'CropShift demo dataset',
      verification_status: 'Demo data — not real farmer verification',
      peers: [
        {
          id: 1,
          peer_display_id: 'Basavaraj Patil',
          district: 'Tumkur',
          acres: 2.0,
          yield_per_acre: 9.5,
          contactable: true,
          verification_status: 'Verified',
        },
      ],
    });

    vi.spyOn(peerProofService, 'requestPeerContact').mockResolvedValue({
      id: 1,
      farmer_display_name: 'Basavaraj Patil',
      district: 'Tumkur',
      state: 'Karnataka',
      phone: '9876111111',
      email: 'basavaraj@example.com',
      contactable: true,
      verification_status: 'Verified',
    });

    render(<PeerProofCard cropId={2} cropName="Groundnut" district="Tumkur" />);

    const contactBtn = await screen.findByText(/Request Contact/i);
    fireEvent.click(contactBtn);

    await waitFor(() => {
      expect(screen.getByText(/9876111111/i)).toBeInTheDocument();
      expect(screen.getByText(/basavaraj@example.com/i)).toBeInTheDocument();
    });
  });

  it('4. Demo provenance labels are shown — no real-farmer language displayed', async () => {
    vi.spyOn(peerProofService, 'getPeerProof').mockResolvedValue({
      available: true,
      crop_id: 2,
      crop_name: 'Groundnut',
      cohort_count: 4,
      geographic_scope: 'Your district',
      season: 'Kharif 2025',
      farm_size_range: '1.5 - 3.0 acres',
      average_yield_quintals_per_acre: 9.6,
      average_selling_price_per_quintal: 5850,
      average_net_realization_per_acre: 44355,
      data_source: 'CropShift demo dataset',
      verification_status: 'Demo data — not real farmer verification',
      peers: [],
    });

    render(<PeerProofCard cropId={2} cropName="Groundnut" district="Tumkur" />);

    // Demo source label must appear
    expect(await screen.findByText(/CropShift demo dataset/i)).toBeInTheDocument();
    // Demo verification status must appear
    expect(screen.getByText(/Demo data.*not real farmer verification/i)).toBeInTheDocument();
    // Must NOT contain real-farmer language
    expect(screen.queryByText(/verified farmer records/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/self-reported.*verified/i)).not.toBeInTheDocument();
  });
});
