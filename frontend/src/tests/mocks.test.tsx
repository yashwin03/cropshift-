import { describe, test, expect } from 'vitest';
import { GOLDEN_DEMO_RECOMMENDATION, CAUTION_RECOMMENDATION, DONT_SWITCH_RECOMMENDATION } from '../mocks/fixtures';
import { GOLDEN_DEMO_GEOSPATIAL } from '../mocks/geospatialFixtures';
import { GOLDEN_DEMO_GROUNDNUT_MARKET, GOLDEN_DEMO_PADDY_MARKET } from '../mocks/marketFixtures';
import { GOLDEN_DEMO_SUBSIDIES } from '../mocks/subsidyFixtures';
import { GOLDEN_DEMO_RISK } from '../mocks/riskFixtures';
import { GOLDEN_DEMO_IVR } from '../mocks/ivrFixtures';

describe('Mock Data Shape Verification Tests', () => {
  test('golden recommendation fields match api contract exactly', () => {
    const keys = Object.keys(GOLDEN_DEMO_RECOMMENDATION);
    expect(keys).toContain('recommended_crop');
    expect(keys).toContain('suitability_score');
    expect(keys).toContain('profitability_score');
    expect(keys).toContain('market_score');
    expect(keys).toContain('risk_score');
    expect(keys).toContain('safety_score');
    expect(keys).toContain('decision');
    expect(keys).toContain('expected_profit');
    expect(keys).toContain('current_crop_profit');
    expect(keys).toContain('profit_difference');
    expect(keys).toContain('reasons');
    expect(keys).toContain('risks');

    expect(GOLDEN_DEMO_RECOMMENDATION.decision).toBe('SWITCH');
    expect(CAUTION_RECOMMENDATION.decision).toBe('CAUTION');
    expect(DONT_SWITCH_RECOMMENDATION.decision).toBe('DONT_SWITCH');
  });

  test('golden geospatial fields match api contract exactly', () => {
    const keys = Object.keys(GOLDEN_DEMO_GEOSPATIAL);
    expect(keys).toContain('farm');
    expect(keys).toContain('nearby_markets');
    expect(keys).toContain('distance_information');
    expect(keys).toContain('geographic_context');

    expect(GOLDEN_DEMO_GEOSPATIAL.farm.latitude).toBeDefined();
    expect(GOLDEN_DEMO_GEOSPATIAL.farm.longitude).toBeDefined();
  });

  test('golden market fields match api contract exactly', () => {
    const keys = Object.keys(GOLDEN_DEMO_GROUNDNUT_MARKET);
    expect(keys).toContain('crop_id');
    expect(keys).toContain('crop_name');
    expect(keys).toContain('price');
    expect(keys).toContain('price_unit');
    expect(keys).toContain('market_name');
    expect(keys).toContain('market_location');
    expect(keys).toContain('distance_km');
    expect(keys).toContain('trend');
    expect(keys).toContain('market_score');
    expect(keys).toContain('data_status');
    expect(keys).toContain('data_source');
  });

  test('golden subsidies fields match api contract exactly', () => {
    GOLDEN_DEMO_SUBSIDIES.forEach(scheme => {
      const keys = Object.keys(scheme);
      expect(keys).toContain('scheme_id');
      expect(keys).toContain('scheme_name');
      expect(keys).toContain('relevance');
      expect(keys).toContain('eligibility_status');
      expect(keys).toContain('eligibility_factors');
      expect(keys).toContain('required_information');
      expect(keys).toContain('support_information');
      expect(keys).toContain('verification_required');
      expect(keys).toContain('data_source');
    });
  });

  test('golden risk simulation fields match api contract exactly', () => {
    const keys = Object.keys(GOLDEN_DEMO_RISK);
    expect(keys).toContain('baseline');
    expect(keys).toContain('price_down');
    expect(keys).toContain('yield_down');
    expect(keys).toContain('water_risk');

    expect(GOLDEN_DEMO_RISK.baseline.decision).toBe('SWITCH');
    expect(GOLDEN_DEMO_RISK.water_risk.decision).toBe('DONT_SWITCH');
  });

  test('golden ivr fields match api contract exactly', () => {
    const keys = Object.keys(GOLDEN_DEMO_IVR);
    expect(keys).toContain('farmer_name');
    expect(keys).toContain('voice_script');
    expect(keys).toContain('recommendation');
  });
});
