"""Automated test suite for Buyer Demand endpoints and security authorization."""
import uuid
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.user import User, UserRole
from app.models.crop import Crop, CropType
from app.models.buyer_demand import BuyerDemand, BuyerDemandStatus
from app.api.v1.auth import get_password_hash, create_access_token
from app.database.session import SessionLocal

client = TestClient(app)


@pytest.fixture(autouse=True)
def ensure_test_crop():
    """Ensure at least one standard crop exists in test database."""
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
            db.refresh(crop)
    finally:
        db.close()


def _create_user(role: UserRole, prefix="user"):
    db = SessionLocal()
    uid = uuid.uuid4().hex[:6]
    try:
        u = User(
            username=f"{prefix}_{uid}",
            email=f"{prefix}_{uid}@example.com",
            hashed_password=get_password_hash("Secret123!"),
            role=role
        )
        db.add(u)
        db.commit()
        db.refresh(u)
        token = create_access_token(data={"sub": u.username, "user_id": u.id, "role": role.value})
        return u.id, u.username, token
    finally:
        db.close()


def test_1_buyer_can_create_demand():
    buyer_id, username, token = _create_user(UserRole.BUYER, "buyer1")
    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        res = client.post(
            "/api/v1/buyer/demands",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "crop_id": 1,
                "variety": "Kadir-6",
                "quantity_quintals": 150.0,
                "target_price_per_quintal": 6400.0,
                "delivery_district": "Dharwad",
                "quality_grade": "Grade A"
            }
        )
        assert res.status_code == 201
        data = res.json()
        assert data["buyer_id"] == buyer_id
        assert data["status"] == "ACTIVE"
        assert data["quantity_quintals"] == 150.0
    finally:
        app.dependency_overrides = old_overrides


def test_2_farmer_cannot_create_demand():
    _, _, token = _create_user(UserRole.FARMER, "farmer1")
    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        res = client.post(
            "/api/v1/buyer/demands",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "crop_id": 1,
                "quantity_quintals": 50.0,
                "target_price_per_quintal": 6000.0,
                "delivery_district": "Belagavi"
            }
        )
        assert res.status_code == 403
    finally:
        app.dependency_overrides = old_overrides


def test_3_unauthenticated_create_rejected():
    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        res = client.post(
            "/api/v1/buyer/demands",
            json={
                "crop_id": 1,
                "quantity_quintals": 50.0,
                "target_price_per_quintal": 6000.0,
                "delivery_district": "Belagavi"
            }
        )
        assert res.status_code == 401
    finally:
        app.dependency_overrides = old_overrides


