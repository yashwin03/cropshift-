
# Frontend Routing System

This document outlines the routing scheme built into CropShift using eact-router-dom.

## Route Definitions

All routes are declared in src/App.tsx and wrapped inside MainLayout for navigation, header status banners, and footers.

| Path | Page Component | Required Params / Context | Description |
|---|---|---|---|
| / | HomePage | None | Dashboard. Displays the farmer greeting, farm details (if configured), recommendation summary card, and quick links to other modules. |
| /analyze | FarmInfoPage | None (reads/writes local storage) | Step-by-step wizard to collect details (State, District, Current Crop, Land Area, Soil Type, Water Availability). Form state is validated and persists to localStorage. |
| /recommendation | RecommendationPage | Local Storage context (requires farm profile) | Decision Support screen showing safety score, 4-factor breakdown (Suitability, Profitability, Market, Risk), calculations accordion, and forward navigation options. |
| /profit | ProfitabilityPage | Local Storage context (requires farm profile) | Details crop margins per acre, comparative profitability charts (expected revenue, production costs, estimated profits), and detailed line comparisons. |
| /market | MarketPage | Local Storage context (requires farm profile) | Local market metrics, price trends, demand index, data sources, and verified credentials. |
| /map | MapPage | Local Storage context (requires farm profile) | Leaflet geospatial map containing local market yards, crop-growing centers, and sorted distances in km. |
| /subsidies | SubsidiesPage | Local Storage context (requires farm profile) | matching government schemes, eligibility details, application steps, and verify-required warnings. |
| /risk | RiskSimulationPage | Local Storage context (requires farm profile) | Simulates four risk scenarios (baseline, price drop, yield drop, water risk) and highlights decision changes. |
| /ivr | IvrPage | None | Dialpad simulator to experience the decision support engine via voice script and transcripts. |
| * | NotFoundPage | None | Generic 404 handler for unknown routes. Renders a message and link back to Home (/). |
