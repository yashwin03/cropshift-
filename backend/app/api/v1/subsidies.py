from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database.session import get_db
from app.models.recommendation import Recommendation
from app.decision_engine.recommendation import generate_recommendation
from app.services.subsidy_service import match_subsidies
from app.schemas.subsidy import SubsidyScheme

router = APIRouter()

@router.get("/{farm_id}", response_model=List[SubsidyScheme])
def get_subsidies(
    farm_id: int,
    has_land_proof: bool = False,
    has_soil_health_card: bool = False,
    db: Session = Depends(get_db)
):
    from app.models.farm import Farm
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found.")

    # Retrieve latest recommendation to get recommended crop ID
    rec = (
        db.query(Recommendation)
        .filter(Recommendation.farm_id == farm_id)
        .order_by(Recommendation.id.desc())
        .first()
    )
    if not rec:
        rec = generate_recommendation(db, farm_id)

    rec_crop_id = rec.recommended_crop_id if rec else None

    schemes = match_subsidies(
        db=db,
        farm_id=farm_id,
        has_land_proof=has_land_proof,
        has_soil_health_card=has_soil_health_card,
        recommended_crop_id=rec_crop_id
    )

    return [SubsidyScheme(**s) for s in schemes] if schemes else []
