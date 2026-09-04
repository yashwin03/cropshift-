"""
test_crop_cultivation.py -- Tests for Crop Cultivation Record system and API endpoints.
"""
import pytest
from app.models.user import User, UserRole
from app.models.farm import Farm
from app.models.crop import Crop, CropType
from app.models.crop_cultivation import CropCultivationRecord, CultivationStage, EvidenceStatus
from app.main import app
from app.api.v1.auth import get_current_user
from app.services.peer_proof_service import get_peer_proof_for_crop


from app.database.session import get_db


@pytest.fixture
def seed_test_env(db_session):
    """Seed crops, farmers, and farms for testing."""
    app.dependency_overrides[get_db] = lambda: db_session
    crop_gn = db_session.query(Crop).filter_by(name="Groundnut").first()
    if not crop_gn:
        crop_gn = Crop(id=2, name="Groundnut", crop_type=CropType.OILSEED, season="Kharif", water_requirement="MEDIUM", is_oilseed=True)
        db_session.add(crop_gn)

    crop_sf = db_session.query(Crop).filter_by(name="Sunflower").first()
    if not crop_sf:
        crop_sf = Crop(id=3, name="Sunflower", crop_type=CropType.OILSEED, season="Rabi", water_requirement="MEDIUM", is_oilseed=True)
        db_session.add(crop_sf)

    db_session.commit()

    from app.models.farmer import Farmer

    farmer1 = db_session.query(User).filter_by(username="test_farmer_1").first()
    if not farmer1:
        farmer1 = User(username="test_farmer_1", email="farmer1_cult@test.com", hashed_password="mock_hashed_password", role=UserRole.FARMER)
        db_session.add(farmer1)
        db_session.commit()
        db_session.refresh(farmer1)

    farmer2 = db_session.query(User).filter_by(username="test_farmer_2").first()
    if not farmer2:
        farmer2 = User(username="test_farmer_2", email="farmer2_cult@test.com", hashed_password="mock_hashed_password", role=UserRole.FARMER)
        db_session.add(farmer2)
        db_session.commit()
        db_session.refresh(farmer2)

    buyer1 = db_session.query(User).filter_by(username="test_buyer_1").first()
    if not buyer1:
        buyer1 = User(username="test_buyer_1", email="buyer1_cult@test.com", hashed_password="mock_hashed_password", role=UserRole.BUYER)
        db_session.add(buyer1)
        db_session.commit()
        db_session.refresh(buyer1)

    farmer_rec1 = db_session.query(Farmer).filter_by(id=farmer1.id).first()
    if not farmer_rec1:
        farmer_rec1 = Farmer(id=farmer1.id, name="test_farmer_1", district="Dharwad", state="Karnataka")
        db_session.add(farmer_rec1)

    farmer_rec2 = db_session.query(Farmer).filter_by(id=farmer2.id).first()
    if not farmer_rec2:
        farmer_rec2 = Farmer(id=farmer2.id, name="test_farmer_2", district="Shivamogga", state="Karnataka")
        db_session.add(farmer_rec2)

    db_session.commit()

    farm1 = db_session.query(Farm).filter_by(farmer_id=farmer1.id).first()
    if not farm1:
        farm1 = Farm(farmer_id=farmer1.id, land_area_acre=2.5, district="Dharwad", state="Karnataka", owner_id=farmer1.id)
        db_session.add(farm1)

    farm2 = db_session.query(Farm).filter_by(farmer_id=farmer2.id).first()
    if not farm2:
        farm2 = Farm(farmer_id=farmer2.id, land_area_acre=4.0, district="Shivamogga", state="Karnataka", owner_id=farmer2.id)
        db_session.add(farm2)

    db_session.commit()
    return {"farmer1": farmer1, "farmer2": farmer2, "buyer1": buyer1, "crop_gn": crop_gn, "crop_sf": crop_sf, "farm1": farm1, "farm2": farm2}


from fastapi import HTTPException, status


