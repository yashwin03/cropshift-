import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.database.session import get_db
from app.models.user import User, UserRole
from app.models.farm import Farm
from app.models.farmer import Farmer
from app.models.crop import Crop
from app.models.stock_lot import StockLot, StockLotStatus
from app.models.trade_order import TradeOrder, TradeOrderStatus
from app.api.v1.auth import get_current_user


@pytest.fixture
def test_users(db_session: Session):
    # Ensure test session is bound to FastAPI get_db dependency
    app.dependency_overrides[get_db] = lambda: db_session

    import uuid
    uid = uuid.uuid4().hex[:6]

    # Farmer 1
    farmer1 = User(
        username=f"farmer_mkt1_{uid}",
        email=f"farmer1_{uid}@test.com",
        hashed_password="fakehashpassword",
        role=UserRole.FARMER,
        full_name="Test Farmer One"
    )
    # Farmer 2
    farmer2 = User(
        username=f"farmer_mkt2_{uid}",
        email=f"farmer2_{uid}@test.com",
        hashed_password="fakehashpassword",
        role=UserRole.FARMER,
        full_name="Test Farmer Two"
    )
    # Buyer
    buyer = User(
        username=f"buyer_mkt1_{uid}",
        email=f"buyer1_{uid}@test.com",
        hashed_password="fakehashpassword",
        role=UserRole.BUYER,
        full_name="Test Buyer One"
    )
    db_session.add_all([farmer1, farmer2, buyer])
    db_session.commit()
    db_session.refresh(farmer1)
    db_session.refresh(farmer2)
    db_session.refresh(buyer)

    # Farmer profile for farmer1 & farmer2
    f_profile1 = Farmer(name=farmer1.username, district="Dharwad", state="Karnataka")
    f_profile2 = Farmer(name=farmer2.username, district="Belagavi", state="Karnataka")
    db_session.add_all([f_profile1, f_profile2])
    db_session.commit()

    # Farm for farmer1
    farm1 = Farm(
        farmer_id=f_profile1.id,
        owner_id=farmer1.id,
        land_area_acre=5.0,
        water_availability=True,
        district="Dharwad",
        state="Karnataka"
    )
    # Farm for farmer2
    farm2 = Farm(
        farmer_id=f_profile2.id,
        owner_id=farmer2.id,
        land_area_acre=3.0,
        water_availability=True,
        district="Belagavi",
        state="Karnataka"
    )
    db_session.add_all([farm1, farm2])

    # Crop
    crop = db_session.query(Crop).first()
    if not crop:
        crop = Crop(name="Groundnut", crop_type="OILSEED", is_oilseed=True)
        db_session.add(crop)

    db_session.commit()
    db_session.refresh(farm1)
    db_session.refresh(farm2)
    db_session.refresh(crop)

    return {
        "farmer1": farmer1,
        "farmer2": farmer2,
        "buyer": buyer,
        "farm1": farm1,
        "farm2": farm2,
        "crop": crop,
    }


def set_auth_user(user: User):
    app.dependency_overrides[get_current_user] = lambda: user


def get_err_msg(res) -> str:
    data = res.json()
    if isinstance(data, dict):
        if "error" in data and isinstance(data["error"], dict):
            return str(data["error"].get("message", ""))
        return str(data.get("detail", ""))
    return str(data)


def test_farm_ownership_validation(client: TestClient, test_users):
    farmer1 = test_users["farmer1"]
    farm1 = test_users["farm1"]
    farm2 = test_users["farm2"]
    crop = test_users["crop"]

    set_auth_user(farmer1)

    # 1. Farmer 1 creates crop specifying their own farm -> Success
    res = client.post(
        "/api/v1/future-crop-lots",
        json={
            "farm_id": farm1.id,
            "crop_id": crop.id,
            "planned_acres": 2.5,
            "expected_quantity_quintals": 25.0,
            "planned_sowing_date": "2026-06-01",
            "expected_harvest_start": "2026-10-01",
            "expected_harvest_end": "2026-10-15",
            "status": "OPEN",
        },
    )
    assert res.status_code == 201, f"Expected 201, got {res.status_code}: {get_err_msg(res)}"
    assert res.json()["farm_id"] == farm1.id

    # 2. Farmer 1 attempts to use Farmer 2's farm -> 403 Forbidden
    res_err = client.post(
        "/api/v1/future-crop-lots",
        json={
            "farm_id": farm2.id,
            "crop_id": crop.id,
            "planned_acres": 2.5,
            "expected_quantity_quintals": 25.0,
            "planned_sowing_date": "2026-06-01",
            "expected_harvest_start": "2026-10-01",
            "expected_harvest_end": "2026-10-15",
        },
    )
    assert res_err.status_code == 403
    assert "you do not own this farm" in get_err_msg(res_err).lower()


