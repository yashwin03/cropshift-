import type { RecommendationResponse, ProfitabilityResponse, CropEconomics } from '../types/api';

export interface FarmDetails {
  farm_id: number;
  farm_name: string;
  land_area: number;
  current_crop: string;
  water_availability: 'Available' | 'Limited' | 'Scarce';
  district: string;
  state: string;
  soil_type?: string;
  latitude?: number;
  longitude?: number;
}

export const GOLDEN_DEMO_FARM: FarmDetails = {
  farm_id: 1,
  farm_name: 'Green Field Farm',
  land_area: 1,
  current_crop: 'Paddy',
  water_availability: 'Available',
  district: 'Demo District',
  state: 'Demo State',
  soil_type: 'Clayey',
  latitude: 12.9716,
  longitude: 77.5946
};

export const GOLDEN_DEMO_RECOMMENDATION: RecommendationResponse = {
  recommended_crop: 'Groundnut',
  suitability_score: 87,
  profitability_score: 76,
  market_score: 90,
  risk_score: 28,
  safety_score: 82,
  decision: 'SWITCH',
  expected_profit: 43000,
  current_crop_profit: 34000,
  profit_difference: 9000,
  reasons: [
    'Suitable for your farm',
    'Higher expected profit',
    'Favorable market conditions'
  ],
  risks: [
    'Market price may fluctuate'
  ]
};

// CAUTION scenario: Switch to Cotton with caution
export const CAUTION_RECOMMENDATION: RecommendationResponse = {
  recommended_crop: 'Cotton',
  suitability_score: 72,
  profitability_score: 75,
  market_score: 65,
  risk_score: 60,
  safety_score: 68,
  decision: 'CAUTION',
  expected_profit: 38000,
  current_crop_profit: 34000,
  profit_difference: 6000,
  reasons: [
    'Moderate suitability for soil type',
    'Slightly higher margins than Paddy'
  ],
  risks: [
    'Requires more water monitoring',
    'Market prices are currently volatile'
  ]
};

// DONT_SWITCH scenario: continue Paddy
export const DONT_SWITCH_RECOMMENDATION: RecommendationResponse = {
  recommended_crop: 'Paddy',
  suitability_score: 90,
  profitability_score: 50,
  market_score: 45,
  risk_score: 40,
  safety_score: 56,
  decision: 'DONT_SWITCH',
  expected_profit: 30000,
  current_crop_profit: 34000,
  profit_difference: -2000,
  reasons: [
    'Highly suitable for your current water availability',
    'Stable production history'
  ],
  risks: [
    'Lower profits compared to continuation',
    'Market prices falling for shift crops'
  ]
};

// ─── Profitability Fixtures ───────────────────────────────────────────────

export const GOLDEN_DEMO_PADDY_ECONOMICS: CropEconomics = {
  crop_id: 1,
  crop_name: 'Paddy',
  expected_yield: 20,
  yield_unit: 'Quintal / acre',
  production_cost: 18000,
  expected_revenue: 52000,
  estimated_profit: 34000,
  data_status: 'STATIC',
};

export const GOLDEN_DEMO_GROUNDNUT_ECONOMICS: CropEconomics = {
  crop_id: 2,
  crop_name: 'Groundnut',
  expected_yield: 10,
  yield_unit: 'Quintal / acre',
  production_cost: 12000,
  expected_revenue: 55000,
  estimated_profit: 43000,
  data_status: 'ESTIMATED',
};

export const GOLDEN_DEMO_PROFITABILITY: ProfitabilityResponse = {
  current_crop: GOLDEN_DEMO_PADDY_ECONOMICS,
  recommended_crop: GOLDEN_DEMO_GROUNDNUT_ECONOMICS,
  expected_yield: 10,
  production_cost: 12000,
  expected_revenue: 55000,
  estimated_profit: 43000,
  profit_difference: 9000,
};

export const CAUTION_COTTON_ECONOMICS: CropEconomics = {
  crop_id: 3,
  crop_name: 'Cotton',
  expected_yield: 12,
  yield_unit: 'Quintal / acre',
  production_cost: 26000,
  expected_revenue: 64000,
  estimated_profit: 38000,
  data_status: 'ESTIMATED',
};

export const CAUTION_PROFITABILITY: ProfitabilityResponse = {
  current_crop: GOLDEN_DEMO_PADDY_ECONOMICS,
  recommended_crop: CAUTION_COTTON_ECONOMICS,
  expected_yield: 12,
  production_cost: 26000,
  expected_revenue: 64000,
  estimated_profit: 38000,
  profit_difference: 6000,
};

export const DONT_SWITCH_PROFITABILITY: ProfitabilityResponse = {
  current_crop: GOLDEN_DEMO_PADDY_ECONOMICS,
  recommended_crop: {
    ...GOLDEN_DEMO_PADDY_ECONOMICS,
    estimated_profit: 30000,
    expected_revenue: 58000,
  },
  expected_yield: 25,
  production_cost: 28000,
  expected_revenue: 58000,
  estimated_profit: 30000,
  profit_difference: -2000,
};