def test_create_and_retrieve_cultivation_record(client, db_session, seed_test_env):
    """1 & 2 & 5. Farmer can create and retrieve own cultivation record."""
    farmer1 = seed_test_env["farmer1"]
    farm1 = seed_test_env["farm1"]
    gn_id = seed_test_env["crop_gn"].id

    app.dependency_overrides[get_current_user] = lambda: farmer1

    create_payload = {
        "farm_id": farm1.id,
        "crop_id": gn_id,
        "variety": "TMV-2",
        "area_acres": 2.5,
        "cultivation_stage": "GROWING",
        "sowing_date": "2025-06-15",
        "expected_harvest_date": "2025-10-15",
        "expected_yield_quintals": 25.0,
        "notes": "Good rainfed soil condition"
    }

    res = client.post("/api/v1/cultivation-records", json=create_payload)
    assert res.status_code == 201
    data = res.json()
    assert data["crop_name"] == "Groundnut"
    assert data["cultivation_stage"] == "GROWING"
    assert data["expected_yield_quintals"] == 25.0
    record_id = data["id"]

    # Retrieve list
    list_res = client.get("/api/v1/cultivation-records")
    assert list_res.status_code == 200
    records = list_res.json()
    assert len(records) >= 1
    assert any(r["id"] == record_id for r in records)


def test_farmer_cannot_access_other_record(client, db_session, seed_test_env):
    """3. Farmer cannot update or delete another farmer's record."""
    farmer1 = seed_test_env["farmer1"]
    farmer2 = seed_test_env["farmer2"]
    farm1 = seed_test_env["farm1"]
    gn_id = seed_test_env["crop_gn"].id

    rec = CropCultivationRecord(
        farmer_id=farmer1.id,
        farm_id=farm1.id,
        crop_id=gn_id,
        crop_name="Groundnut",
        area_acres=2.0,
        cultivation_stage=CultivationStage.GROWING,
        evidence_status=EvidenceStatus.FARMER_DECLARED
    )
    db_session.add(rec)
    db_session.commit()

    app.dependency_overrides[get_current_user] = lambda: farmer2

    get_res = client.get(f"/api/v1/cultivation-records/{rec.id}")
    assert get_res.status_code == 403

    put_res = client.put(f"/api/v1/cultivation-records/{rec.id}", json={"area_acres": 10.0})
    assert put_res.status_code == 403

    del_res = client.delete(f"/api/v1/cultivation-records/{rec.id}")
    assert del_res.status_code == 403


def test_buyer_cannot_create_cultivation_record(client, db_session, seed_test_env):
    """4. Buyer cannot create cultivation records (returns 403)."""
    buyer1 = seed_test_env["buyer1"]
    farm1 = seed_test_env["farm1"]
    gn_id = seed_test_env["crop_gn"].id

    app.dependency_overrides[get_current_user] = lambda: buyer1

    create_payload = {
        "farm_id": farm1.id,
        "crop_id": gn_id,
        "area_acres": 2.0,
        "cultivation_stage": "GROWING"
    }

    res = client.post("/api/v1/cultivation-records", json=create_payload)
    assert res.status_code == 403


def test_stage_transitions_and_actual_harvest_preservation(client, db_session, seed_test_env):
    """6 & 7. Lifecycle stage moves and actual harvest preserves expected yield."""
    farmer1 = seed_test_env["farmer1"]
    farm1 = seed_test_env["farm1"]
    gn_id = seed_test_env["crop_gn"].id

    rec = CropCultivationRecord(
        farmer_id=farmer1.id,
        farm_id=farm1.id,
        crop_id=gn_id,
        crop_name="Groundnut",
        area_acres=2.0,
        expected_yield_quintals=24.0,
        cultivation_stage=CultivationStage.PLANNED,
        evidence_status=EvidenceStatus.FARMER_DECLARED
    )
    db_session.add(rec)
    db_session.commit()

    app.dependency_overrides[get_current_user] = lambda: farmer1

    upd1 = client.put(f"/api/v1/cultivation-records/{rec.id}", json={"cultivation_stage": "GROWING"})
    assert upd1.status_code == 200
    assert upd1.json()["cultivation_stage"] == "GROWING"

    upd2 = client.put(f"/api/v1/cultivation-records/{rec.id}", json={"cultivation_stage": "READY_FOR_HARVEST"})
    assert upd2.status_code == 200
    assert upd2.json()["cultivation_stage"] == "READY_FOR_HARVEST"

    harvest_res = client.post(f"/api/v1/cultivation-records/{rec.id}/harvest", json={"actual_harvest_quantity_quintals": 21.5, "notes": "Dry spell reduced yield slightly"})
    assert harvest_res.status_code == 200
    hdata = harvest_res.json()

    assert hdata["cultivation_stage"] == "HARVESTED"
    assert hdata["actual_harvest_quantity_quintals"] == 21.5
    assert hdata["expected_yield_quintals"] == 24.0


