import apiClient from './apiClient';
import type {
  Bid,
  BidCreate,
  ContactSharing,
  FutureCropLot,
  FutureCropLotMarketplaceView
} from '../types/api';

/**
 * Pre-Sowing Indicative Bidding API services (Phase 5C)
 */

export async function createBid(payload: BidCreate): Promise<Bid> {
  const response = await apiClient.post<Bid>('/api/v1/bids', payload);
  return response.data;
}

export async function getMyBids(): Promise<Bid[]> {
  const response = await apiClient.get<Bid[]>('/api/v1/bids/me');
  return response.data;
}

export async function getBidsForFarmerLot(lotId: number): Promise<Bid[]> {
  const response = await apiClient.get<Bid[]>(`/api/v1/farmer/future-crop-lots/${lotId}/bids`);
  return response.data;
}

export async function withdrawBid(bidId: number): Promise<Bid> {
  const response = await apiClient.post<Bid>(`/api/v1/bids/${bidId}/withdraw`);
  return response.data;
}

export async function acceptBid(bidId: number): Promise<Bid> {
  const response = await apiClient.post<Bid>(`/api/v1/bids/${bidId}/accept`);
  return response.data;
}

export async function getOpenFutureCropLots(): Promise<FutureCropLotMarketplaceView[]> {
  const response = await apiClient.get<FutureCropLotMarketplaceView[]>('/api/v1/future-crop-lots/open');
  return response.data;
}

export async function getFarmerFutureCropLotsMe(): Promise<FutureCropLot[]> {
  const response = await apiClient.get<FutureCropLot[]>('/api/v1/farmer/future-crop-lots/me');
  return response.data;
}

export async function getContactSharing(bidId: number): Promise<ContactSharing> {
  const response = await apiClient.get<ContactSharing>(`/api/v1/bids/${bidId}/contact-sharing`);
  return response.data;
}

export async function consentContactSharing(bidId: number): Promise<ContactSharing> {
  const response = await apiClient.post<ContactSharing>(`/api/v1/bids/${bidId}/contact-sharing/consent`);
  return response.data;
}

export async function revokeContactSharing(bidId: number): Promise<ContactSharing> {
  const response = await apiClient.post<ContactSharing>(`/api/v1/bids/${bidId}/contact-sharing/revoke`);
  return response.data;
}

