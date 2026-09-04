"""API endpoints for submitting and inspecting misconduct reports."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ...database.session import get_db
from ...models.user import User
from ...models.report import Report
from .auth import get_current_user

router = APIRouter(prefix="/reports", tags=["reports"])


class ReportCreate(BaseModel):
    target_user_id: int
    trade_order_id: Optional[int] = None
    category: str
    description: str


class ReportResponse(BaseModel):
    id: int
    reporter_id: int
    target_user_id: int
    trade_order_id: Optional[int] = None
    category: str
    description: str
    status: str
    created_at: str

    class Config:
        from_attributes = True


@router.post("", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
def submit_report(
    payload: ReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.target_user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot report yourself",
        )

    target_user = db.query(User).filter(User.id == payload.target_user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target user not found",
        )

    report = Report(
        reporter_id=current_user.id,
        target_user_id=payload.target_user_id,
        trade_order_id=payload.trade_order_id,
        category=payload.category,
        description=payload.description,
        status="PENDING_REVIEW",
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    return ReportResponse(
        id=report.id,
        reporter_id=report.reporter_id,
        target_user_id=report.target_user_id,
        trade_order_id=report.trade_order_id,
        category=report.category,
        description=report.description,
        status=report.status,
        created_at=report.created_at.isoformat(),
    )


@router.get("/my-submitted", response_model=List[ReportResponse])
def get_my_submitted_reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    reports = (
        db.query(Report)
        .filter(Report.reporter_id == current_user.id)
        .order_by(Report.created_at.desc())
        .all()
    )
    return [
        ReportResponse(
            id=r.id,
            reporter_id=r.reporter_id,
            target_user_id=r.target_user_id,
            trade_order_id=r.trade_order_id,
            category=r.category,
            description=r.description,
            status=r.status,
            created_at=r.created_at.isoformat(),
        )
        for r in reports
    ]
