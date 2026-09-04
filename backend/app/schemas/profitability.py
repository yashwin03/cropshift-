from pydantic import BaseModel

class CropProfitabilitySummary(BaseModel):
    crop_id: int
    crop_name: str
    expected_yield: float
    yield_unit: str
    production_cost: float
    expected_revenue: float
    estimated_profit: float
    data_status: str

class ProfitabilityResponse(BaseModel):
    current_crop: CropProfitabilitySummary
    recommended_crop: CropProfitabilitySummary
    expected_yield: float
    production_cost: float
    expected_revenue: float
    estimated_profit: float
    profit_difference: float
