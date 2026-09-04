# CropShift Golden Demo Reference

This document describes the parameters, expected values, and safety score derivation for the Golden Demo Farm (Farm ID 1) shifting from Paddy to Groundnut.

## Golden Demo Farm (Farm ID 1) Baseline Parameters
- **Farmer:** Raju Naik (district Tumkur, state Karnataka)
- **Land Area:** 1.0 acre
- **Water Availability:** True (available)
- **Soil Type:** "red laterite"
- **Current Crop:** Paddy (Crop ID 1)

## Crop Economics & Prices (Tumkur Region - Sourced from Database)
*   **Paddy (Current Crop):**
    *   Expected Yield: 20.0 quintals/acre
    *   Production Cost: ₹18,000/acre
    *   Market Reference Price: ₹2,600/quintal
    *   Expected Revenue: `20.0 * 2600 = ₹52,000/acre`
    *   Estimated Profit: `52,000 - 18,000 = ₹34,000/acre`
*   **Groundnut (Alternative Crop):**
    *   Expected Yield: 10.0 quintals/acre
    *   Production Cost: ₹12,000/acre
    *   Market Reference Price: ₹5,500/quintal
    *   Expected Revenue: `10.0 * 5500 = ₹55,000/acre`
    *   Estimated Profit: `55,000 - 12,000 = ₹43,000/acre`

Profit Difference: `₹43,000 - ₹34,000 = ₹9,000/acre` (favoring Groundnut).
Profitability Score: `round(50 + (9000 / 34000) * 100) = 76`.

## Components & Weights
The headline Safety Score is computed from four components:

| Component | Weight | Golden Demo Value | Weighted Contribution |
| :--- | :---: | :---: | :---: |
| **Suitability** | 0.35 | 87 | 30.45 |
| **Profitability** | 0.30 | 76 | 22.80 |
| **Market Intelligence** | 0.20 | 90 | 18.00 |
| **Risk Inverse (100 - Risk)** | 0.15 | 72 (Risk = 28) | 10.80 |

### Derivation & Rounding
Under baseline conditions, the calculated Risk Score is `28`, yielding a Risk Inverse score of `72` (100 - 28).

$$\text{Safety Score} = 87 \times 0.35 + 76 \times 0.30 + 90 \times 0.20 + (100 - 28) \times 0.15$$
$$\text{Safety Score} = 30.45 + 22.80 + 18.00 + 10.80 = 82.05$$

Applying Python's `round()` once at the end:
$$\text{Safety Score} = \text{round}(82.05) = 82$$

### Decision Thresholds
Since the computed safety score is `82` (within the `80-100` bracket), the recommended decision is **`SWITCH`**.
