"""Comprehensive unit test suite for StockLot harvest and discovery API."""
import uuid
from datetime import date, timedelta
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.user import User, UserRole
from app.models.farmer import Farmer
from app.models.farm import Farm
from app.models.crop import Crop, CropType
from app.models.future_crop_lot import FutureCropLot, FutureCropLotStatus
from app.models.bid import Bid, BidStatus
from app.models.contact_sharing import ContactSharing, ContactSharingStatus
from app.models.stock_lot import StockLot, StockLotStatus
from app.api.v1.auth import get_current_user, get_password_hash
from app.database.session import SessionLocal, engine
from app.database.base import Base

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_test_context():
    """Clear dependency overrides and ensure test environment has all tables."""
    app.dependency_overrides.clear()
    Base.metadata.create_all(bind=engine)
    yield
    app.dependency_overrides.clear()


def _create_user(role=UserRole.FARMER, prefix="user"):
    db = SessionLocal()
    uid = uuid.uuid4().hex[:10]
    try:
        u = User(
            username=f"{prefix}_{uid}",
            email=f"{prefix}_{uid}@example.com",
            hashed_password=get_password_hash("secret123"),
            role=role,
            full_name=f"Test {prefix.capitalize()} {uid}",
            phone=f"+919876{uid[:6].zfill(6)}",
        )
        db.add(u)
        db.commit()
        db.refresh(u)
        return u
    finally:
        db.close()


def _create_farm(farmer_user_id):
    db = SessionLocal()
    uid = uuid.uuid4().hex[:6]
    try:
        farmer_entity = Farmer(
            name=f"Farmer {uid}",
            phone="9876543210",
            district="Dharwad",
            state="Karnataka",
        )
        db.add(farmer_entity)
        db.commit()
        db.refresh(farmer_entity)

        f = Farm(
            owner_id=farmer_user_id,
            farmer_id=farmer_entity.id,
            land_area_acre=5.0,
            water_availability=True,
            district="Dharwad",
            state="Karnataka",
        )
        db.add(f)
        db.commit()
        db.refresh(f)
        return f
    finally:
        db.close()


def _create_crop(name="Paddy"):
    db = SessionLocal()
    try:
        c = db.query(Crop).filter(Crop.name == name).first()
        if not c:
            c = Crop(name=name, crop_type=CropType.CEREAL, season="Kharif", duration_days=100)
            db.add(c)
            db.commit()
            db.refresh(c)
        return c
    finally:
        db.close()


def _create_future_lot(farmer_id, farm_id, crop_id, status=FutureCropLotStatus.OPEN):
    db = SessionLocal()
    try:
        lot = FutureCropLot(
            farmer_id=farmer_id,
            farm_id=farm_id,
            crop_id=crop_id,
            planned_acres=4.0,
            expected_quantity_quintals=80.0,
            asking_price_per_quintal=2500.0,
            planned_sowing_date=date.today(),
            expected_harvest_start=date.today() + timedelta(days=60),
            expected_harvest_end=date.today() + timedelta(days=90),
            status=status,
        )
        db.add(lot)
        db.commit()
        db.refresh(lot)
        return lot
    finally:
        db.close()


# ==========================================
# TEST CASES
# ==========================================

def test_farmer_harvests_future_crop_lot():
    farmer = _create_user(role=UserRole.FARMER, prefix="farmer")
    farm = _create_farm(farmer.id)
    crop = _create_crop("Rice")
    future_lot = _create_future_lot(farmer.id, farm.id, crop.id)

    app.dependency_overrides[get_current_user] = lambda: farmer

    payload = {
        "actual_quantity_quintals": 85.0,
        "actual_harvest_date": str(date.today()),
        "quality_grade": "Grade A",
        "asking_price_per_quintal": 2700.0,
    }

    res = client.post(f"/api/v1/farmer/future-crop-lots/{future_lot.id}/harvest", json=payload)
    assert res.status_code == 201
    data = res.json()

    assert data["farmer_id"] == farmer.id
    assert data["future_crop_lot_id"] == future_lot.id
    assert data["actual_quantity_quintals"] == 85.0
    assert data["available_quantity_quintals"] == 85.0
    assert data["status"] == "DRAFT"
    assert data["crop_name"] == "Rice"
    assert data["district"] == "Dharwad"


