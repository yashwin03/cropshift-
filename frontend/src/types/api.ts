// Enums as string literal unions as required by Phase B0 Task 6

export type Decision = 'SWITCH' | 'CAUTION' | 'DONT_SWITCH';

export type Trend = 'RISING' | 'STABLE' | 'FALLING';

export type DataStatus = 'REAL' | 'STATIC' | 'DEMO' | 'ESTIMATED';

export type Relevance = 'HIGH' | 'MEDIUM' | 'LOW';

export type EligibilityStatus = 
  | 'LIKELY_ELIGIBLE'
  | 'VERIFICATION_REQUIRED'
  | 'LIKELY_NOT_ELIGIBLE';

// Coordinate structure for mapping
export interface User {
  id: number;
  username: string;
  email?: string;
  role?: string;
  farmer_id?: string;
}

export interface Coordinate {
  latitude: number;
  longitude: number;
}

// 10.1 Recommendation Types
export interface RecommendationRequest {
  farm_id: number;
  latitude?: number;
  longitude?: number;
}

export interface TopOilseedItem {
  rank: number;
  crop_id: number;
  crop_name: string;
  farm_suitability_score: number;
  water_suitability_score: number;
  economic_potential_score: number;
  overall_score: number;
  decision: Decision;
  expected_profit: number;
  profit_difference: number;
}

export interface RecommendationResponse {
  recommended_crop: string;
  suitability_score: number;
  profitability_score: number;
  market_score: number;
  risk_score: number;
  safety_score: number;
  decision: Decision;
  expected_profit: number;
  current_crop_profit: number;
  profit_difference: number;
  reasons: string[];
  risks: string[];

  // Oilseed-First Component Scores & Top 10 Ranking
  farm_suitability_score?: number;
  water_suitability_score?: number;
  economic_potential_score?: number;
  overall_score?: number;
  top_oilseeds?: TopOilseedItem[];
}

export interface PeerProofPeer {
  id: number;
  peer_display_id: string;
  crop_id?: number;
  crop_name?: string;
  district: string;
  state?: string;
  distance_km?: number;
  latitude?: number;
  longitude?: number;
  acres: number;
  yield_per_acre: number;
  selling_price?: number;
  net_realization?: number;
  crop_stage?: string;
  expected_harvest?: string;
  soil_type?: string;
  water_source?: string;
  contactable: boolean;
  verification_status: string;
  label?: string;
}

export interface PeerProofRegionSummary {
  district: string;
  farmer_count: number;
}

export interface PeerProofResponse {
  available: boolean;
  crop_id: number;
  crop_name: string;
  radius_km?: number;
  cohort_count: number;
  total_farmers?: number;
  total_districts?: number;
  regions?: PeerProofRegionSummary[];
  center_latitude?: number;
  center_longitude?: number;
  geographic_scope: string;
  season?: string;
  farm_size_range?: string;
  average_yield_quintals_per_acre?: number;
  average_selling_price_per_quintal?: number;
  average_net_realization_per_acre?: number;
  data_source: string;
  verification_status: string;
  message?: string;
  peers?: PeerProofPeer[];
}

// 10.2 Profitability Types
export interface CropEconomics {
  crop_id: number;
  crop_name: string;
  expected_yield: number;
  yield_unit: string;
  production_cost: number;
  expected_revenue: number;
  estimated_profit: number;
  data_status: DataStatus;
}

export interface ProfitabilityResponse {
  current_crop: CropEconomics;
  recommended_crop: CropEconomics;
  expected_yield: number;
  production_cost: number;
  expected_revenue: number;
  estimated_profit: number;
  profit_difference: number;
}

// 10.3 Market Types
export interface MarketItem {
  crop_id: number;
  crop_name: string;
  price: number;
  price_unit: string;
  market_name: string;
  market_location: string;
  distance_km: number;
  trend: Trend;
  market_score: number;
  data_status: DataStatus;
  data_source: string;
}

// 10.4 Subsidies Types
export interface SubsidyScheme {
  scheme_id: string;
  scheme_name: string;
  relevance: Relevance;
  eligibility_status: EligibilityStatus;
  eligibility_factors: string[];
  required_information: string[];
  support_information: string;
  verification_required: boolean;
  official_url?: string;
  data_source: string;
}

