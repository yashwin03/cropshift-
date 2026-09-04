import type { RiskSimulationResponse } from '../types/api';

export const GOLDEN_DEMO_RISK: RiskSimulationResponse = {
  baseline: {
    safety_score: 82,
    decision: 'SWITCH',
  },
  price_down: {
    safety_score: 69,
    decision: 'CAUTION',
  },
  yield_down: {
    safety_score: 63,
    decision: 'CAUTION',
  },
  water_risk: {
    safety_score: 48,
    decision: 'DONT_SWITCH',
  },
};
