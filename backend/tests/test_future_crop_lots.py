"""Automated test suite for Future Crop Lot endpoints and security authorization."""
import uuid
import pytest
from datetime import date, timedelta
from fastapi.testclient import TestClient

from app.main import app
from app.models.user import User, UserRole
from app.models.farmer import Farmer
from app.models.farm import Farm
from app.models.crop import Crop, CropType
from app.models.buyer_demand import BuyerDemand, BuyerDemandStatus
from app.models.recommendation import Recommendation
from app.models.future_crop_lot import FutureCropLot, FutureCropLotStatus
from app.api.v1.auth import get_password_hash, create_access_token
from app.database.session import SessionLocal

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_test_entities():
    """Ensure standard crop entity exists for tests."""
    db = SessionLocal()
    try:
        crop = db.query(Crop).filter(Crop.name == "Groundnut").first()
        if not crop:
            crop = Crop(
                name="Groundnut",
                crop_type=CropType.OILSEED,
                season="Kharif",
                duration_days=110,
                is_oilseed=True
            )
            db.add(crop)
            db.commit()
    finally:
        db.close()


def _create_farmer_and_farm(prefix="farmer"):
    db = SessionLocal()
    uid = uuid.uuid4().hex[:6]
    try:
        u = User(
            username=f"{prefix}_{uid}",
            email=f"{prefix}_{uid}@example.com",
            hashed_password=get_password_hash("Secret123!"),
            role=UserRole.FARMER
        )
        db.add(u)
        db.commit()
        db.refresh(u)

        farmer_entity = Farmer(
            name=f"Farmer {uid}",
            phone="9876543210",
            district="Dharwad",
            state="Karnataka"
        )
        db.add(farmer_entity)
        db.commit()
        db.refresh(farmer_entity)

        farm = Farm(
            owner_id=u.id,
            farmer_id=farmer_entity.id,
            land_area_acre=5.0,
            water_availability=True,
            district="Dharwad",
            state="Karnataka"
        )
        db.add(farm)
        db.commit()
        db.refresh(farm)

        token = create_access_token(data={"sub": u.username, "user_id": u.id, "role": "FARMER"})
        return u.id, farm.id, token
    finally:
        db.close()


def _create_buyer(prefix="buyer"):
    db = SessionLocal()
    uid = uuid.uuid4().hex[:6]
    try:
        u = User(
            username=f"{prefix}_{uid}",
            email=f"{prefix}_{uid}@example.com",
            hashed_password=get_password_hash("Secret123!"),
            role=UserRole.BUYER
        )
        db.add(u)
        db.commit()
        db.refresh(u)
        token = create_access_token(data={"sub": u.username, "user_id": u.id, "role": "BUYER"})
        return u.id, token
    finally:
        db.close()


def test_1_farmer_can_create_future_crop_lot():
    farmer_id, farm_id, token = _create_farmer_and_farm("f1")
    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        res = client.post(
            "/api/v1/farmer/future-crop-lots",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "farm_id": farm_id,
                "crop_id": 1,
                "variety": "Kadir-6",
                "planned_acres": 3.0,
                "expected_quantity_quintals": 60.0,
                "asking_price_per_quintal": 6300.0,
                "planned_sowing_date": "2026-06-01",
                "expected_harvest_start": "2026-09-15",
                "expected_harvest_end": "2026-09-30",
                "quality_grade": "Grade A"
            }
        )
        assert res.status_code == 201
        data = res.json()
        assert data["farmer_id"] == farmer_id
        assert data["status"] == "DRAFT"
    finally:
        app.dependency_overrides = old_overrides


def test_2_buyer_cannot_create_future_crop_lot():
    _, token_buyer = _create_buyer("b2")
    _, farm_id, _ = _create_farmer_and_farm("f2_owner")
    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        res = client.post(
            "/api/v1/farmer/future-crop-lots",
            headers={"Authorization": f"Bearer {token_buyer}"},
            json={
                "farm_id": farm_id,
                "crop_id": 1,
                "planned_acres": 2.0,
                "expected_quantity_quintals": 40.0,
                "planned_sowing_date": "2026-06-01",
                "expected_harvest_start": "2026-09-15",
                "expected_harvest_end": "2026-09-30"
            }
        )
        assert res.status_code == 403
    finally:
        app.dependency_overrides = old_overrides


