"""Automated test suite for Pre-Sowing Indicative Bidding endpoints and security authorization."""
import uuid
import pytest
from datetime import date
from fastapi.testclient import TestClient

from app.main import app
from app.models.user import User, UserRole
from app.models.farmer import Farmer
from app.models.farm import Farm
from app.models.crop import Crop, CropType
from app.models.market import Market
from app.models.future_crop_lot import FutureCropLot, FutureCropLotStatus
from app.models.bid import Bid, BidStatus
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


def _create_open_lot(farmer_token, farm_id, expected_qty=100.0):
    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        res = client.post(
            "/api/v1/farmer/future-crop-lots",
            headers={"Authorization": f"Bearer {farmer_token}"},
            json={
                "farm_id": farm_id,
                "crop_id": 1,
                "status": "OPEN",
                "planned_acres": 5.0,
                "expected_quantity_quintals": expected_qty,
                "asking_price_per_quintal": 6200.0,
                "planned_sowing_date": "2026-06-01",
                "expected_harvest_start": "2026-09-15",
                "expected_harvest_end": "2026-09-30"
            }
        )
        assert res.status_code == 201
        return res.json()["id"]
    finally:
        app.dependency_overrides = old_overrides


def test_1_buyer_can_create_bid():
    _, farm_id, token_farmer = _create_farmer_and_farm("f1")
    buyer_id, token_buyer = _create_buyer("b1")
    lot_id = _create_open_lot(token_farmer, farm_id)

    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        res = client.post(
            "/api/v1/bids",
            headers={"Authorization": f"Bearer {token_buyer}"},
            json={
                "future_crop_lot_id": lot_id,
                "offered_price_per_quintal": 6500.0,
                "quantity_quintals": 50.0,
                "conditions": "Moisture < 8%"
            }
        )
        assert res.status_code == 201
        data = res.json()
        assert data["buyer_id"] == buyer_id
        assert data["status"] == "SUBMITTED"
        assert data["offered_price_per_quintal"] == 6500.0
    finally:
        app.dependency_overrides = old_overrides


def test_2_farmer_cannot_create_bid():
    _, farm_id, token_farmer = _create_farmer_and_farm("f2")
    lot_id = _create_open_lot(token_farmer, farm_id)

    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        res = client.post(
            "/api/v1/bids",
            headers={"Authorization": f"Bearer {token_farmer}"},
            json={
                "future_crop_lot_id": lot_id,
                "offered_price_per_quintal": 6500.0,
                "quantity_quintals": 50.0
            }
        )
        assert res.status_code == 403
    finally:
        app.dependency_overrides = old_overrides


def test_3_unauthenticated_cannot_create_bid():
    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        res = client.post(
            "/api/v1/bids",
            json={
                "future_crop_lot_id": 1,
                "offered_price_per_quintal": 6500.0,
                "quantity_quintals": 50.0
            }
        )
        assert res.status_code == 401
    finally:
        app.dependency_overrides = old_overrides


def test_4_client_buyer_id_cannot_impersonate_another_buyer():
    buyer_id, token_buyer = _create_buyer("b4")
    _, farm_id, token_farmer = _create_farmer_and_farm("f4")
    lot_id = _create_open_lot(token_farmer, farm_id)

    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        res = client.post(
            "/api/v1/bids",
            headers={"Authorization": f"Bearer {token_buyer}"},
            json={
                "buyer_id": 999999,
                "future_crop_lot_id": lot_id,
                "offered_price_per_quintal": 6500.0,
                "quantity_quintals": 50.0
            }
        )
        assert res.status_code == 201
        assert res.json()["buyer_id"] == buyer_id
    finally:
        app.dependency_overrides = old_overrides


def test_5_invalid_future_crop_lot_rejected():
    _, token_buyer = _create_buyer("b5")

    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        res = client.post(
            "/api/v1/bids",
            headers={"Authorization": f"Bearer {token_buyer}"},
            json={
                "future_crop_lot_id": 999999,
                "offered_price_per_quintal": 6500.0,
                "quantity_quintals": 50.0
            }
        )
        assert res.status_code == 404
    finally:
        app.dependency_overrides = old_overrides


