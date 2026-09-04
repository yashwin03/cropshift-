"""
test_peer_proof.py -- Unit tests for Peer-Proof Engine.
"""
import pytest
from app.models.peer_proof import PeerProof
from app.services.peer_proof_service import get_peer_proof_for_crop, request_peer_contact


def test_peer_proof_same_district(db_session):
    # Groundnut (crop_id=2) has seeded records in Karnataka cluster
    res = get_peer_proof_for_crop(db_session, crop_id=2, district="Tumkur", land_area_acres=2.0, radius_km=100.0)
    assert res["available"] is True
    assert res["cohort_count"] >= 1
    assert res["crop_name"] == "Groundnut"
    assert res["average_yield_quintals_per_acre"] > 0
    assert res["average_selling_price_per_quintal"] > 0
    assert res["average_net_realization_per_acre"] > 0
    assert res["data_source"] == "CropShift demo dataset"
    assert res["verification_status"] == "Demo data — not real farmer verification"


def test_peer_proof_nearby_district_fallback(db_session):
    # Sunflower (crop_id=3) spatial distance filter test
    p1 = PeerProof(crop_id=3, district="Dharwad", state="Karnataka", latitude=15.4589, longitude=75.0078, yield_quintals_per_acre=7.0, selling_price_per_quintal=5000.0, cultivated_area_acres=2.0)
    p2 = PeerProof(crop_id=3, district="Belagavi", state="Karnataka", latitude=15.8497, longitude=74.5085, yield_quintals_per_acre=7.2, selling_price_per_quintal=5100.0, cultivated_area_acres=2.0)
    p3 = PeerProof(crop_id=3, district="Belagavi", state="Karnataka", latitude=15.8497, longitude=74.5085, yield_quintals_per_acre=7.5, selling_price_per_quintal=5200.0, cultivated_area_acres=2.0)
    db_session.add_all([p1, p2, p3])
    db_session.commit()

    res = get_peer_proof_for_crop(db_session, crop_id=3, district="Dharwad", land_area_acres=2.0, radius_km=100.0)
    assert res["available"] is True
    assert res["cohort_count"] >= 1


def test_peer_proof_insufficient_cohort_returns_unavailable(db_session):
    # Query for crop_id=999 (Non-existent crop) in district with no records in 5km
    res = get_peer_proof_for_crop(db_session, crop_id=999, district="RareDistrict", land_area_acres=1.0, radius_km=5.0, latitude=28.6139, longitude=77.2090)
    assert res["available"] is False
    assert res["cohort_count"] == 0
    assert "no verified peer records" in res["message"].lower()


def test_peer_proof_privacy_no_private_contacts_in_get(client, farmer_user_token):
    token = farmer_user_token["token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/peer-proof/2?district=Tumkur&radius_km=100", headers=headers)
    assert response.status_code == 200
    data = response.json()

    assert data["available"] is True
    assert "contact_phone" not in data
    assert "contact_email" not in data

    if data.get("peers"):
        for p in data["peers"]:
            assert "contact_phone" not in p
            assert "contact_email" not in p
            assert "peer_display_id" in p


def test_peer_contact_request_flow(client, farmer_user_token, db_session):
    token = farmer_user_token["token"]
    headers = {"Authorization": f"Bearer {token}"}

    rec = db_session.query(PeerProof).filter(PeerProof.contactable == True).first()
    assert rec is not None

    response = client.post(
        "/api/v1/peer-proof/contact-request",
        json={"peer_proof_id": rec.id},
        headers=headers
    )
    assert response.status_code == 200
    contact_data = response.json()
    assert contact_data["contactable"] is True
    assert "phone" in contact_data
    assert "email" in contact_data


def test_peer_contact_request_fails_for_non_contactable(client, farmer_user_token, db_session):
    token = farmer_user_token["token"]
    headers = {"Authorization": f"Bearer {token}"}

    rec = PeerProof(
        crop_id=2,
        district="TumkurTest",
        contactable=False,
        yield_quintals_per_acre=8.0,
        selling_price_per_quintal=5500.0,
        cultivated_area_acres=1.0
    )
    db_session.add(rec)
    db_session.commit()
    db_session.refresh(rec)

    response = client.post(
        "/api/v1/peer-proof/contact-request",
        json={"peer_proof_id": rec.id},
        headers=headers
    )
    assert response.status_code == 400
    assert "not contactable" in str(response.json()).lower()


def test_seed_peer_proof_provenance_labels(db_session):
    """
    Verify that all seeded PeerProof records use the correct demo/synthetic
    provenance labels.
    """
    seeded_records = db_session.query(PeerProof).all()
    assert len(seeded_records) >= 34, "Expected at least 34 seeded PeerProof records"

    for rec in seeded_records:
        if rec.id <= 70:
            assert rec.verification_status == "Demo data — not real farmer verification"
