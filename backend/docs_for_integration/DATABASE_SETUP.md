# CropShift Database Setup & Seeding

This guide documents the installation, configuration, and verification of the PostgreSQL / PostGIS database instance for the CropShift backend.

---

## 1. Prerequisites
- **PostgreSQL:** Version 15+ (local port: `5433`).
- **PostGIS:** Version 3+ extension.
- **Python Virtual Environment:** Installed packages listed in `requirements.txt` (specifically `SQLAlchemy`, `psycopg2-binary`, and `GeoAlchemy2`).

---

## 2. Environment Configuration
Update your `.env` file in the `backend/` directory:
```env
DATABASE_URL=postgresql://postgres:12345@localhost:5433/cropshift
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
```

---

## 3. Creating & Seeding the Database
The schema initialization and data seeding are structured as automated scripts. Execute the following commands in the virtual environment:

```powershell
# 1. Initialize Tables (this automatically loads schema and enables PostGIS spatial extension)
.\.venv\Scripts\python.exe -m app.database.init_db

# 2. Seed Data (deterministic baseline database rows)
.\.venv\Scripts\python.exe -m app.database.seed
```

---

## 4. Verification Queries
Connect using `psql` or any SQL runner and run these verification queries:

### 4.1 PostGIS Version Check
```sql
SELECT PostGIS_Full_Version();
```
*Expected Output:* Shows active PostGIS spatial extension version (e.g. `3.6.2`).

### 4.2 Seed Verification Query
```sql
SELECT id, name, district, state FROM farmer;
```
*Expected Output:*
```
 id |    name    | district |   state   
----+------------+----------+-----------
  1 | Raju Naik  | Tumkur   | Karnataka
```

### 4.3 Spatial Geometry Coordinate Check
```sql
SELECT id, name, ST_AsText(location) FROM market;
```
*Expected Output:* Shows WKT geometries:
```
 id |    name     |         st_astext          
----+-------------+----------------------------
  1 | Tumkur APMC | POINT(77.1025 13.3409)
```
