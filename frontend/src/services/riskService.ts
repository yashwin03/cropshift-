import apiClient from './apiClient';
import type { RiskRequest, RiskSimulationResponse } from '../types/api';
import { USE_MOCKS, delay } from '../mocks';
import { GOLDEN_DEMO_RISK } from '../mocks/riskFixtures';

/**
 * Mock risk simulation details resolver.
 */
export async function getMockRiskSimulation(): Promise<RiskSimulationResponse> {
  await delay(300);
  return GOLDEN_DEMO_RISK;
}

/**
 * Risk simulation service method.
 * Contract endpoint: POST /api/v1/risk-simulation
 */
export async function simulateRisk(req: RiskRequest): Promise<RiskSimulationResponse> {
  if (USE_MOCKS) {
    return getMockRiskSimulation();
  }

  const response = await apiClient.post<RiskSimulationResponse>('/api/v1/risk-simulation', req);
  return response.data;
}