def test_3_unauthenticated_creation_rejected():
    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        res = client.post(
            "/api/v1/farmer/future-crop-lots",
            json={
                "farm_id": 1,
                "crop_id": 1,
                "planned_acres": 2.0,
                "expected_quantity_quintals": 40.0,
                "planned_sowing_date": "2026-06-01",
                "expected_harvest_start": "2026-09-15",
                "expected_harvest_end": "2026-09-30"
            }
        )
        assert res.status_code == 401
    finally:
        app.dependency_overrides = old_overrides


def test_4_farmer_id_cannot_be_spoofed():
    farmer_id, farm_id, token = _create_farmer_and_farm("f4")
    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        res = client.post(
            "/api/v1/farmer/future-crop-lots",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "farmer_id": 999999,
                "farm_id": farm_id,
                "crop_id": 1,
                "planned_acres": 2.0,
                "expected_quantity_quintals": 40.0,
                "planned_sowing_date": "2026-06-01",
                "expected_harvest_start": "2026-09-15",
                "expected_harvest_end": "2026-09-30"
            }
        )
        assert res.status_code == 201
        assert res.json()["farmer_id"] == farmer_id
    finally:
        app.dependency_overrides = old_overrides


def test_5_farmer_cannot_use_another_farmers_farm():
    _, farm_id_other, _ = _create_farmer_and_farm("f5_other")
    _, _, token_hacker = _create_farmer_and_farm("f5_hacker")
    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        res = client.post(
            "/api/v1/farmer/future-crop-lots",
            headers={"Authorization": f"Bearer {token_hacker}"},
            json={
                "farm_id": farm_id_other,
                "crop_id": 1,
                "planned_acres": 2.0,
                "expected_quantity_quintals": 40.0,
                "planned_sowing_date": "2026-06-01",
                "expected_harvest_start": "2026-09-15",
                "expected_harvest_end": "2026-09-30"
            }
        )
        assert res.status_code == 403
    finally:
        app.dependency_overrides = old_overrides


def test_6_farmer_can_list_own_lots():
    farmer_id, farm_id, token = _create_farmer_and_farm("f6")
    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        client.post(
            "/api/v1/farmer/future-crop-lots",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "farm_id": farm_id,
                "crop_id": 1,
                "planned_acres": 2.0,
                "expected_quantity_quintals": 40.0,
                "planned_sowing_date": "2026-06-01",
                "expected_harvest_start": "2026-09-15",
                "expected_harvest_end": "2026-09-30"
            }
        )
        res = client.get("/api/v1/farmer/future-crop-lots/me", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200
        items = res.json()
        assert len(items) >= 1
        assert all(item["farmer_id"] == farmer_id for item in items)
    finally:
        app.dependency_overrides = old_overrides


def test_7_farmer_can_retrieve_own_lot():
    _, farm_id, token = _create_farmer_and_farm("f7")
    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        res_create = client.post(
            "/api/v1/farmer/future-crop-lots",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "farm_id": farm_id,
                "crop_id": 1,
                "planned_acres": 2.0,
                "expected_quantity_quintals": 40.0,
                "planned_sowing_date": "2026-06-01",
                "expected_harvest_start": "2026-09-15",
                "expected_harvest_end": "2026-09-30"
            }
        )
        lot_id = res_create.json()["id"]

        res = client.get(f"/api/v1/farmer/future-crop-lots/{lot_id}", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200
        assert res.json()["id"] == lot_id
    finally:
        app.dependency_overrides = old_overrides


def test_8_farmer_cannot_retrieve_another_farmers_private_lot():
    _, farm_id1, token1 = _create_farmer_and_farm("f8a")
    _, _, token2 = _create_farmer_and_farm("f8b")
    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        res_create = client.post(
            "/api/v1/farmer/future-crop-lots",
            headers={"Authorization": f"Bearer {token1}"},
            json={
                "farm_id": farm_id1,
                "crop_id": 1,
                "planned_acres": 2.0,
                "expected_quantity_quintals": 40.0,
                "planned_sowing_date": "2026-06-01",
                "expected_harvest_start": "2026-09-15",
                "expected_harvest_end": "2026-09-30"
            }
        )
        lot_id = res_create.json()["id"]

        res = client.get(f"/api/v1/farmer/future-crop-lots/{lot_id}", headers={"Authorization": f"Bearer {token2}"})
        assert res.status_code == 403
    finally:
        app.dependency_overrides = old_overrides


def test_9_farmer_can_update_own_draft_lot():
    _, farm_id, token = _create_farmer_and_farm("f9")
    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        res_create = client.post(
            "/api/v1/farmer/future-crop-lots",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "farm_id": farm_id,
                "crop_id": 1,
                "planned_acres": 2.0,
                "expected_quantity_quintals": 40.0,
                "planned_sowing_date": "2026-06-01",
                "expected_harvest_start": "2026-09-15",
                "expected_harvest_end": "2026-09-30"
            }
        )
        lot_id = res_create.json()["id"]

        res_update = client.put(
            f"/api/v1/farmer/future-crop-lots/{lot_id}",
            headers={"Authorization": f"Bearer {token}"},
            json={"planned_acres": 3.5, "expected_quantity_quintals": 70.0}
        )
        assert res_update.status_code == 200
        assert res_update.json()["planned_acres"] == 3.5
        assert res_update.json()["expected_quantity_quintals"] == 70.0
    finally:
        app.dependency_overrides = old_overrides


