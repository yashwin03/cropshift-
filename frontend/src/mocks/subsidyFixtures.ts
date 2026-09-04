import type { SubsidyScheme } from '../types/api';

export const GOLDEN_DEMO_SUBSIDIES: SubsidyScheme[] = [
  {
    scheme_id: 'scheme_1',
    scheme_name: 'National Mission on Oilseeds and Oil Palm (NMOOP)',
    relevance: 'HIGH',
    eligibility_status: 'LIKELY_ELIGIBLE',
    eligibility_factors: [
      'Shifting to Groundnut (Oilseed)',
      'Located in regional dry zone',
      'Water availability classified as Available',
    ],
    required_information: [
      'Land ownership title (Patta)',
      'Active bank account linked to Aadhaar',
      'Crop sowing self-declaration / photo',
    ],
    support_information: '₹2,500 per hectare direct seed subsidy + subsidised bio-fertilisers.',
    verification_required: true,
    data_source: 'Ministry of Agriculture & Farmers Welfare, Govt of India',
  },
  {
    scheme_id: 'scheme_2',
    scheme_name: 'Pradhan Mantri Krishi Sinchayee Yojana (PMKSY) - Micro Irrigation',
    relevance: 'MEDIUM',
    eligibility_status: 'VERIFICATION_REQUIRED',
    eligibility_factors: [
      'Micro-irrigation setup suitable for row-crops',
      'Land area under 5 acres',
    ],
    required_information: [
      'Soil & Water testing report (optional)',
      'Quotation from registered micro-irrigation vendor',
    ],
    support_information: 'Up to 55% subsidy on Drip & Sprinkler irrigation equipment installation.',
    verification_required: true,
    data_source: 'State Department of Agriculture',
  },
  {
    scheme_id: 'scheme_3',
    scheme_name: 'Rainfed Area Development (RAD) Component',
    relevance: 'LOW',
    eligibility_status: 'LIKELY_NOT_ELIGIBLE',
    eligibility_factors: [
      'Requires land in identified rainfed districts',
      'Requires integrated farming system setup',
    ],
    required_information: [
      'Detailed farm map and project report',
    ],
    support_information: 'Financial assistance of ₹25,500/hectare for farming systems.',
    verification_required: false,
    data_source: 'National Mission for Sustainable Agriculture',
  },
];
