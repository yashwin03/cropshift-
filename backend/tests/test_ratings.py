"""
Comprehensive backend tests for CropShift Two-Sided Rating & Trust System.
"""
import pytest
import uuid
from datetime import datetime
from fastapi import status
from app.models.user import User, UserRole
from app.models.farmer import Farmer
from app.models.farm import Farm
from app.models.crop import Crop, CropType
from app.models.future_crop_lot import FutureCropLot, FutureCropLotStatus
from app.models.trade_order import TradeOrder, TradeOrderStatus
from app.models.rating import Rating
from app.models.report import Report
from app.schemas.bid import BidCreate
from app.schemas.future_crop_lot import FutureCropLotCreate
from app.api.v1.future_crop_lots import create_future_crop_lot
from app.api.v1.bids import create_bid, accept_bid
from app.api.v1.trade_orders import fulfill_trade_order
from app.api.v1.ratings import submit_rating, get_user_ratings, get_my_trade_order_rating, RatingCreate
from app.api.v1.reports import submit_report, ReportCreate

def setup_completed_deal(db):
    uid = uuid.uuid4().hex[:8]

    farmer_profile = Farmer(name=f"Farmer {uid}", district="Dharwad", state="Karnataka")
    db.add(farmer_profile)
    db.commit()
    db.refresh(farmer_profile)

    farmer = User(
        username=f"farmer_{uid}",
        email=f"farmer_{uid}@example.com",
        hashed_password="hash",
        full_name="Test Farmer",
        role=UserRole.FARMER,
        farmer_id=str(farmer_profile.id),
        is_active=True
    )
    buyer = User(
        username=f"buyer_{uid}",
        email=f"buyer_{uid}@example.com",
        hashed_password="hash",
        full_name="Test Buyer",
        role=UserRole.BUYER,
        is_active=True
    )
    outsider = User(
        username=f"outsider_{uid}",
        email=f"outsider_{uid}@example.com",
        hashed_password="hash",
        full_name="Outsider User",
        role=UserRole.BUYER,
        is_active=True
    )
    db.add_all([farmer, buyer, outsider])
    db.commit()
    db.refresh(farmer)
    db.refresh(buyer)
    db.refresh(outsider)

    crop = db.query(Crop).filter(Crop.is_oilseed == True).first()
    if not crop:
        crop = Crop(name=f"Groundnut {uid}", crop_type=CropType.OILSEED, season="Kharif", is_oilseed=True)
        db.add(crop)
        db.commit()
        db.refresh(crop)

    farm = Farm(farmer_id=farmer_profile.id, owner_id=farmer.id, land_area_acre=5.0, district="Dharwad", state="Karnataka")
    db.add(farm)
    db.commit()
    db.refresh(farm)

    # Create & publish FutureCropLot
    today = datetime.utcnow().date()
    lot_payload = FutureCropLotCreate(
        farm_id=farm.id,
        crop_id=crop.id,
        variety="Kadir-6",
        planned_acres=2.5,
        expected_quantity_quintals=50.0,
        asking_price_per_quintal=6400.0,
        planned_sowing_date=today,
        expected_harvest_start=today,
        expected_harvest_end=today,
        status=FutureCropLotStatus.OPEN
    )
    lot_res = create_future_crop_lot(payload=lot_payload, db=db, current_user=farmer)

    # Submit bid
    bid_payload = BidCreate(future_crop_lot_id=lot_res.id, offered_price_per_quintal=6400.0, quantity_quintals=50.0)
    bid_res = create_bid(payload=bid_payload, db=db, current_user=buyer)

    # Accept bid -> TradeOrder created
    accept_bid(bid_id=bid_res.id, db=db, current_user=farmer)
    
    trade_order = (
        db.query(TradeOrder)
        .filter(TradeOrder.buyer_id == buyer.id, TradeOrder.farmer_id == farmer.id)
        .order_by(TradeOrder.id.desc())
        .first()
    )

    return farmer, buyer, outsider, trade_order