def test_10_farmer_can_publish_draft_lot():
    _, farm_id, token = _create_farmer_and_farm("f10")
    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        res_create = client.post(
            "/api/v1/farmer/future-crop-lots",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "farm_id": farm_id,
                "crop_id": 1,
                "planned_acres": 2.0,
                "expected_quantity_quintals": 40.0,
                "planned_sowing_date": "2026-06-01",
                "expected_harvest_start": "2026-09-15",
                "expected_harvest_end": "2026-09-30"
            }
        )
        lot_id = res_create.json()["id"]
        assert res_create.json()["status"] == "DRAFT"

        res_pub = client.post(f"/api/v1/farmer/future-crop-lots/{lot_id}/publish", headers={"Authorization": f"Bearer {token}"})
        assert res_pub.status_code == 200
        assert res_pub.json()["status"] == "OPEN"
    finally:
        app.dependency_overrides = old_overrides


def test_11_cannot_update_cancelled_lot():
    _, farm_id, token = _create_farmer_and_farm("f11")
    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        res_create = client.post(
            "/api/v1/farmer/future-crop-lots",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "farm_id": farm_id,
                "crop_id": 1,
                "planned_acres": 2.0,
                "expected_quantity_quintals": 40.0,
                "planned_sowing_date": "2026-06-01",
                "expected_harvest_start": "2026-09-15",
                "expected_harvest_end": "2026-09-30"
            }
        )
        lot_id = res_create.json()["id"]

        # Cancel
        client.delete(f"/api/v1/farmer/future-crop-lots/{lot_id}", headers={"Authorization": f"Bearer {token}"})

        # Update should fail -> 400
        res_up = client.put(
            f"/api/v1/farmer/future-crop-lots/{lot_id}",
            headers={"Authorization": f"Bearer {token}"},
            json={"planned_acres": 5.0}
        )
        assert res_up.status_code == 400
    finally:
        app.dependency_overrides = old_overrides


def test_12_cannot_update_harvested_lot():
    farmer_id, farm_id, token = _create_farmer_and_farm("f12")
    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    db = SessionLocal()
    try:
        lot = FutureCropLot(
            farm_id=farm_id,
            farmer_id=farmer_id,
            crop_id=1,
            planned_acres=2.0,
            expected_quantity_quintals=40.0,
            planned_sowing_date=date(2026, 6, 1),
            expected_harvest_start=date(2026, 9, 15),
            expected_harvest_end=date(2026, 9, 30),
            status=FutureCropLotStatus.HARVESTED
        )
        db.add(lot)
        db.commit()
        db.refresh(lot)

        res_up = client.put(
            f"/api/v1/farmer/future-crop-lots/{lot.id}",
            headers={"Authorization": f"Bearer {token}"},
            json={"planned_acres": 5.0}
        )
        assert res_up.status_code == 400
    finally:
        db.close()
        app.dependency_overrides = old_overrides