def test_direct_stock_creation():
    farmer = _create_user(role=UserRole.FARMER, prefix="farmer")
    farm = _create_farm(farmer.id)
    crop = _create_crop("Wheat")

    app.dependency_overrides[get_current_user] = lambda: farmer

    payload = {
        "farm_id": farm.id,
        "crop_id": crop.id,
        "actual_quantity_quintals": 60.0,
        "actual_harvest_date": str(date.today()),
        "variety": "Sharbati",
        "quality_grade": "FAQ",
        "asking_price_per_quintal": 2300.0,
    }

    res = client.post("/api/v1/farmer/stock-lots", json=payload)
    assert res.status_code == 201
    data = res.json()

    assert data["future_crop_lot_id"] is None
    assert data["actual_quantity_quintals"] == 60.0
    assert data["available_quantity_quintals"] == 60.0
    assert data["status"] == "DRAFT"


def test_unauthenticated_harvest_fails():
    farmer = _create_user(role=UserRole.FARMER)
    farm = _create_farm(farmer.id)
    crop = _create_crop()
    future_lot = _create_future_lot(farmer.id, farm.id, crop.id)

    app.dependency_overrides.clear()

    res = client.post(
        f"/api/v1/farmer/future-crop-lots/{future_lot.id}/harvest",
        json={"actual_quantity_quintals": 50.0, "actual_harvest_date": str(date.today())},
    )
    assert res.status_code == 401


def test_buyer_cannot_create_stock_lot():
    buyer = _create_user(role=UserRole.BUYER, prefix="buyer")
    farmer = _create_user(role=UserRole.FARMER, prefix="farmer")
    farm = _create_farm(farmer.id)
    crop = _create_crop()

    app.dependency_overrides[get_current_user] = lambda: buyer

    res = client.post(
        "/api/v1/farmer/stock-lots",
        json={
            "farm_id": farm.id,
            "crop_id": crop.id,
            "actual_quantity_quintals": 50.0,
            "actual_harvest_date": str(date.today()),
        },
    )
    assert res.status_code == 403


def test_unrelated_farmer_cannot_harvest():
    farmer1 = _create_user(role=UserRole.FARMER, prefix="farmer1")
    farmer2 = _create_user(role=UserRole.FARMER, prefix="farmer2")
    farm = _create_farm(farmer1.id)
    crop = _create_crop()
    future_lot = _create_future_lot(farmer1.id, farm.id, crop.id)

    app.dependency_overrides[get_current_user] = lambda: farmer2

    res = client.post(
        f"/api/v1/farmer/future-crop-lots/{future_lot.id}/harvest",
        json={"actual_quantity_quintals": 50.0, "actual_harvest_date": str(date.today())},
    )
    assert res.status_code == 403


def test_invalid_quantity_rejected():
    farmer = _create_user(role=UserRole.FARMER)
    farm = _create_farm(farmer.id)
    crop = _create_crop()
    future_lot = _create_future_lot(farmer.id, farm.id, crop.id)

    app.dependency_overrides[get_current_user] = lambda: farmer

    res = client.post(
        f"/api/v1/farmer/future-crop-lots/{future_lot.id}/harvest",
        json={"actual_quantity_quintals": -10.0, "actual_harvest_date": str(date.today())},
    )
    assert res.status_code == 422


def test_negative_asking_price_rejected():
    farmer = _create_user(role=UserRole.FARMER)
    farm = _create_farm(farmer.id)
    crop = _create_crop()
    future_lot = _create_future_lot(farmer.id, farm.id, crop.id)

    app.dependency_overrides[get_current_user] = lambda: farmer

    res = client.post(
        f"/api/v1/farmer/future-crop-lots/{future_lot.id}/harvest",
        json={
            "actual_quantity_quintals": 50.0,
            "actual_harvest_date": str(date.today()),
            "asking_price_per_quintal": -500.0,
        },
    )
    assert res.status_code == 422


