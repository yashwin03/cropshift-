
# API Endpoint Mapping

This document details every service method in the frontend API client, its corresponding backend HTTP endpoint, the pages consuming the service, and the associated TypeScript types.

## Services & Endpoints

### 1. getFarmRecommendation(farmId: number)
- **HTTP Endpoint**: POST /api/v1/recommendations
- **Method**: POST
- **Request Body**: { farm_id: number }
- **Consumed By**: RecommendationPage (decision gauge, reasons, risks breakdown)
- **TypeScript Interface**: RecommendationResponse (inside frontend/src/types/api.ts)

### 2. getProfitability(farmId: number)
- **HTTP Endpoint**: POST /api/v1/profitability
- **Method**: POST
- **Request Body**: { farm_id: number }
- **Consumed By**: ProfitabilityPage, ProfitComparison, ProfitChart
- **TypeScript Interface**: ProfitabilityResponse (inside frontend/src/types/api.ts)

### 3. getMarketData(farmId: number)
- **HTTP Endpoint**: POST /api/v1/markets
- **Method**: POST
- **Request Body**: { farm_id: number }
- **Consumed By**: MarketPage, MarketCard
- **TypeScript Interface**: MarketResponse (inside frontend/src/types/api.ts)

### 4. getMapData(farmId: number)
- **HTTP Endpoint**: POST /api/v1/map
- **Method**: POST
- **Request Body**: { farm_id: number }
- **Consumed By**: MapPage, FarmMap
- **TypeScript Interface**: MapResponse (inside frontend/src/types/api.ts)

### 5. getSubsidies(farmId: number)
- **HTTP Endpoint**: POST /api/v1/subsidies
- **Method**: POST
- **Request Body**: { farm_id: number }
- **Consumed By**: SubsidiesPage, SubsidyCard
- **TypeScript Interface**: SubsidiesResponse (inside frontend/src/types/api.ts)

### 6. runRiskSimulation(farmId: number)
- **HTTP Endpoint**: POST /api/v1/risk-simulation
- **Method**: POST
- **Request Body**: { farm_id: number }
- **Consumed By**: RiskSimulationPage
- **TypeScript Interface**: RiskSimulationResponse (inside frontend/src/types/api.ts)

### 7. getIvrRecommendation(farmerId: number)
- **HTTP Endpoint**: POST /api/v1/ivr
- **Method**: POST
- **Request Body**: { farmer_id: number }
- **Consumed By**: IvrPage
- **TypeScript Interface**: IvrResponse (inside frontend/src/types/api.ts)
