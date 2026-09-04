import apiClient from './apiClient';
import type { RecommendationRequest, RecommendationResponse } from '../types/api';
import { USE_MOCKS, delay } from '../mocks';
import {
  GOLDEN_DEMO_RECOMMENDATION,
  CAUTION_RECOMMENDATION,
  DONT_SWITCH_RECOMMENDATION,
} from '../mocks/fixtures';
import type { FarmDetails } from '../mocks/fixtures';
/**
 * Mock recommendation engine service.
 * Simulates server-side decision logic during mock development mode.
 * Centralized in the service layer — NOT inside React UI components.
 */
export async function getMockRecommendation(farm: Partial<FarmDetails>): Promise<RecommendationResponse> {
  await delay(400);
  if (farm.water_availability === 'Available') {
    return GOLDEN_DEMO_RECOMMENDATION;
  }
  if (farm.water_availability === 'Limited') {
    return CAUTION_RECOMMENDATION;
  }
  return DONT_SWITCH_RECOMMENDATION;
}

/**
 * Recommendation service method.
 * Contract endpoint: POST /api/v1/recommendations
 */
export async function getRecommendation(farm: FarmDetails | RecommendationRequest): Promise<RecommendationResponse> {
  if (USE_MOCKS) {
    return getMockRecommendation(farm as Partial<FarmDetails>);
  }
  const response = await apiClient.post<RecommendationResponse>('/api/v1/recommendations', {
    farm_id: 'farm_id' in farm ? farm.farm_id : 1,
  });
  return response.data;
}
