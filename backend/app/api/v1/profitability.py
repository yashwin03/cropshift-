from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.crop import Crop
from app.models.crop_economics import CropEconomics
from app.models.recommendation import Recommendation
from app.services.farm_service import get_farm_conditions
from app.services.crop_service import get_current_crop
from app.decision_engine.recommendation import generate_recommendation
from app.decision_engine.profitability import calculate_profitability
from app.schemas.profitability import ProfitabilityResponse, CropProfitabilitySummary

router = APIRouter()

@router.get("/{farm_id}", response_model=ProfitabilityResponse)
def get_profitability(
    farm_id: int,
    db: Session = Depends(get_db)
):
    # Retrieve farm conditions
    farm_cond = get_farm_conditions(db, farm_id)
    if not farm_cond:
        raise HTTPException(status_code=404, detail="Farm not found.")

    # Get current crop
    curr_crop = get_current_crop(db, farm_id)
    if not curr_crop:
        raise HTTPException(status_code=404, detail="Current crop not found for this farm.")

    # Get latest recommendation to determine recommended crop ID
    rec = (
        db.query(Recommendation)
        .filter(Recommendation.farm_id == farm_id)
        .order_by(Recommendation.id.desc())
        .first()
    )
    if not rec:
        # Generate on the fly
        rec = generate_recommendation(db, farm_id)
    
    if not rec:
        raise HTTPException(status_code=404, detail="No recommended crop found or generated.")

    rec_crop_id = rec.recommended_crop_id
    rec_crop = db.get(Crop, rec_crop_id)
    if not rec_crop:
        raise HTTPException(status_code=404, detail="Recommended crop not found in database.")

    # Fetch current crop economics
    curr_econ = (
        db.query(CropEconomics)
        .filter(CropEconomics.crop_id == curr_crop["id"], CropEconomics.region == farm_cond["state"])
        .first()
    )
    if not curr_econ:
        curr_econ = db.query(CropEconomics).filter(CropEconomics.crop_id == curr_crop["id"]).first()
    
    # Fetch recommended crop economics
    rec_econ = (
        db.query(CropEconomics)
        .filter(CropEconomics.crop_id == rec_crop_id, CropEconomics.region == farm_cond["state"])
        .first()
    )
    if not rec_econ:
        rec_econ = db.query(CropEconomics).filter(CropEconomics.crop_id == rec_crop_id).first()

    if not curr_econ or not rec_econ:
        raise HTTPException(status_code=404, detail="Crop economics data not found.")

    curr_econ_dict = {
        "expected_yield_per_acre": curr_econ.expected_yield_per_acre,
        "yield_unit": curr_econ.yield_unit,
        "production_cost_per_acre": curr_econ.production_cost_per_acre,
        "expected_price_per_unit": curr_econ.expected_price_per_unit,
        "data_source": curr_econ.data_source,
        "data_status": curr_econ.data_status,
    }

    rec_econ_dict = {
        "expected_yield_per_acre": rec_econ.expected_yield_per_acre,
        "yield_unit": rec_econ.yield_unit,
        "production_cost_per_acre": rec_econ.production_cost_per_acre,
        "expected_price_per_unit": rec_econ.expected_price_per_unit,
        "data_source": rec_econ.data_source,
        "data_status": rec_econ.data_status,
    }

    # Run profitability calculation
    land_area = farm_cond["land_area_acre"]
    p_res = calculate_profitability(
        farm_conditions=farm_cond,
        current_crop_econ=curr_econ_dict,
        alternative_crop_econ=rec_econ_dict,
        land_area_acre=land_area
    )

    curr_summary = CropProfitabilitySummary(
        crop_id=curr_crop["id"],
        crop_name=curr_crop["name"],
        expected_yield=float(curr_econ.expected_yield_per_acre * land_area),
        yield_unit=curr_econ.yield_unit,
        production_cost=float(curr_econ.production_cost_per_acre * land_area),
        expected_revenue=float(curr_econ.expected_yield_per_acre * curr_econ.expected_price_per_unit * land_area),
        estimated_profit=float(p_res.current_crop_profit),
        data_status=curr_econ.data_status
    )

    rec_summary = CropProfitabilitySummary(
        crop_id=rec_crop.id,
        crop_name=rec_crop.name,
        expected_yield=float(rec_econ.expected_yield_per_acre * land_area),
        yield_unit=rec_econ.yield_unit,
        production_cost=float(rec_econ.production_cost_per_acre * land_area),
        expected_revenue=float(rec_econ.expected_yield_per_acre * rec_econ.expected_price_per_unit * land_area),
        estimated_profit=float(p_res.estimated_profit),
        data_status=rec_econ.data_status
    )

    return ProfitabilityResponse(
        current_crop=curr_summary,
        recommended_crop=rec_summary,
        expected_yield=float(rec_summary.expected_yield),
        production_cost=float(rec_summary.production_cost),
        expected_revenue=float(rec_summary.expected_revenue),
        estimated_profit=float(rec_summary.estimated_profit),
        profit_difference=float(p_res.profit_difference)
    )
