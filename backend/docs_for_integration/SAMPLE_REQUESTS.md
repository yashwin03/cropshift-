# CropShift Sample Requests (curl & JSON)

Use these copy-pasteable curl commands and JSON payloads to execute requests against a running local server instance (assumed running on `http://localhost:8000`).

---

## 1. Health Checks
```bash
curl -X GET http://localhost:8000/health
```

```bash
curl -X GET http://localhost:8000/api/v1/health
```

---

## 2. Generate Recommendations
```bash
curl -X POST http://localhost:8000/api/v1/recommendations \
  -H "Content-Type: application/json" \
  -d '{"farm_id": 1}'
```

---

## 3. Crop Profitability
```bash
curl -X GET http://localhost:8000/api/v1/profitability/1
```

---

## 4. Market Intelligence
```bash
curl -X GET "http://localhost:8000/api/v1/markets/2?farm_id=1"
```

---

## 5. Government Subsidies
```bash
curl -X GET "http://localhost:8000/api/v1/subsidies/1?has_land_proof=true&has_soil_health_card=true"
```

---

## 6. Geospatial Intelligence
```bash
curl -X GET http://localhost:8000/api/v1/geospatial/1
```

---

## 7. Risk Simulation
```bash
curl -X POST http://localhost:8000/api/v1/risk-simulation \
  -H "Content-Type: application/json" \
  -d '{"farm_id": 1, "crop_id": 2}'
```

---

## 8. IVR (Interactive Voice Response) Call Flow
```bash
curl -X POST http://localhost:8000/api/v1/ivr/recommendation \
  -H "Content-Type: application/json" \
  -d '{"farmer_id": 1}'
```
