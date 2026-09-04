"""
crop_cultivation.py -- API endpoints for Farmer Crop Cultivation Records.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.user import User, UserRole
from app.models.farm import Farm
from app.models.crop import Crop
from app.models.crop_cultivation import CropCultivationRecord, CultivationStage, EvidenceStatus
from app.api.v1.auth import get_current_user, require_role
from app.api.v1.farms import resolve_farmer_farm

from app.schemas.crop_cultivation import (
    CropCultivationCreate,
    CropCultivationUpdate,
    RecordHarvestPayload,
    CropCultivationResponse,
)

router = APIRouter()


def _format_record_response(rec: CropCultivationRecord, farm: Optional[Farm] = None) -> CropCultivationResponse:
    farm_obj = farm or rec.farm
    district = farm_obj.district if farm_obj else None
    state = farm_obj.state if farm_obj else "Karnataka"
    return CropCultivationResponse(
        id=rec.id,
        farmer_id=rec.farmer_id,
        farm_id=rec.farm_id,
        crop_id=rec.crop_id,
        crop_name=rec.crop_name,
        variety=rec.variety,
        area_acres=rec.area_acres,
        cultivation_stage=rec.cultivation_stage,
        sowing_date=rec.sowing_date,
        expected_harvest_date=rec.expected_harvest_date,
        expected_yield_quintals=rec.expected_yield_quintals,
        actual_harvest_quantity_quintals=rec.actual_harvest_quantity_quintals,
        notes=rec.notes,
        evidence_status=rec.evidence_status,
        source_type=rec.source_type,
        created_at=rec.created_at,
        updated_at=rec.updated_at,
        district=district,
        state=state,
    )


@router.post("", response_model=CropCultivationResponse, status_code=status.HTTP_21F_CREATED if hasattr(status, 'HTTP_21F_CREATED') else 201)
def create_cultivation_record(
    payload: CropCultivationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != UserRole.FARMER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only farmers can create or manage crop cultivation records."
        )

    crop = db.get(Crop, payload.crop_id)
    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found.")

    farm = resolve_farmer_farm(db, current_user, payload.farm_id)

    # Duplicate protection check (Requirement 13)
    existing = db.query(CropCultivationRecord).filter(
        CropCultivationRecord.farmer_id == current_user.id,
        CropCultivationRecord.farm_id == farm.id,
        CropCultivationRecord.crop_id == crop.id,
        CropCultivationRecord.cultivation_stage.in_([
            CultivationStage.PLANNED,
            CultivationStage.GROWING,
            CultivationStage.READY_FOR_HARVEST
        ])
    ).first()

    if existing:
        if payload.variety is not None:
            existing.variety = payload.variety
        if payload.area_acres is not None:
            existing.area_acres = payload.area_acres
        if payload.cultivation_stage is not None:
            existing.cultivation_stage = payload.cultivation_stage
        if payload.sowing_date is not None:
            existing.sowing_date = payload.sowing_date
        if payload.expected_harvest_date is not None:
            existing.expected_harvest_date = payload.expected_harvest_date
        if payload.expected_yield_quintals is not None:
            existing.expected_yield_quintals = payload.expected_yield_quintals
        if payload.notes is not None:
            existing.notes = payload.notes

        if existing.cultivation_stage == CultivationStage.GROWING:
            farm.current_crop_id = crop.id

        db.commit()
        db.refresh(existing)
        return _format_record_response(existing, farm)

    record = CropCultivationRecord(
        farmer_id=current_user.id,
        farm_id=farm.id,
        crop_id=crop.id,
        crop_name=crop.name,
        variety=payload.variety,
        area_acres=payload.area_acres,
        cultivation_stage=payload.cultivation_stage,
        sowing_date=payload.sowing_date,
        expected_harvest_date=payload.expected_harvest_date,
        expected_yield_quintals=payload.expected_yield_quintals,
        notes=payload.notes,
        evidence_status=EvidenceStatus.FARMER_DECLARED,
        source_type="CropShift farmer network dataset",
    )

    if payload.cultivation_stage == CultivationStage.GROWING:
        farm.current_crop_id = crop.id

    db.add(record)
    db.commit()
    db.refresh(record)

    return _format_record_response(record, farm)


@router.get("", response_model=List[CropCultivationResponse])
def list_cultivation_records(
    stage: Optional[CultivationStage] = Query(None),
    crop_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != UserRole.FARMER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only farmers can view their cultivation records."
        )

    query = db.query(CropCultivationRecord).filter(CropCultivationRecord.farmer_id == current_user.id)

    if stage is not None:
        query = query.filter(CropCultivationRecord.cultivation_stage == stage)
    if crop_id is not None:
        query = query.filter(CropCultivationRecord.crop_id == crop_id)

    records = query.order_by(CropCultivationRecord.created_at.desc()).all()
    return [_format_record_response(r) for r in records]


@router.get("/{record_id}", response_model=CropCultivationResponse)
def get_cultivation_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != UserRole.FARMER:
        raise HTTPException(status_code=403, detail="Only farmers can view cultivation records.")

    record = db.get(CropCultivationRecord, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Crop cultivation record not found.")

    if record.farmer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this record.")

    return _format_record_response(record)


@router.put("/{record_id}", response_model=CropCultivationResponse)
def update_cultivation_record(
    record_id: int,
    payload: CropCultivationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != UserRole.FARMER:
        raise HTTPException(status_code=403, detail="Only farmers can update cultivation records.")

    record = db.get(CropCultivationRecord, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Crop cultivation record not found.")

    if record.farmer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this record.")

    if payload.variety is not None:
        record.variety = payload.variety
    if payload.area_acres is not None:
        record.area_acres = payload.area_acres
    if payload.cultivation_stage is not None:
        record.cultivation_stage = payload.cultivation_stage
    if payload.sowing_date is not None:
        record.sowing_date = payload.sowing_date
    if payload.expected_harvest_date is not None:
        record.expected_harvest_date = payload.expected_harvest_date
    if payload.expected_yield_quintals is not None:
        record.expected_yield_quintals = payload.expected_yield_quintals
    if payload.notes is not None:
        record.notes = payload.notes

    db.commit()
    db.refresh(record)
    return _format_record_response(record)


@router.post("/{record_id}/harvest", response_model=CropCultivationResponse)
@router.post("/{record_id}/record-harvest", response_model=CropCultivationResponse)
def record_harvest(
    record_id: int,
    payload: RecordHarvestPayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != UserRole.FARMER:
        raise HTTPException(status_code=403, detail="Only farmers can record harvest quantities.")

    record = db.get(CropCultivationRecord, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Crop cultivation record not found.")

    if record.farmer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this record.")

    # Record actual harvest quantity separately without overwriting expected yield!
    record.actual_harvest_quantity_quintals = payload.actual_harvest_quantity_quintals
    record.cultivation_stage = CultivationStage.HARVESTED
    if payload.notes:
        record.notes = (record.notes or "") + f"\nHarvest note: {payload.notes}"

    db.commit()
    db.refresh(record)
    return _format_record_response(record)


@router.delete("/{record_id}")
def delete_cultivation_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != UserRole.FARMER:
        raise HTTPException(status_code=403, detail="Only farmers can delete cultivation records.")

    record = db.get(CropCultivationRecord, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Crop cultivation record not found.")

    if record.farmer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this record.")

    db.delete(record)
    db.commit()
    return {"message": f"Cultivation record {record_id} successfully deleted."}
