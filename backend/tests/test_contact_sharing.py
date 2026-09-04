"""Automated test suite for Post-Acceptance Mutual Contact Sharing endpoints and privacy rules."""
import uuid
import pytest
from datetime import date
from fastapi.testclient import TestClient

from app.main import app
from app.models.user import User, UserRole
from app.models.farmer import Farmer
from app.models.farm import Farm
from app.models.crop import Crop, CropType
from app.models.contact_sharing import ContactSharing, ContactSharingStatus
from app.api.v1.auth import get_password_hash, create_access_token
from app.database.session import SessionLocal

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_test_entities():
    """Clear dependency overrides and ensure standard crop entity exists for tests."""
    app.dependency_overrides.clear()
    db = SessionLocal()
    try:
        crop = db.query(Crop).filter(Crop.name == "Groundnut").first()
        if not crop:
            crop = Crop(name="Groundnut", crop_type=CropType.OILSEED, season="Kharif", duration_days=110, is_oilseed=True)
            db.add(crop)
            db.commit()
    finally:
        db.close()


def _create_farmer(prefix="farmer"):
    db = SessionLocal()
    uid = uuid.uuid4().hex[:6]
    try:
        u = User(
            username=f"{prefix}_{uid}",
            email=f"{prefix}_{uid}@example.com",
            hashed_password=get_password_hash("Secret123!"),
            role=UserRole.FARMER,
            full_name=f"Farmer {uid}",
            phone="+919800011111"
        )
        db.add(u)
        db.commit()
        db.refresh(u)

        farmer_entity = Farmer(name=f"Farmer {uid}", phone="+919800011111", district="Dharwad", state="Karnataka")
        db.add(farmer_entity)
        db.commit()
        db.refresh(farmer_entity)

        farm = Farm(owner_id=u.id, farmer_id=farmer_entity.id, land_area_acre=5.0, water_availability=True, district="Dharwad", state="Karnataka")
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
            role=UserRole.BUYER,
            full_name=f"Buyer {uid}",
            phone="+919800022222"
        )
        db.add(u)
        db.commit()
        db.refresh(u)
        token = create_access_token(data={"sub": u.username, "user_id": u.id, "role": "BUYER"})
        return u.id, token
    finally:
        db.close()


def _create_accepted_bid():
    farmer_id, farm_id, f_token = _create_farmer()
    buyer_id, b_token = _create_buyer()

    # Create Lot via API
    lot_res = client.post(
        "/api/v1/farmer/future-crop-lots",
        headers={"Authorization": f"Bearer {f_token}"},
        json={
            "farm_id": farm_id,
            "crop_id": 1,
            "planned_acres": 5.0,
            "expected_quantity_quintals": 100.0,
            "asking_price_per_quintal": 4500.0,
            "planned_sowing_date": "2026-06-01",
            "expected_harvest_start": "2026-09-15",
            "expected_harvest_end": "2026-10-01",
            "status": "OPEN"
        }
    )
    assert lot_res.status_code == 201
    lot_id = lot_res.json()["id"]

    # Submit Bid via API
    bid_res = client.post(
        "/api/v1/bids",
        headers={"Authorization": f"Bearer {b_token}"},
        json={
            "future_crop_lot_id": lot_id,
            "offered_price_per_quintal": 4600.0,
            "quantity_quintals": 50.0
        }
    )
    assert bid_res.status_code == 201
    bid_id = bid_res.json()["id"]

    # Accept Bid via API
    accept_res = client.post(
        f"/api/v1/bids/{bid_id}/accept",
        headers={"Authorization": f"Bearer {f_token}"}
    )
    assert accept_res.status_code == 200

    return farmer_id, f_token, buyer_id, b_token, lot_id, bid_id


