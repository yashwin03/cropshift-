from fastapi import APIRouter

router = APIRouter()

@router.get("/health", tags=["Health"])
async def get_health():
    return {
        "status": "ok",
        "service": "cropshift-api",
        "version": "1.0.0"
    }
