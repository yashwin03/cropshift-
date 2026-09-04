from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.crop import Crop
from app.models.farm import Farm
from app.models.user import User, UserRole
from app.api.v1.auth import get_current_user, require_role
from app.decision_engine.recommendation import generate_recommendation, evaluate_all_oilseeds
from app.schemas.recommendation import RecommendationRequest, RecommendationResponse, TopOilseedItem

router = APIRouter()

@router.post("", response_model=RecommendationResponse)
def create_recommendation(
    payload: RecommendationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.FARMER))
):
    farm = db.get(Farm, payload.farm_id)
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found.")
    
    if farm.owner_id is not None and farm.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this farm.")

    if payload.latitude is not None and payload.longitude is not None:
        farm.location = f"SRID=4326;POINT({payload.longitude} {payload.latitude})"
        db.commit()

    all_oilseeds = evaluate_all_oilseeds(db, payload.farm_id)
    rec = generate_recommendation(db, payload.farm_id)
    if not rec:
        raise HTTPException(
            status_code=404,
            detail=f"Farm with ID {payload.farm_id} not found or recommendation failed."
        )
    
    crop = db.get(Crop, rec.recommended_crop_id)
    crop_name = crop.name if crop else "Unknown"

    best_candidate = next((c for c in all_oilseeds if c["recommended_crop_id"] == rec.recommended_crop_id), None)
    farm_suitability = best_candidate["farm_suitability_score"] if best_candidate else int(rec.suitability_score)
    water_suitability = best_candidate["water_suitability_score"] if best_candidate else int(rec.suitability_score)
    economic_potential = best_candidate["economic_potential_score"] if best_candidate else int(rec.profitability_score)
    overall_score = best_candidate["overall_score"] if best_candidate else int(rec.safety_score)

    top_items = [
        TopOilseedItem(
            rank=c["rank"],
            crop_id=c["recommended_crop_id"],
            crop_name=c["crop_name"],
            farm_suitability_score=c["farm_suitability_score"],
            water_suitability_score=c["water_suitability_score"],
            economic_potential_score=c["economic_potential_score"],
            overall_score=c["overall_score"],
            decision=c["decision"],
            expected_profit=c["expected_profit"],
            profit_difference=c["profit_difference"]
        ) for c in all_oilseeds
    ]

    return RecommendationResponse(
        recommended_crop=crop_name,
        suitability_score=int(rec.suitability_score),
        profitability_score=int(rec.profitability_score),
        market_score=int(rec.market_score),
        risk_score=int(rec.risk_score),
        safety_score=int(rec.safety_score),
        decision=rec.decision,
        expected_profit=float(rec.expected_profit),
        current_crop_profit=float(rec.current_crop_profit),
        profit_difference=float(rec.profit_difference),
        reasons=rec.reasons or [],
        risks=rec.risks or [],
        farm_suitability_score=farm_suitability,
        water_suitability_score=water_suitability,
        economic_potential_score=economic_potential,
        overall_score=overall_score,
        top_oilseeds=top_items
    )