def test_6_draft_lot_rejects_bid():
    _, farm_id, token_farmer = _create_farmer_and_farm("f6")
    _, token_buyer = _create_buyer("b6")

    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        res_lot = client.post(
            "/api/v1/farmer/future-crop-lots",
            headers={"Authorization": f"Bearer {token_farmer}"},
            json={
                "farm_id": farm_id,
                "crop_id": 1,
                "status": "DRAFT",
                "planned_acres": 5.0,
                "expected_quantity_quintals": 100.0,
                "planned_sowing_date": "2026-06-01",
                "expected_harvest_start": "2026-09-15",
                "expected_harvest_end": "2026-09-30"
            }
        )
        lot_id = res_lot.json()["id"]

        res_bid = client.post(
            "/api/v1/bids",
            headers={"Authorization": f"Bearer {token_buyer}"},
            json={"future_crop_lot_id": lot_id, "offered_price_per_quintal": 6500.0, "quantity_quintals": 50.0}
        )
        assert res_bid.status_code == 400
    finally:
        app.dependency_overrides = old_overrides


def test_7_cancelled_lot_rejects_bid():
    _, farm_id, token_farmer = _create_farmer_and_farm("f7")
    _, token_buyer = _create_buyer("b7")
    lot_id = _create_open_lot(token_farmer, farm_id)

    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        client.delete(f"/api/v1/farmer/future-crop-lots/{lot_id}", headers={"Authorization": f"Bearer {token_farmer}"})

        res_bid = client.post(
            "/api/v1/bids",
            headers={"Authorization": f"Bearer {token_buyer}"},
            json={"future_crop_lot_id": lot_id, "offered_price_per_quintal": 6500.0, "quantity_quintals": 50.0}
        )
        assert res_bid.status_code == 400
    finally:
        app.dependency_overrides = old_overrides


def test_8_harvested_lot_rejects_bid():
    farmer_id, farm_id, token_farmer = _create_farmer_and_farm("f8")
    _, token_buyer = _create_buyer("b8")

    db = SessionLocal()
    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        lot = FutureCropLot(
            farm_id=farm_id,
            farmer_id=farmer_id,
            crop_id=1,
            planned_acres=5.0,
            expected_quantity_quintals=100.0,
            planned_sowing_date=date(2026, 6, 1),
            expected_harvest_start=date(2026, 9, 15),
            expected_harvest_end=date(2026, 9, 30),
            status=FutureCropLotStatus.HARVESTED
        )
        db.add(lot)
        db.commit()
        db.refresh(lot)

        res_bid = client.post(
            "/api/v1/bids",
            headers={"Authorization": f"Bearer {token_buyer}"},
            json={"future_crop_lot_id": lot.id, "offered_price_per_quintal": 6500.0, "quantity_quintals": 50.0}
        )
        assert res_bid.status_code == 400
    finally:
        db.close()
        app.dependency_overrides = old_overrides


def test_9_expired_lot_rejects_bid():
    farmer_id, farm_id, token_farmer = _create_farmer_and_farm("f9")
    _, token_buyer = _create_buyer("b9")

    db = SessionLocal()
    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        lot = FutureCropLot(
            farm_id=farm_id,
            farmer_id=farmer_id,
            crop_id=1,
            planned_acres=5.0,
            expected_quantity_quintals=100.0,
            planned_sowing_date=date(2026, 6, 1),
            expected_harvest_start=date(2026, 9, 15),
            expected_harvest_end=date(2026, 9, 30),
            status=FutureCropLotStatus.EXPIRED
        )
        db.add(lot)
        db.commit()
        db.refresh(lot)

        res_bid = client.post(
            "/api/v1/bids",
            headers={"Authorization": f"Bearer {token_buyer}"},
            json={"future_crop_lot_id": lot.id, "offered_price_per_quintal": 6500.0, "quantity_quintals": 50.0}
        )
        assert res_bid.status_code == 400
    finally:
        db.close()
        app.dependency_overrides = old_overrides


def test_10_indicative_accepted_lot_rejects_bid():
    farmer_id, farm_id, token_farmer = _create_farmer_and_farm("f10")
    _, token_buyer = _create_buyer("b10")

    db = SessionLocal()
    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        lot = FutureCropLot(
            farm_id=farm_id,
            farmer_id=farmer_id,
            crop_id=1,
            planned_acres=5.0,
            expected_quantity_quintals=100.0,
            planned_sowing_date=date(2026, 6, 1),
            expected_harvest_start=date(2026, 9, 15),
            expected_harvest_end=date(2026, 9, 30),
            status=FutureCropLotStatus.INDICATIVE_ACCEPTED
        )
        db.add(lot)
        db.commit()
        db.refresh(lot)

        res_bid = client.post(
            "/api/v1/bids",
            headers={"Authorization": f"Bearer {token_buyer}"},
            json={"future_crop_lot_id": lot.id, "offered_price_per_quintal": 6500.0, "quantity_quintals": 50.0}
        )
        assert res_bid.status_code == 400
    finally:
        db.close()
        app.dependency_overrides = old_overrides


