# CropShift API Specification

This document contains the frozen API specification for the CropShift backend engine endpoints. All request and response formats use Pydantic models with JSON payloads.

---

## 1. Health Endpoints

### 1.1 GET `/health` (Root Health Check)
*   **Description:** Core health check endpoint at the application root.
*   **Request:** None
*   **Response Status:** `200 OK`
*   **Response Body (JSON):**
    ```json
    {
      "status": "ok",
      "service": "cropshift-api",
      "version": "1.0.0"
    }
    ```

### 1.2 GET `/api/v1/health` (API V1 Health Check)
*   **Description:** API v1 health check endpoint.
*   **Request:** None
*   **Response Status:** `200 OK`
*   **Response Body (JSON):** Identical to root health check.

---

## 2. Decision Engine Endpoints

### 2.1 POST `/api/v1/recommendations`
*   **Description:** Generates recommendations for alternative oilseed crops based on farm conditions.
*   **Request Body (JSON):**
    ```json
    {
      "farm_id": 1
    }
    ```
*   **Response Status:** `200 OK`
*   **Response Body (JSON):**
    ```json
    {
      "recommended_crop": "Groundnut",
      "suitability_score": 87,
      "profitability_score": 76,
      "market_score": 90,
      "risk_score": 28,
      "safety_score": 82,
      "decision": "SWITCH",
      "expected_profit": 43000.0,
      "current_crop_profit": 34000.0,
      "profit_difference": 9000.0,
      "reasons": [
        "Regionally suitable for your state and district.",
        "Expected profit is higher than Paddy.",
        "Market prices and trends are favorable."
      ],
      "risks": [
        "Price risk is moderate.",
        "Drought or weather conditions can impact yield."
      ]
    }
    ```
*   **Error Responses:**
    *   `404 Not Found` (Code: `FARM_NOT_FOUND`) if the farm does not exist.
    *   `422 Unprocessable Entity` (Code: `INVALID_INPUT`) if `farm_id` is missing or malformed.

### 2.2 GET `/api/v1/profitability/{farm_id}`
*   **Description:** Returns detailed economic figures comparing the current crop vs recommended crop.
*   **Request:** None (Path parameter: `farm_id`)
*   **Response Status:** `200 OK`
*   **Response Body (JSON):**
    ```json
    {
      "current_crop": {
        "crop_id": 1,
        "crop_name": "Paddy",
        "expected_yield": 20.0,
        "yield_unit": "quintal",
        "production_cost": 18000.0,
        "expected_revenue": 52000.0,
        "estimated_profit": 34000.0,
        "data_status": "VERIFIED"
      },
      "recommended_crop": {
        "crop_id": 2,
        "crop_name": "Groundnut",
        "expected_yield": 10.0,
        "yield_unit": "quintal",
        "production_cost": 12000.0,
        "expected_revenue": 55000.0,
        "estimated_profit": 43000.0,
        "data_status": "VERIFIED"
      },
      "expected_yield": 10.0,
      "production_cost": 12000.0,
      "expected_revenue": 55000.0,
      "estimated_profit": 43000.0,
      "profit_difference": 9000.0
    }
    ```

### 2.3 GET `/api/v1/markets/{crop_id}`
*   **Description:** Sourced market intelligence details including reference price, local market price, distance, and scoring.
*   **Request Query Parameters:**
    *   `farm_id` (Optional, integer) to calculate actual distance and localized market scores.
*   **Response Status:** `200 OK`
*   **Response Body (JSON):**
    ```json
    {
      "crop_id": 2,
      "crop_name": "Groundnut",
      "price": 5500.0,
      "price_unit": "quintal",
      "market_name": "Tumkur APMC",
      "market_location": {
        "latitude": 13.34,
        "longitude": 77.1
      },
      "distance_km": 0.3,
      "trend": "UPWARD",
      "market_score": 90,
      "data_status": "VERIFIED",
      "data_source": "Seeded Database"
    }
    ```

