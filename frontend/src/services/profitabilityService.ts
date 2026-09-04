import apiClient from './apiClient';
import type { ProfitabilityResponse } from '../types/api';
import { USE_MOCKS, delay } from '../mocks';
import {
  GOLDEN_DEMO_PROFITABILITY,
  CAUTION_PROFITABILITY,
  DONT_SWITCH_PROFITABILITY,
} from '../mocks/fixtures';
import { getRecommendation } from '../utils/storage';

/**
 * Mock profitability engine resolver.
 * Correlates scenario with the active recommendation if available.
 */
export async function getMockProfitability(): Promise<ProfitabilityResponse> {
  await delay(350);
  const activeRec = getRecommendation();
  if (activeRec?.decision === 'CAUTION' || activeRec?.recommended_crop === 'Cotton') {
    return CAUTION_PROFITABILITY;
  }
  if (activeRec?.decision === 'DONT_SWITCH' || (activeRec && activeRec.profit_difference < 0)) {
    return DONT_SWITCH_PROFITABILITY;
  }
  return GOLDEN_DEMO_PROFITABILITY;
}

/**
 * Profitability service method.
 * Contract endpoint: GET /api/v1/profitability
 */
export async function getProfitability(
  farmId?: number,
  cropId?: number
): Promise<ProfitabilityResponse> {
  if (USE_MOCKS) {
    return getMockProfitability();
  }

  const response = await apiClient.get<ProfitabilityResponse>('/api/v1/profitability', {
    params: {
      farm_id: farmId || 1,
      crop_id: cropId,
    },
  });
  return response.data;
}