def test_11_positive_quantity_succeeds():
    _, farm_id, token_farmer = _create_farmer_and_farm("f11")
    _, token_buyer = _create_buyer("b11")
    lot_id = _create_open_lot(token_farmer, farm_id)

    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        res = client.post(
            "/api/v1/bids",
            headers={"Authorization": f"Bearer {token_buyer}"},
            json={"future_crop_lot_id": lot_id, "offered_price_per_quintal": 6500.0, "quantity_quintals": 10.0}
        )
        assert res.status_code == 201
        assert res.json()["quantity_quintals"] == 10.0
    finally:
        app.dependency_overrides = old_overrides


def test_12_zero_quantity_rejected():
    _, farm_id, token_farmer = _create_farmer_and_farm("f12")
    _, token_buyer = _create_buyer("b12")
    lot_id = _create_open_lot(token_farmer, farm_id)

    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        res = client.post(
            "/api/v1/bids",
            headers={"Authorization": f"Bearer {token_buyer}"},
            json={"future_crop_lot_id": lot_id, "offered_price_per_quintal": 6500.0, "quantity_quintals": 0.0}
        )
        assert res.status_code == 422
    finally:
        app.dependency_overrides = old_overrides


def test_13_negative_quantity_rejected():
    _, farm_id, token_farmer = _create_farmer_and_farm("f13")
    _, token_buyer = _create_buyer("b13")
    lot_id = _create_open_lot(token_farmer, farm_id)

    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        res = client.post(
            "/api/v1/bids",
            headers={"Authorization": f"Bearer {token_buyer}"},
            json={"future_crop_lot_id": lot_id, "offered_price_per_quintal": 6500.0, "quantity_quintals": -20.0}
        )
        assert res.status_code == 422
    finally:
        app.dependency_overrides = old_overrides


def test_14_quantity_greater_than_lot_expected_quantity_rejected():
    _, farm_id, token_farmer = _create_farmer_and_farm("f14")
    _, token_buyer = _create_buyer("b14")
    lot_id = _create_open_lot(token_farmer, farm_id, expected_qty=100.0)

    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        res = client.post(
            "/api/v1/bids",
            headers={"Authorization": f"Bearer {token_buyer}"},
            json={"future_crop_lot_id": lot_id, "offered_price_per_quintal": 6500.0, "quantity_quintals": 150.0}
        )
        assert res.status_code == 400
    finally:
        app.dependency_overrides = old_overrides


def test_15_partial_quantity_accepted():
    _, farm_id, token_farmer = _create_farmer_and_farm("f15")
    _, token_buyer = _create_buyer("b15")
    lot_id = _create_open_lot(token_farmer, farm_id, expected_qty=100.0)

    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        res = client.post(
            "/api/v1/bids",
            headers={"Authorization": f"Bearer {token_buyer}"},
            json={"future_crop_lot_id": lot_id, "offered_price_per_quintal": 6500.0, "quantity_quintals": 60.0}
        )
        assert res.status_code == 201
        assert res.json()["quantity_quintals"] == 60.0
    finally:
        app.dependency_overrides = old_overrides


def test_16_positive_price_succeeds():
    _, farm_id, token_farmer = _create_farmer_and_farm("f16")
    _, token_buyer = _create_buyer("b16")
    lot_id = _create_open_lot(token_farmer, farm_id)

    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        res = client.post(
            "/api/v1/bids",
            headers={"Authorization": f"Bearer {token_buyer}"},
            json={"future_crop_lot_id": lot_id, "offered_price_per_quintal": 7000.0, "quantity_quintals": 50.0}
        )
        assert res.status_code == 201
        assert res.json()["offered_price_per_quintal"] == 7000.0
    finally:
        app.dependency_overrides = old_overrides


def test_17_zero_price_rejected():
    _, farm_id, token_farmer = _create_farmer_and_farm("f17")
    _, token_buyer = _create_buyer("b17")
    lot_id = _create_open_lot(token_farmer, farm_id)

    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        res = client.post(
            "/api/v1/bids",
            headers={"Authorization": f"Bearer {token_buyer}"},
            json={"future_crop_lot_id": lot_id, "offered_price_per_quintal": 0.0, "quantity_quintals": 50.0}
        )
        assert res.status_code == 422
    finally:
        app.dependency_overrides = old_overrides


