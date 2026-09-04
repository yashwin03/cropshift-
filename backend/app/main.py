import app.patch_bcrypt
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.router import api_router
from app.api.errors import register_exception_handlers

app = FastAPI(
    title="CropShift API",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount uploads directory for quality certificates and documents
import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

uploads_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../uploads"))
os.makedirs(os.path.join(uploads_dir, "quality_certs"), exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

# Mount the v1 router under /api/v1
app.include_router(api_router, prefix="/api/v1")

# A14: Register global exception handlers
register_exception_handlers(app)

import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Route GET /health directly at the root, as per the shared API contract and requirements
@app.get("/health", tags=["Health"])
async def root_health_check():
    return {
        "status": "ok",
        "service": "cropshift-api",
        "version": "1.0.0"
    }

# Serve React static frontend files in production/integrated mode
frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend/dist"))
if os.path.exists(frontend_dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")
    
    # Root favicon or public assets serving
    @app.get("/favicon.svg")
    async def serve_favicon():
        return FileResponse(os.path.join(frontend_dist, "favicon.svg"))
        
    @app.get("/icons.svg")
    async def serve_icons():
        return FileResponse(os.path.join(frontend_dist, "icons.svg"))

    # Fallback to serve index.html for any frontend React routes (SPA routing)
    @app.get("/{fallback_path:path}")
    async def serve_frontend(fallback_path: str):
        if fallback_path.startswith(("api/", "health", "docs", "redoc", "openapi.json")):
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="API route not found")
        
        index_path = os.path.join(frontend_dist, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"message": "index.html not found"}
else:
    print(f"Warning: Frontend dist directory not found at {frontend_dist}")
