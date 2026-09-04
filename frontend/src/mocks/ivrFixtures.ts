import type { IvrResponse } from '../types/api';

export const GOLDEN_DEMO_IVR: IvrResponse = {
  farmer_name: 'Rajesh Kumar',
  voice_script: 'Namaste Rajesh ji. Aapke do acre khet ke liye CropShift Salah kehta hai ki aap Dhan yaani Paddy ki jagah Mungphali yaani Groundnut lagayein. Groundnut lagane se aapko ₹9,000 prati acre ka zyada munafe hone ki sambhavna hai. Is badlaav ki safety score 82 pratishat hai jo ki surakshit hai.',
  recommendation: {
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
    reasons: ['Suitable for your farm', 'Higher expected profit'],
    risks: ['Market price may fluctuate'],
  },
};