def test_future_lot_status_transitions_to_harvested():
    farmer = _create_user(role=UserRole.FARMER)
    farm = _create_farm(farmer.id)
    crop = _create_crop()
    future_lot = _create_future_lot(farmer.id, farm.id, crop.id)

    app.dependency_overrides[get_current_user] = lambda: farmer

    res = client.post(
        f"/api/v1/farmer/future-crop-lots/{future_lot.id}/harvest",
        json={"actual_quantity_quintals": 75.0, "actual_harvest_date": str(date.today())},
    )
    assert res.status_code == 201

    db = SessionLocal()
    updated_lot = db.query(FutureCropLot).filter(FutureCropLot.id == future_lot.id).first()
    assert updated_lot.status == FutureCropLotStatus.HARVESTED
    db.close()


def test_duplicate_harvest_rejected():
    farmer = _create_user(role=UserRole.FARMER)
    farm = _create_farm(farmer.id)
    crop = _create_crop()
    future_lot = _create_future_lot(farmer.id, farm.id, crop.id)

    app.dependency_overrides[get_current_user] = lambda: farmer

    payload = {"actual_quantity_quintals": 75.0, "actual_harvest_date": str(date.today())}
    res1 = client.post(f"/api/v1/farmer/future-crop-lots/{future_lot.id}/harvest", json=payload)
    assert res1.status_code == 201

    res2 = client.post(f"/api/v1/farmer/future-crop-lots/{future_lot.id}/harvest", json=payload)
    assert res2.status_code == 400
    assert "already been harvested" in str(res2.json())


def test_draft_stock_not_publicly_visible():
    farmer = _create_user(role=UserRole.FARMER, prefix="farmer")
    buyer = _create_user(role=UserRole.BUYER, prefix="buyer")
    farm = _create_farm(farmer.id)
    crop = _create_crop()
    future_lot = _create_future_lot(farmer.id, farm.id, crop.id)

    app.dependency_overrides[get_current_user] = lambda: farmer
    res = client.post(
        f"/api/v1/farmer/future-crop-lots/{future_lot.id}/harvest",
        json={"actual_quantity_quintals": 50.0, "actual_harvest_date": str(date.today())},
    )
    stock_id = res.json()["id"]

    app.dependency_overrides[get_current_user] = lambda: buyer
    open_res = client.get("/api/v1/stock-lots/open")
    assert open_res.status_code == 200
    open_ids = [s["id"] for s in open_res.json()]
    assert stock_id not in open_ids


def test_publish_stock_lot_success():
    farmer = _create_user(role=UserRole.FARMER, prefix="farmer")
    buyer = _create_user(role=UserRole.BUYER, prefix="buyer")
    farm = _create_farm(farmer.id)
    crop = _create_crop()
    future_lot = _create_future_lot(farmer.id, farm.id, crop.id)

    app.dependency_overrides[get_current_user] = lambda: farmer
    res = client.post(
        f"/api/v1/farmer/future-crop-lots/{future_lot.id}/harvest",
        json={"actual_quantity_quintals": 50.0, "actual_harvest_date": str(date.today())},
    )
    stock_id = res.json()["id"]

    pub_res = client.post(f"/api/v1/farmer/stock-lots/{stock_id}/publish")
    assert pub_res.status_code == 200
    assert pub_res.json()["status"] == "AVAILABLE"

    app.dependency_overrides[get_current_user] = lambda: buyer
    open_res = client.get("/api/v1/stock-lots/open")
    assert open_res.status_code == 200
    assert any(s["id"] == stock_id for s in open_res.json())