// 10.5 Geospatial Types
export interface NearbyMarketLocation {
  market_id?: number;
  market_name: string;
  latitude: number;
  longitude: number;
  distance_km: number;
  within_radius?: boolean;
  district?: string;
  state?: string;
  crop?: string;
  current_price?: number;
  price_unit?: string;
  trend?: string;
}

export interface FarmLocation {
  farm_id: number;
  farm_name?: string;
  latitude: number;
  longitude: number;
}

export interface GeospatialResponse {
  farm: FarmLocation;
  nearby_markets: NearbyMarketLocation[];
  distance_information: string; // distance information
  geographic_context: {
    district: string;
    state: string;
    markets_count: number;
  };
}

// 10.6 Risk Simulation Types
export interface RiskRequest {
  farm_id: number;
  crop_id: number;
}

export interface RiskScenario {
  safety_score: number;
  decision: Decision;
}

export interface RiskSimulationResponse {
  baseline: RiskScenario;
  price_down: RiskScenario;
  yield_down: RiskScenario;
  water_risk: RiskScenario;
}

// 10.7 IVR Types
export interface IvrRequest {
  farmer_id: number;
}

export interface IvrResponse {
  farmer_name: string;
  voice_script: string;
  recommendation: RecommendationResponse;
}

// Error Interface (Section 13)
export interface AppErrorDetail {
  field?: string;
  message: string;
}

export interface AppErrorResponse {
  error: {
    code: 'INVALID_FARM' | 'FARM_NOT_FOUND' | 'FARMER_NOT_FOUND' | 'CROP_NOT_FOUND' | 'INVALID_INPUT' | 'DATA_UNAVAILABLE' | 'INTERNAL_ERROR' | 'NETWORK_ERROR' | string;
    message: string;
    details: AppErrorDetail[];
  };
}

// Normalized UI error representation
export interface AppError {
  code: string;
  message: string;
  details?: AppErrorDetail[];
}

// 10.8 Buyer Demand Types
export type BuyerDemandStatus = 'ACTIVE' | 'FULFILLED' | 'CANCELLED' | 'EXPIRED';

export interface BuyerDemand {
  id: number;
  buyer_id: number;
  crop_id: number;
  crop_name?: string;
  variety?: string;
  quantity_quintals: number;
  target_price_per_quintal: number;
  delivery_district: string;
  delivery_state?: string;
  delivery_market_name?: string;
  expected_harvest_start?: string;
  expected_harvest_end?: string;
  quality_grade?: string;
  status: BuyerDemandStatus;
  created_at: string;
  updated_at: string;
  company_name?: string;
  posted_date?: string;
}

export interface BuyerDemandCreate {
  crop_id: number;
  variety?: string;
  quantity_quintals: number;
  target_price_per_quintal: number;
  delivery_district: string;
  delivery_state?: string;
  delivery_market_id?: number;
  expected_harvest_start?: string;
  expected_harvest_end?: string;
  quality_grade?: string;
}

export type FutureCropLotStatus = 'DRAFT' | 'OPEN' | 'INDICATIVE_ACCEPTED' | 'CANCELLED' | 'HARVESTED' | 'EXPIRED';

export interface FutureCropLot {
  id: number;
  farm_id: number;
  farmer_id: number;
  crop_id: number;
  demand_id?: number | null;
  recommendation_id?: number | null;
  variety?: string | null;
  planned_acres: number;
  expected_quantity_quintals: number;
  asking_price_per_quintal?: number | null;
  planned_sowing_date: string;
  expected_harvest_start: string;
  expected_harvest_end: string;
  quality_grade?: string | null;
  status: FutureCropLotStatus;
  created_at: string;
  updated_at: string;
  farm_name?: string | null;
  crop_name?: string | null;
  district?: string | null;
  state?: string | null;
  demand_title?: string | null;
}