def test_rating_lifecycle_and_trust_summary(db_session):
    farmer, buyer, outsider, trade_order = setup_completed_deal(db_session)

    # 1. Rating before completion must be rejected (400)
    with pytest.raises(Exception) as exc_info:
        submit_rating(
            payload=RatingCreate(target_user_id=buyer.id, trade_order_id=trade_order.id, stars=5, comment="Great buyer"),
            db=db_session,
            current_user=farmer
        )
    assert getattr(exc_info.value, 'status_code', 0) == 400

    # 2. Fulfill TradeOrder
    fulfill_trade_order(order_id=trade_order.id, db=db_session, current_user=farmer)

    # 3. Non-participant cannot rate (403)
    with pytest.raises(Exception) as exc_info_out:
        submit_rating(
            payload=RatingCreate(target_user_id=farmer.id, trade_order_id=trade_order.id, stars=4, comment="Imposter"),
            db=db_session,
            current_user=outsider
        )
    assert getattr(exc_info_out.value, 'status_code', 0) == 403

    # 4. Valid Farmer -> Buyer Rating
    farmer_rating = submit_rating(
        payload=RatingCreate(target_user_id=buyer.id, trade_order_id=trade_order.id, stars=5, comment="Prompt payment"),
        db=db_session,
        current_user=farmer
    )
    assert farmer_rating.stars == 5
    assert farmer_rating.target_user_id == buyer.id

    # 5. Duplicate rating attempt by Farmer must fail with 409 Conflict
    with pytest.raises(Exception) as exc_dup:
        submit_rating(
            payload=RatingCreate(target_user_id=buyer.id, trade_order_id=trade_order.id, stars=4, comment="Duplicate attempt"),
            db=db_session,
            current_user=farmer
        )
    assert getattr(exc_dup.value, 'status_code', 0) == 409

    # 6. Valid Buyer -> Farmer Rating
    buyer_rating = submit_rating(
        payload=RatingCreate(target_user_id=farmer.id, trade_order_id=trade_order.id, stars=4, comment="Good crop quality"),
        db=db_session,
        current_user=buyer
    )
    assert buyer_rating.stars == 4
    assert buyer_rating.target_user_id == farmer.id

    # 7. Rating lookup endpoint for trade order
    my_rating = get_my_trade_order_rating(trade_order_id=trade_order.id, db=db_session, current_user=farmer)
    assert my_rating.stars == 5

    # 8. User rating summaries
    buyer_summary = get_user_ratings(user_id=buyer.id, db=db_session)
    assert buyer_summary.average_rating == 5.0
    assert buyer_summary.total_ratings == 1

    farmer_summary = get_user_ratings(user_id=farmer.id, db=db_session)
    assert farmer_summary.average_rating == 4.0
    assert farmer_summary.total_ratings == 1

def test_report_does_not_modify_or_delete_rating(db_session):
    farmer, buyer, _, trade_order = setup_completed_deal(db_session)
    fulfill_trade_order(order_id=trade_order.id, db=db_session, current_user=farmer)

    # Farmer rates buyer 5 stars
    submit_rating(
        payload=RatingCreate(target_user_id=buyer.id, trade_order_id=trade_order.id, stars=5, comment="Excellent"),
        db=db_session,
        current_user=farmer
    )

    # Farmer files a misconduct report against buyer
    rep_payload = ReportCreate(
        target_user_id=buyer.id,
        trade_order_id=trade_order.id,
        category="NON_PAYMENT",
        description="Filing optional reference report"
    )
    report = submit_report(payload=rep_payload, db=db_session, current_user=farmer)
    assert report.id is not None

    # Verify Buyer's rating summary remains 5.0 stars (report does NOT alter rating!)
    buyer_summary = get_user_ratings(user_id=buyer.id, db=db_session)
    assert buyer_summary.average_rating == 5.0
    assert buyer_summary.total_ratings == 1
