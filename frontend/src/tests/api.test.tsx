import { vi, describe, test, expect } from 'vitest';
import apiClient from '../services/apiClient';
import { 
  getRecommendation, 
  getProfitability, 
  getMarkets, 
  getSubsidies, 
  getGeospatial, 
  runRiskSimulation, 
  getIvrRecommendation,
  getHealth
} from '../services/api';

vi.mock('../services/apiClient', () => ({
  default: {
    post: vi.fn(),
    get: vi.fn(),
  },
  AxiosError: class extends Error {},
}));

vi.mock('../mocks', () => ({
  USE_MOCKS: false,
  delay: () => Promise.resolve(),
}));

describe('API Services Central Client Tests', () => {
  test('central callers dispatch to correct endpoint structures', async () => {
    vi.mocked(apiClient.post).mockResolvedValue({ data: { mock: 'data' } });
    vi.mocked(apiClient.get).mockResolvedValue({ data: { mock: 'data' } });

    await getRecommendation({ farm_id: 1 });
    expect(apiClient.post).toHaveBeenCalledWith('/api/v1/recommendations', { farm_id: 1 });

    await getProfitability(1, 2);
    expect(apiClient.get).toHaveBeenCalledWith('/api/v1/profitability/1', { params: { crop_id: 2 } });

    await getMarkets(10);
    expect(apiClient.get).toHaveBeenCalledWith('/api/v1/markets/10');

    await getSubsidies(1);
    expect(apiClient.get).toHaveBeenCalledWith('/api/v1/subsidies/1');

    await getGeospatial(1);
    expect(apiClient.get).toHaveBeenCalledWith('/api/v1/geospatial/1', { params: { radius_km: 50 } });

    await runRiskSimulation(1, 2);
    expect(apiClient.post).toHaveBeenCalledWith('/api/v1/risk-simulation', {
      farm_id: 1, crop_id: 2, price_variance: 0.8, yield_variance: 0.7
    });

    await getIvrRecommendation({ farmer_id: 1 });
    expect(apiClient.post).toHaveBeenCalledWith('/api/v1/ivr/recommendation', { farmer_id: 1 });

    await getHealth();
    expect(apiClient.get).toHaveBeenCalledWith('/health');
  });
});
