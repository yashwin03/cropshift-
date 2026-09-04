import apiClient from './apiClient';
import type { SubsidyScheme } from '../types/api';
import { USE_MOCKS, delay } from '../mocks';
import { GOLDEN_DEMO_SUBSIDIES } from '../mocks/subsidyFixtures';

/**
 * Mock subsidies matcher resolver.
 */
export async function getMockSubsidies(): Promise<SubsidyScheme[]> {
  await delay(400);
  return GOLDEN_DEMO_SUBSIDIES;
}

/**
 * Subsidies service method.
 * Contract endpoint: GET /api/v1/subsidies/{farm_id}
 */
export async function getSubsidies(farmId: number): Promise<SubsidyScheme[]> {
  if (USE_MOCKS) {
    return getMockSubsidies();
  }

  const response = await apiClient.get<SubsidyScheme[]>(`/api/v1/subsidies/${farmId}`);
  return response.data;
}
