import uuid
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.user import User, UserRole
from app.api.v1.auth import get_password_hash, create_access_token
from app.database.session import SessionLocal

client = TestClient(app)

def test_register_farmer_and_buyer_accounts():
    uid = uuid.uuid4().hex[:6]
    # 1. Register Farmer
    res_farmer = client.post(
        "/api/v1/auth/register",
        json={
            "username": f"farmer_reg_{uid}",
            "email": f"farmer_{uid}@example.com",
            "password": "Password123!",
            "role": "FARMER"
        }
    )
    assert res_farmer.status_code == 200
    data_farmer = res_farmer.json()
    assert data_farmer["username"] == f"farmer_reg_{uid}"
    assert data_farmer["role"] == "FARMER"

    # 2. Register Buyer
    res_buyer = client.post(
        "/api/v1/auth/register",
        json={
            "username": f"buyer_reg_{uid}",
            "email": f"buyer_{uid}@example.com",
            "password": "Password123!",
            "role": "BUYER"
        }
    )
    assert res_buyer.status_code == 200
    data_buyer = res_buyer.json()
    assert data_buyer["username"] == f"buyer_reg_{uid}"
    assert data_buyer["role"] == "BUYER"

def test_register_invalid_role_escalation_rejected():
    uid = uuid.uuid4().hex[:6]
    res = client.post(
        "/api/v1/auth/register",
        json={
            "username": f"hacker_{uid}",
            "email": f"hacker_{uid}@example.com",
            "password": "Password123!",
            "role": "ADMIN"
        }
    )
    assert res.status_code == 422 or res.status_code == 400

def test_login_returns_jwt_with_role_claim():
    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    db = SessionLocal()
    uid = uuid.uuid4().hex[:6]
    try:
        user = User(
            username=f"buyer_jwt_{uid}",
            email=f"buyerjwt_{uid}@example.com",
            hashed_password=get_password_hash("Secret123"),
            role=UserRole.BUYER
        )
        db.add(user)
        db.commit()

        res = client.post(
            "/api/v1/auth/token",
            data={"username": f"buyer_jwt_{uid}", "password": "Secret123"}
        )
        assert res.status_code == 200
        token = res.json()["access_token"]
        assert token is not None

        # Fetch /auth/me
        res_me = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert res_me.status_code == 200
        assert res_me.json()["role"] == "BUYER"
    finally:
        db.close()
        app.dependency_overrides = old_overrides

def test_buyer_forbidden_from_farmer_endpoints():
    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    db = SessionLocal()
    uid = uuid.uuid4().hex[:6]
    try:
        buyer_user = User(
            username=f"buyer_only_{uid}",
            email=f"buyeronly_{uid}@example.com",
            hashed_password=get_password_hash("Secret123"),
            role=UserRole.BUYER
        )
        db.add(buyer_user)
        db.commit()

        token = create_access_token(data={"sub": buyer_user.username, "user_id": buyer_user.id, "role": "BUYER"})

        # Attempt to post to /api/v1/farms as BUYER -> 403 Forbidden
        res = client.post(
            "/api/v1/farms",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "land_area_acre": 5.0,
                "water_availability": True,
                "district": "Dharwad",
                "state": "Karnataka",
                "current_crop": "Groundnut"
            }
        )
        assert res.status_code == 403
    finally:
        db.close()
        app.dependency_overrides = old_overrides

def test_farmer_allowed_on_farmer_endpoints():
    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    db = SessionLocal()
    uid = uuid.uuid4().hex[:6]
    try:
        farmer_user = User(
            username=f"farmer_valid_{uid}",
            email=f"farmerauth_{uid}@example.com",
            hashed_password=get_password_hash("Secret123"),
            role=UserRole.FARMER
        )
        db.add(farmer_user)
        db.commit()

        token = create_access_token(data={"sub": farmer_user.username, "user_id": farmer_user.id, "role": "FARMER"})

        res = client.post(
            "/api/v1/farms",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "land_area_acre": 3.5,
                "water_availability": True,
                "district": "Belagavi",
                "state": "Karnataka",
                "current_crop": "Groundnut"
            }
        )
        assert res.status_code == 200
    finally:
        db.close()
        app.dependency_overrides = old_overrides

def test_unauthenticated_request_rejected():
    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    try:
        res = client.post(
            "/api/v1/farms",
            json={
                "land_area_acre": 2.0,
                "water_availability": True,
                "district": "Guntur",
                "state": "Andhra Pradesh",
                "current_crop": "Groundnut"
            }
        )
        assert res.status_code == 401
    finally:
        app.dependency_overrides = old_overrides

def test_fake_role_header_or_query_param_ignored():
    old_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.clear()
    db = SessionLocal()
    uid = uuid.uuid4().hex[:6]
    try:
        farmer_user = User(
            username=f"farmer_fake_{uid}",
            email=f"farmerfake_{uid}@example.com",
            hashed_password=get_password_hash("Secret123"),
            role=UserRole.FARMER
        )
        db.add(farmer_user)
        db.commit()

        token = create_access_token(data={"sub": farmer_user.username, "user_id": farmer_user.id, "role": "FARMER"})

        # Send fake X-Role header trying to claim BUYER
        res = client.post(
            "/api/v1/farms",
            headers={
                "Authorization": f"Bearer {token}",
                "X-Role": "BUYER"
            },
            json={
                "land_area_acre": 2.0,
                "water_availability": True,
                "district": "Guntur",
                "state": "Andhra Pradesh",
                "current_crop": "Groundnut"
            }
        )
        # Backend still uses authenticated identity (FARMER) -> allowed for farm creation
        assert res.status_code == 200
    finally:
        db.close()
        app.dependency_overrides = old_overrides