### 2.4 GET `/api/v1/subsidies/{farm_id}`
*   **Description:** Government schemes matched dynamically against farm details.
*   **Request Query Parameters:**
    *   `has_land_proof` (Optional, boolean, defaults to false)
    *   `has_soil_health_card` (Optional, boolean, defaults to false)
*   **Response Status:** `200 OK`
*   **Response Body (JSON):**
    ```json
    [
      {
        "scheme_id": "nmeo_os",
        "scheme_name": "National Mission on Edible Oils — Oilseeds (NMEO-OS)",
        "relevance": "HIGH",
        "eligibility_status": "VERIFICATION_REQUIRED",
        "eligibility_factors": [
          "Recommended crop: Groundnut (Oilseed: True)",
          "Farm state: Karnataka",
          "Land ownership proof provided: False"
        ],
        "required_information": [
          "Land ownership certificate (RoR/Patta)",
          "Aadhaar card linked to land records"
        ],
        "support_information": "Subsidies for high-yielding oilseed seed distribution, farm toolkits, and cultivator training.",
        "verification_required": true,
        "data_source": "Ministry of Agriculture & Farmers Welfare, Government of India"
      }
    ]
    ```

### 2.5 GET `/api/v1/geospatial/{farm_id}`
*   **Description:** Geographic coordinates, context, and nearest market details calculated using PostGIS.
*   **Request:** None (Path parameter: `farm_id`)
*   **Response Status:** `200 OK`
*   **Response Body (JSON):**
    ```json
    {
      "farm": {
        "latitude": 13.3409,
        "longitude": 77.1025
      },
      "nearby_markets": [
        {
          "market_id": 1,
          "market_name": "Tumkur APMC",
          "distance_km": 0.3
        }
      ],
      "distance_information": "Nearest market is Tumkur APMC at 0.3 km.",
      "geographic_context": {
        "district": "Tumkur",
        "state": "Karnataka",
        "agro_climatic_zone": null,
        "nearby_market_count": 1
      }
    }
    ```

### 2.6 POST `/api/v1/risk-simulation`
*   **Description:** Risk simulation evaluating Safety Score and Decision output under four environmental scenarios.
*   **Request Body (JSON):**
    ```json
    {
      "farm_id": 1,
      "crop_id": 2
    }
    ```
*   **Response Status:** `200 OK`
*   **Response Body (JSON):**
    ```json
    {
      "baseline": { "safety_score": 82, "decision": "SWITCH" },
      "price_down": { "safety_score": 69, "decision": "CAUTION" },
      "yield_down": { "safety_score": 63, "decision": "CAUTION" },
      "water_risk": { "safety_score": 48, "decision": "DONT_SWITCH" }
    }
    ```

### 2.7 POST `/api/v1/ivr/recommendation`
*   **Description:** Voice-compatible recommendation flow for agricultural Interactive Voice Response (IVR) phone calls.
*   **Request Body (JSON):**
    ```json
    {
      "farmer_id": 1
    }
    ```
*   **Response Status:** `200 OK`
*   **Response Body (JSON):**
    ```json
    {
      "farmer_name": "Raju Naik",
      "verified": true,
      "voice_script": "Namaste Raju Naik. For your one acre farm, groundnut is recommended. Safety score eighty two out of one hundred. Expected profit is higher by nine thousand rupees per acre. Market prices may change.",
      "recommendation": {
        "recommended_crop": "Groundnut",
        "suitability_score": 87,
        "profitability_score": 76,
        "market_score": 90,
        "risk_score": 28,
        "safety_score": 82,
        "decision": "SWITCH",
        "expected_profit": 43000.0,
        "current_crop_profit": 34000.0,
        "profit_difference": 9000.0,
        "reasons": [...],
        "risks": [...]
      },
      "language": "en"
    }
    ```
