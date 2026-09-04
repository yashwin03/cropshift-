from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.user import User, UserRole
from app.models.farm import Farm
from app.models.farmer import Farmer
from app.models.crop import Crop
from app.api.v1.auth import get_current_user, require_role
from app.schemas.farm import FarmCreate, FarmUpdate, FarmResponse

router = APIRouter()

@router.get("/me", response_model=FarmResponse)
def get_my_farm(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.FARMER))
):
    farm = db.query(Farm).filter(Farm.owner_id == current_user.id).first()
    if not farm:
        farmer = db.query(Farmer).filter(Farmer.name == current_user.username).first()
        if farmer:
            farm = db.query(Farm).filter(Farm.farmer_id == farmer.id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="No farm profile found for current user.")
    return farm

@router.post("", response_model=FarmResponse)
def create_farm(
    payload: FarmCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.FARMER))
):
    # Map current_crop string to crop_id
    crop_id = None
    if payload.current_crop:
        crop = db.query(Crop).filter(Crop.name.ilike(payload.current_crop)).first()
        if crop:
            crop_id = crop.id
        else:
            raise HTTPException(status_code=422, detail=f"Crop '{payload.current_crop}' is not supported.")

    # Find or create a Farmer record for this user
    farmer = db.query(Farmer).filter(Farmer.name == current_user.username).first()
    if not farmer:
        farmer = Farmer(
            name=current_user.username,
            district=payload.district,
            state=payload.state
        )
        db.add(farmer)
        db.commit()
        db.refresh(farmer)

    new_farm = Farm(
        farmer_id=farmer.id,
        owner_id=current_user.id,
        land_area_acre=payload.land_area_acre,
        water_availability=payload.water_availability,
        soil_type=payload.soil_type,
        district=payload.district,
        state=payload.state,
        current_crop_id=crop_id
    )

    if payload.latitude is not None and payload.longitude is not None:
        new_farm.location = f"SRID=4326;POINT({payload.longitude} {payload.latitude})"

    db.add(new_farm)
    db.commit()
    db.refresh(new_farm)

    return new_farm

@router.put("/{farm_id}", response_model=FarmResponse)
def update_farm(
    farm_id: int,
    payload: FarmUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.FARMER))
):
    farm = db.get(Farm, farm_id)
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found.")
    
    if farm.owner_id is not None and farm.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this farm.")

    if payload.land_area_acre is not None:
        farm.land_area_acre = payload.land_area_acre
    if payload.water_availability is not None:
        farm.water_availability = payload.water_availability
    if payload.soil_type is not None:
        farm.soil_type = payload.soil_type
    if payload.district is not None:
        farm.district = payload.district
    if payload.state is not None:
        farm.state = payload.state

    if payload.current_crop is not None:
        crop = db.query(Crop).filter(Crop.name.ilike(payload.current_crop)).first()
        if crop:
            farm.current_crop_id = crop.id
        else:
            raise HTTPException(status_code=422, detail=f"Crop '{payload.current_crop}' is not supported.")

    if payload.latitude is not None and payload.longitude is not None:
        farm.location = f"SRID=4326;POINT({payload.longitude} {payload.latitude})"

    db.commit()
    db.refresh(farm)
    
    return farm

