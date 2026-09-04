import apiClient from './apiClient';

export interface RatingCreatePayload {
  target_user_id: number;
  trade_order_id: number;
  stars: number;
  comment?: string;
}

export interface RatingResponse {
  id: number;
  rater_id: number;
  target_user_id: number;
  trade_order_id: number;
  stars: number;
  comment?: string;
  created_at: string;
}

export interface UserRatingSummary {
  user_id: number;
  average_rating: number | null;
  total_ratings: number;
  completed_transactions: number;
  ratings: RatingResponse[];
}

export async function submitRating(payload: RatingCreatePayload): Promise<RatingResponse> {
  const response = await apiClient.post<RatingResponse>('/api/v1/ratings', payload);
  return response.data;
}

export async function getUserRatingSummary(userId: number): Promise<UserRatingSummary> {
  const response = await apiClient.get<UserRatingSummary>(`/api/v1/ratings/user/${userId}`);
  return response.data;
}

export async function getMyGivenRatings(): Promise<RatingResponse[]> {
  const response = await apiClient.get<RatingResponse[]>('/api/v1/ratings/my-given');
  return response.data;
}

export async function getTradeOrderRatingForMe(tradeOrderId: number): Promise<RatingResponse | null> {
  try {
    const response = await apiClient.get<RatingResponse>(`/api/v1/ratings/trade-order/${tradeOrderId}/me`);
    return response.data;
  } catch (err: any) {
    if (err?.response?.status === 404 || err?.status === 404) {
      return null;
    }
    throw err;
  }
}