def test_cancelled_stock_not_visible():
    farmer = _create_user(role=UserRole.FARMER, prefix="farmer")
    buyer = _create_user(role=UserRole.BUYER, prefix="buyer")
    farm = _create_farm(farmer.id)
    crop = _create_crop()
    future_lot = _create_future_lot(farmer.id, farm.id, crop.id)

    app.dependency_overrides[get_current_user] = lambda: farmer
    res = client.post(
        f"/api/v1/farmer/future-crop-lots/{future_lot.id}/harvest",
        json={"actual_quantity_quintals": 50.0, "actual_harvest_date": str(date.today())},
    )
    stock_id = res.json()["id"]

    client.post(f"/api/v1/farmer/stock-lots/{stock_id}/publish")
    cancel_res = client.delete(f"/api/v1/farmer/stock-lots/{stock_id}")
    assert cancel_res.status_code == 200
    assert cancel_res.json()["status"] == "CANCELLED"

    app.dependency_overrides[get_current_user] = lambda: buyer
    open_res = client.get("/api/v1/stock-lots/open")
    assert all(s["id"] != stock_id for s in open_res.json())


def test_public_discovery_privacy_shielding():
    farmer = _create_user(role=UserRole.FARMER, prefix="farmer")
    buyer = _create_user(role=UserRole.BUYER, prefix="buyer")
    farm = _create_farm(farmer.id)
    crop = _create_crop()
    future_lot = _create_future_lot(farmer.id, farm.id, crop.id)

    app.dependency_overrides[get_current_user] = lambda: farmer
    res = client.post(
        f"/api/v1/farmer/future-crop-lots/{future_lot.id}/harvest",
        json={"actual_quantity_quintals": 50.0, "actual_harvest_date": str(date.today())},
    )
    stock_id = res.json()["id"]
    client.post(f"/api/v1/farmer/stock-lots/{stock_id}/publish")

    app.dependency_overrides[get_current_user] = lambda: buyer
    open_res = client.get("/api/v1/stock-lots/open")
    item = next(s for s in open_res.json() if s["id"] == stock_id)

    assert "farmer_phone" not in item
    assert "farmer_email" not in item
    assert "location" not in item
    assert item["district"] == "Dharwad"
    assert item["state"] == "Karnataka"


def test_indicative_bid_remains_intact_post_harvest():
    farmer = _create_user(role=UserRole.FARMER, prefix="farmer")
    buyer = _create_user(role=UserRole.BUYER, prefix="buyer")
    farm = _create_farm(farmer.id)
    crop = _create_crop()
    future_lot = _create_future_lot(farmer.id, farm.id, crop.id, status=FutureCropLotStatus.INDICATIVE_ACCEPTED)

    db = SessionLocal()
    bid = Bid(
        future_crop_lot_id=future_lot.id,
        buyer_id=buyer.id,
        offered_price_per_quintal=2600.0,
        quantity_quintals=40.0,
        status=BidStatus.ACCEPTED,
    )
    db.add(bid)
    db.commit()
    bid_id = bid.id
    db.close()

    app.dependency_overrides[get_current_user] = lambda: farmer
    res = client.post(
        f"/api/v1/farmer/future-crop-lots/{future_lot.id}/harvest",
        json={"actual_quantity_quintals": 50.0, "actual_harvest_date": str(date.today())},
    )
    assert res.status_code == 201

    db = SessionLocal()
    check_bid = db.query(Bid).filter(Bid.id == bid_id).first()
    assert check_bid.status == BidStatus.ACCEPTED
    db.close()


def test_contact_sharing_remains_intact_post_harvest():
    farmer = _create_user(role=UserRole.FARMER, prefix="farmer")
    buyer = _create_user(role=UserRole.BUYER, prefix="buyer")
    farm = _create_farm(farmer.id)
    crop = _create_crop()
    future_lot = _create_future_lot(farmer.id, farm.id, crop.id, status=FutureCropLotStatus.INDICATIVE_ACCEPTED)

    db = SessionLocal()
    bid = Bid(
        future_crop_lot_id=future_lot.id,
        buyer_id=buyer.id,
        offered_price_per_quintal=2600.0,
        quantity_quintals=40.0,
        status=BidStatus.ACCEPTED,
    )
    db.add(bid)
    db.commit()

    sharing = ContactSharing(
        bid_id=bid.id,
        farmer_id=farmer.id,
        buyer_id=buyer.id,
        farmer_consented=True,
        buyer_consented=True,
        status=ContactSharingStatus.MUTUAL_CONSENT,
    )
    db.add(sharing)
    db.commit()
    sharing_id = sharing.id
    db.close()

    app.dependency_overrides[get_current_user] = lambda: farmer
    res = client.post(
        f"/api/v1/farmer/future-crop-lots/{future_lot.id}/harvest",
        json={"actual_quantity_quintals": 50.0, "actual_harvest_date": str(date.today())},
    )
    assert res.status_code == 201

    db = SessionLocal()
    check_sharing = db.query(ContactSharing).filter(ContactSharing.id == sharing_id).first()
    assert check_sharing.status == ContactSharingStatus.MUTUAL_CONSENT
    assert check_sharing.farmer_consented is True
    db.close()