def test_farmer_consent_works():
    farmer_id, f_token, buyer_id, b_token, lot_id, bid_id = _create_accepted_bid()

    res = client.post(
        f"/api/v1/bids/{bid_id}/contact-sharing/consent",
        headers={"Authorization": f"Bearer {f_token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["farmer_consented"] is True
    assert data["buyer_consented"] is False
    assert data["status"] == "PENDING"
    assert data["farmer_contact"] is None
    assert data["buyer_contact"] is None


def test_buyer_consent_works():
    farmer_id, f_token, buyer_id, b_token, lot_id, bid_id = _create_accepted_bid()

    res = client.post(
        f"/api/v1/bids/{bid_id}/contact-sharing/consent",
        headers={"Authorization": f"Bearer {b_token}"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["buyer_consented"] is True
    assert data["farmer_consented"] is False
    assert data["status"] == "PENDING"


def test_unrelated_farmer_receives_403():
    farmer_id, f_token, buyer_id, b_token, lot_id, bid_id = _create_accepted_bid()
    _, _, uf_token = _create_farmer("unrelated_farmer")

    res = client.post(
        f"/api/v1/bids/{bid_id}/contact-sharing/consent",
        headers={"Authorization": f"Bearer {uf_token}"},
    )
    assert res.status_code == 403


def test_unrelated_buyer_receives_403():
    farmer_id, f_token, buyer_id, b_token, lot_id, bid_id = _create_accepted_bid()
    _, ub_token = _create_buyer("unrelated_buyer")

    res = client.post(
        f"/api/v1/bids/{bid_id}/contact-sharing/consent",
        headers={"Authorization": f"Bearer {ub_token}"},
    )
    assert res.status_code == 403


def test_unauthenticated_request_receives_401():
    res = client.post("/api/v1/bids/99999/contact-sharing/consent")
    assert res.status_code == 401


def test_consent_on_submitted_bid_fails():
    farmer_id, farm_id, f_token = _create_farmer()
    buyer_id, b_token = _create_buyer()

    lot_res = client.post(
        "/api/v1/farmer/future-crop-lots",
        headers={"Authorization": f"Bearer {f_token}"},
        json={
            "farm_id": farm_id,
            "crop_id": 1,
            "planned_acres": 5.0,
            "expected_quantity_quintals": 100.0,
            "asking_price_per_quintal": 4500.0,
            "planned_sowing_date": "2026-06-01",
            "expected_harvest_start": "2026-09-15",
            "expected_harvest_end": "2026-10-01",
            "status": "OPEN"
        }
    )
    bid_res = client.post(
        "/api/v1/bids",
        headers={"Authorization": f"Bearer {b_token}"},
        json={"future_crop_lot_id": lot_res.json()["id"], "offered_price_per_quintal": 4600.0, "quantity_quintals": 50.0}
    )
    bid_id = bid_res.json()["id"]

    res = client.post(
        f"/api/v1/bids/{bid_id}/contact-sharing/consent",
        headers={"Authorization": f"Bearer {f_token}"},
    )
    assert res.status_code == 400
    assert "ACCEPTED" in str(res.json())


def test_consent_on_rejected_bid_fails():
    farmer_id, farm_id, f_token = _create_farmer()
    b1_id, b1_token = _create_buyer("b1")
    b2_id, b2_token = _create_buyer("b2")

    lot_res = client.post(
        "/api/v1/farmer/future-crop-lots",
        headers={"Authorization": f"Bearer {f_token}"},
        json={
            "farm_id": farm_id,
            "crop_id": 1,
            "planned_acres": 5.0,
            "expected_quantity_quintals": 100.0,
            "asking_price_per_quintal": 4500.0,
            "planned_sowing_date": "2026-06-01",
            "expected_harvest_start": "2026-09-15",
            "expected_harvest_end": "2026-10-01",
            "status": "OPEN"
        }
    )
    bid1 = client.post("/api/v1/bids", headers={"Authorization": f"Bearer {b1_token}"}, json={"future_crop_lot_id": lot_res.json()["id"], "offered_price_per_quintal": 4600.0, "quantity_quintals": 50.0}).json()["id"]
    bid2 = client.post("/api/v1/bids", headers={"Authorization": f"Bearer {b2_token}"}, json={"future_crop_lot_id": lot_res.json()["id"], "offered_price_per_quintal": 4700.0, "quantity_quintals": 50.0}).json()["id"]

    # Accept bid2, rejecting bid1
    client.post(f"/api/v1/bids/{bid2}/accept", headers={"Authorization": f"Bearer {f_token}"})

    # Try consent on rejected bid1
    res = client.post(f"/api/v1/bids/{bid1}/contact-sharing/consent", headers={"Authorization": f"Bearer {b1_token}"})
    assert res.status_code == 400


def test_consent_on_withdrawn_bid_fails():
    farmer_id, farm_id, f_token = _create_farmer()
    buyer_id, b_token = _create_buyer()

    lot_res = client.post(
        "/api/v1/farmer/future-crop-lots",
        headers={"Authorization": f"Bearer {f_token}"},
        json={
            "farm_id": farm_id,
            "crop_id": 1,
            "planned_acres": 5.0,
            "expected_quantity_quintals": 100.0,
            "asking_price_per_quintal": 4500.0,
            "planned_sowing_date": "2026-06-01",
            "expected_harvest_start": "2026-09-15",
            "expected_harvest_end": "2026-10-01",
            "status": "OPEN"
        }
    )
    bid_id = client.post("/api/v1/bids", headers={"Authorization": f"Bearer {b_token}"}, json={"future_crop_lot_id": lot_res.json()["id"], "offered_price_per_quintal": 4600.0, "quantity_quintals": 50.0}).json()["id"]

    # Withdraw bid
    client.post(f"/api/v1/bids/{bid_id}/withdraw", headers={"Authorization": f"Bearer {b_token}"})

    res = client.post(f"/api/v1/bids/{bid_id}/contact-sharing/consent", headers={"Authorization": f"Bearer {b_token}"})
    assert res.status_code == 400


def test_one_consent_keeps_contact_hidden():
    farmer_id, f_token, buyer_id, b_token, lot_id, bid_id = _create_accepted_bid()

    # Farmer consents
    client.post(f"/api/v1/bids/{bid_id}/contact-sharing/consent", headers={"Authorization": f"Bearer {f_token}"})

    # Check GET as farmer
    res_f = client.get(f"/api/v1/bids/{bid_id}/contact-sharing", headers={"Authorization": f"Bearer {f_token}"})
    assert res_f.status_code == 200
    assert res_f.json()["buyer_contact"] is None

    # Check GET as buyer
    res_b = client.get(f"/api/v1/bids/{bid_id}/contact-sharing", headers={"Authorization": f"Bearer {b_token}"})
    assert res_b.status_code == 200
    assert res_b.json()["farmer_contact"] is None


def test_both_consents_unlock_contact():
    farmer_id, f_token, buyer_id, b_token, lot_id, bid_id = _create_accepted_bid()

    # Farmer consents
    client.post(f"/api/v1/bids/{bid_id}/contact-sharing/consent", headers={"Authorization": f"Bearer {f_token}"})
    # Buyer consents
    res = client.post(f"/api/v1/bids/{bid_id}/contact-sharing/consent", headers={"Authorization": f"Bearer {b_token}"})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "MUTUAL_CONSENT"
    assert data["farmer_contact"]["phone"] == "+919800011111"

    # Check GET as farmer to verify buyer contact
    res_f = client.get(f"/api/v1/bids/{bid_id}/contact-sharing", headers={"Authorization": f"Bearer {f_token}"})
    assert res_f.status_code == 200
    data_f = res_f.json()
    assert data_f["buyer_contact"]["phone"] == "+919800022222"


def test_duplicate_consent_is_idempotent():
    farmer_id, f_token, buyer_id, b_token, lot_id, bid_id = _create_accepted_bid()

    res1 = client.post(f"/api/v1/bids/{bid_id}/contact-sharing/consent", headers={"Authorization": f"Bearer {f_token}"})
    assert res1.status_code == 200
    res2 = client.post(f"/api/v1/bids/{bid_id}/contact-sharing/consent", headers={"Authorization": f"Bearer {f_token}"})
    assert res2.status_code == 200
    assert res2.json()["farmer_consented"] is True


def test_revocation_hides_contact_again():
    farmer_id, f_token, buyer_id, b_token, lot_id, bid_id = _create_accepted_bid()

    # Both consent
    client.post(f"/api/v1/bids/{bid_id}/contact-sharing/consent", headers={"Authorization": f"Bearer {f_token}"})
    client.post(f"/api/v1/bids/{bid_id}/contact-sharing/consent", headers={"Authorization": f"Bearer {b_token}"})

    # Farmer revokes consent
    res_r = client.post(f"/api/v1/bids/{bid_id}/contact-sharing/revoke", headers={"Authorization": f"Bearer {f_token}"})
    assert res_r.status_code == 200
    assert res_r.json()["status"] == "REVOKED"
    assert res_r.json()["farmer_contact"] is None

    # Buyer GET after farmer revocation
    res_b = client.get(f"/api/v1/bids/{bid_id}/contact-sharing", headers={"Authorization": f"Bearer {b_token}"})
    assert res_b.status_code == 200
    assert res_b.json()["status"] == "REVOKED"
    assert res_b.json()["farmer_contact"] is None


def test_reconsent_restores_mutual_consent():
    farmer_id, f_token, buyer_id, b_token, lot_id, bid_id = _create_accepted_bid()

    # Both consent
    client.post(f"/api/v1/bids/{bid_id}/contact-sharing/consent", headers={"Authorization": f"Bearer {f_token}"})
    client.post(f"/api/v1/bids/{bid_id}/contact-sharing/consent", headers={"Authorization": f"Bearer {b_token}"})

    # Farmer revokes
    client.post(f"/api/v1/bids/{bid_id}/contact-sharing/revoke", headers={"Authorization": f"Bearer {f_token}"})

    # Farmer re-consents
    res_rc = client.post(f"/api/v1/bids/{bid_id}/contact-sharing/consent", headers={"Authorization": f"Bearer {f_token}"})
    assert res_rc.status_code == 200
    assert res_rc.json()["status"] == "MUTUAL_CONSENT"
    assert res_rc.json()["buyer_contact"]["phone"] == "+919800022222"


def test_exact_gps_is_never_exposed():
    farmer_id, f_token, buyer_id, b_token, lot_id, bid_id = _create_accepted_bid()

    # Both consent
    client.post(f"/api/v1/bids/{bid_id}/contact-sharing/consent", headers={"Authorization": f"Bearer {f_token}"})
    res = client.post(f"/api/v1/bids/{bid_id}/contact-sharing/consent", headers={"Authorization": f"Bearer {b_token}"})
    data = res.json()
    assert "location" not in str(data)
    assert "coordinates" not in str(data)
    assert "gps" not in str(data)


def test_private_address_is_never_exposed():
    farmer_id, f_token, buyer_id, b_token, lot_id, bid_id = _create_accepted_bid()

    res = client.post(f"/api/v1/bids/{bid_id}/contact-sharing/consent", headers={"Authorization": f"Bearer {b_token}"})
    data = res.json()
    assert "street" not in str(data)
    assert "address" not in str(data)


def test_contact_fields_absent_before_mutual_consent():
    farmer_id, f_token, buyer_id, b_token, lot_id, bid_id = _create_accepted_bid()

    res = client.get(f"/api/v1/bids/{bid_id}/contact-sharing", headers={"Authorization": f"Bearer {f_token}"})
    assert res.status_code == 200
    assert res.json()["farmer_contact"] is None
    assert res.json()["buyer_contact"] is None


def test_concurrent_consent_safety():
    farmer_id, f_token, buyer_id, b_token, lot_id, bid_id = _create_accepted_bid()

    r1 = client.post(f"/api/v1/bids/{bid_id}/contact-sharing/consent", headers={"Authorization": f"Bearer {f_token}"})
    r2 = client.post(f"/api/v1/bids/{bid_id}/contact-sharing/consent", headers={"Authorization": f"Bearer {b_token}"})
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r2.json()["status"] == "MUTUAL_CONSENT"


def test_contact_sharing_uniqueness_constraint():
    db = SessionLocal()
    try:
        farmer_id, f_token, buyer_id, b_token, lot_id, bid_id = _create_accepted_bid()

        count = db.query(ContactSharing).filter(ContactSharing.bid_id == bid_id).count()
        assert count == 1
    finally:
        db.close()


def test_bid_acceptance_creates_contact_sharing_once():
    farmer_id, farm_id, f_token = _create_farmer()
    buyer_id, b_token = _create_buyer()

    lot_res = client.post(
        "/api/v1/farmer/future-crop-lots",
        headers={"Authorization": f"Bearer {f_token}"},
        json={
            "farm_id": farm_id,
            "crop_id": 1,
            "planned_acres": 5.0,
            "expected_quantity_quintals": 100.0,
            "asking_price_per_quintal": 4500.0,
            "planned_sowing_date": "2026-06-01",
            "expected_harvest_start": "2026-09-15",
            "expected_harvest_end": "2026-10-01",
            "status": "OPEN"
        }
    )
    bid_res = client.post(
        "/api/v1/bids",
        headers={"Authorization": f"Bearer {b_token}"},
        json={"future_crop_lot_id": lot_res.json()["id"], "offered_price_per_quintal": 4600.0, "quantity_quintals": 50.0}
    )
    bid_id = bid_res.json()["id"]

    res = client.post(f"/api/v1/bids/{bid_id}/accept", headers={"Authorization": f"Bearer {f_token}"})
    assert res.status_code == 200

    db = SessionLocal()
    try:
        sharing = db.query(ContactSharing).filter(ContactSharing.bid_id == bid_id).first()
        assert sharing is not None
        assert sharing.status == ContactSharingStatus.PENDING
        assert sharing.farmer_consented is False
        assert sharing.buyer_consented is False
    finally:
        db.close()


def test_bid_acceptance_behavior_intact():
    farmer_id, farm_id, f_token = _create_farmer()
    b1_id, b1_token = _create_buyer("b1")
    b2_id, b2_token = _create_buyer("b2")

    lot_res = client.post(
        "/api/v1/farmer/future-crop-lots",
        headers={"Authorization": f"Bearer {f_token}"},
        json={
            "farm_id": farm_id,
            "crop_id": 1,
            "planned_acres": 5.0,
            "expected_quantity_quintals": 100.0,
            "asking_price_per_quintal": 4500.0,
            "planned_sowing_date": "2026-06-01",
            "expected_harvest_start": "2026-09-15",
            "expected_harvest_end": "2026-10-01",
            "status": "OPEN"
        }
    )
    bid1 = client.post("/api/v1/bids", headers={"Authorization": f"Bearer {b1_token}"}, json={"future_crop_lot_id": lot_res.json()["id"], "offered_price_per_quintal": 4600.0, "quantity_quintals": 50.0}).json()["id"]
    bid2 = client.post("/api/v1/bids", headers={"Authorization": f"Bearer {b2_token}"}, json={"future_crop_lot_id": lot_res.json()["id"], "offered_price_per_quintal": 4700.0, "quantity_quintals": 50.0}).json()["id"]

    res = client.post(f"/api/v1/bids/{bid2}/accept", headers={"Authorization": f"Bearer {f_token}"})
    assert res.status_code == 200

    b2_resp = client.get("/api/v1/bids/me", headers={"Authorization": f"Bearer {b2_token}"}).json()[0]
    assert b2_resp["status"] == "ACCEPTED"

    b1_resp = client.get("/api/v1/bids/me", headers={"Authorization": f"Bearer {b1_token}"}).json()[0]
    assert b1_resp["status"] == "REJECTED"