def test_4_buyer_can_list_own_demands():
    buyer_id, _, token = _create_user(UserRole.BUYER, "buyer2")
    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        # Create 2 demands
        client.post(
            "/api/v1/buyer/demands",
            headers={"Authorization": f"Bearer {token}"},
            json={"crop_id": 1, "quantity_quintals": 100.0, "target_price_per_quintal": 6200.0, "delivery_district": "Dharwad"}
        )
        client.post(
            "/api/v1/buyer/demands",
            headers={"Authorization": f"Bearer {token}"},
            json={"crop_id": 1, "quantity_quintals": 200.0, "target_price_per_quintal": 6300.0, "delivery_district": "Gadag"}
        )

        res = client.get("/api/v1/buyer/demands/me", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200
        items = res.json()
        assert len(items) >= 2
        assert all(item["buyer_id"] == buyer_id for item in items)
    finally:
        app.dependency_overrides = old_overrides


def test_5_buyer_can_retrieve_own_demand():
    buyer_id, _, token = _create_user(UserRole.BUYER, "buyer3")
    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        res_create = client.post(
            "/api/v1/buyer/demands",
            headers={"Authorization": f"Bearer {token}"},
            json={"crop_id": 1, "quantity_quintals": 80.0, "target_price_per_quintal": 6100.0, "delivery_district": "Dharwad"}
        )
        demand_id = res_create.json()["id"]

        res = client.get(f"/api/v1/buyer/demands/{demand_id}", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200
        assert res.json()["id"] == demand_id
    finally:
        app.dependency_overrides = old_overrides


def test_6_buyer_can_update_own_active_demand():
    buyer_id, _, token = _create_user(UserRole.BUYER, "buyer4")
    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        res_create = client.post(
            "/api/v1/buyer/demands",
            headers={"Authorization": f"Bearer {token}"},
            json={"crop_id": 1, "quantity_quintals": 80.0, "target_price_per_quintal": 6100.0, "delivery_district": "Dharwad"}
        )
        demand_id = res_create.json()["id"]

        res_update = client.put(
            f"/api/v1/buyer/demands/{demand_id}",
            headers={"Authorization": f"Bearer {token}"},
            json={"quantity_quintals": 120.0, "target_price_per_quintal": 6250.0}
        )
        assert res_update.status_code == 200
        assert res_update.json()["quantity_quintals"] == 120.0
        assert res_update.json()["target_price_per_quintal"] == 6250.0
    finally:
        app.dependency_overrides = old_overrides


def test_7_buyer_can_cancel_own_active_demand():
    buyer_id, _, token = _create_user(UserRole.BUYER, "buyer5")
    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        res_create = client.post(
            "/api/v1/buyer/demands",
            headers={"Authorization": f"Bearer {token}"},
            json={"crop_id": 1, "quantity_quintals": 80.0, "target_price_per_quintal": 6100.0, "delivery_district": "Dharwad"}
        )
        demand_id = res_create.json()["id"]

        res_del = client.delete(f"/api/v1/buyer/demands/{demand_id}", headers={"Authorization": f"Bearer {token}"})
        assert res_del.status_code == 200
        assert res_del.json()["status"] == "CANCELLED"
    finally:
        app.dependency_overrides = old_overrides


def test_8_buyer_cannot_update_another_buyers_demand():
    _, _, token1 = _create_user(UserRole.BUYER, "buyer6a")
    _, _, token2 = _create_user(UserRole.BUYER, "buyer6b")
    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        res_create = client.post(
            "/api/v1/buyer/demands",
            headers={"Authorization": f"Bearer {token1}"},
            json={"crop_id": 1, "quantity_quintals": 80.0, "target_price_per_quintal": 6100.0, "delivery_district": "Dharwad"}
        )
        demand_id = res_create.json()["id"]

        # Buyer 2 tries to update Buyer 1's demand -> 403 Forbidden
        res_update = client.put(
            f"/api/v1/buyer/demands/{demand_id}",
            headers={"Authorization": f"Bearer {token2}"},
            json={"quantity_quintals": 999.0}
        )
        assert res_update.status_code == 403
    finally:
        app.dependency_overrides = old_overrides


def test_9_buyer_cannot_cancel_another_buyers_demand():
    _, _, token1 = _create_user(UserRole.BUYER, "buyer7a")
    _, _, token2 = _create_user(UserRole.BUYER, "buyer7b")
    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        res_create = client.post(
            "/api/v1/buyer/demands",
            headers={"Authorization": f"Bearer {token1}"},
            json={"crop_id": 1, "quantity_quintals": 80.0, "target_price_per_quintal": 6100.0, "delivery_district": "Dharwad"}
        )
        demand_id = res_create.json()["id"]

        # Buyer 2 tries to cancel Buyer 1's demand -> 403 Forbidden
        res_cancel = client.delete(f"/api/v1/buyer/demands/{demand_id}", headers={"Authorization": f"Bearer {token2}"})
        assert res_cancel.status_code == 403
    finally:
        app.dependency_overrides = old_overrides


def test_10_farmer_can_discover_active_demands():
    _, _, token_buyer = _create_user(UserRole.BUYER, "buyer8")
    _, _, token_farmer = _create_user(UserRole.FARMER, "farmer8")
    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        client.post(
            "/api/v1/buyer/demands",
            headers={"Authorization": f"Bearer {token_buyer}"},
            json={"crop_id": 1, "quantity_quintals": 100.0, "target_price_per_quintal": 6500.0, "delivery_district": "Haveri"}
        )

        res = client.get("/api/v1/demands/active", headers={"Authorization": f"Bearer {token_farmer}"})
        assert res.status_code == 200
        demands = res.json()
        assert len(demands) >= 1
        assert any(d["delivery_district"] == "Haveri" for d in demands)
    finally:
        app.dependency_overrides = old_overrides


def test_11_cancelled_demand_hidden_from_active_discovery():
    _, _, token_buyer = _create_user(UserRole.BUYER, "buyer9")
    _, _, token_farmer = _create_user(UserRole.FARMER, "farmer9")
    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        res_create = client.post(
            "/api/v1/buyer/demands",
            headers={"Authorization": f"Bearer {token_buyer}"},
            json={"crop_id": 1, "quantity_quintals": 100.0, "target_price_per_quintal": 6500.0, "delivery_district": "UniqueCancelDist"}
        )
        demand_id = res_create.json()["id"]

        # Cancel it
        client.delete(f"/api/v1/buyer/demands/{demand_id}", headers={"Authorization": f"Bearer {token_buyer}"})

        # Farmer active discovery should not include the cancelled demand
        res = client.get("/api/v1/demands/active", headers={"Authorization": f"Bearer {token_farmer}"})
        assert res.status_code == 200
        demands = res.json()
        assert not any(d["id"] == demand_id for d in demands)
    finally:
        app.dependency_overrides = old_overrides


def test_12_fulfilled_demand_hidden_from_active_discovery():
    _, _, token_buyer = _create_user(UserRole.BUYER, "buyer10")
    _, _, token_farmer = _create_user(UserRole.FARMER, "farmer10")
    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        res_create = client.post(
            "/api/v1/buyer/demands",
            headers={"Authorization": f"Bearer {token_buyer}"},
            json={"crop_id": 1, "quantity_quintals": 100.0, "target_price_per_quintal": 6500.0, "delivery_district": "UniqueFulfilledDist"}
        )
        demand_id = res_create.json()["id"]

        # Update status to FULFILLED
        client.put(
            f"/api/v1/buyer/demands/{demand_id}",
            headers={"Authorization": f"Bearer {token_buyer}"},
            json={"status": "FULFILLED"}
        )

        res = client.get("/api/v1/demands/active", headers={"Authorization": f"Bearer {token_farmer}"})
        assert res.status_code == 200
        demands = res.json()
        assert not any(d["id"] == demand_id for d in demands)
    finally:
        app.dependency_overrides = old_overrides


def test_13_negative_quantity_rejected():
    _, _, token = _create_user(UserRole.BUYER, "buyer11")
    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        res = client.post(
            "/api/v1/buyer/demands",
            headers={"Authorization": f"Bearer {token}"},
            json={"crop_id": 1, "quantity_quintals": -10.0, "target_price_per_quintal": 6000.0, "delivery_district": "Dharwad"}
        )
        assert res.status_code == 422
    finally:
        app.dependency_overrides = old_overrides


def test_14_zero_quantity_rejected():
    _, _, token = _create_user(UserRole.BUYER, "buyer12")
    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        res = client.post(
            "/api/v1/buyer/demands",
            headers={"Authorization": f"Bearer {token}"},
            json={"crop_id": 1, "quantity_quintals": 0.0, "target_price_per_quintal": 6000.0, "delivery_district": "Dharwad"}
        )
        assert res.status_code == 422
    finally:
        app.dependency_overrides = old_overrides


def test_15_negative_price_rejected():
    _, _, token = _create_user(UserRole.BUYER, "buyer13")
    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        res = client.post(
            "/api/v1/buyer/demands",
            headers={"Authorization": f"Bearer {token}"},
            json={"crop_id": 1, "quantity_quintals": 100.0, "target_price_per_quintal": -500.0, "delivery_district": "Dharwad"}
        )
        assert res.status_code == 422
    finally:
        app.dependency_overrides = old_overrides


def test_16_invalid_date_range_rejected():
    _, _, token = _create_user(UserRole.BUYER, "buyer14")
    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        res = client.post(
            "/api/v1/buyer/demands",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "crop_id": 1,
                "quantity_quintals": 100.0,
                "target_price_per_quintal": 6000.0,
                "delivery_district": "Dharwad",
                "expected_harvest_start": "2026-10-30",
                "expected_harvest_end": "2026-10-01"
            }
        )
        assert res.status_code == 422
    finally:
        app.dependency_overrides = old_overrides


def test_17_client_supplied_buyer_id_cannot_override():
    buyer_id, _, token = _create_user(UserRole.BUYER, "buyer15")
    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        res = client.post(
            "/api/v1/buyer/demands",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "buyer_id": 999999,
                "crop_id": 1,
                "quantity_quintals": 100.0,
                "target_price_per_quintal": 6000.0,
                "delivery_district": "Dharwad"
            }
        )
        assert res.status_code == 201
        assert res.json()["buyer_id"] == buyer_id  # Derived strictly from token
    finally:
        app.dependency_overrides = old_overrides