def test_farmer_update_draft_stock():
    farmer = _create_user(role=UserRole.FARMER)
    farm = _create_farm(farmer.id)
    crop = _create_crop()

    app.dependency_overrides[get_current_user] = lambda: farmer
    res = client.post(
        "/api/v1/farmer/stock-lots",
        json={
            "farm_id": farm.id,
            "crop_id": crop.id,
            "actual_quantity_quintals": 40.0,
            "actual_harvest_date": str(date.today()),
        },
    )
    stock_id = res.json()["id"]

    up_res = client.put(
        f"/api/v1/farmer/stock-lots/{stock_id}",
        json={"actual_quantity_quintals": 45.0, "quality_grade": "Grade A"},
    )
    assert up_res.status_code == 200
    assert up_res.json()["actual_quantity_quintals"] == 45.0
    assert up_res.json()["available_quantity_quintals"] == 45.0
    assert up_res.json()["quality_grade"] == "Grade A"


def test_cannot_update_published_stock():
    farmer = _create_user(role=UserRole.FARMER)
    farm = _create_farm(farmer.id)
    crop = _create_crop()

    app.dependency_overrides[get_current_user] = lambda: farmer
    res = client.post(
        "/api/v1/farmer/stock-lots",
        json={
            "farm_id": farm.id,
            "crop_id": crop.id,
            "actual_quantity_quintals": 40.0,
            "actual_harvest_date": str(date.today()),
        },
    )
    stock_id = res.json()["id"]
    client.post(f"/api/v1/farmer/stock-lots/{stock_id}/publish")

    up_res = client.put(f"/api/v1/farmer/stock-lots/{stock_id}", json={"actual_quantity_quintals": 50.0})
    assert up_res.status_code == 400
    assert "Only DRAFT stock lots can be modified" in str(up_res.json())


def test_unrelated_farmer_cannot_update_or_publish():
    farmer1 = _create_user(role=UserRole.FARMER, prefix="farmer1")
    farmer2 = _create_user(role=UserRole.FARMER, prefix="farmer2")
    farm1 = _create_farm(farmer1.id)
    crop = _create_crop()

    app.dependency_overrides[get_current_user] = lambda: farmer1
    res = client.post(
        "/api/v1/farmer/stock-lots",
        json={
            "farm_id": farm1.id,
            "crop_id": crop.id,
            "actual_quantity_quintals": 40.0,
            "actual_harvest_date": str(date.today()),
        },
    )
    stock_id = res.json()["id"]

    app.dependency_overrides[get_current_user] = lambda: farmer2
    up_res = client.put(f"/api/v1/farmer/stock-lots/{stock_id}", json={"actual_quantity_quintals": 50.0})
    assert up_res.status_code == 403

    pub_res = client.post(f"/api/v1/farmer/stock-lots/{stock_id}/publish")
    assert pub_res.status_code == 403


def test_get_my_stock_lots():
    farmer = _create_user(role=UserRole.FARMER)
    farm = _create_farm(farmer.id)
    crop = _create_crop()

    app.dependency_overrides[get_current_user] = lambda: farmer
    client.post(
        "/api/v1/farmer/stock-lots",
        json={
            "farm_id": farm.id,
            "crop_id": crop.id,
            "actual_quantity_quintals": 30.0,
            "actual_harvest_date": str(date.today()),
        },
    )

    my_res = client.get("/api/v1/farmer/stock-lots/me")
    assert my_res.status_code == 200
    assert len(my_res.json()) >= 1