def test_18_negative_price_rejected():
    _, farm_id, token_farmer = _create_farmer_and_farm("f18")
    _, token_buyer = _create_buyer("b18")
    lot_id = _create_open_lot(token_farmer, farm_id)

    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        res = client.post(
            "/api/v1/bids",
            headers={"Authorization": f"Bearer {token_buyer}"},
            json={"future_crop_lot_id": lot_id, "offered_price_per_quintal": -100.0, "quantity_quintals": 50.0}
        )
        assert res.status_code == 422
    finally:
        app.dependency_overrides = old_overrides


def test_19_buyer_sees_only_own_bids():
    buyer_id1, token_buyer1 = _create_buyer("b19a")
    _, token_buyer2 = _create_buyer("b19b")
    _, farm_id, token_farmer = _create_farmer_and_farm("f19")
    lot_id = _create_open_lot(token_farmer, farm_id)

    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        client.post(
            "/api/v1/bids",
            headers={"Authorization": f"Bearer {token_buyer1}"},
            json={"future_crop_lot_id": lot_id, "offered_price_per_quintal": 6400.0, "quantity_quintals": 50.0}
        )

        res1 = client.get("/api/v1/bids/me", headers={"Authorization": f"Bearer {token_buyer1}"})
        assert res1.status_code == 200
        assert len(res1.json()) >= 1
        assert all(b["buyer_id"] == buyer_id1 for b in res1.json())

        res2 = client.get("/api/v1/bids/me", headers={"Authorization": f"Bearer {token_buyer2}"})
        assert res2.status_code == 200
        assert not any(b["buyer_id"] == buyer_id1 for b in res2.json())
    finally:
        app.dependency_overrides = old_overrides


def test_20_buyer_cannot_withdraw_another_buyers_bid():
    _, token_buyer1 = _create_buyer("b20a")
    _, token_buyer2 = _create_buyer("b20b")
    _, farm_id, token_farmer = _create_farmer_and_farm("f20")
    lot_id = _create_open_lot(token_farmer, farm_id)

    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        res_create = client.post(
            "/api/v1/bids",
            headers={"Authorization": f"Bearer {token_buyer1}"},
            json={"future_crop_lot_id": lot_id, "offered_price_per_quintal": 6400.0, "quantity_quintals": 50.0}
        )
        bid_id = res_create.json()["id"]

        res_withdraw = client.post(f"/api/v1/bids/{bid_id}/withdraw", headers={"Authorization": f"Bearer {token_buyer2}"})
        assert res_withdraw.status_code == 403
    finally:
        app.dependency_overrides = old_overrides


def test_21_farmer_can_see_bids_on_own_lot():
    _, farm_id, token_farmer = _create_farmer_and_farm("f21")
    _, token_buyer = _create_buyer("b21")
    lot_id = _create_open_lot(token_farmer, farm_id)

    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        client.post(
            "/api/v1/bids",
            headers={"Authorization": f"Bearer {token_buyer}"},
            json={"future_crop_lot_id": lot_id, "offered_price_per_quintal": 6400.0, "quantity_quintals": 50.0}
        )

        res = client.get(f"/api/v1/farmer/future-crop-lots/{lot_id}/bids", headers={"Authorization": f"Bearer {token_farmer}"})
        assert res.status_code == 200
        assert len(res.json()) == 1
    finally:
        app.dependency_overrides = old_overrides


def test_22_farmer_cannot_see_bids_on_another_farmers_lot():
    _, farm_id1, token_farmer1 = _create_farmer_and_farm("f22a")
    _, _, token_farmer2 = _create_farmer_and_farm("f22b")
    _, token_buyer = _create_buyer("b22")
    lot_id = _create_open_lot(token_farmer1, farm_id1)

    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        client.post(
            "/api/v1/bids",
            headers={"Authorization": f"Bearer {token_buyer}"},
            json={"future_crop_lot_id": lot_id, "offered_price_per_quintal": 6400.0, "quantity_quintals": 50.0}
        )

        res = client.get(f"/api/v1/farmer/future-crop-lots/{lot_id}/bids", headers={"Authorization": f"Bearer {token_farmer2}"})
        assert res.status_code == 403
    finally:
        app.dependency_overrides = old_overrides


def test_23_submitted_bid_can_be_withdrawn():
    _, token_buyer = _create_buyer("b23")
    _, farm_id, token_farmer = _create_farmer_and_farm("f23")
    lot_id = _create_open_lot(token_farmer, farm_id)

    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        res_create = client.post(
            "/api/v1/bids",
            headers={"Authorization": f"Bearer {token_buyer}"},
            json={"future_crop_lot_id": lot_id, "offered_price_per_quintal": 6400.0, "quantity_quintals": 50.0}
        )
        bid_id = res_create.json()["id"]

        res_withdraw = client.post(f"/api/v1/bids/{bid_id}/withdraw", headers={"Authorization": f"Bearer {token_buyer}"})
        assert res_withdraw.status_code == 200
        assert res_withdraw.json()["status"] == "WITHDRAWN"
    finally:
        app.dependency_overrides = old_overrides


