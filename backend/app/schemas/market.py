from pydantic import BaseModel
from typing import Optional, Any

class MarketResponse(BaseModel):
    crop_id: int
    crop_name: str
    price: Optional[float] = None
    price_unit: str
    market_name: str
    market_location: Optional[Any] = None
    distance_km: Optional[float] = None
    trend: str
    market_score: int
    data_status: str
    data_source: str
    price_date: Optional[str] = None
    min_target_price: Optional[float] = None
    max_target_price: Optional[float] = None

