from pydantic import BaseModel
from typing import List, Optional


class RecommendationRequest(BaseModel):
    farm_id: int
    latitude: float | None = None
    longitude: float | None = None


class TopOilseedItem(BaseModel):
    rank: int
    crop_id: int
    crop_name: str
    farm_suitability_score: int
    water_suitability_score: int
    economic_potential_score: int
    overall_score: int
    decision: str
    expected_profit: float
    profit_difference: float


class RecommendationResponse(BaseModel):
    recommended_crop: str
    suitability_score: int
    profitability_score: int
    market_score: int
    risk_score: int
    safety_score: int
    decision: str
    expected_profit: float
    current_crop_profit: float
    profit_difference: float
    reasons: List[str]
    risks: List[str]

    # Oilseed-First Component Scores & Top 10 Ranking
    farm_suitability_score: Optional[int] = None
    water_suitability_score: Optional[int] = None
    economic_potential_score: Optional[int] = None
    overall_score: Optional[int] = None
    top_oilseeds: Optional[List[TopOilseedItem]] = None
