import apiClient from './apiClient';
import type { GeospatialResponse } from '../types/api';
import { USE_MOCKS, delay } from '../mocks';
import { GOLDEN_DEMO_GEOSPATIAL } from '../mocks/geospatialFixtures';

/**
 * Mock geospatial details resolver.
 */
export async function getMockGeospatial(): Promise<GeospatialResponse> {
  await delay(350);
  return GOLDEN_DEMO_GEOSPATIAL;
}

/**
 * Geospatial service method.
 * Contract endpoint: GET /api/v1/geospatial/{farm_id}
 */
export async function getGeospatial(farmId: number): Promise<GeospatialResponse> {
  if (USE_MOCKS) {
    return getMockGeospatial();
  }

  const response = await apiClient.get<GeospatialResponse>(`/api/v1/geospatial/${farmId}`);
  return response.data;
}
