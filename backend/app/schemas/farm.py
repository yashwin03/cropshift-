from pydantic import BaseModel
from typing import Optional

class FarmBase(BaseModel):
    farm_name: Optional[str] = None
    land_area_acre: float
    water_availability: bool
    soil_type: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    current_crop: Optional[str] = None  # We accept string from frontend, will map to crop_id in backend
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class FarmCreate(FarmBase):
    pass

class FarmUpdate(FarmBase):
    land_area_acre: Optional[float] = None
    water_availability: Optional[bool] = None

class FarmResponse(BaseModel):
    id: int
    farmer_id: int
    land_area_acre: float
    water_availability: bool
    soil_type: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    current_crop_id: Optional[int] = None
    owner_id: Optional[int] = None

    class Config:
        orm_mode = True
        from_attributes = True
