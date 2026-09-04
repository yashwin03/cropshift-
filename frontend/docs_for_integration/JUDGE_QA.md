
# Judge Credibility Answers (Frontend)

This document contains frontend answers to the judge credibility questions (Section 19 of the brief).

---

### 1. How did you calculate 82?
The safety score of 82 is not calculated directly in the frontend layer to avoid business logic duplication. It is computed deterministically in the backend's crop-shift decision engine using a weighted formula. The frontend exposes this scoring structure transparently:
- An explainable breakdown lists the 4 factors: Suitability (35%), Profitability (30%), Market (20%), and Risk (15%).
- A detailed calculation methodology drawer (accordion) explicitly documents the weights and calculation formulas.

### 2. Where did the market data come from?
The market information is linked directly to authoritative, verifiable data sources visible on the Market Page:
- Market yards are attributed to Agmarknet (Ministry of Agriculture).
- All market prices clearly show their data source (e.g., Agmarknet), and cards display their verification status (e.g., Government Verified).

### 3. Where did subsidy information come from?
Subsidy information matches government schemes like the National Mission on Oilseeds & Oil Palm (NMOOP) and Soil Health Card Scheme:
- Per-scheme details list the official data source (e.g., Department of Agriculture).
- Cards explicitly show a Verification Required indicator reminding farmers to verify details with local agricultural officers before applying.

### 4. Is this AI?
No. It is a robust, deterministic, rule-based decision support system. It is designed to prioritize complete explainability rather than a black-box AI recommendation, providing reasons and risk lists for every output.

### 5. Is the data live?
The data status and freshness are honestly marked using visual badges:
- Data marked as MOCK or DEMO is simulated sandbox data.
- Live data from backend endpoints carries timestamps or status details.

### 6. What happens when conditions change?
Farmers can simulate variations on the Risk Simulation Page. This page evaluates how the recommendation changes under four potential stress scenarios: baseline, price drop, yield drop, and water risk.

### 7. How does risk affect the recommendation?
Risk vulnerability is a key factor representing 15% of the overall safety score. High risk (e.g., high price volatility or drought vulnerability) directly lowers the safety score. The breakdown screen explicitly visualizes this weight.

### 8. How does IVR use the same engine?
The IVR channel interacts with the exact same backend decision engine. The IVR simulator page sends calls containing the farmer_id to the /api/v1/ivr endpoint, which maps directly to the recommendation model data.

### 9. Can the farmer understand the recommendation?
Yes, the recommendation page provides:
- A colored decision gauge (Green/Amber/Red representing Switch/Caution/Don't Switch).
- Simple plain-language bulleted reasons (e.g., why to switch, caution alerts).
- Clean, responsive mobile-first layouts designed for standard handheld devices.

### 10. Can this scale beyond the demo?
Yes. The app utilizes a fully typed client architecture where every service maps to defined TypeScript interfaces matching the frozen API contract, allowing easy integration with production backend APIs by switching VITE_USE_MOCKS=false.
