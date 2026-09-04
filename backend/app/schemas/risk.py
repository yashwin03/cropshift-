from pydantic import BaseModel

class RiskSimulationRequest(BaseModel):
    farm_id: int
    crop_id: int
    price_variance: float = 0.8  # Default -20%
    yield_variance: float = 0.7  # Default -30%

class RiskScenarioResult(BaseModel):
    safety_score: int
    decision: str

class RiskSimulationResponse(BaseModel):
    baseline: RiskScenarioResult
    price_down: RiskScenarioResult
    yield_down: RiskScenarioResult
    water_risk: RiskScenarioResult
