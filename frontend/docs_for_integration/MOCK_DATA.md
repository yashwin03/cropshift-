
# Frontend Mock Data & Fixtures

This document details the mock data system that allows running the application in a fully isolated sandbox mode without an active backend.

## Toggle Switch

To control the mock engine, configure the environment variable:
- VITE_USE_MOCKS=true: Mock API endpoints intercept all API calls and return the static mock fixtures.
- VITE_USE_MOCKS=false: The API client makes real network requests.

## Mock Fixtures Location
All mock data generators and handler responses are located in src/mocks.ts.

## Mock Scenarios & Exercises

### 1. Golden Demo Data (Rajesh Kumar)
- Trigger: Click Load Golden Demo on the HomePage.
- Farm Profile: Rajesh Kumar, Cotton (2 acres), Groundnut recommendation.
- Exercises:
  - RecommendationPage: Renders a SWITCH decision with 82 Safety Score.
  - ProfitabilityPage: Compares Cotton vs Groundnut showing +₹18,000 profit difference.
  - MarketPage: Groundnut market price (₹7,500/Q) with rising trend; Cotton (₹6,800/Q) stable.
  - MapPage: 3 yards nearby (Kurnool Yard at 12km, Adoni Yard at 28km, Yemmiganur at 35km).
  - SubsidiesPage: Matches National Mission on Oilseeds (Eligible) and Soil Health Scheme.
  - RiskSimulationPage: Water risk drops safety score to 48 (DONT_SWITCH decision alert).

### 2. IVR Simulator ID Mappings
- Farmer ID 1: Rajesh Kumar (Returns SWITCH decision recommendation for Groundnut).
- Farmer ID 2: Ramesh Rao (Returns CAUTION decision recommendation).
- Farmer ID 3: Suresh Patel (Returns DONT_SWITCH decision recommendation).
- Any Other ID: Returns 404 client error with code FARMER_NOT_FOUND.