def test_peer_query_filters_by_crop_and_excludes_planned(db_session, seed_test_env):
    """8 & 9. Peer proof queries only matching crop and excludes PLANNED records."""
    gn_id = seed_test_env["crop_gn"].id
    sf_id = seed_test_env["crop_sf"].id
    farmer1_id = seed_test_env["farmer1"].id
    farm1_id = seed_test_env["farm1"].id
    farmer2_id = seed_test_env["farmer2"].id
    farm2_id = seed_test_env["farm2"].id

    rec1 = CropCultivationRecord(
        farmer_id=farmer1_id, farm_id=farm1_id, crop_id=gn_id, crop_name="Groundnut", area_acres=3.0, cultivation_stage=CultivationStage.GROWING
    )
    rec2 = CropCultivationRecord(
        farmer_id=farmer2_id, farm_id=farm2_id, crop_id=gn_id, crop_name="Groundnut", area_acres=2.0, cultivation_stage=CultivationStage.PLANNED
    )
    rec3 = CropCultivationRecord(
        farmer_id=farmer2_id, farm_id=farm2_id, crop_id=sf_id, crop_name="Sunflower", area_acres=4.0, cultivation_stage=CultivationStage.GROWING
    )
    db_session.add_all([rec1, rec2, rec3])
    db_session.commit()

    gn_peer = get_peer_proof_for_crop(db_session, crop_id=gn_id, district="Dharwad", radius_km=100.0)
    assert gn_peer["available"] is True
    peer_ids = [p["id"] for p in gn_peer["peers"]]
    assert (rec1.id + 10000) in peer_ids
    assert (rec2.id + 10000) not in peer_ids
    assert (rec3.id + 10000) not in peer_ids

    sf_peer = get_peer_proof_for_crop(db_session, crop_id=sf_id, district="Shivamogga", radius_km=100.0)
    assert sf_peer["available"] is True
    sf_peer_ids = [p["id"] for p in sf_peer["peers"]]
    assert (rec3.id + 10000) in sf_peer_ids
    assert (rec1.id + 10000) not in sf_peer_ids


def test_cannot_add_crop_to_other_farmers_farm(client, db_session, seed_test_env):
    """Authenticated farmer cannot add crop to another farmer's farm (403)."""
    farmer1 = seed_test_env["farmer1"]
    farm2 = seed_test_env["farm2"]
    gn_id = seed_test_env["crop_gn"].id

    app.dependency_overrides[get_current_user] = lambda: farmer1

    payload = {
        "farm_id": farm2.id,
        "crop_id": gn_id,
        "area_acres": 2.5,
        "cultivation_stage": "GROWING"
    }

    res = client.post("/api/v1/cultivation-records", json=payload)
    assert res.status_code == 403
    assert "You can only add crops to farms you own." in res.json()["detail"]


def test_unauthenticated_crop_addition_rejected(client, seed_test_env):
    """Unauthenticated request to add crop is rejected with 401."""
    gn_id = seed_test_env["crop_gn"].id
    farm1 = seed_test_env["farm1"]

    def raise_unauth():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

    app.dependency_overrides[get_current_user] = raise_unauth

    payload = {
        "farm_id": farm1.id,
        "crop_id": gn_id,
        "area_acres": 2.5,
        "cultivation_stage": "GROWING"
    }
    res = client.post("/api/v1/cultivation-records", json=payload)
    assert res.status_code == 401


def test_invalid_farm_id_rejected(client, seed_test_env):
    """Non-existent farm ID request is rejected with 404."""
    farmer1 = seed_test_env["farmer1"]
    gn_id = seed_test_env["crop_gn"].id

    app.dependency_overrides[get_current_user] = lambda: farmer1

    payload = {
        "farm_id": 999999,
        "crop_id": gn_id,
        "area_acres": 2.5,
        "cultivation_stage": "GROWING"
    }
    res = client.post("/api/v1/cultivation-records", json=payload)
    assert res.status_code == 404


def test_farmer_identity_derived_from_jwt_auto_selects_owned_farm(client, seed_test_env):
    """Omitting farm_id derives farmer identity from JWT and selects owned farm."""
    farmer1 = seed_test_env["farmer1"]
    farm1 = seed_test_env["farm1"]
    gn_id = seed_test_env["crop_gn"].id

    app.dependency_overrides[get_current_user] = lambda: farmer1

    payload = {
        "crop_id": gn_id,
        "area_acres": 3.0,
        "cultivation_stage": "GROWING"
    }
    res = client.post("/api/v1/cultivation-records", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["farmer_id"] == farmer1.id
    assert data["farm_id"] == farm1.id

