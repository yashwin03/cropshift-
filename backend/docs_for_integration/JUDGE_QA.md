# CropShift Backend Credibility - Judge Q&A

This document contains honest, technical answers to the judge credibility questions for the CropShift backend engine.

---

### 1. "How did you calculate 82?"
The headline Safety Score of `82` for the Golden Demo (Farm 1 shifting to Groundnut) is derived deterministically from four weighted component scores:
*   **Suitability (35% weight):** Score = `87` (Regional suitability: 30, Water: 30, Soil: 12, Season: 15) -> Contribution = `30.45`
*   **Profitability (30% weight):** Score = `76` (`round(50 + (9000 / 34000) * 100)`) -> Contribution = `22.80`
*   **Market Intelligence (20% weight):** Score = `90` -> Contribution = `18.00`
*   **Risk Inverse (15% weight):** Score = `72` (100 - Risk Score of 28) -> Contribution = `10.80`

**Sum of Contributions:**
$$\text{Safety Score} = 30.45 + 22.80 + 18.00 + 10.80 = 82.05$$
Applying Python's built-in `round()` once at the end yields `82`.

---

### 2. "Where did the market data come from?"
The market data is sourced from a static relational database snapshot reflecting regional market figures for Tumkur district. The `data_status` of the seeded market record is marked as `VERIFIED`.

---

### 3. "Where did subsidy information come from?"
Subsidy schemes are mapped from official Indian agricultural programs (Ministry of Agriculture & Farmers Welfare) including PM-KISAN, PMFBY, and the National Edible Oil Mission (NMEO-OS). To maintain credibility, matches default to `VERIFICATION_REQUIRED` when land ownership proofs are missing rather than falsely assuming eligibility.

---

### 4. "Is this AI?"
No, this is a fully deterministic, weighted, rule-based decision engine. We explicitly do not use ML or probabilistic models. This is a deliberate choice: it makes every score completely explainable, auditable, traceable, and repeatable without hallucination risks or unpredictable outputs.

---

### 5. "Is the data live?"
No, the database contains static snapshots seeded for the MVP demonstration. The endpoint payloads carry a `data_status` metadata field (`VERIFIED`, `ESTIMATED`, or `DEMO`) to inform judges and farmers honestly about the data source status.

---

### 6. "What happens when conditions change?"
When conditions change (e.g. simulated price drop or water shortage), the risk engine re-runs the identical pipeline logic with the modified parameters (e.g. `water_availability = False`). This recalculates the sub-scores and Safety Score dynamically, generating a new decision output.

---

### 7. "How does risk affect the recommendation?"
The Risk Inverse (100 - Risk) represents 15% of the overall Safety Score. The Risk Score itself is calculated dynamically by evaluating four key threat vectors: region-crop compatibility risk, water scarcity risk, soil mismatch risk, and market price trend fluctuation risk.

---

### 8. "How does IVR use the same engine?"
The IVR endpoint `POST /api/v1/ivr/recommendation` imports and calls the exact same `generate_recommendation()` function from `app/decision_engine/recommendation.py` that the web API uses. This is enforced by a automated parity test asserting matching Safety Scores and decisions.

---

### 9. "Can the farmer understand the recommendation?"
Yes. The explainability layer translates the raw numeric scores into plain-language bullet points of 3–5 reasons (why to switch) and 1–4 risk factors (things to be cautious about), displayed alongside the safety score and decision threshold context.

---

### 10. "Can this scale beyond the demo?"
Yes. The codebase is designed as a modular monolith. Data-retrieval layers are abstracted into services (`crop_service`, `market_service`). To scale, the static database adapters would be replaced with real-time service endpoints (e.g., live Agmarknet APIs for prices and IMD APIs for weather coordinates).
