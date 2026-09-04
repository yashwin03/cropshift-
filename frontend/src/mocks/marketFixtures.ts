import type { MarketItem } from '../types/api';

export const GOLDEN_DEMO_GROUNDNUT_MARKET: MarketItem = {
  crop_id: 2,
  crop_name: 'Groundnut',
  price: 6200,
  price_unit: 'Quintal',
  market_name: 'Kurnool Market',
  market_location: 'Kurnool, AP',
  distance_km: 12.5,
  trend: 'RISING',
  market_score: 90,
  data_status: 'REAL',
  data_source: 'Agmarknet (live feed)',
};

export const GOLDEN_DEMO_PADDY_MARKET: MarketItem = {
  crop_id: 1,
  crop_name: 'Paddy',
  price: 2183,
  price_unit: 'Quintal',
  market_name: 'Adoni Market',
  market_location: 'Adoni, AP',
  distance_km: 24.0,
  trend: 'STABLE',
  market_score: 65,
  data_status: 'STATIC',
  data_source: 'Agmarknet (reference snapshot)',
};

export const CAUTION_COTTON_MARKET: MarketItem = {
  crop_id: 3,
  crop_name: 'Cotton',
  price: 7100,
  price_unit: 'Quintal',
  market_name: 'Yemmiganur Market',
  market_location: 'Yemmiganur, AP',
  distance_km: 18.2,
  trend: 'FALLING',
  market_score: 55,
  data_status: 'ESTIMATED',
  data_source: 'APMC Market Intelligence Cell',
};

export const UNAVAILABLE_MARKET: MarketItem = {
  crop_id: 99,
  crop_name: 'Unknown Crop',
  price: 0, // indicates unavailable/missing price
  price_unit: 'Quintal',
  market_name: 'Regional APMC Hub',
  market_location: 'District Headquarter',
  distance_km: 45.0,
  trend: 'STABLE',
  market_score: 30,
  data_status: 'DEMO',
  data_source: 'Demo price repository',
};
