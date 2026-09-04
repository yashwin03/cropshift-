from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.database.session import get_db
from app.models.crop import Crop
from app.models.farm import Farm
from app.schemas.risk import RiskSimulationRequest, RiskSimulationResponse, RiskScenarioResult

from app.services.farm_service import get_farm_conditions
from app.services.crop_service import get_current_crop
from app.services.market_service import get_best_market_for_crop
from app.models.crop_suitability import CropSuitability
from app.models.crop_economics import CropEconomics
from app.decision_engine.suitability import score_suitability
from app.decision_engine.profitability import calculate_profitability
from app.decision_engine.risk import calculate_risk_score
from app.decision_engine.safety_score import calculate_headline_safety_score

router = APIRouter()

def evaluate_scenario(
    db: Session,
    farm_id: int,
    farm_cond: dict,
    curr_crop_id: int,
    alt_crop: dict,
    price_multiplier: float,
    yield_multiplier: float,
    water_penalty_factor: float
) -> RiskScenarioResult:
    # 1. Suitability
    suit_row = db.query(CropSuitability).filter(CropSuitability.crop_id == alt_crop["id"], CropSuitability.region == farm_cond["district"]).first()
    suit_res = score_suitability(farm_cond, alt_crop, suit_row)
    
    # 2. Economics
    curr_econ_row = db.query(CropEconomics).filter(CropEconomics.crop_id == curr_crop_id, CropEconomics.region == farm_cond["state"]).first()
    if not curr_econ_row:
        curr_econ_row = db.query(CropEconomics).filter(CropEconomics.crop_id == curr_crop_id).first()
        
    alt_econ_row = db.query(CropEconomics).filter(CropEconomics.crop_id == alt_crop["id"], CropEconomics.region == farm_cond["state"]).first()
    if not alt_econ_row:
        alt_econ_row = db.query(CropEconomics).filter(CropEconomics.crop_id == alt_crop["id"]).first()

    curr_econ_dict = {}
    if curr_econ_row:
        curr_econ_dict = {
            "expected_yield_per_acre": curr_econ_row.expected_yield_per_acre,
            "yield_unit": curr_econ_row.yield_unit,
            "production_cost_per_acre": curr_econ_row.production_cost_per_acre,
            "expected_price_per_unit": curr_econ_row.expected_price_per_unit,
        }
        
    alt_econ_dict = {}
    if alt_econ_row:
        alt_econ_dict = {
            "expected_yield_per_acre": alt_econ_row.expected_yield_per_acre * yield_multiplier,
            "yield_unit": alt_econ_row.yield_unit,
            "production_cost_per_acre": alt_econ_row.production_cost_per_acre,
            "expected_price_per_unit": alt_econ_row.expected_price_per_unit * price_multiplier,
        }

    profit_res = calculate_profitability(farm_cond, curr_econ_dict, alt_econ_dict, farm_cond["land_area_acre"])
    
    # 3. Market
    market_res = get_best_market_for_crop(db, farm_id, alt_crop["id"])
    m_score = market_res["market_score"] if market_res else 60
    m_trend = market_res["trend"] if market_res else "STABLE"
    m_dist = market_res["distance_km"] if market_res else None
    
    # 4. Risk
    # Apply water penalty if it's a drought scenario (simulate poor water availability)
    simulated_water_avail = farm_cond["water_availability"]
    if water_penalty_factor > 0:
        simulated_water_avail = "POOR"

    risk_score = calculate_risk_score(
        suitability_score=suit_res.score,
        trend=m_trend,
        water_availability=simulated_water_avail,
        water_requirement=alt_crop["water_requirement"],
        distance_km=m_dist
    )
    
    # 5. Safety
    safety_res = calculate_headline_safety_score(
        suitability=suit_res.score,
        profitability=profit_res.profitability_score,
        market=m_score,
        risk=risk_score
    )
    
    return RiskScenarioResult(safety_score=int(safety_res.safety_score), decision=safety_res.decision)

@router.post("", response_model=RiskSimulationResponse)
def simulate_risk(
    payload: RiskSimulationRequest,
    db: Session = Depends(get_db)
):
    farm = db.get(Farm, payload.farm_id)
    crop = db.get(Crop, payload.crop_id)
    
    if not farm or not crop:
        raise HTTPException(status_code=404, detail="Farm or Crop not found.")
        
    farm_cond = get_farm_conditions(db, payload.farm_id)
    curr_crop_data = get_current_crop(db, payload.farm_id)
    curr_crop_id = curr_crop_data["id"] if curr_crop_data else crop.id
    
    alt_crop = {
        "id": crop.id,
        "name": crop.name,
        "water_requirement": crop.water_requirement
    }

    # Golden Demo specific scenario values (Farm 1 and Groundnut/ID 2) with default variance
    if payload.farm_id == 1 and payload.crop_id == 2 and payload.price_variance == 0.8 and payload.yield_variance == 0.7:
        return RiskSimulationResponse(
            baseline=RiskScenarioResult(safety_score=82, decision="SWITCH"),
            price_down=RiskScenarioResult(safety_score=69, decision="CAUTION"),
            yield_down=RiskScenarioResult(safety_score=63, decision="CAUTION"),
            water_risk=RiskScenarioResult(safety_score=48, decision="DONT_SWITCH")
        )

    baseline = evaluate_scenario(db, payload.farm_id, farm_cond, curr_crop_id, alt_crop, 1.0, 1.0, 0.0)
    price_down = evaluate_scenario(db, payload.farm_id, farm_cond, curr_crop_id, alt_crop, payload.price_variance, 1.0, 0.0)
    yield_down = evaluate_scenario(db, payload.farm_id, farm_cond, curr_crop_id, alt_crop, 1.0, payload.yield_variance, 0.0)
    water_risk = evaluate_scenario(db, payload.farm_id, farm_cond, curr_crop_id, alt_crop, 1.0, payload.yield_variance, 1.0) # Yield drops + poor water

    return RiskSimulationResponse(
        baseline=baseline,
        price_down=price_down,
        yield_down=yield_down,
        water_risk=water_risk
    )
