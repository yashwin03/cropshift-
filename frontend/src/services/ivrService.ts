import apiClient from './apiClient';
import type { IvrRequest, IvrResponse } from '../types/api';
import { USE_MOCKS, delay } from '../mocks';
import { GOLDEN_DEMO_IVR } from '../mocks/ivrFixtures';

/**
 * Mock IVR details resolver.
 * Centralized simulation logic.
 */
export async function getMockIvrResponse(farmerId: number): Promise<IvrResponse> {
  await delay(600);
  if (farmerId === 1) {
    return GOLDEN_DEMO_IVR;
  }
  // Simulate API error contract structure for farmer not found
  throw {
    response: {
      data: {
        error: {
          code: 'FARMER_NOT_FOUND',
          message: `Farmer profile with ID ${farmerId} does not exist in our systems.`,
          details: [],
        },
      },
    },
    message: `Farmer ID ${farmerId} not found.`,
  };
}

/**
 * IVR service method.
 * Contract endpoint: POST /api/v1/ivr/recommendation
 */
export async function getIvrRecommendation(req: IvrRequest): Promise<IvrResponse> {
  if (USE_MOCKS) {
    return getMockIvrResponse(req.farmer_id);
  }

  const response = await apiClient.post<IvrResponse>('/api/v1/ivr/recommendation', req);
  return response.data;
}