def test_all_four_crop_stages_creation(client: TestClient, test_users):
    farmer1 = test_users["farmer1"]
    farm1 = test_users["farm1"]
    crop = test_users["crop"]

    set_auth_user(farmer1)

    # Stage 1: Planning to Grow
    res1 = client.post(
        "/api/v1/future-crop-lots",
        json={
            "farm_id": farm1.id,
            "crop_id": crop.id,
            "planned_acres": 2.0,
            "expected_quantity_quintals": 20.0,
            "planned_sowing_date": "2026-06-15",
            "expected_harvest_start": "2026-10-15",
            "expected_harvest_end": "2026-10-30",
            "status": "OPEN",
        },
    )
    assert res1.status_code == 201

    # Stage 2: Currently Growing
    res2 = client.post(
        "/api/v1/future-crop-lots",
        json={
            "farm_id": farm1.id,
            "crop_id": crop.id,
            "planned_acres": 3.0,
            "expected_quantity_quintals": 30.0,
            "planned_sowing_date": "2026-05-15",
            "expected_harvest_start": "2026-09-15",
            "expected_harvest_end": "2026-09-30",
            "status": "OPEN",
        },
    )
    assert res2.status_code == 201

    # Stage 3: Ready for Harvest
    res3 = client.post(
        "/api/v1/future-crop-lots",
        json={
            "farm_id": farm1.id,
            "crop_id": crop.id,
            "planned_acres": 4.0,
            "expected_quantity_quintals": 40.0,
            "planned_sowing_date": "2026-04-15",
            "expected_harvest_start": "2026-09-05",
            "expected_harvest_end": "2026-09-15",
            "status": "OPEN",
        },
    )
    assert res3.status_code == 201

    # Stage 4: Already Harvested (direct stock lot)
    res4 = client.post(
        "/api/v1/farmer/stock-lots",
        json={
            "farm_id": farm1.id,
            "crop_id": crop.id,
            "actual_quantity_quintals": 35.0,
            "actual_harvest_date": "2026-09-01",
            "asking_price_per_quintal": 6500,
            "quality_grade": "A",
        },
    )
    assert res4.status_code == 201
    assert res4.json()["actual_quantity_quintals"] == 35.0


def test_transaction_rating_eligibility_and_duplication(client: TestClient, db_session: Session, test_users):
    farmer1 = test_users["farmer1"]
    buyer = test_users["buyer"]
    farm1 = test_users["farm1"]
    crop = test_users["crop"]

    # Create a StockLot
    stock_lot = StockLot(
        farmer_id=farmer1.id,
        farm_id=farm1.id,
        crop_id=crop.id,
        actual_quantity_quintals=50.0,
        available_quantity_quintals=50.0,
        actual_harvest_date="2026-09-01",
        status=StockLotStatus.AVAILABLE,
    )
    db_session.add(stock_lot)
    db_session.commit()

    # Create TradeOrder in CREATED status
    order = TradeOrder(
        stock_lot_id=stock_lot.id,
        buyer_id=buyer.id,
        farmer_id=farmer1.id,
        allocated_quantity_quintals=20.0,
        agreed_price_per_quintal=6400,
        status=TradeOrderStatus.CREATED,
    )
    db_session.add(order)
    db_session.commit()

    # 1. Attempt rating when order is CREATED -> 400 Error
    set_auth_user(buyer)
    res_created = client.post(
        "/api/v1/ratings",
        json={
            "target_user_id": farmer1.id,
            "trade_order_id": order.id,
            "stars": 5,
            "comment": "Great trade!",
        },
    )
    assert res_created.status_code == 400
    assert "completed transactions" in get_err_msg(res_created).lower()

    # Mark order as FULFILLED
    order.status = TradeOrderStatus.FULFILLED
    db_session.commit()

    # 2. Buyer rates Farmer for FULFILLED order -> Success
    set_auth_user(buyer)
    res_rate_farmer = client.post(
        "/api/v1/ratings",
        json={
            "target_user_id": farmer1.id,
            "trade_order_id": order.id,
            "stars": 5,
            "comment": "Excellent quality groundnut!",
        },
    )
    assert res_rate_farmer.status_code == 201
    assert res_rate_farmer.json()["stars"] == 5

    # 3. Duplicate rating attempt by Buyer -> 400 Error
    res_dup = client.post(
        "/api/v1/ratings",
        json={
            "target_user_id": farmer1.id,
            "trade_order_id": order.id,
            "stars": 4,
        },
    )
    assert res_dup.status_code == 400
    assert "already rated" in get_err_msg(res_dup).lower()

    # 4. Farmer rates Buyer for same FULFILLED order -> Success
    set_auth_user(farmer1)
    res_rate_buyer = client.post(
        "/api/v1/ratings",
        json={
            "target_user_id": buyer.id,
            "trade_order_id": order.id,
            "stars": 5,
            "comment": "Prompt payment and clear communication",
        },
    )
    assert res_rate_buyer.status_code == 201

    # 5. Check Farmer Profile Rating Summary
    res_summary = client.get(f"/api/v1/ratings/user/{farmer1.id}")
    assert res_summary.status_code == 200
    sum_data = res_summary.json()
    assert sum_data["average_rating"] == 5.0
    assert sum_data["total_ratings"] == 1
    assert sum_data["completed_transactions"] == 1

    # 6. Check user with NO ratings -> average_rating should be None (not 5.0)
    farmer2 = test_users["farmer2"]
    res_no_ratings = client.get(f"/api/v1/ratings/user/{farmer2.id}")
    assert res_no_ratings.status_code == 200
    no_rat_data = res_no_ratings.json()
    assert no_rat_data["average_rating"] is None
    assert no_rat_data["total_ratings"] == 0


