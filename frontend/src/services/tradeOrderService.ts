import apiClient from './apiClient';
import type { TradeOrder, TradeOrderCancelRequest } from '../types/api';

/**
 * Get trade orders for authenticated user (buyer or farmer).
 */
export async function getMyTradeOrders(): Promise<TradeOrder[]> {
  const response = await apiClient.get<TradeOrder[]>('/v1/trade-orders/me');
  return response.data;
}

/**
 * Get trade order by ID.
 */
export async function getTradeOrderById(orderId: number): Promise<TradeOrder> {
  const response = await apiClient.get<TradeOrder>(`/v1/trade-orders/${orderId}`);
  return response.data;
}

/**
 * Mark a trade order as FULFILLED.
 */
export async function fulfillTradeOrder(orderId: number): Promise<TradeOrder> {
  const response = await apiClient.post<TradeOrder>(`/v1/trade-orders/${orderId}/fulfill`);
  return response.data;
}

/**
 * Cancel a trade order.
 */
export async function cancelTradeOrder(
  orderId: number,
  payload?: TradeOrderCancelRequest
): Promise<TradeOrder> {
  const response = await apiClient.post<TradeOrder>(`/v1/trade-orders/${orderId}/cancel`, payload || {});
  return response.data;
}
