"""API endpoints for submitting and retrieving 2-sided marketplace ratings."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ...database.session import get_db
from ...models.user import User
from ...models.rating import Rating
from ...models.trade_order import TradeOrder, TradeOrderStatus
from .auth import get_current_user

router = APIRouter(prefix="/ratings", tags=["ratings"])


class RatingCreate(BaseModel):
    target_user_id: int
    trade_order_id: int
    stars: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None


class RatingResponse(BaseModel):
    id: int
    rater_id: int
    target_user_id: int
    trade_order_id: int
    stars: int
    comment: Optional[str] = None
    created_at: str

    class Config:
        from_attributes = True


class UserRatingSummary(BaseModel):
    user_id: int
    average_rating: Optional[float] = None
    total_ratings: int
    completed_transactions: int
    ratings: List[RatingResponse]


@router.post("", response_model=RatingResponse, status_code=status.HTTP_201_CREATED)
def submit_rating(
    payload: RatingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.target_user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot rate yourself",
        )

    target_user = db.query(User).filter(User.id == payload.target_user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target user not found",
        )

    if not payload.trade_order_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="trade_order_id is required to submit a rating",
        )

    trade_order = db.query(TradeOrder).filter(TradeOrder.id == payload.trade_order_id).first()
    if not trade_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trade order {payload.trade_order_id} not found",
        )

    if trade_order.status != TradeOrderStatus.FULFILLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rating is allowed only for successfully completed transactions",
        )

    if current_user.id not in (trade_order.buyer_id, trade_order.farmer_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to rate this trade order",
        )

    expected_target = trade_order.farmer_id if current_user.id == trade_order.buyer_id else trade_order.buyer_id
    if payload.target_user_id != expected_target:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Target user does not match the trade order counterparty",
        )

    existing_rating = (
        db.query(Rating)
        .filter(Rating.rater_id == current_user.id, Rating.trade_order_id == payload.trade_order_id)
        .first()
    )
    if existing_rating:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already rated this transaction",
        )

    rating = Rating(
        rater_id=current_user.id,
        target_user_id=payload.target_user_id,
        trade_order_id=payload.trade_order_id,
        stars=payload.stars,
        comment=payload.comment,
    )
    db.add(rating)
    db.commit()
    db.refresh(rating)

    return RatingResponse(
        id=rating.id,
        rater_id=rating.rater_id,
        target_user_id=rating.target_user_id,
        trade_order_id=rating.trade_order_id,
        stars=rating.stars,
        comment=rating.comment,
        created_at=rating.created_at.isoformat(),
    )


@router.get("/trade-order/{trade_order_id}/me", response_model=RatingResponse)
def get_my_trade_order_rating(
    trade_order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve the authenticated user's rating for a specific completed trade order."""
    rating = (
        db.query(Rating)
        .filter(Rating.rater_id == current_user.id, Rating.trade_order_id == trade_order_id)
        .first()
    )
    if not rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rating not found for this trade order",
        )
    return RatingResponse(
        id=rating.id,
        rater_id=rating.rater_id,
        target_user_id=rating.target_user_id,
        trade_order_id=rating.trade_order_id,
        stars=rating.stars,
        comment=rating.comment,
        created_at=rating.created_at.isoformat(),
    )


@router.get("/user/{user_id}", response_model=UserRatingSummary)
def get_user_ratings(
    user_id: int,
    db: Session = Depends(get_db),
):
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    completed_count = (
        db.query(TradeOrder)
        .filter(
            (TradeOrder.buyer_id == user_id) | (TradeOrder.farmer_id == user_id),
            TradeOrder.status == TradeOrderStatus.FULFILLED,
        )
        .count()
    )

    ratings_list = (
        db.query(Rating)
        .filter(Rating.target_user_id == user_id)
        .order_by(Rating.created_at.desc())
        .all()
    )

    if not ratings_list:
        return UserRatingSummary(
            user_id=user_id,
            average_rating=None,
            total_ratings=0,
            completed_transactions=completed_count,
            ratings=[],
        )

    avg_stars = sum(r.stars for r in ratings_list) / len(ratings_list)

    return UserRatingSummary(
        user_id=user_id,
        average_rating=round(avg_stars, 1),
        total_ratings=len(ratings_list),
        completed_transactions=completed_count,
        ratings=[
            RatingResponse(
                id=r.id,
                rater_id=r.rater_id,
                target_user_id=r.target_user_id,
                trade_order_id=r.trade_order_id,
                stars=r.stars,
                comment=r.comment,
                created_at=r.created_at.isoformat(),
            )
            for r in ratings_list
        ],
    )


@router.get("/my-given", response_model=List[RatingResponse])
def get_my_given_ratings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ratings_list = (
        db.query(Rating)
        .filter(Rating.rater_id == current_user.id)
        .order_by(Rating.created_at.desc())
        .all()
    )
    return [
        RatingResponse(
            id=r.id,
            rater_id=r.rater_id,
            target_user_id=r.target_user_id,
            trade_order_id=r.trade_order_id,
            stars=r.stars,
            comment=r.comment,
            created_at=r.created_at.isoformat(),
        )
        for r in ratings_list
    ]