def test_same_farmer_name_ownership_rejection(client: TestClient, db_session: Session):
    """
    Regression test:
    - Farmer A and Farmer B have the exact same name ("Raju Naik").
    - Farmer B owns a farm.
    - Farmer A attempts to access/claim Farmer B's farm.
    - Expected result: 403 Forbidden / ownership rejection ("You do not own this farm.").
    """
    import uuid
    uid = uuid.uuid4().hex[:6]

    farmer_a = User(
        username=f"farmer_a_{uid}",
        email=f"farmer_a_{uid}@test.com",
        hashed_password="fakehashpassword",
        role=UserRole.FARMER,
        full_name="Raju Naik"
    )
    farmer_b = User(
        username=f"farmer_b_{uid}",
        email=f"farmer_b_{uid}@test.com",
        hashed_password="fakehashpassword",
        role=UserRole.FARMER,
        full_name="Raju Naik"
    )
    db_session.add_all([farmer_a, farmer_b])
    db_session.commit()
    db_session.refresh(farmer_a)
    db_session.refresh(farmer_b)

    # Farmer profile for Farmer B with name "Raju Naik"
    f_profile_b = Farmer(name="Raju Naik", district="Dharwad", state="Karnataka")
    db_session.add(f_profile_b)
    db_session.commit()
    db_session.refresh(f_profile_b)

    # Farm owned by Farmer B
    farm_b = Farm(
        farmer_id=f_profile_b.id,
        owner_id=farmer_b.id,
        land_area_acre=5.0,
        water_availability=True,
        district="Dharwad",
        state="Karnataka"
    )
    db_session.add(farm_b)
    db_session.commit()
    db_session.refresh(farm_b)

    crop = db_session.query(Crop).first()
    if not crop:
        crop = Crop(name="Groundnut", crop_type="OILSEED", is_oilseed=True)
        db_session.add(crop)
        db_session.commit()
        db_session.refresh(crop)

    # Authenticate as Farmer A
    set_auth_user(farmer_a)

    # Farmer A attempts to publish a lot specifying Farmer B's farm_id
    res = client.post(
        "/api/v1/future-crop-lots",
        json={
            "farm_id": farm_b.id,
            "crop_id": crop.id,
            "planned_acres": 2.5,
            "expected_quantity_quintals": 25.0,
            "planned_sowing_date": "2026-06-01",
            "expected_harvest_start": "2026-10-01",
            "expected_harvest_end": "2026-10-15",
            "status": "OPEN",
        },
    )

    # Expected result: 403 Forbidden ("You do not own this farm.")
    assert res.status_code == 403
    assert "you do not own this farm" in get_err_msg(res).lower()

