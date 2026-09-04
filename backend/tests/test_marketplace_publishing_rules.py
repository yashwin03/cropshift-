"""
Comprehensive backend tests for CropShift Marketplace Publishing Rules & Duplicate Prevention.
"""
import pytest
import uuid
from datetime import date, timedelta
from app.models.user import User, UserRole
from app.models.farmer import Farmer
from app.models.farm import Farm
from app.models.crop import Crop, CropType
from app.models.crop_cultivation import CropCultivationRecord
from app.models.future_crop_lot import FutureCropLot, FutureCropLotStatus
from app.models.stock_lot import StockLot, StockLotStatus
from app.models.bid import Bid, BidStatus
from app.models.stock_bid import StockBid, StockBidStatus
from app.models.trade_order import TradeOrder
from app.schemas.future_crop_lot import FutureCropLotCreate
from app.schemas.stock_lot import StockLotCreate
from app.schemas.bid import BidCreate
from app.api.v1.future_crop_lots import create_future_crop_lot, publish_future_crop_lot
from app.api.v1.stock_lots import create_direct_stock_lot, publish_stock_lot
from app.api.v1.bids import create_bid, accept_bid

def setup_test_entities(db):
    uid = uuid.uuid4().hex[:8]
    
    farmer_profile = Farmer(
        name=f"Farmer {uid}",
        district="Dharwad",
        state="Karnataka"
    )
    db.add(farmer_profile)
    db.commit()
    db.refresh(farmer_profile)

    farmer_user = User(
        username=f"farmer_{uid}",
        email=f"farmer_{uid}@example.com",
        hashed_password="hash",
        full_name="Test Farmer",
        role=UserRole.FARMER,
        farmer_id=str(farmer_profile.id),
        is_active=True
    )
    buyer1 = User(
        username=f"buyer1_{uid}",
        email=f"buyer1_{uid}@example.com",
        hashed_password="hash",
        full_name="Test Buyer 1",
        role=UserRole.BUYER,
        is_active=True
    )
    buyer2 = User(
        username=f"buyer2_{uid}",
        email=f"buyer2_{uid}@example.com",
        hashed_password="hash",
        full_name="Test Buyer 2",
        role=UserRole.BUYER,
        is_active=True
    )
    db.add_all([farmer_user, buyer1, buyer2])
    db.commit()
    db.refresh(farmer_user)
    db.refresh(buyer1)
    db.refresh(buyer2)

    crop = db.query(Crop).filter(Crop.is_oilseed == True).first()
    if not crop:
        crop = Crop(
            name=f"Groundnut Test {uid}",
            crop_type=CropType.OILSEED,
            season="Kharif",
            duration_days=120,
            water_requirement="LOW",
            is_oilseed=True
        )
        db.add(crop)
        db.commit()
        db.refresh(crop)

    farm = Farm(
        farmer_id=farmer_profile.id,
        owner_id=farmer_user.id,
        land_area_acre=5.0,
        district="Dharwad",
        state="Karnataka"
    )
    db.add(farm)
    db.commit()
    db.refresh(farm)

    return farmer_user, buyer1, buyer2, crop, farm, farmer_profile

def test_farmer_creates_crop_profile_only_does_not_create_marketplace_listing(db_session):
    farmer, _, _, crop, farm, farmer_profile = setup_test_entities(db_session)
    
    # Farmer records crop cultivation in farm profile
    cultivation = CropCultivationRecord(
        farmer_id=farmer.id,
        farm_id=farm.id,
        crop_id=crop.id,
        crop_name=crop.name,
        area_acres=2.5,
        sowing_date=str(date.today()),
        expected_harvest_date=str(date.today() + timedelta(days=60)),
        expected_yield_quintals=50.0
    )
    db_session.add(cultivation)
    db_session.commit()

    # Verify marketplace listings count for this farmer is 0
    fcl_count = db_session.query(FutureCropLot).filter(
        FutureCropLot.farmer_id == farmer.id,
        FutureCropLot.status == FutureCropLotStatus.OPEN
    ).count()
    sl_count = db_session.query(StockLot).filter(
        StockLot.farmer_id == farmer.id,
        StockLot.status == StockLotStatus.AVAILABLE
    ).count()
    assert fcl_count == 0
    assert sl_count == 0

