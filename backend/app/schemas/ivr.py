from pydantic import BaseModel
from app.schemas.recommendation import RecommendationResponse

from typing import Optional

class IVRRequest(BaseModel):
    farmer_id: int

class IVRResponse(BaseModel):
    farmer_name: Optional[str] = None
    verified: bool
    voice_script: str
    recommendation: Optional[RecommendationResponse] = None
    language: str
