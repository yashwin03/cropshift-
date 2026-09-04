"""Automated test suite for Market-based Target Price validation across marketplace endpoints."""
import uuid
import pytest
from datetime import date, timedelta
from fastapi.testclient import TestClient

from app.main import app
from app.models.user import User, UserRole
from app.models.farmer import Farmer
from app.models.farm import Farm
from app.models.crop import Crop, CropType
from app.models.market_price import MarketPrice
from app.api.v1.auth import get_password_hash, create_access_token
from app.database.session import SessionLocal

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_dependency_overrides():
    """Clear any mock dependency overrides left by other test modules."""
    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    yield
    app.dependency_overrides = old_overrides


def _create_farmer_and_farm(prefix="tp_farmer"):
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

        u.farmer_id = f"FS-{farmer_entity.id:06d}"
        db.commit()

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
        return u.id, farm, token
    finally:
        db.close()





def test_market_price_info_endpoint():
    """Verify GET /api/v1/markets/{crop_id} returns price range bounds."""
    response = client.get("/api/v1/markets/2")
    assert response.status_code == 200
    data = response.json()
    assert data["crop_id"] == 2
    assert data["price"] is not None
    assert data["min_target_price"] is not None
    assert data["max_target_price"] is not None
    assert data["min_target_price"] <= data["price"] <= data["max_target_price"]


def test_create_future_crop_lot_valid_target_price():
    """Valid target price inside allowed range succeeds."""
    _, farm, token = _create_farmer_and_farm("valid_tp")
    m_res = client.get(f"/api/v1/markets/2?farm_id={farm.id}").json()
    valid_price = m_res["price"]

    payload = {
        "crop_id": 2,
        "farm_id": farm.id,
        "planned_acres": 2.5,
        "expected_quantity_quintals": 30.0,
        "asking_price_per_quintal": valid_price,
        "planned_sowing_date": "2026-06-01",
        "expected_harvest_start": "2026-10-01",
        "expected_harvest_end": "2026-10-15",
        "quality_grade": "A",
        "status": "OPEN"
    }

    res = client.post(
        "/api/v1/farmer/future-crop-lots",
        headers={"Authorization": f"Bearer {token}"},
        json=payload
    )
    assert res.status_code == 201
    assert res.json()["asking_price_per_quintal"] == valid_price


def test_create_future_crop_lot_price_above_range_rejected():
    """Target price above allowed range is rejected by backend with 400."""
    _, farm, token = _create_farmer_and_farm("high_tp")

    payload = {
        "crop_id": 2,
        "farm_id": farm.id,
        "planned_acres": 2.5,
        "expected_quantity_quintals": 30.0,
        "asking_price_per_quintal": 10000.0,  # Invalid high price
        "planned_sowing_date": "2026-06-01",
        "expected_harvest_start": "2026-10-01",
        "expected_harvest_end": "2026-10-15",
        "quality_grade": "A",
        "status": "OPEN"
    }

    res = client.post(
        "/api/v1/farmer/future-crop-lots",
        headers={"Authorization": f"Bearer {token}"},
        json=payload
    )
    assert res.status_code == 400
    res_data = res.json()
    msg = res_data.get("detail") or res_data.get("error", {}).get("message", "")
    assert "Target price must be between" in msg


def test_create_future_crop_lot_price_below_range_rejected():
    """Target price below allowed range is rejected by backend with 400."""
    _, farm, token = _create_farmer_and_farm("low_tp")

    payload = {
        "crop_id": 2,
        "farm_id": farm.id,
        "planned_acres": 2.5,
        "expected_quantity_quintals": 30.0,
        "asking_price_per_quintal": 1000.0,  # Invalid low price
        "planned_sowing_date": "2026-06-01",
        "expected_harvest_start": "2026-10-01",
        "expected_harvest_end": "2026-10-15",
        "quality_grade": "A",
        "status": "OPEN"
    }

    res = client.post(
        "/api/v1/farmer/future-crop-lots",
        headers={"Authorization": f"Bearer {token}"},
        json=payload
    )
    assert res.status_code == 400
    res_data = res.json()
    msg = res_data.get("detail") or res_data.get("error", {}).get("message", "")
    assert "Target price must be between" in msg


def test_direct_stock_lot_target_price_validation():
    """Direct stock lot asking price validation."""
    _, farm, token = _create_farmer_and_farm("stock_tp")

    invalid_payload = {
        "crop_id": 2,
        "farm_id": farm.id,
        "actual_quantity_quintals": 20.0,
        "actual_harvest_date": "2026-09-01",
        "asking_price_per_quintal": 12000.0,
        "quality_grade": "A"
    }

    res = client.post(
        "/api/v1/farmer/stock-lots",
        headers={"Authorization": f"Bearer {token}"},
        json=invalid_payload
    )
    assert res.status_code == 400
    res_data = res.json()
    msg = res_data.get("detail") or res_data.get("error", {}).get("message", "")
    assert "Target price must be between" in msg
