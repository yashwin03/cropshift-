import apiClient from './apiClient';
import type {
  StockBid,
  StockBidCreate,
  StockBidAcceptRequest,
  StockBidFarmerView,
  ContactSharing,
} from '../types/api';

/**
 * Post-Harvest StockBid API services (Phase 7C)
 */

export async function createStockBid(stockId: number, payload: StockBidCreate): Promise<StockBid> {
  const response = await apiClient.post<StockBid>(`/api/v1/stock-lots/${stockId}/bids`, payload);
  return response.data;
}

export async function getMyStockBids(): Promise<StockBid[]> {
  const response = await apiClient.get<StockBid[]>('/api/v1/stock-bids/me');
  return response.data;
}

export async function getFarmerStockLotBids(stockId: number): Promise<StockBidFarmerView[]> {
  const response = await apiClient.get<StockBidFarmerView[]>(`/api/v1/farmer/stock-lots/${stockId}/bids`);
  return response.data;
}

export async function withdrawStockBid(bidId: number): Promise<StockBid> {
  const response = await apiClient.post<StockBid>(`/api/v1/stock-bids/${bidId}/withdraw`);
  return response.data;
}

export async function acceptStockBid(bidId: number, payload: StockBidAcceptRequest): Promise<StockBid> {
  const response = await apiClient.post<StockBid>(`/api/v1/stock-bids/${bidId}/accept`, payload);
  return response.data;
}

export async function rejectStockBid(bidId: number): Promise<StockBid> {
  const response = await apiClient.post<StockBid>(`/api/v1/stock-bids/${bidId}/reject`);
  return response.data;
}

export async function getStockBidContactSharing(bidId: number): Promise<ContactSharing> {
  const response = await apiClient.get<ContactSharing>(`/api/v1/stock-bids/${bidId}/contact-sharing`);
  return response.data;
}

export async function consentStockBidContactSharing(bidId: number): Promise<ContactSharing> {
  const response = await apiClient.post<ContactSharing>(`/api/v1/stock-bids/${bidId}/contact-sharing/consent`);
  return response.data;
}

export async function revokeStockBidContactSharing(bidId: number): Promise<ContactSharing> {
  const response = await apiClient.post<ContactSharing>(`/api/v1/stock-bids/${bidId}/contact-sharing/revoke`);
  return response.data;
}