export interface FutureCropLotCreate {
  farm_id: number;
  crop_id: number;
  demand_id?: number | null;
  recommendation_id?: number | null;
  variety?: string | null;
  planned_acres: number;
  expected_quantity_quintals: number;
  asking_price_per_quintal?: number | null;
  planned_sowing_date: string;
  expected_harvest_start: string;
  expected_harvest_end: string;
  quality_grade?: string | null;
  status?: FutureCropLotStatus;
}

export interface FutureCropLotMarketplaceView {
  id: number;
  crop_id: number;
  crop_name?: string | null;
  variety?: string | null;
  planned_acres: number;
  expected_quantity_quintals: number;
  asking_price_per_quintal?: number | null;
  expected_harvest_start: string;
  expected_harvest_end: string;
  quality_grade?: string | null;
  district?: string | null;
  state?: string | null;
  status: FutureCropLotStatus;
  demand_id?: number | null;
  demand_title?: string | null;
  farmer_display_id?: string | null;
}

// 10.9 Pre-Sowing Bidding Types (Phase 5C)
export type BidStatus = 'SUBMITTED' | 'WITHDRAWN' | 'ACCEPTED' | 'REJECTED' | 'EXPIRED';

export interface Bid {
  id: number;
  future_crop_lot_id: number;
  buyer_id: number;
  offered_price_per_quintal: number;
  quantity_quintals: number;
  conditions?: string | null;
  status: BidStatus;
  created_at: string;
  updated_at: string;
  crop_name?: string | null;
  district?: string | null;
  buyer_display_id?: string | null;
  effective_offer_per_quintal?: number | null;
  effective_offer_note?: string | null;
}

export interface BidCreate {
  future_crop_lot_id: number;
  offered_price_per_quintal: number;
  quantity_quintals: number;
  conditions?: string | null;
}

// 10.10 Mutual Contact Sharing Types (Phase 6B)
export type ContactSharingStatus = 'PENDING' | 'MUTUAL_CONSENT' | 'REVOKED';

export interface ContactDetails {
  full_name?: string | null;
  phone?: string | null;
  email?: string | null;
  district?: string | null;
  state?: string | null;
  business_name?: string | null;
}

export interface ContactSharing {
  id: number;
  bid_id: number;
  status: ContactSharingStatus;
  farmer_consented: boolean;
  farmer_consented_at?: string | null;
  buyer_consented: boolean;
  buyer_consented_at?: string | null;
  created_at: string;
  updated_at: string;
  farmer_contact?: ContactDetails | null;
  buyer_contact?: ContactDetails | null;
}

// 10.11 StockLot / Harvest Types (Phase 7B)
export type StockLotStatus = 'DRAFT' | 'AVAILABLE' | 'PARTIALLY_SOLD' | 'SOLD' | 'CANCELLED';

export interface HarvestRequest {
  actual_quantity_quintals: number;
  actual_harvest_date: string;
  quality_grade?: string | null;
  asking_price_per_quintal?: number | null;
}

export interface StockLotCreate {
  farm_id: number;
  crop_id: number;
  actual_quantity_quintals: number;
  actual_harvest_date: string;
  variety?: string | null;
  quality_grade?: string | null;
  asking_price_per_quintal?: number | null;
}

export interface StockLotUpdate {
  actual_quantity_quintals?: number;
  actual_harvest_date?: string;
  variety?: string | null;
  quality_grade?: string | null;
  asking_price_per_quintal?: number | null;
}

export interface StockLot {
  id: number;
  farmer_id: number;
  farm_id: number;
  future_crop_lot_id?: number | null;
  crop_id: number;
  variety?: string | null;
  actual_quantity_quintals: number;
  available_quantity_quintals: number;
  actual_harvest_date: string;
  quality_grade?: string | null;
  asking_price_per_quintal?: number | null;
  status: StockLotStatus;
  created_at: string;
  updated_at: string;
  crop_name?: string | null;
  farm_name?: string | null;
  district?: string | null;
  state?: string | null;
}

export interface StockLotMarketplaceView {
  id: number;
  crop_id: number;
  crop_name?: string | null;
  variety?: string | null;
  available_quantity_quintals: number;
  actual_harvest_date: string;
  quality_grade?: string | null;
  asking_price_per_quintal?: number | null;
  district?: string | null;
  state?: string | null;
  status: StockLotStatus;
}

