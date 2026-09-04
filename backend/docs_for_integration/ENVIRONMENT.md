# CropShift Backend Environment Variables

This document lists all configuration variables required by the CropShift backend engine.

---

## 1. Environment Variables Config Checklist

| Variable | Description | Example / Default | Required? |
| :--- | :--- | :--- | :---: |
| `DATABASE_URL` | PostgreSQL connection string including port and credentials. | `postgresql://postgres:12345@localhost:5433/cropshift` | Yes |
| `CORS_ORIGINS` | JSON list of allowed origins for cross-origin requests. | `["http://localhost:3000","http://localhost:5173"]` | Yes |

---

## 2. Working Example `.env` File
Create a `.env` file in the root of the `backend/` folder with exactly these contents:

```env
DATABASE_URL=postgresql://postgres:12345@localhost:5433/cropshift
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
```