def test_24_accepted_bid_cannot_be_withdrawn():
    _, token_buyer = _create_buyer("b24")
    _, farm_id, token_farmer = _create_farmer_and_farm("f24")
    lot_id = _create_open_lot(token_farmer, farm_id)

    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        res_create = client.post(
            "/api/v1/bids",
            headers={"Authorization": f"Bearer {token_buyer}"},
            json={"future_crop_lot_id": lot_id, "offered_price_per_quintal": 6400.0, "quantity_quintals": 50.0}
        )
        bid_id = res_create.json()["id"]

        # Farmer accepts
        client.post(f"/api/v1/bids/{bid_id}/accept", headers={"Authorization": f"Bearer {token_farmer}"})

        # Buyer attempts withdrawal -> 400
        res_withdraw = client.post(f"/api/v1/bids/{bid_id}/withdraw", headers={"Authorization": f"Bearer {token_buyer}"})
        assert res_withdraw.status_code == 400
    finally:
        app.dependency_overrides = old_overrides


def test_25_rejected_bid_cannot_be_withdrawn():
    _, token_buyer1 = _create_buyer("b25a")
    _, token_buyer2 = _create_buyer("b25b")
    _, farm_id, token_farmer = _create_farmer_and_farm("f25")
    lot_id = _create_open_lot(token_farmer, farm_id)

    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        res1 = client.post("/api/v1/bids", headers={"Authorization": f"Bearer {token_buyer1}"}, json={"future_crop_lot_id": lot_id, "offered_price_per_quintal": 6400.0, "quantity_quintals": 50.0})
        res2 = client.post("/api/v1/bids", headers={"Authorization": f"Bearer {token_buyer2}"}, json={"future_crop_lot_id": lot_id, "offered_price_per_quintal": 6500.0, "quantity_quintals": 50.0})
        bid_id1 = res1.json()["id"]
        bid_id2 = res2.json()["id"]

        # Accept bid2 -> bid1 becomes REJECTED
        client.post(f"/api/v1/bids/{bid_id2}/accept", headers={"Authorization": f"Bearer {token_farmer}"})

        # Buyer 1 tries to withdraw rejected bid -> 400
        res_w = client.post(f"/api/v1/bids/{bid_id1}/withdraw", headers={"Authorization": f"Bearer {token_buyer1}"})
        assert res_w.status_code == 400
    finally:
        app.dependency_overrides = old_overrides


def test_26_withdrawn_bid_cannot_be_withdrawn_again():
    _, token_buyer = _create_buyer("b26")
    _, farm_id, token_farmer = _create_farmer_and_farm("f26")
    lot_id = _create_open_lot(token_farmer, farm_id)

    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        res_create = client.post("/api/v1/bids", headers={"Authorization": f"Bearer {token_buyer}"}, json={"future_crop_lot_id": lot_id, "offered_price_per_quintal": 6400.0, "quantity_quintals": 50.0})
        bid_id = res_create.json()["id"]

        client.post(f"/api/v1/bids/{bid_id}/withdraw", headers={"Authorization": f"Bearer {token_buyer}"})

        # Second withdrawal -> 400
        res_w2 = client.post(f"/api/v1/bids/{bid_id}/withdraw", headers={"Authorization": f"Bearer {token_buyer}"})
        assert res_w2.status_code == 400
    finally:
        app.dependency_overrides = old_overrides


def test_27_farmer_can_accept_submitted_bid():
    _, token_buyer = _create_buyer("b27")
    _, farm_id, token_farmer = _create_farmer_and_farm("f27")
    lot_id = _create_open_lot(token_farmer, farm_id)

    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        res_create = client.post("/api/v1/bids", headers={"Authorization": f"Bearer {token_buyer}"}, json={"future_crop_lot_id": lot_id, "offered_price_per_quintal": 6400.0, "quantity_quintals": 50.0})
        bid_id = res_create.json()["id"]

        res_accept = client.post(f"/api/v1/bids/{bid_id}/accept", headers={"Authorization": f"Bearer {token_farmer}"})
        assert res_accept.status_code == 200
        assert res_accept.json()["status"] == "ACCEPTED"
    finally:
        app.dependency_overrides = old_overrides