def test_18_farmer_cannot_access_buyer_me_endpoint():
    _, _, token = _create_user(UserRole.FARMER, "farmer16")
    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        res = client.get("/api/v1/buyer/demands/me", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 403
    finally:
        app.dependency_overrides = old_overrides


def test_19_invalid_crop_id_rejected():
    _, _, token = _create_user(UserRole.BUYER, "buyer17")
    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        res = client.post(
            "/api/v1/buyer/demands",
            headers={"Authorization": f"Bearer {token}"},
            json={"crop_id": 999999, "quantity_quintals": 100.0, "target_price_per_quintal": 6000.0, "delivery_district": "Dharwad"}
        )
        assert res.status_code == 404
    finally:
        app.dependency_overrides = old_overrides


def test_20_demand_ownership_remains_unchanged_after_update():
    buyer_id, _, token = _create_user(UserRole.BUYER, "buyer18")
    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        res_create = client.post(
            "/api/v1/buyer/demands",
            headers={"Authorization": f"Bearer {token}"},
            json={"crop_id": 1, "quantity_quintals": 100.0, "target_price_per_quintal": 6000.0, "delivery_district": "Dharwad"}
        )
        demand_id = res_create.json()["id"]

        res_update = client.put(
            f"/api/v1/buyer/demands/{demand_id}",
            headers={"Authorization": f"Bearer {token}"},
            json={"buyer_id": 888888, "quantity_quintals": 150.0}
        )
        assert res_update.status_code == 200
        assert res_update.json()["buyer_id"] == buyer_id
    finally:
        app.dependency_overrides = old_overrides
