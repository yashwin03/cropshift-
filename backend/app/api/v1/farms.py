from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.user import User, UserRole
from app.models.farm import Farm
from app.models.farmer import Farmer
from app.models.crop import Crop
from app.api.v1.auth import get_current_user, require_role
from app.schemas.farm import FarmCreate, FarmUpdate, FarmResponse

router = APIRouter()


def get_user_owned_farms(db: Session, current_user: User) -> List[Farm]:
    """
    Finds all farms owned by or associated with the given authenticated user via relational identity.
    Auto-links unowned farm.owner_id to current_user.id if matched via authenticated farmer ID.
    Relies STRICTLY on relational identity (User.id -> Farmer.id -> Farm.farmer_id or Farm.owner_id).
    Matching farmer names NEVER grants ownership authorization.
    """
    farms_dict = {}

    # 1. Direct owner_id match on User.id
    direct_owned = db.query(Farm).filter(Farm.owner_id == current_user.id).all()
    for f in direct_owned:
        farms_dict[f.id] = f

    # 2. Relational lookup by Farmer.id (never by name)
    farmer_ids = {current_user.id}
    if current_user.farmer_id:
        import re
        digits = re.sub(r'\D', '', str(current_user.farmer_id))
        if digits:
            try:
                farmer_ids.add(int(digits))
            except (ValueError, TypeError):
                pass

    farmers = db.query(Farmer).filter(Farmer.id.in_(farmer_ids)).all()
    for farmer in farmers:
        farmer_farms = db.query(Farm).filter(Farm.farmer_id == farmer.id).all()
        for ff in farmer_farms:
            if ff.owner_id is None:
                ff.owner_id = current_user.id
            if (ff.owner_id == current_user.id or ff.farmer_id in farmer_ids) and ff.id not in farms_dict:
                farms_dict[ff.id] = ff

    # 3. Direct match on Farm.farmer_id in farmer_ids
    direct_farmer_farms = db.query(Farm).filter(Farm.farmer_id.in_(farmer_ids)).all()
    for df in direct_farmer_farms:
        if df.owner_id is None:
            df.owner_id = current_user.id
        if (df.owner_id == current_user.id or df.farmer_id in farmer_ids) and df.id not in farms_dict:
            farms_dict[df.id] = df

    return list(farms_dict.values())


def resolve_farmer_farm(db: Session, current_user: User, requested_farm_id: Optional[int] = None) -> Farm:
    """
    Resolves the authenticated farmer's farm and strictly validates ownership.
    - If requested_farm_id is specified:
      - If requested_farm_id is owned by current_user: returns it.
      - If requested_farm_id exists in DB but belongs to another user: raises 403 "You can only add crops to farms you own."
      - If requested_farm_id does not exist in DB: raises 404 "Farm not found."
    - If requested_farm_id is None / 0:
      - If current_user has owned farms: returns owned_farms[0].
      - If current_user has 0 farms: auto-creates an authoritative Farm profile for current_user.
    """
    owned_farms = get_user_owned_farms(db, current_user)
    owned_ids = {f.id for f in owned_farms}

    if requested_farm_id and requested_farm_id > 0:
        if requested_farm_id in owned_ids:
            return next(f for f in owned_farms if f.id == requested_farm_id)

        target_farm = db.query(Farm).filter(Farm.id == requested_farm_id).first()
        if target_farm:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only add crops to farms you own."
            )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No farm is associated with this profile. Add or configure your farm first."
        )

    if owned_farms:
        return owned_farms[0]

    # Auto-create authoritative farm profile for authenticated user if 0 farms exist
    farmer_id_to_lookup = current_user.id
    if current_user.farmer_id:
        import re
        digits = re.sub(r'\D', '', str(current_user.farmer_id))
        if digits:
            try:
                farmer_id_to_lookup = int(digits)
            except (ValueError, TypeError):
                pass

    farmer = db.query(Farmer).filter(Farmer.id == farmer_id_to_lookup).first()
    if not farmer:
        farmer = Farmer(
            id=farmer_id_to_lookup,
            name=current_user.full_name or current_user.username,
            district="Shivamogga",
            state="Karnataka"
        )
        db.add(farmer)
        db.commit()
        db.refresh(farmer)

    new_farm = Farm(
        farmer_id=farmer.id,
        owner_id=current_user.id,
        land_area_acre=2.5,
        water_availability=True,
        soil_type="Black (Vertisol)",
        district="Shivamogga",
        state="Karnataka"
    )
    db.add(new_farm)
    db.commit()
    db.refresh(new_farm)
    return new_farm


@router.get("/me", response_model=FarmResponse)
def get_my_farm(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.FARMER))
):
    try:
        return resolve_farmer_farm(db, current_user)
    except HTTPException as e:
        if e.status_code == status.HTTP_400_BAD_REQUEST:
            raise HTTPException(status_code=404, detail="No farm profile found for current user.")
        raise e


@router.get("/my-farms", response_model=List[FarmResponse])
def get_my_farms(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.FARMER))
):
    return get_user_owned_farms(db, current_user)


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

    # Find or create a Farmer record for this user using relational ID
    farmer_id_to_lookup = current_user.id
    if current_user.farmer_id:
        try:
            farmer_id_to_lookup = int(current_user.farmer_id)
        except (ValueError, TypeError):
            pass

    farmer = db.query(Farmer).filter(Farmer.id == farmer_id_to_lookup).first()
    if not farmer:
        farmer = Farmer(
            id=farmer_id_to_lookup,
            name=current_user.full_name or current_user.username,
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
    farm = resolve_farmer_farm(db, current_user, farm_id)

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