def test_13_farmer_can_cancel_own_lot():
    _, farm_id, token = _create_farmer_and_farm("f13")
    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        res_create = client.post(
            "/api/v1/farmer/future-crop-lots",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "farm_id": farm_id,
                "crop_id": 1,
                "planned_acres": 2.0,
                "expected_quantity_quintals": 40.0,
                "planned_sowing_date": "2026-06-01",
                "expected_harvest_start": "2026-09-15",
                "expected_harvest_end": "2026-09-30"
            }
        )
        lot_id = res_create.json()["id"]

        res_del = client.delete(f"/api/v1/farmer/future-crop-lots/{lot_id}", headers={"Authorization": f"Bearer {token}"})
        assert res_del.status_code == 200
        assert res_del.json()["status"] == "CANCELLED"
    finally:
        app.dependency_overrides = old_overrides


def test_14_cancellation_is_soft_cancellation():
    _, farm_id, token = _create_farmer_and_farm("f14")
    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        res_create = client.post(
            "/api/v1/farmer/future-crop-lots",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "farm_id": farm_id,
                "crop_id": 1,
                "planned_acres": 2.0,
                "expected_quantity_quintals": 40.0,
                "planned_sowing_date": "2026-06-01",
                "expected_harvest_start": "2026-09-15",
                "expected_harvest_end": "2026-09-30"
            }
        )
        lot_id = res_create.json()["id"]

        client.delete(f"/api/v1/farmer/future-crop-lots/{lot_id}", headers={"Authorization": f"Bearer {token}"})

        # Query GET me -> lot is still returned with CANCELLED status
        res_me = client.get("/api/v1/farmer/future-crop-lots/me", headers={"Authorization": f"Bearer {token}"})
        assert res_me.status_code == 200
        cancelled_item = next(item for item in res_me.json() if item["id"] == lot_id)
        assert cancelled_item["status"] == "CANCELLED"
    finally:
        app.dependency_overrides = old_overrides


def test_15_valid_active_buyer_demand_can_be_linked():
    buyer_id, token_buyer = _create_buyer("b15")
    _, farm_id, token_farmer = _create_farmer_and_farm("f15")
    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        res_dem = client.post(
            "/api/v1/buyer/demands",
            headers={"Authorization": f"Bearer {token_buyer}"},
            json={"crop_id": 1, "quantity_quintals": 100.0, "target_price_per_quintal": 6200.0, "delivery_district": "Dharwad"}
        )
        demand_id = res_dem.json()["id"]

        res_lot = client.post(
            "/api/v1/farmer/future-crop-lots",
            headers={"Authorization": f"Bearer {token_farmer}"},
            json={
                "farm_id": farm_id,
                "crop_id": 1,
                "demand_id": demand_id,
                "planned_acres": 2.0,
                "expected_quantity_quintals": 40.0,
                "planned_sowing_date": "2026-06-01",
                "expected_harvest_start": "2026-09-15",
                "expected_harvest_end": "2026-09-30"
            }
        )
        assert res_lot.status_code == 201
        assert res_lot.json()["demand_id"] == demand_id
    finally:
        app.dependency_overrides = old_overrides


def test_16_cancelled_buyer_demand_cannot_be_linked():
    buyer_id, token_buyer = _create_buyer("b16")
    _, farm_id, token_farmer = _create_farmer_and_farm("f16")
    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        res_dem = client.post(
            "/api/v1/buyer/demands",
            headers={"Authorization": f"Bearer {token_buyer}"},
            json={"crop_id": 1, "quantity_quintals": 100.0, "target_price_per_quintal": 6200.0, "delivery_district": "Dharwad"}
        )
        demand_id = res_dem.json()["id"]
        client.delete(f"/api/v1/buyer/demands/{demand_id}", headers={"Authorization": f"Bearer {token_buyer}"})

        res_lot = client.post(
            "/api/v1/farmer/future-crop-lots",
            headers={"Authorization": f"Bearer {token_farmer}"},
            json={
                "farm_id": farm_id,
                "crop_id": 1,
                "demand_id": demand_id,
                "planned_acres": 2.0,
                "expected_quantity_quintals": 40.0,
                "planned_sowing_date": "2026-06-01",
                "expected_harvest_start": "2026-09-15",
                "expected_harvest_end": "2026-09-30"
            }
        )
        assert res_lot.status_code == 400
    finally:
        app.dependency_overrides = old_overrides


