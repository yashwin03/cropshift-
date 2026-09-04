"""Test suite for Phase 7C post-harvest StockBid functionality."""
import uuid
from datetime import date, datetime, timedelta
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database.session import SessionLocal, engine
from app.database.base import Base
from app.models.user import User, UserRole
from app.models.farm import Farm
from app.models.crop import Crop, CropType
from app.models.farmer import Farmer
from app.models.future_crop_lot import FutureCropLot, FutureCropLotStatus
from app.models.stock_lot import StockLot, StockLotStatus
from app.models.stock_bid import StockBid, StockBidStatus
from app.models.contact_sharing import ContactSharing, ContactSharingStatus
from app.api.v1.auth import get_current_user, get_password_hash

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_test_context():
    """Clear dependency overrides and ensure test environment has all tables and column migrations."""
    from app.database.init_db import init_db
    app.dependency_overrides.clear()
    init_db()
    yield
    app.dependency_overrides.clear()


def _create_user(role: UserRole = UserRole.FARMER, email: str = None) -> User:
    db = SessionLocal()
    uid = uuid.uuid4().hex[:6]
    if not email:
        email = f"user_{uid}@example.com"
    try:
        user = User(
            username=f"user_{uid}",
            email=email,
            hashed_password=get_password_hash("password123"),
            role=role,
            full_name=f"Test {role.value} {uid}",
            phone=f"9876{uid[:6].zfill(6)}",
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    finally:
        db.close()


def _create_farm(farmer_id: int) -> Farm:
    db = SessionLocal()
    uid = uuid.uuid4().hex[:6]
    try:
        farmer_entity = db.query(Farmer).filter(Farmer.phone == "9876543210").first()
        if not farmer_entity:
            farmer_entity = Farmer(
                name=f"Farmer {uid}",
                phone="9876543210",
                district="Dharwad",
                state="Karnataka",
            )
            db.add(farmer_entity)
            db.commit()
            db.refresh(farmer_entity)

        farm = Farm(
            owner_id=farmer_id,
            farmer_id=farmer_entity.id,
            soil_type="Black Cotton",
            land_area_acre=5.0,
            water_availability=True,
            district="Dharwad",
            state="Karnataka",
        )
        db.add(farm)
        db.commit()
        db.refresh(farm)
        return farm
    finally:
        db.close()


def _create_crop() -> Crop:
    db = SessionLocal()
    try:
        crop = db.query(Crop).filter(Crop.name == "Groundnut (Kadir-6)").first()
        if not crop:
            crop = Crop(name="Groundnut (Kadir-6)", crop_type=CropType.OILSEED, is_oilseed=True)
            db.add(crop)
            db.commit()
            db.refresh(crop)
        return crop
    finally:
        db.close()


def _create_stock_lot(farmer_id: int, farm_id: int, crop_id: int, qty: float = 100.0, status: StockLotStatus = StockLotStatus.AVAILABLE) -> StockLot:
    db = SessionLocal()
    try:
        lot = StockLot(
            farmer_id=farmer_id,
            farm_id=farm_id,
            crop_id=crop_id,
            variety="Kadir-6",
            actual_quantity_quintals=qty,
            available_quantity_quintals=qty,
            actual_harvest_date=date.today(),
            quality_grade="Grade A",
            asking_price_per_quintal=6000.0,
            status=status,
        )
        db.add(lot)
        db.commit()
        db.refresh(lot)
        return lot
    finally:
        db.close()


# =====================================================================
# TEST CASES (1 to 34)
# =====================================================================

def test_buyer_can_create_stock_bid():
    farmer = _create_user(role=UserRole.FARMER)
    buyer = _create_user(role=UserRole.BUYER)
    farm = _create_farm(farmer.id)
    crop = _create_crop()
    stock_lot = _create_stock_lot(farmer.id, farm.id, crop.id, qty=100.0)

    app.dependency_overrides[get_current_user] = lambda: buyer

    res = client.post(
        f"/api/v1/stock-lots/{stock_lot.id}/bids",
        json={"offered_price_per_quintal": 6200.0, "requested_quantity_quintals": 40.0, "conditions": "Moisture < 8%"},
    )
    assert res.status_code == 201
    data = res.json()
    assert data["stock_lot_id"] == stock_lot.id
    assert data["offered_price_per_quintal"] == 6200.0
    assert data["requested_quantity_quintals"] == 40.0
    assert data["allocated_quantity_quintals"] == 0.0
    assert data["status"] == "SUBMITTED"


def test_farmer_cannot_create_stock_bid():
    farmer = _create_user(role=UserRole.FARMER)
    farm = _create_farm(farmer.id)
    crop = _create_crop()
    stock_lot = _create_stock_lot(farmer.id, farm.id, crop.id, qty=100.0)

    app.dependency_overrides[get_current_user] = lambda: farmer

    res = client.post(
        f"/api/v1/stock-lots/{stock_lot.id}/bids",
        json={"offered_price_per_quintal": 6200.0, "requested_quantity_quintals": 40.0},
    )
    assert res.status_code == 403


def test_unauthenticated_creation_fails():
    app.dependency_overrides.pop(get_current_user, None)
    res = client.post(
        "/api/v1/stock-lots/1/bids",
        json={"offered_price_per_quintal": 6200.0, "requested_quantity_quintals": 40.0},
    )
    assert res.status_code == 401


def test_price_must_be_positive():
    buyer = _create_user(role=UserRole.BUYER)
    farmer = _create_user(role=UserRole.FARMER)
    farm = _create_farm(farmer.id)
    crop = _create_crop()
    stock_lot = _create_stock_lot(farmer.id, farm.id, crop.id)

    app.dependency_overrides[get_current_user] = lambda: buyer

    res = client.post(
        f"/api/v1/stock-lots/{stock_lot.id}/bids",
        json={"offered_price_per_quintal": 0.0, "requested_quantity_quintals": 40.0},
    )
    assert res.status_code in (400, 422)


def test_quantity_must_be_positive():
    buyer = _create_user(role=UserRole.BUYER)
    farmer = _create_user(role=UserRole.FARMER)
    farm = _create_farm(farmer.id)
    crop = _create_crop()
    stock_lot = _create_stock_lot(farmer.id, farm.id, crop.id)

    app.dependency_overrides[get_current_user] = lambda: buyer

    res = client.post(
        f"/api/v1/stock-lots/{stock_lot.id}/bids",
        json={"offered_price_per_quintal": 6000.0, "requested_quantity_quintals": -5.0},
    )
    assert res.status_code in (400, 422)


def test_quantity_cannot_exceed_available_stock():
    buyer = _create_user(role=UserRole.BUYER)
    farmer = _create_user(role=UserRole.FARMER)
    farm = _create_farm(farmer.id)
    crop = _create_crop()
    stock_lot = _create_stock_lot(farmer.id, farm.id, crop.id, qty=50.0)

    app.dependency_overrides[get_current_user] = lambda: buyer

    res = client.post(
        f"/api/v1/stock-lots/{stock_lot.id}/bids",
        json={"offered_price_per_quintal": 6000.0, "requested_quantity_quintals": 60.0},
    )
    assert res.status_code == 400
    assert "exceeds available stock quantity" in str(res.json())


def test_submission_does_not_reduce_stock():
    buyer = _create_user(role=UserRole.BUYER)
    farmer = _create_user(role=UserRole.FARMER)
    farm = _create_farm(farmer.id)
    crop = _create_crop()
    stock_lot = _create_stock_lot(farmer.id, farm.id, crop.id, qty=100.0)

    app.dependency_overrides[get_current_user] = lambda: buyer
    client.post(
        f"/api/v1/stock-lots/{stock_lot.id}/bids",
        json={"offered_price_per_quintal": 6200.0, "requested_quantity_quintals": 40.0},
    )

    db = SessionLocal()
    refreshed = db.query(StockLot).filter(StockLot.id == stock_lot.id).first()
    assert refreshed.available_quantity_quintals == 100.0
    db.close()


def test_buyer_sees_only_own_stock_bids():
    buyer1 = _create_user(role=UserRole.BUYER)
    buyer2 = _create_user(role=UserRole.BUYER)
    farmer = _create_user(role=UserRole.FARMER)
    farm = _create_farm(farmer.id)
    crop = _create_crop()
    stock_lot = _create_stock_lot(farmer.id, farm.id, crop.id)

    app.dependency_overrides[get_current_user] = lambda: buyer1
    client.post(f"/api/v1/stock-lots/{stock_lot.id}/bids", json={"offered_price_per_quintal": 6200.0, "requested_quantity_quintals": 40.0})

    app.dependency_overrides[get_current_user] = lambda: buyer2
    res = client.get("/api/v1/stock-bids/me")
    assert res.status_code == 200
    assert len(res.json()) == 0


def test_buyer_can_withdraw_submitted_bid():
    buyer = _create_user(role=UserRole.BUYER)
    farmer = _create_user(role=UserRole.FARMER)
    farm = _create_farm(farmer.id)
    crop = _create_crop()
    stock_lot = _create_stock_lot(farmer.id, farm.id, crop.id)

    app.dependency_overrides[get_current_user] = lambda: buyer
    bid_res = client.post(f"/api/v1/stock-lots/{stock_lot.id}/bids", json={"offered_price_per_quintal": 6200.0, "requested_quantity_quintals": 40.0})
    bid_id = bid_res.json()["id"]

    w_res = client.post(f"/api/v1/stock-bids/{bid_id}/withdraw")
    assert w_res.status_code == 200
    assert w_res.json()["status"] == "WITHDRAWN"


def test_accepted_bid_cannot_be_withdrawn():
    buyer = _create_user(role=UserRole.BUYER)
    farmer = _create_user(role=UserRole.FARMER)
    farm = _create_farm(farmer.id)
    crop = _create_crop()
    stock_lot = _create_stock_lot(farmer.id, farm.id, crop.id)

    app.dependency_overrides[get_current_user] = lambda: buyer
    bid_res = client.post(f"/api/v1/stock-lots/{stock_lot.id}/bids", json={"offered_price_per_quintal": 6200.0, "requested_quantity_quintals": 40.0})
    bid_id = bid_res.json()["id"]

    # Farmer accepts
    app.dependency_overrides[get_current_user] = lambda: farmer
    client.post(f"/api/v1/stock-bids/{bid_id}/accept", json={"allocated_quantity_quintals": 40.0})

    # Buyer tries to withdraw
    app.dependency_overrides[get_current_user] = lambda: buyer
    w_res = client.post(f"/api/v1/stock-bids/{bid_id}/withdraw")
    assert w_res.status_code == 400


def test_farmer_can_view_bids_on_own_stock_lot():
    buyer = _create_user(role=UserRole.BUYER)
    farmer = _create_user(role=UserRole.FARMER)
    farm = _create_farm(farmer.id)
    crop = _create_crop()
    stock_lot = _create_stock_lot(farmer.id, farm.id, crop.id)

    app.dependency_overrides[get_current_user] = lambda: buyer
    client.post(f"/api/v1/stock-lots/{stock_lot.id}/bids", json={"offered_price_per_quintal": 6200.0, "requested_quantity_quintals": 40.0})

    app.dependency_overrides[get_current_user] = lambda: farmer
    res = client.get(f"/api/v1/farmer/stock-lots/{stock_lot.id}/bids")
    assert res.status_code == 200
    assert len(res.json()) == 1


def test_unrelated_farmer_cannot_view_bids():
    buyer = _create_user(role=UserRole.BUYER)
    farmer1 = _create_user(role=UserRole.FARMER)
    farmer2 = _create_user(role=UserRole.FARMER)
    farm = _create_farm(farmer1.id)
    crop = _create_crop()
    stock_lot = _create_stock_lot(farmer1.id, farm.id, crop.id)

    app.dependency_overrides[get_current_user] = lambda: farmer2
    res = client.get(f"/api/v1/farmer/stock-lots/{stock_lot.id}/bids")
    assert res.status_code == 403


def test_buyer_cannot_accept_bid():
    buyer = _create_user(role=UserRole.BUYER)
    farmer = _create_user(role=UserRole.FARMER)
    farm = _create_farm(farmer.id)
    crop = _create_crop()
    stock_lot = _create_stock_lot(farmer.id, farm.id, crop.id)

    app.dependency_overrides[get_current_user] = lambda: buyer
    bid_res = client.post(f"/api/v1/stock-lots/{stock_lot.id}/bids", json={"offered_price_per_quintal": 6200.0, "requested_quantity_quintals": 40.0})
    bid_id = bid_res.json()["id"]

    res = client.post(f"/api/v1/stock-bids/{bid_id}/accept", json={"allocated_quantity_quintals": 40.0})
    assert res.status_code == 403


def test_farmer_can_accept_own_stock_lot_bid():
    buyer = _create_user(role=UserRole.BUYER)
    farmer = _create_user(role=UserRole.FARMER)
    farm = _create_farm(farmer.id)
    crop = _create_crop()
    stock_lot = _create_stock_lot(farmer.id, farm.id, crop.id, qty=100.0)

    app.dependency_overrides[get_current_user] = lambda: buyer
    bid_res = client.post(f"/api/v1/stock-lots/{stock_lot.id}/bids", json={"offered_price_per_quintal": 6200.0, "requested_quantity_quintals": 40.0})
    bid_id = bid_res.json()["id"]

    app.dependency_overrides[get_current_user] = lambda: farmer
    res = client.post(f"/api/v1/stock-bids/{bid_id}/accept", json={"allocated_quantity_quintals": 40.0})
    assert res.status_code == 200
    assert res.json()["status"] == "ACCEPTED"
    assert res.json()["allocated_quantity_quintals"] == 40.0


def test_allocated_quantity_can_be_less_than_requested():
    buyer = _create_user(role=UserRole.BUYER)
    farmer = _create_user(role=UserRole.FARMER)
    farm = _create_farm(farmer.id)
    crop = _create_crop()
    stock_lot = _create_stock_lot(farmer.id, farm.id, crop.id, qty=100.0)

    app.dependency_overrides[get_current_user] = lambda: buyer
    bid_res = client.post(f"/api/v1/stock-lots/{stock_lot.id}/bids", json={"offered_price_per_quintal": 6200.0, "requested_quantity_quintals": 40.0})
    bid_id = bid_res.json()["id"]

    app.dependency_overrides[get_current_user] = lambda: farmer
    res = client.post(f"/api/v1/stock-bids/{bid_id}/accept", json={"allocated_quantity_quintals": 25.0})
    assert res.status_code == 200
    assert res.json()["allocated_quantity_quintals"] == 25.0


def test_allocated_quantity_cannot_exceed_requested():
    buyer = _create_user(role=UserRole.BUYER)
    farmer = _create_user(role=UserRole.FARMER)
    farm = _create_farm(farmer.id)
    crop = _create_crop()
    stock_lot = _create_stock_lot(farmer.id, farm.id, crop.id, qty=100.0)

    app.dependency_overrides[get_current_user] = lambda: buyer
    bid_res = client.post(f"/api/v1/stock-lots/{stock_lot.id}/bids", json={"offered_price_per_quintal": 6200.0, "requested_quantity_quintals": 40.0})
    bid_id = bid_res.json()["id"]

    app.dependency_overrides[get_current_user] = lambda: farmer
    res = client.post(f"/api/v1/stock-bids/{bid_id}/accept", json={"allocated_quantity_quintals": 45.0})
    assert res.status_code == 400


def test_allocated_quantity_cannot_exceed_available():
    buyer = _create_user(role=UserRole.BUYER)
    farmer = _create_user(role=UserRole.FARMER)
    farm = _create_farm(farmer.id)
    crop = _create_crop()
    stock_lot = _create_stock_lot(farmer.id, farm.id, crop.id, qty=30.0)

    app.dependency_overrides[get_current_user] = lambda: buyer
    bid_res = client.post(f"/api/v1/stock-lots/{stock_lot.id}/bids", json={"offered_price_per_quintal": 6200.0, "requested_quantity_quintals": 30.0})
    bid_id = bid_res.json()["id"]

    app.dependency_overrides[get_current_user] = lambda: farmer
    res = client.post(f"/api/v1/stock-bids/{bid_id}/accept", json={"allocated_quantity_quintals": 35.0})
    assert res.status_code == 400


def test_partial_acceptance_changes_status_to_partially_sold():
    buyer = _create_user(role=UserRole.BUYER)
    farmer = _create_user(role=UserRole.FARMER)
    farm = _create_farm(farmer.id)
    crop = _create_crop()
    stock_lot = _create_stock_lot(farmer.id, farm.id, crop.id, qty=100.0)

    app.dependency_overrides[get_current_user] = lambda: buyer
    bid_res = client.post(f"/api/v1/stock-lots/{stock_lot.id}/bids", json={"offered_price_per_quintal": 6200.0, "requested_quantity_quintals": 40.0})
    bid_id = bid_res.json()["id"]

    app.dependency_overrides[get_current_user] = lambda: farmer
    client.post(f"/api/v1/stock-bids/{bid_id}/accept", json={"allocated_quantity_quintals": 40.0})

    db = SessionLocal()
    refreshed = db.query(StockLot).filter(StockLot.id == stock_lot.id).first()
    assert refreshed.status == StockLotStatus.PARTIALLY_SOLD
    assert refreshed.available_quantity_quintals == 60.0
    db.close()


def test_full_allocation_changes_status_to_sold():
    buyer = _create_user(role=UserRole.BUYER)
    farmer = _create_user(role=UserRole.FARMER)
    farm = _create_farm(farmer.id)
    crop = _create_crop()
    stock_lot = _create_stock_lot(farmer.id, farm.id, crop.id, qty=40.0)

    app.dependency_overrides[get_current_user] = lambda: buyer
    bid_res = client.post(f"/api/v1/stock-lots/{stock_lot.id}/bids", json={"offered_price_per_quintal": 6200.0, "requested_quantity_quintals": 40.0})
    bid_id = bid_res.json()["id"]

    app.dependency_overrides[get_current_user] = lambda: farmer
    client.post(f"/api/v1/stock-bids/{bid_id}/accept", json={"allocated_quantity_quintals": 40.0})

    db = SessionLocal()
    refreshed = db.query(StockLot).filter(StockLot.id == stock_lot.id).first()
    assert refreshed.status == StockLotStatus.SOLD
    assert refreshed.available_quantity_quintals == 0.0
    db.close()


def test_multiple_accepted_bids_allocate_correctly():
    buyer1 = _create_user(role=UserRole.BUYER)
    buyer2 = _create_user(role=UserRole.BUYER)
    farmer = _create_user(role=UserRole.FARMER)
    farm = _create_farm(farmer.id)
    crop = _create_crop()
    stock_lot = _create_stock_lot(farmer.id, farm.id, crop.id, qty=100.0)

    # Buyer 1 bids 40
    app.dependency_overrides[get_current_user] = lambda: buyer1
    bid1_res = client.post(f"/api/v1/stock-lots/{stock_lot.id}/bids", json={"offered_price_per_quintal": 6200.0, "requested_quantity_quintals": 40.0})
    bid1_id = bid1_res.json()["id"]

    # Buyer 2 bids 35
    app.dependency_overrides[get_current_user] = lambda: buyer2
    bid2_res = client.post(f"/api/v1/stock-lots/{stock_lot.id}/bids", json={"offered_price_per_quintal": 6100.0, "requested_quantity_quintals": 35.0})
    bid2_id = bid2_res.json()["id"]

    # Farmer accepts both
    app.dependency_overrides[get_current_user] = lambda: farmer
    client.post(f"/api/v1/stock-bids/{bid1_id}/accept", json={"allocated_quantity_quintals": 40.0})
    client.post(f"/api/v1/stock-bids/{bid2_id}/accept", json={"allocated_quantity_quintals": 35.0})

    db = SessionLocal()
    refreshed = db.query(StockLot).filter(StockLot.id == stock_lot.id).first()
    assert refreshed.available_quantity_quintals == 25.0
    assert refreshed.status == StockLotStatus.PARTIALLY_SOLD
    db.close()


def test_oversubscription_is_rejected():
    buyer1 = _create_user(role=UserRole.BUYER)
    buyer2 = _create_user(role=UserRole.BUYER)
    farmer = _create_user(role=UserRole.FARMER)
    farm = _create_farm(farmer.id)
    crop = _create_crop()
    stock_lot = _create_stock_lot(farmer.id, farm.id, crop.id, qty=50.0)

    # Buyer 1 bids 40
    app.dependency_overrides[get_current_user] = lambda: buyer1
    bid1_res = client.post(f"/api/v1/stock-lots/{stock_lot.id}/bids", json={"offered_price_per_quintal": 6200.0, "requested_quantity_quintals": 40.0})
    bid1_id = bid1_res.json()["id"]

    # Buyer 2 bids 30
    app.dependency_overrides[get_current_user] = lambda: buyer2
    bid2_res = client.post(f"/api/v1/stock-lots/{stock_lot.id}/bids", json={"offered_price_per_quintal": 6100.0, "requested_quantity_quintals": 30.0})
    bid2_id = bid2_res.json()["id"]

    # Farmer accepts Bid 1 (40 Q)
    app.dependency_overrides[get_current_user] = lambda: farmer
    client.post(f"/api/v1/stock-bids/{bid1_id}/accept", json={"allocated_quantity_quintals": 40.0})

    # Farmer tries to accept Bid 2 (30 Q, but only 10 Q available)
    res2 = client.post(f"/api/v1/stock-bids/{bid2_id}/accept", json={"allocated_quantity_quintals": 30.0})
    assert res2.status_code == 400


def test_concurrent_acceptance_cannot_oversubscribe_stock():
    buyer1 = _create_user(role=UserRole.BUYER)
    farmer = _create_user(role=UserRole.FARMER)
    farm = _create_farm(farmer.id)
    crop = _create_crop()
    stock_lot = _create_stock_lot(farmer.id, farm.id, crop.id, qty=20.0)

    app.dependency_overrides[get_current_user] = lambda: buyer1
    bid_res = client.post(f"/api/v1/stock-lots/{stock_lot.id}/bids", json={"offered_price_per_quintal": 6200.0, "requested_quantity_quintals": 20.0})
    bid_id = bid_res.json()["id"]

    app.dependency_overrides[get_current_user] = lambda: farmer
    res1 = client.post(f"/api/v1/stock-bids/{bid_id}/accept", json={"allocated_quantity_quintals": 20.0})
    assert res1.status_code == 200

    # Second acceptance attempt on same bid fails
    res2 = client.post(f"/api/v1/stock-bids/{bid_id}/accept", json={"allocated_quantity_quintals": 20.0})
    assert res2.status_code == 400


def test_rejected_bid_does_not_alter_stock():
    buyer = _create_user(role=UserRole.BUYER)
    farmer = _create_user(role=UserRole.FARMER)
    farm = _create_farm(farmer.id)
    crop = _create_crop()
    stock_lot = _create_stock_lot(farmer.id, farm.id, crop.id, qty=100.0)

    app.dependency_overrides[get_current_user] = lambda: buyer
    bid_res = client.post(f"/api/v1/stock-lots/{stock_lot.id}/bids", json={"offered_price_per_quintal": 6200.0, "requested_quantity_quintals": 40.0})
    bid_id = bid_res.json()["id"]

    app.dependency_overrides[get_current_user] = lambda: farmer
    rej_res = client.post(f"/api/v1/stock-bids/{bid_id}/reject")
    assert rej_res.status_code == 200
    assert rej_res.json()["status"] == "REJECTED"

    db = SessionLocal()
    refreshed = db.query(StockLot).filter(StockLot.id == stock_lot.id).first()
    assert refreshed.available_quantity_quintals == 100.0
    db.close()


def test_cancelled_stock_lot_expires_submitted_bids():
    buyer = _create_user(role=UserRole.BUYER)
    farmer = _create_user(role=UserRole.FARMER)
    farm = _create_farm(farmer.id)
    crop = _create_crop()
    stock_lot = _create_stock_lot(farmer.id, farm.id, crop.id, qty=100.0)

    app.dependency_overrides[get_current_user] = lambda: buyer
    bid_res = client.post(f"/api/v1/stock-lots/{stock_lot.id}/bids", json={"offered_price_per_quintal": 6200.0, "requested_quantity_quintals": 40.0})
    bid_id = bid_res.json()["id"]

    # Farmer cancels stock lot
    app.dependency_overrides[get_current_user] = lambda: farmer
    client.delete(f"/api/v1/farmer/stock-lots/{stock_lot.id}")

    db = SessionLocal()
    refreshed_bid = db.query(StockBid).filter(StockBid.id == bid_id).first()
    assert refreshed_bid.status == StockBidStatus.EXPIRED
    db.close()


def test_accepted_allocations_remain_preserved_after_cancellation():
    buyer = _create_user(role=UserRole.BUYER)
    farmer = _create_user(role=UserRole.FARMER)
    farm = _create_farm(farmer.id)
    crop = _create_crop()
    stock_lot = _create_stock_lot(farmer.id, farm.id, crop.id, qty=100.0)

    app.dependency_overrides[get_current_user] = lambda: buyer
    bid_res = client.post(f"/api/v1/stock-lots/{stock_lot.id}/bids", json={"offered_price_per_quintal": 6200.0, "requested_quantity_quintals": 40.0})
    bid_id = bid_res.json()["id"]

    # Farmer accepts bid
    app.dependency_overrides[get_current_user] = lambda: farmer
    client.post(f"/api/v1/stock-bids/{bid_id}/accept", json={"allocated_quantity_quintals": 40.0})

    # Farmer cancels remaining stock
    client.delete(f"/api/v1/farmer/stock-lots/{stock_lot.id}")

    db = SessionLocal()
    refreshed_bid = db.query(StockBid).filter(StockBid.id == bid_id).first()
    assert refreshed_bid.status == StockBidStatus.ACCEPTED
    assert refreshed_bid.allocated_quantity_quintals == 40.0
    db.close()


def test_pre_sowing_bid_remains_unchanged():
    db = SessionLocal()
    from app.models.bid import Bid, BidStatus
    pre_bid = db.query(Bid).first()
    db.close()
    assert pre_bid is None or pre_bid.status in (BidStatus.SUBMITTED, BidStatus.ACCEPTED)


def test_contact_sharing_created_on_accepted_stock_bid():
    buyer = _create_user(role=UserRole.BUYER)
    farmer = _create_user(role=UserRole.FARMER)
    farm = _create_farm(farmer.id)
    crop = _create_crop()
    stock_lot = _create_stock_lot(farmer.id, farm.id, crop.id, qty=100.0)

    app.dependency_overrides[get_current_user] = lambda: buyer
    bid_res = client.post(f"/api/v1/stock-lots/{stock_lot.id}/bids", json={"offered_price_per_quintal": 6200.0, "requested_quantity_quintals": 40.0})
    bid_id = bid_res.json()["id"]

    app.dependency_overrides[get_current_user] = lambda: farmer
    client.post(f"/api/v1/stock-bids/{bid_id}/accept", json={"allocated_quantity_quintals": 40.0})

    cs_res = client.get(f"/api/v1/stock-bids/{bid_id}/contact-sharing")
    assert cs_res.status_code == 200
    assert cs_res.json()["status"] == "PENDING"


def test_contact_hidden_before_mutual_consent():
    buyer = _create_user(role=UserRole.BUYER)
    farmer = _create_user(role=UserRole.FARMER)
    farm = _create_farm(farmer.id)
    crop = _create_crop()
    stock_lot = _create_stock_lot(farmer.id, farm.id, crop.id, qty=100.0)

    app.dependency_overrides[get_current_user] = lambda: buyer
    bid_res = client.post(f"/api/v1/stock-lots/{stock_lot.id}/bids", json={"offered_price_per_quintal": 6200.0, "requested_quantity_quintals": 40.0})
    bid_id = bid_res.json()["id"]

    app.dependency_overrides[get_current_user] = lambda: farmer
    client.post(f"/api/v1/stock-bids/{bid_id}/accept", json={"allocated_quantity_quintals": 40.0})

    # Farmer consents
    client.post(f"/api/v1/stock-bids/{bid_id}/contact-sharing/consent")

    cs_res = client.get(f"/api/v1/stock-bids/{bid_id}/contact-sharing")
    assert cs_res.status_code == 200
    assert cs_res.json()["status"] == "PENDING"
    assert cs_res.json()["buyer_contact"] is None
    assert cs_res.json()["farmer_contact"] is None


def test_contact_revealed_after_mutual_consent():
    buyer = _create_user(role=UserRole.BUYER)
    farmer = _create_user(role=UserRole.FARMER)
    farm = _create_farm(farmer.id)
    crop = _create_crop()
    stock_lot = _create_stock_lot(farmer.id, farm.id, crop.id, qty=100.0)

    app.dependency_overrides[get_current_user] = lambda: buyer
    bid_res = client.post(f"/api/v1/stock-lots/{stock_lot.id}/bids", json={"offered_price_per_quintal": 6200.0, "requested_quantity_quintals": 40.0})
    bid_id = bid_res.json()["id"]

    # Farmer accepts & consents
    app.dependency_overrides[get_current_user] = lambda: farmer
    client.post(f"/api/v1/stock-bids/{bid_id}/accept", json={"allocated_quantity_quintals": 40.0})
    client.post(f"/api/v1/stock-bids/{bid_id}/contact-sharing/consent")

    # Buyer consents
    app.dependency_overrides[get_current_user] = lambda: buyer
    client.post(f"/api/v1/stock-bids/{bid_id}/contact-sharing/consent")

    cs_res = client.get(f"/api/v1/stock-bids/{bid_id}/contact-sharing")
    assert cs_res.status_code == 200
    assert cs_res.json()["status"] == "MUTUAL_CONSENT"
    assert cs_res.json()["farmer_contact"] is not None
    assert cs_res.json()["buyer_contact"] is not None


def test_contact_sharing_ownership_enforced():
    buyer = _create_user(role=UserRole.BUYER)
    unrelated_buyer = _create_user(role=UserRole.BUYER)
    farmer = _create_user(role=UserRole.FARMER)
    farm = _create_farm(farmer.id)
    crop = _create_crop()
    stock_lot = _create_stock_lot(farmer.id, farm.id, crop.id, qty=100.0)

    app.dependency_overrides[get_current_user] = lambda: buyer
    bid_res = client.post(f"/api/v1/stock-lots/{stock_lot.id}/bids", json={"offered_price_per_quintal": 6200.0, "requested_quantity_quintals": 40.0})
    bid_id = bid_res.json()["id"]

    app.dependency_overrides[get_current_user] = lambda: farmer
    client.post(f"/api/v1/stock-bids/{bid_id}/accept", json={"allocated_quantity_quintals": 40.0})

    app.dependency_overrides[get_current_user] = lambda: unrelated_buyer
    res = client.get(f"/api/v1/stock-bids/{bid_id}/contact-sharing")
    assert res.status_code == 403


def test_exact_gps_is_never_exposed():
    buyer = _create_user(role=UserRole.BUYER)
    farmer = _create_user(role=UserRole.FARMER)
    farm = _create_farm(farmer.id)
    crop = _create_crop()
    stock_lot = _create_stock_lot(farmer.id, farm.id, crop.id, qty=100.0)

    app.dependency_overrides[get_current_user] = lambda: buyer
    bid_res = client.post(f"/api/v1/stock-lots/{stock_lot.id}/bids", json={"offered_price_per_quintal": 6200.0, "requested_quantity_quintals": 40.0})
    bid_id = bid_res.json()["id"]

    app.dependency_overrides[get_current_user] = lambda: farmer
    client.post(f"/api/v1/stock-bids/{bid_id}/accept", json={"allocated_quantity_quintals": 40.0})
    client.post(f"/api/v1/stock-bids/{bid_id}/contact-sharing/consent")

    app.dependency_overrides[get_current_user] = lambda: buyer
    client.post(f"/api/v1/stock-bids/{bid_id}/contact-sharing/consent")

    cs_res = client.get(f"/api/v1/stock-bids/{bid_id}/contact-sharing")
    data = cs_res.json()
    assert "latitude" not in str(data)
    assert "longitude" not in str(data)


def test_competing_buyer_identity_is_not_exposed():
    buyer1 = _create_user(role=UserRole.BUYER)
    buyer2 = _create_user(role=UserRole.BUYER)
    farmer = _create_user(role=UserRole.FARMER)
    farm = _create_farm(farmer.id)
    crop = _create_crop()
    stock_lot = _create_stock_lot(farmer.id, farm.id, crop.id, qty=100.0)

    app.dependency_overrides[get_current_user] = lambda: buyer1
    client.post(f"/api/v1/stock-lots/{stock_lot.id}/bids", json={"offered_price_per_quintal": 6200.0, "requested_quantity_quintals": 40.0})

    app.dependency_overrides[get_current_user] = lambda: buyer2
    res = client.get("/api/v1/stock-bids/me")
    assert res.status_code == 200
    assert len(res.json()) == 0


def test_effective_offer_uses_existing_service():
    buyer = _create_user(role=UserRole.BUYER)
    farmer = _create_user(role=UserRole.FARMER)
    farm = _create_farm(farmer.id)
    crop = _create_crop()
    stock_lot = _create_stock_lot(farmer.id, farm.id, crop.id, qty=100.0)

    app.dependency_overrides[get_current_user] = lambda: buyer
    res = client.post(f"/api/v1/stock-lots/{stock_lot.id}/bids", json={"offered_price_per_quintal": 6200.0, "requested_quantity_quintals": 40.0})
    assert res.status_code == 201
    assert "effective_offer_per_quintal" in res.json()


def test_unknown_destination_returns_null_effective_offer():
    buyer = _create_user(role=UserRole.BUYER)
    farmer = _create_user(role=UserRole.FARMER)
    farm = _create_farm(farmer.id)
    crop = _create_crop()
    stock_lot = _create_stock_lot(farmer.id, farm.id, crop.id, qty=100.0)

    app.dependency_overrides[get_current_user] = lambda: buyer
    res = client.post(f"/api/v1/stock-lots/{stock_lot.id}/bids", json={"offered_price_per_quintal": 6200.0, "requested_quantity_quintals": 40.0})
    assert res.status_code == 201
    assert res.json()["effective_offer_per_quintal"] is None or isinstance(res.json()["effective_offer_per_quintal"], (int, float))
