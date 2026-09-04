import apiClient from './apiClient';
import type { 
  RecommendationRequest, 
  RecommendationResponse,
  ProfitabilityResponse,
  MarketItem,
  SubsidyScheme,
  GeospatialResponse,
  RiskRequest,
  RiskSimulationResponse,
  IvrRequest,
  IvrResponse
} from '../types/api';
import { USE_MOCKS, delay } from '../mocks';

// Mock Resolvers
import { getMockRecommendation } from './recommendationService';
import { getMockProfitability } from './profitabilityService';
import { getMockMarkets } from './marketService';
import { getMockSubsidies } from './subsidyService';
import { getMockGeospatial } from './geospatialService';
import { getMockRiskSimulation } from './riskService';
import { getMockIvrResponse } from './ivrService';

/**
 * centralized api services
 */

export async function createFarm(farmData: any): Promise<any> {
  const response = await apiClient.post('/api/v1/farms', farmData);
  return response.data;
}

export async function updateFarm(farmId: number, farmData: any): Promise<any> {
  const response = await apiClient.put(`/api/v1/farms/${farmId}`, farmData);
  return response.data;
}

export async function getRecommendation(farm: any): Promise<RecommendationResponse> {
  if (USE_MOCKS) {
    return getMockRecommendation(farm);
  }
  const payload: RecommendationRequest = {
    farm_id: farm.farm_id, // now explicitly expecting farm_id
  };
  if (farm.latitude !== undefined) payload.latitude = farm.latitude;
  if (farm.longitude !== undefined) payload.longitude = farm.longitude;
  
  const response = await apiClient.post<RecommendationResponse>('/api/v1/recommendations', payload);
  return response.data;
}

export async function getProfitability(farmId?: number, cropId?: number): Promise<ProfitabilityResponse> {
  if (USE_MOCKS) {
    return getMockProfitability();
  }
  const response = await apiClient.get<ProfitabilityResponse>(`/api/v1/profitability/${farmId || 1}`, {
    params: { crop_id: cropId },
  });
  return response.data;
}

export async function getMarkets(cropId: number): Promise<MarketItem> {
  if (USE_MOCKS) {
    return getMockMarkets(cropId);
  }
  const response = await apiClient.get<MarketItem>(`/api/v1/markets/${cropId}`);
  return response.data;
}

export async function getSubsidies(farmId: number): Promise<SubsidyScheme[]> {
  if (USE_MOCKS) {
    return getMockSubsidies();
  }
  const response = await apiClient.get<SubsidyScheme[]>(`/api/v1/subsidies/${farmId}`);
  return response.data;
}

export async function getGeospatial(farmId: number, radiusKm: number = 50): Promise<GeospatialResponse> {
  if (USE_MOCKS) {
    return getMockGeospatial();
  }
  const response = await apiClient.get<GeospatialResponse>(`/api/v1/geospatial/${farmId}`, {
    params: { radius_km: radiusKm },
  });
  return response.data;
}

export async function runRiskSimulation(farmId: number, cropId: number, priceVariance: number = 0.8, yieldVariance: number = 0.7): Promise<RiskSimulationResponse> {
  if (USE_MOCKS) {
    return getMockRiskSimulation();
  }
  const response = await apiClient.post<RiskSimulationResponse>('/api/v1/risk-simulation', {
    farm_id: farmId,
    crop_id: cropId,
    price_variance: priceVariance,
    yield_variance: yieldVariance,
  });
  return response.data;
}

export async function getIvrRecommendation(req: IvrRequest): Promise<IvrResponse> {
  if (USE_MOCKS) {
    return getMockIvrResponse(req.farmer_id);
  }
  const response = await apiClient.post<IvrResponse>('/api/v1/ivr/recommendation', req);
  return response.data;
}

export async function getHealth(): Promise<{ status: string }> {
  const response = await apiClient.get<{ status: string }>('/health');
  return response.data;
}

export async function createFutureCropLot(payload: any, token?: string): Promise<any> {
  const response = await apiClient.post('/api/v1/farmer/future-crop-lots', payload, {
    headers: token ? { Authorization: `Bearer ${token}` } : undefined,
  });
  return response.data;
}

export { createDirectStockLot as createStockLot, uploadQualityCertificate, publishFarmerStockLot } from './stockLotService';