def test_17_expired_buyer_demand_cannot_be_linked():
    buyer_id, token_buyer = _create_buyer("b17")
    _, farm_id, token_farmer = _create_farmer_and_farm("f17")
    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    db = SessionLocal()
    try:
        demand = BuyerDemand(
            buyer_id=buyer_id,
            crop_id=1,
            quantity_quintals=100.0,
            target_price_per_quintal=6000.0,
            delivery_district="Dharwad",
            status=BuyerDemandStatus.EXPIRED
        )
        db.add(demand)
        db.commit()
        db.refresh(demand)

        res_lot = client.post(
            "/api/v1/farmer/future-crop-lots",
            headers={"Authorization": f"Bearer {token_farmer}"},
            json={
                "farm_id": farm_id,
                "crop_id": 1,
                "demand_id": demand.id,
                "planned_acres": 2.0,
                "expected_quantity_quintals": 40.0,
                "planned_sowing_date": "2026-06-01",
                "expected_harvest_start": "2026-09-15",
                "expected_harvest_end": "2026-09-30"
            }
        )
        assert res_lot.status_code == 400
    finally:
        db.close()
        app.dependency_overrides = old_overrides


def test_18_demand_crop_mismatch_is_rejected():
    buyer_id, token_buyer = _create_buyer("b18")
    _, farm_id, token_farmer = _create_farmer_and_farm("f18")
    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    db = SessionLocal()
    try:
        crop2 = Crop(name=f"Crop_{uuid.uuid4().hex[:4]}", crop_type=CropType.OILSEED, is_oilseed=True)
        db.add(crop2)
        db.commit()
        db.refresh(crop2)

        res_dem = client.post(
            "/api/v1/buyer/demands",
            headers={"Authorization": f"Bearer {token_buyer}"},
            json={"crop_id": crop2.id, "quantity_quintals": 100.0, "target_price_per_quintal": 6200.0, "delivery_district": "Dharwad"}
        )
        demand_id = res_dem.json()["id"]

        res_lot = client.post(
            "/api/v1/farmer/future-crop-lots",
            headers={"Authorization": f"Bearer {token_farmer}"},
            json={
                "farm_id": farm_id,
                "crop_id": 1,
                "demand_id": demand_id,
                "planned_acres": 2.0,
                "expected_quantity_quintals": 40.0,
                "planned_sowing_date": "2026-06-01",
                "expected_harvest_start": "2026-09-15",
                "expected_harvest_end": "2026-09-30"
            }
        )
        assert res_lot.status_code == 400
    finally:
        db.close()
        app.dependency_overrides = old_overrides


def test_19_recommendation_must_belong_to_selected_farm():
    _, farm_id1, token1 = _create_farmer_and_farm("f19a")
    _, farm_id2, _ = _create_farmer_and_farm("f19b")
    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    db = SessionLocal()
    try:
        rec2 = Recommendation(
            farm_id=farm_id2,
            recommended_crop_id=1,
            decision="SWITCH"
        )
        db.add(rec2)
        db.commit()
        db.refresh(rec2)

        res_lot = client.post(
            "/api/v1/farmer/future-crop-lots",
            headers={"Authorization": f"Bearer {token1}"},
            json={
                "farm_id": farm_id1,
                "crop_id": 1,
                "recommendation_id": rec2.id,
                "planned_acres": 2.0,
                "expected_quantity_quintals": 40.0,
                "planned_sowing_date": "2026-06-01",
                "expected_harvest_start": "2026-09-15",
                "expected_harvest_end": "2026-09-30"
            }
        )
        assert res_lot.status_code == 400
    finally:
        db.close()
        app.dependency_overrides = old_overrides


def test_20_invalid_quantity_rejected():
    _, farm_id, token = _create_farmer_and_farm("f20")
    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        res = client.post(
            "/api/v1/farmer/future-crop-lots",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "farm_id": farm_id,
                "crop_id": 1,
                "planned_acres": 2.0,
                "expected_quantity_quintals": -50.0,
                "planned_sowing_date": "2026-06-01",
                "expected_harvest_start": "2026-09-15",
                "expected_harvest_end": "2026-09-30"
            }
        )
        assert res.status_code == 422
    finally:
        app.dependency_overrides = old_overrides