def test_28_accepted_bid_changes_lot_to_indicative_accepted():
    _, token_buyer = _create_buyer("b28")
    _, farm_id, token_farmer = _create_farmer_and_farm("f28")
    lot_id = _create_open_lot(token_farmer, farm_id)

    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        res_create = client.post("/api/v1/bids", headers={"Authorization": f"Bearer {token_buyer}"}, json={"future_crop_lot_id": lot_id, "offered_price_per_quintal": 6400.0, "quantity_quintals": 50.0})
        bid_id = res_create.json()["id"]

        client.post(f"/api/v1/bids/{bid_id}/accept", headers={"Authorization": f"Bearer {token_farmer}"})

        # Query lot details
        res_lot = client.get(f"/api/v1/farmer/future-crop-lots/{lot_id}", headers={"Authorization": f"Bearer {token_farmer}"})
        assert res_lot.status_code == 200
        assert res_lot.json()["status"] == "INDICATIVE_ACCEPTED"
    finally:
        app.dependency_overrides = old_overrides


def test_29_competing_submitted_bids_become_rejected():
    _, token_buyer1 = _create_buyer("b29a")
    _, token_buyer2 = _create_buyer("b29b")
    _, farm_id, token_farmer = _create_farmer_and_farm("f29")
    lot_id = _create_open_lot(token_farmer, farm_id)

    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        res1 = client.post("/api/v1/bids", headers={"Authorization": f"Bearer {token_buyer1}"}, json={"future_crop_lot_id": lot_id, "offered_price_per_quintal": 6400.0, "quantity_quintals": 50.0})
        res2 = client.post("/api/v1/bids", headers={"Authorization": f"Bearer {token_buyer2}"}, json={"future_crop_lot_id": lot_id, "offered_price_per_quintal": 6500.0, "quantity_quintals": 50.0})
        bid_id1 = res1.json()["id"]
        bid_id2 = res2.json()["id"]

        client.post(f"/api/v1/bids/{bid_id2}/accept", headers={"Authorization": f"Bearer {token_farmer}"})

        # Query bids for lot
        res_bids = client.get(f"/api/v1/farmer/future-crop-lots/{lot_id}/bids", headers={"Authorization": f"Bearer {token_farmer}"})
        bids_by_id = {b["id"]: b["status"] for b in res_bids.json()}
        assert bids_by_id[bid_id2] == "ACCEPTED"
        assert bids_by_id[bid_id1] == "REJECTED"
    finally:
        app.dependency_overrides = old_overrides


def test_30_farmer_cannot_accept_bid_on_another_farmers_lot():
    _, farm_id1, token_farmer1 = _create_farmer_and_farm("f30a")
    _, _, token_farmer2 = _create_farmer_and_farm("f30b")
    _, token_buyer = _create_buyer("b30")
    lot_id = _create_open_lot(token_farmer1, farm_id1)

    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        res_create = client.post("/api/v1/bids", headers={"Authorization": f"Bearer {token_buyer}"}, json={"future_crop_lot_id": lot_id, "offered_price_per_quintal": 6400.0, "quantity_quintals": 50.0})
        bid_id = res_create.json()["id"]

        res_accept = client.post(f"/api/v1/bids/{bid_id}/accept", headers={"Authorization": f"Bearer {token_farmer2}"})
        assert res_accept.status_code == 403
    finally:
        app.dependency_overrides = old_overrides


def test_31_buyer_cannot_accept_bid():
    _, token_buyer = _create_buyer("b31")
    _, farm_id, token_farmer = _create_farmer_and_farm("f31")
    lot_id = _create_open_lot(token_farmer, farm_id)

    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        res_create = client.post("/api/v1/bids", headers={"Authorization": f"Bearer {token_buyer}"}, json={"future_crop_lot_id": lot_id, "offered_price_per_quintal": 6400.0, "quantity_quintals": 50.0})
        bid_id = res_create.json()["id"]

        res_accept = client.post(f"/api/v1/bids/{bid_id}/accept", headers={"Authorization": f"Bearer {token_buyer}"})
        assert res_accept.status_code == 403
    finally:
        app.dependency_overrides = old_overrides


