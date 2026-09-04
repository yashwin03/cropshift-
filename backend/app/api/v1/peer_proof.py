from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database.session import get_db
from app.models.farm import Farm
from app.models.user import User, UserRole
from app.api.v1.auth import get_current_user
from app.services.peer_proof_service import get_peer_proof_for_crop, request_peer_contact

router = APIRouter()


class PeerContactRequestPayload(BaseModel):
    peer_proof_id: int


@router.get("/{crop_id}")
def get_crop_peer_proof(
    crop_id: int,
    farm_id: Optional[int] = Query(None),
    district: Optional[str] = Query(None),
    radius_km: Optional[float] = Query(50.0),
    latitude: Optional[float] = Query(None),
    longitude: Optional[float] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    target_district = district or "Dharwad"
    land_area = 1.0

    if farm_id is not None:
        farm = db.get(Farm, farm_id)
        if farm:
            if farm.district:
                target_district = farm.district
            if farm.land_area_acre:
                land_area = farm.land_area_acre

    return get_peer_proof_for_crop(
        db,
        crop_id,
        district=target_district,
        land_area_acres=land_area,
        radius_km=radius_km or 50.0,
        latitude=latitude,
        longitude=longitude,
        farm_id=farm_id,
    )


@router.post("/contact-request")
def request_contact(
    payload: PeerContactRequestPayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    res = request_peer_contact(db, payload.peer_proof_id)
    if not res:
        raise HTTPException(
            status_code=400,
            detail="Peer is not contactable or peer proof record not found."
        )
    return res
