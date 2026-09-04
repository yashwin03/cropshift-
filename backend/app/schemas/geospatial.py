from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional

class Coordinate(BaseModel):
    latitude: float
    longitude: float

class NearbyMarket(BaseModel):
    market_id: int
    market_name: str
    district: Optional[str] = None
    state: Optional[str] = None
    distance_km: float
    latitude: float
    longitude: float
    within_radius: bool = True
    crop: Optional[str] = None
    current_price: Optional[float] = None
    price_unit: Optional[str] = None
    trend: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)

class GeographicContext(BaseModel):
    district: Optional[str] = None
    state: Optional[str] = None
    agro_climatic_zone: Optional[str] = None
    markets_count: int

    model_config = ConfigDict(populate_by_name=True)

class GeospatialResponse(BaseModel):
    farm: Optional[Coordinate] = None
    nearby_markets: List[NearbyMarket]
    distance_information: Optional[str] = None
    geographic_context: GeographicContext

    model_config = ConfigDict(populate_by_name=True)