def test_32_already_accepted_bid_cannot_be_accepted_again():
    _, token_buyer = _create_buyer("b32")
    _, farm_id, token_farmer = _create_farmer_and_farm("f32")
    lot_id = _create_open_lot(token_farmer, farm_id)

    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        res_create = client.post("/api/v1/bids", headers={"Authorization": f"Bearer {token_buyer}"}, json={"future_crop_lot_id": lot_id, "offered_price_per_quintal": 6400.0, "quantity_quintals": 50.0})
        bid_id = res_create.json()["id"]

        client.post(f"/api/v1/bids/{bid_id}/accept", headers={"Authorization": f"Bearer {token_farmer}"})

        # Second accept -> 400
        res_accept2 = client.post(f"/api/v1/bids/{bid_id}/accept", headers={"Authorization": f"Bearer {token_farmer}"})
        assert res_accept2.status_code == 400
    finally:
        app.dependency_overrides = old_overrides


def test_33_acceptance_fails_if_lot_is_no_longer_open():
    _, token_buyer1 = _create_buyer("b33a")
    _, token_buyer2 = _create_buyer("b33b")
    _, farm_id, token_farmer = _create_farmer_and_farm("f33")
    lot_id = _create_open_lot(token_farmer, farm_id)

    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        res1 = client.post("/api/v1/bids", headers={"Authorization": f"Bearer {token_buyer1}"}, json={"future_crop_lot_id": lot_id, "offered_price_per_quintal": 6400.0, "quantity_quintals": 50.0})
        res2 = client.post("/api/v1/bids", headers={"Authorization": f"Bearer {token_buyer2}"}, json={"future_crop_lot_id": lot_id, "offered_price_per_quintal": 6500.0, "quantity_quintals": 50.0})
        bid_id1 = res1.json()["id"]
        bid_id2 = res2.json()["id"]

        client.post(f"/api/v1/bids/{bid_id1}/accept", headers={"Authorization": f"Bearer {token_farmer}"})

        # Try to accept bid_id2 when lot is now INDICATIVE_ACCEPTED -> 400
        res_acc2 = client.post(f"/api/v1/bids/{bid_id2}/accept", headers={"Authorization": f"Bearer {token_farmer}"})
        assert res_acc2.status_code == 400
    finally:
        app.dependency_overrides = old_overrides


def test_34_valid_destination_calculates_effective_offer():
    db = SessionLocal()
    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        # Create market in Dharwad with location
        from geoalchemy2.shape import from_shape
        from shapely.geometry import Point
        m = Market(name="Dharwad APMC Mandi 34", district="Dharwad", state="Karnataka", location=from_shape(Point(75.0, 15.45), srid=4326))
        db.add(m)
        db.commit()

        farmer_id, farm_id, token_farmer = _create_farmer_and_farm("f34")
        # Update farm with location
        farm = db.get(Farm, farm_id)
        farm.location = from_shape(Point(75.1, 15.5), srid=4326)
        db.commit()

        _, token_buyer = _create_buyer("b34")
        lot_id = _create_open_lot(token_farmer, farm_id)

        res_bid = client.post("/api/v1/bids", headers={"Authorization": f"Bearer {token_buyer}"}, json={"future_crop_lot_id": lot_id, "offered_price_per_quintal": 6500.0, "quantity_quintals": 50.0})
        assert res_bid.status_code == 201
        data = res_bid.json()
        assert data["effective_offer_per_quintal"] is not None
        assert data["effective_offer_per_quintal"] < 6500.0
    finally:
        db.close()
        app.dependency_overrides = old_overrides


def test_35_unavailable_destination_does_not_fabricate_distance():
    _, farm_id, token_farmer = _create_farmer_and_farm("f35")
    _, token_buyer = _create_buyer("b35")
    lot_id = _create_open_lot(token_farmer, farm_id)

    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        res_bid = client.post("/api/v1/bids", headers={"Authorization": f"Bearer {token_buyer}"}, json={"future_crop_lot_id": lot_id, "offered_price_per_quintal": 6500.0, "quantity_quintals": 50.0})
        assert res_bid.status_code == 201
        data = res_bid.json()
        assert data["effective_offer_per_quintal"] is None
        assert data["effective_offer_note"] == "Destination location unavailable"
    finally:
        app.dependency_overrides = old_overrides


def test_36_effective_offer_calculation_is_correct():
    from app.services.effective_offer_service import compute_effective_offer
    from app.models.bid import Bid
    from geoalchemy2.shape import from_shape
    from shapely.geometry import Point

    db = SessionLocal()
    try:
        m = Market(name="Test Market 36", district="TestDist36", state="Karnataka", location=from_shape(Point(75.0, 15.0), srid=4326))
        db.add(m)
        db.commit()

        farmer_id, farm_id, token_farmer = _create_farmer_and_farm("f36")
        farm = db.get(Farm, farm_id)
        farm.district = "TestDist36"
        farm.location = from_shape(Point(75.0, 15.1), srid=4326) # ~11.1 km
        db.commit()

        lot_id = _create_open_lot(token_farmer, farm_id)
        bid = Bid(future_crop_lot_id=lot_id, buyer_id=1, offered_price_per_quintal=6000.0, quantity_quintals=50.0, status=BidStatus.SUBMITTED)
        db.add(bid)
        db.commit()
        db.refresh(bid)

        eff_price, note = compute_effective_offer(db, bid)
        assert eff_price is not None
        assert note is None
        assert eff_price < 6000.0
    finally:
        db.close()