def test_21_invalid_acres_rejected():
    _, farm_id, token = _create_farmer_and_farm("f21")
    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        res = client.post(
            "/api/v1/farmer/future-crop-lots",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "farm_id": farm_id,
                "crop_id": 1,
                "planned_acres": 0.0,
                "expected_quantity_quintals": 40.0,
                "planned_sowing_date": "2026-06-01",
                "expected_harvest_start": "2026-09-15",
                "expected_harvest_end": "2026-09-30"
            }
        )
        assert res.status_code == 422
    finally:
        app.dependency_overrides = old_overrides


def test_22_invalid_price_rejected():
    _, farm_id, token = _create_farmer_and_farm("f22")
    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        res = client.post(
            "/api/v1/farmer/future-crop-lots",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "farm_id": farm_id,
                "crop_id": 1,
                "planned_acres": 2.0,
                "expected_quantity_quintals": 40.0,
                "asking_price_per_quintal": -100.0,
                "planned_sowing_date": "2026-06-01",
                "expected_harvest_start": "2026-09-15",
                "expected_harvest_end": "2026-09-30"
            }
        )
        assert res.status_code == 422
    finally:
        app.dependency_overrides = old_overrides


def test_23_invalid_harvest_date_range_rejected():
    _, farm_id, token = _create_farmer_and_farm("f23")
    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        res = client.post(
            "/api/v1/farmer/future-crop-lots",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "farm_id": farm_id,
                "crop_id": 1,
                "planned_acres": 2.0,
                "expected_quantity_quintals": 40.0,
                "planned_sowing_date": "2026-06-01",
                "expected_harvest_start": "2026-09-30",
                "expected_harvest_end": "2026-09-01"
            }
        )
        assert res.status_code == 422
    finally:
        app.dependency_overrides = old_overrides


def test_24_open_discovery_excludes_draft():
    _, farm_id, token_farmer = _create_farmer_and_farm("f24")
    _, token_buyer = _create_buyer("b24")
    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        res_create = client.post(
            "/api/v1/farmer/future-crop-lots",
            headers={"Authorization": f"Bearer {token_farmer}"},
            json={
                "farm_id": farm_id,
                "crop_id": 1,
                "status": "DRAFT",
                "planned_acres": 2.0,
                "expected_quantity_quintals": 40.0,
                "planned_sowing_date": "2026-06-01",
                "expected_harvest_start": "2026-09-15",
                "expected_harvest_end": "2026-09-30"
            }
        )
        lot_id = res_create.json()["id"]

        res_disc = client.get("/api/v1/future-crop-lots/open", headers={"Authorization": f"Bearer {token_buyer}"})
        assert res_disc.status_code == 200
        assert not any(l["id"] == lot_id for l in res_disc.json())
    finally:
        app.dependency_overrides = old_overrides


def test_25_open_discovery_excludes_cancelled():
    _, farm_id, token_farmer = _create_farmer_and_farm("f25")
    _, token_buyer = _create_buyer("b25")
    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        res_create = client.post(
            "/api/v1/farmer/future-crop-lots",
            headers={"Authorization": f"Bearer {token_farmer}"},
            json={
                "farm_id": farm_id,
                "crop_id": 1,
                "status": "OPEN",
                "planned_acres": 2.0,
                "expected_quantity_quintals": 40.0,
                "planned_sowing_date": "2026-06-01",
                "expected_harvest_start": "2026-09-15",
                "expected_harvest_end": "2026-09-30"
            }
        )
        lot_id = res_create.json()["id"]

        client.delete(f"/api/v1/farmer/future-crop-lots/{lot_id}", headers={"Authorization": f"Bearer {token_farmer}"})

        res_disc = client.get("/api/v1/future-crop-lots/open", headers={"Authorization": f"Bearer {token_buyer}"})
        assert res_disc.status_code == 200
        assert not any(l["id"] == lot_id for l in res_disc.json())
    finally:
        app.dependency_overrides = old_overrides


def test_26_open_discovery_excludes_expired():
    farmer_id, farm_id, token_farmer = _create_farmer_and_farm("f26")
    _, token_buyer = _create_buyer("b26")
    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    db = SessionLocal()
    try:
        lot = FutureCropLot(
            farm_id=farm_id,
            farmer_id=farmer_id,
            crop_id=1,
            planned_acres=2.0,
            expected_quantity_quintals=40.0,
            planned_sowing_date=date(2026, 6, 1),
            expected_harvest_start=date(2026, 9, 15),
            expected_harvest_end=date(2026, 9, 30),
            status=FutureCropLotStatus.EXPIRED
        )
        db.add(lot)
        db.commit()

        res_disc = client.get("/api/v1/future-crop-lots/open", headers={"Authorization": f"Bearer {token_buyer}"})
        assert res_disc.status_code == 200
        assert not any(l["id"] == lot.id for l in res_disc.json())
    finally:
        db.close()
        app.dependency_overrides = old_overrides