def test_farmer_explicitly_publishes_crop_creates_exactly_one_listing(db_session):
    farmer, _, _, crop, farm, _ = setup_test_entities(db_session)
    
    today = date.today()
    payload = FutureCropLotCreate(
        farm_id=farm.id,
        crop_id=crop.id,
        variety="Kadir-6",
        planned_acres=2.5,
        expected_quantity_quintals=50.0,
        asking_price_per_quintal=6400.0,
        planned_sowing_date=today,
        expected_harvest_start=today + timedelta(days=60),
        expected_harvest_end=today + timedelta(days=75),
        status=FutureCropLotStatus.OPEN
    )
    res = create_future_crop_lot(payload=payload, db=db_session, current_user=farmer)
    
    open_lots = db_session.query(FutureCropLot).filter(
        FutureCropLot.farmer_id == farmer.id,
        FutureCropLot.status == FutureCropLotStatus.OPEN
    ).all()
    assert len(open_lots) == 1
    assert open_lots[0].id == res.id

def test_farmer_clicks_publish_twice_still_exactly_one_listing(db_session):
    farmer, _, _, crop, farm, _ = setup_test_entities(db_session)
    
    today = date.today()
    payload = FutureCropLotCreate(
        farm_id=farm.id,
        crop_id=crop.id,
        variety="Kadir-6",
        planned_acres=2.5,
        expected_quantity_quintals=50.0,
        asking_price_per_quintal=6400.0,
        planned_sowing_date=today,
        expected_harvest_start=today + timedelta(days=60),
        expected_harvest_end=today + timedelta(days=75),
        status=FutureCropLotStatus.OPEN
    )
    res1 = create_future_crop_lot(payload=payload, db=db_session, current_user=farmer)
    res2 = create_future_crop_lot(payload=payload, db=db_session, current_user=farmer)

    assert res1.id == res2.id

    open_lots = db_session.query(FutureCropLot).filter(
        FutureCropLot.farmer_id == farmer.id,
        FutureCropLot.status == FutureCropLotStatus.OPEN
    ).all()
    assert len(open_lots) == 1

def test_buyer_submits_offer_no_duplicate_marketplace_listing(db_session):
    farmer, buyer1, buyer2, crop, farm, _ = setup_test_entities(db_session)
    
    today = date.today()
    # 1. Publish lot
    payload = FutureCropLotCreate(
        farm_id=farm.id,
        crop_id=crop.id,
        variety="Kadir-6",
        planned_acres=2.5,
        expected_quantity_quintals=50.0,
        asking_price_per_quintal=6400.0,
        planned_sowing_date=today,
        expected_harvest_start=today + timedelta(days=60),
        expected_harvest_end=today + timedelta(days=75),
        status=FutureCropLotStatus.OPEN
    )
    lot_res = create_future_crop_lot(payload=payload, db=db_session, current_user=farmer)

    # 2. Buyer 1 submits offer
    bid_payload1 = BidCreate(
        future_crop_lot_id=lot_res.id,
        offered_price_per_quintal=6300.0,
        quantity_quintals=50.0
    )
    create_bid(payload=bid_payload1, db=db_session, current_user=buyer1)

    # 3. Buyer 2 submits offer
    bid_payload2 = BidCreate(
        future_crop_lot_id=lot_res.id,
        offered_price_per_quintal=6350.0,
        quantity_quintals=50.0
    )
    create_bid(payload=bid_payload2, db=db_session, current_user=buyer2)

    # Verify still exactly 1 marketplace listing card for this farmer
    open_lots = db_session.query(FutureCropLot).filter(
        FutureCropLot.farmer_id == farmer.id,
        FutureCropLot.status == FutureCropLotStatus.OPEN
    ).all()
    assert len(open_lots) == 1

    # Verify both bids belong to this single listing
    bids = db_session.query(Bid).filter(Bid.future_crop_lot_id == lot_res.id).all()
    assert len(bids) == 2