def test_37_private_phone_email_fields_not_exposed():
    _, farm_id, token_farmer = _create_farmer_and_farm("f37")
    _, token_buyer = _create_buyer("b37")
    lot_id = _create_open_lot(token_farmer, farm_id)

    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        res_bid = client.post("/api/v1/bids", headers={"Authorization": f"Bearer {token_buyer}"}, json={"future_crop_lot_id": lot_id, "offered_price_per_quintal": 6500.0, "quantity_quintals": 50.0})
        data = res_bid.json()
        assert "phone" not in data
        assert "email" not in data
    finally:
        app.dependency_overrides = old_overrides


def test_38_exact_farm_coordinates_not_exposed_in_bid_responses():
    _, farm_id, token_farmer = _create_farmer_and_farm("f38")
    _, token_buyer = _create_buyer("b38")
    lot_id = _create_open_lot(token_farmer, farm_id)

    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        res_bid = client.post("/api/v1/bids", headers={"Authorization": f"Bearer {token_buyer}"}, json={"future_crop_lot_id": lot_id, "offered_price_per_quintal": 6500.0, "quantity_quintals": 50.0})
        data = res_bid.json()
        assert "latitude" not in data
        assert "longitude" not in data
        assert "location" not in data
    finally:
        app.dependency_overrides = old_overrides


def test_39_acceptance_preserves_single_accepted_bid_invariant():
    _, token_buyer1 = _create_buyer("b39a")
    _, token_buyer2 = _create_buyer("b39b")
    _, farm_id, token_farmer = _create_farmer_and_farm("f39")
    lot_id = _create_open_lot(token_farmer, farm_id)

    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    db = SessionLocal()
    try:
        res1 = client.post("/api/v1/bids", headers={"Authorization": f"Bearer {token_buyer1}"}, json={"future_crop_lot_id": lot_id, "offered_price_per_quintal": 6400.0, "quantity_quintals": 50.0})
        res2 = client.post("/api/v1/bids", headers={"Authorization": f"Bearer {token_buyer2}"}, json={"future_crop_lot_id": lot_id, "offered_price_per_quintal": 6500.0, "quantity_quintals": 50.0})
        bid_id1 = res1.json()["id"]

        client.post(f"/api/v1/bids/{bid_id1}/accept", headers={"Authorization": f"Bearer {token_farmer}"})

        accepted_bids_count = db.query(Bid).filter(Bid.future_crop_lot_id == lot_id, Bid.status == BidStatus.ACCEPTED).count()
        assert accepted_bids_count == 1
    finally:
        db.close()
        app.dependency_overrides = old_overrides


def test_40_competing_acceptance_fails_when_lot_is_accepted():
    _, token_buyer1 = _create_buyer("b40a")
    _, token_buyer2 = _create_buyer("b40b")
    _, farm_id, token_farmer = _create_farmer_and_farm("f40")
    lot_id = _create_open_lot(token_farmer, farm_id)

    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        res1 = client.post("/api/v1/bids", headers={"Authorization": f"Bearer {token_buyer1}"}, json={"future_crop_lot_id": lot_id, "offered_price_per_quintal": 6400.0, "quantity_quintals": 50.0})
        res2 = client.post("/api/v1/bids", headers={"Authorization": f"Bearer {token_buyer2}"}, json={"future_crop_lot_id": lot_id, "offered_price_per_quintal": 6500.0, "quantity_quintals": 50.0})
        bid_id1 = res1.json()["id"]
        bid_id2 = res2.json()["id"]

        # Accept first bid
        res_acc1 = client.post(f"/api/v1/bids/{bid_id1}/accept", headers={"Authorization": f"Bearer {token_farmer}"})
        assert res_acc1.status_code == 200

        # Attempt to accept second bid -> 400
        res_acc2 = client.post(f"/api/v1/bids/{bid_id2}/accept", headers={"Authorization": f"Bearer {token_farmer}"})
        assert res_acc2.status_code == 400
    finally:
        app.dependency_overrides = old_overrides