def test_27_buyer_can_access_open_marketplace_endpoint():
    _, farm_id, token_farmer = _create_farmer_and_farm("f27")
    _, token_buyer = _create_buyer("b27")
    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        client.post(
            "/api/v1/farmer/future-crop-lots",
            headers={"Authorization": f"Bearer {token_farmer}"},
            json={
                "farm_id": farm_id,
                "crop_id": 1,
                "status": "OPEN",
                "planned_acres": 2.0,
                "expected_quantity_quintals": 40.0,
                "planned_sowing_date": "2026-06-01",
                "expected_harvest_start": "2026-09-15",
                "expected_harvest_end": "2026-09-30"
            }
        )

        res = client.get("/api/v1/future-crop-lots/open", headers={"Authorization": f"Bearer {token_buyer}"})
        assert res.status_code == 200
        assert len(res.json()) >= 1
    finally:
        app.dependency_overrides = old_overrides


def test_28_buyer_cannot_modify_future_crop_lot():
    _, farm_id, token_farmer = _create_farmer_and_farm("f28")
    _, token_buyer = _create_buyer("b28")
    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        res_create = client.post(
            "/api/v1/farmer/future-crop-lots",
            headers={"Authorization": f"Bearer {token_farmer}"},
            json={
                "farm_id": farm_id,
                "crop_id": 1,
                "status": "OPEN",
                "planned_acres": 2.0,
                "expected_quantity_quintals": 40.0,
                "planned_sowing_date": "2026-06-01",
                "expected_harvest_start": "2026-09-15",
                "expected_harvest_end": "2026-09-30"
            }
        )
        lot_id = res_create.json()["id"]

        # Buyer tries to update -> 403 Forbidden
        res_up = client.put(
            f"/api/v1/farmer/future-crop-lots/{lot_id}",
            headers={"Authorization": f"Bearer {token_buyer}"},
            json={"planned_acres": 10.0}
        )
        assert res_up.status_code == 403
    finally:
        app.dependency_overrides = old_overrides


def test_29_district_filtering_works_on_discovery():
    _, farm_id, token_farmer = _create_farmer_and_farm("f29")
    _, token_buyer = _create_buyer("b29")
    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        client.post(
            "/api/v1/farmer/future-crop-lots",
            headers={"Authorization": f"Bearer {token_farmer}"},
            json={
                "farm_id": farm_id,
                "crop_id": 1,
                "status": "OPEN",
                "planned_acres": 2.0,
                "expected_quantity_quintals": 40.0,
                "planned_sowing_date": "2026-06-01",
                "expected_harvest_start": "2026-09-15",
                "expected_harvest_end": "2026-09-30"
            }
        )

        res = client.get("/api/v1/future-crop-lots/open?district=Dharwad", headers={"Authorization": f"Bearer {token_buyer}"})
        assert res.status_code == 200
        assert len(res.json()) >= 1
        assert res.json()[0]["district"] == "Dharwad"
    finally:
        app.dependency_overrides = old_overrides


def test_30_crop_filtering_works_on_discovery():
    _, farm_id, token_farmer = _create_farmer_and_farm("f30")
    _, token_buyer = _create_buyer("b30")
    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        client.post(
            "/api/v1/farmer/future-crop-lots",
            headers={"Authorization": f"Bearer {token_farmer}"},
            json={
                "farm_id": farm_id,
                "crop_id": 1,
                "status": "OPEN",
                "planned_acres": 2.0,
                "expected_quantity_quintals": 40.0,
                "planned_sowing_date": "2026-06-01",
                "expected_harvest_start": "2026-09-15",
                "expected_harvest_end": "2026-09-30"
            }
        )

        res = client.get("/api/v1/future-crop-lots/open?crop_id=1", headers={"Authorization": f"Bearer {token_buyer}"})
        assert res.status_code == 200
        assert len(res.json()) >= 1
        assert res.json()[0]["crop_id"] == 1
    finally:
        app.dependency_overrides = old_overrides