// 10.12 Post-Harvest StockBid Types (Phase 7C)
export type StockBidStatus = 'SUBMITTED' | 'WITHDRAWN' | 'ACCEPTED' | 'REJECTED' | 'EXPIRED';

export interface StockBidCreate {
  offered_price_per_quintal: number;
  requested_quantity_quintals: number;
  conditions?: string | null;
}

export interface StockBidAcceptRequest {
  allocated_quantity_quintals: number;
}

export interface StockBid {
  id: number;
  stock_lot_id: number;
  buyer_id: number;
  offered_price_per_quintal: number;
  requested_quantity_quintals: number;
  allocated_quantity_quintals: number;
  conditions?: string | null;
  status: StockBidStatus;
  created_at: string;
  updated_at: string;
  crop_name?: string | null;
  district?: string | null;
  buyer_display_id?: string | null;
  effective_offer_per_quintal?: number | null;
  effective_offer_note?: string | null;
}

export interface StockBidFarmerView {
  id: number;
  stock_lot_id: number;
  offered_price_per_quintal: number;
  requested_quantity_quintals: number;
  allocated_quantity_quintals: number;
  conditions?: string | null;
  status: StockBidStatus;
  created_at: string;
  buyer_display_id: string;
  effective_offer_per_quintal?: number | null;
  effective_offer_note?: string | null;
}

// 10.13 Post-Harvest TradeOrder Types (Phase 8B)
export type TradeOrderStatus = 'CREATED' | 'FULFILLED' | 'CANCELLED';

export type TradeOrderCancellationReason =
  | 'BUYER_CANCELLED'
  | 'FARMER_CANCELLED'
  | 'QUALITY_ISSUE'
  | 'NO_SHOW'
  | 'OTHER';

export interface TradeOrderCancelRequest {
  cancellation_reason?: TradeOrderCancellationReason;
}

export interface TradeOrder {
  id: number;
  stock_bid_id: number | null;
  stock_lot_id: number | null;
  buyer_id: number;
  farmer_id: number;
  allocated_quantity_quintals: number;
  agreed_price_per_quintal: number;
  status: TradeOrderStatus;
  cancellation_reason?: TradeOrderCancellationReason | null;
  created_at: string;
  updated_at: string;
  fulfilled_at?: string | null;
  cancelled_at?: string | null;
  crop_name?: string | null;
  district?: string | null;
  state?: string | null;
  buyer_display_id?: string | null;
  farmer_display_id?: string | null;
  contact_sharing_status?: string | null;
}

// 10.14 Crop Cultivation Record Types
export type CultivationStage = 'PLANNED' | 'GROWING' | 'READY_FOR_HARVEST' | 'HARVESTED';
export type EvidenceStatus = 'FARMER_DECLARED' | 'FIELD_EVIDENCE' | 'VERIFIED';

export interface CropCultivationRecord {
  id: number;
  farmer_id: number;
  farm_id: number;
  crop_id: number;
  crop_name: string;
  variety?: string | null;
  area_acres: number;
  cultivation_stage: CultivationStage;
  sowing_date?: string | null;
  expected_harvest_date?: string | null;
  expected_yield_quintals?: number | null;
  actual_harvest_quantity_quintals?: number | null;
  evidence_status: EvidenceStatus;
  notes?: string | null;
  created_at: string;
  updated_at: string;
  district?: string | null;
  state?: string | null;
}

export interface CropCultivationCreatePayload {
  farm_id: number;
  crop_id: number;
  variety?: string;
  area_acres: number;
  cultivation_stage: CultivationStage;
  sowing_date?: string;
  expected_harvest_date?: string;
  expected_yield_quintals?: number;
  notes?: string;
}

export interface CropCultivationUpdatePayload {
  variety?: string;
  area_acres?: number;
  cultivation_stage?: CultivationStage;
  sowing_date?: string;
  expected_harvest_date?: string;
  expected_yield_quintals?: number;
  notes?: string;
}

export interface RecordHarvestPayload {
  actual_harvest_quantity_quintals: number;
  notes?: string;
}



