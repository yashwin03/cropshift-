# CropShift Backend

CropShift is a farmer-friendly crop-shift decision support platform. This is the FastAPI backend service implementing the smart decision engine, profitability calculations, market intelligence, geospatial queries, and IVR script generation.

## Prerequisites

- Python 3.11+
- PostgreSQL 15+ (with PostGIS extension enabled)

## Setup Instructions

1. **Clone/Open Workspace**:
   Ensure you are working inside the `backend` folder.

2. **Configure Environment Variables**:
   Copy the example environment file and configure the settings:
   ```bash
   cp .env.example .env
   ```

3. **Create a Virtual Environment**:
   ```bash
   python -m venv venv
   ```
   Activate the virtual environment:
   - **Windows (Command Prompt)**: `venv\Scripts\activate.bat`
   - **Windows (PowerShell)**: `.\venv\Scripts\activate.ps1`
   - **macOS/Linux**: `source venv/bin/activate`

4. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

Start the FastAPI local development server using uvicorn:
```bash
python -m uvicorn app.main:app --port 8000 --reload
```

- **API Documentation**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) (Swagger OpenAPI)
- **Health Check Endpoint**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

## Running Tests

Run the test suite using pytest:
```bash
pytest
```
