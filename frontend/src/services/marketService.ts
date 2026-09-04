import apiClient from './apiClient';
import type { MarketItem } from '../types/api';
import { USE_MOCKS, delay } from '../mocks';
import {
  GOLDEN_DEMO_GROUNDNUT_MARKET,
  GOLDEN_DEMO_PADDY_MARKET,
  CAUTION_COTTON_MARKET,
  UNAVAILABLE_MARKET,
} from '../mocks/marketFixtures';

/**
 * Mock market intelligence data retriever.
 */
export async function getMockMarkets(cropId: number): Promise<MarketItem> {
  await delay(300);
  if (cropId === 1) {
    return GOLDEN_DEMO_PADDY_MARKET;
  }
  if (cropId === 2) {
    return GOLDEN_DEMO_GROUNDNUT_MARKET;
  }
  if (cropId === 3) {
    return CAUTION_COTTON_MARKET;
  }
  return {
    ...UNAVAILABLE_MARKET,
    crop_id: cropId,
  };
}

/**
 * Market intelligence service method.
 * Contract endpoint: GET /api/v1/markets/{crop_id}
 */
export async function getMarkets(cropId: number): Promise<MarketItem> {
  if (USE_MOCKS) {
    return getMockMarkets(cropId);
  }

  const response = await apiClient.get<MarketItem>(`/api/v1/markets/${cropId}`);
  return response.data;
}
