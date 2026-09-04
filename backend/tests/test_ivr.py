"""
test_ivr.py -- A13 acceptance tests for IVR engine and endpoint.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.database.session import SessionLocal
from app.database.init_db import init_db
from app.database.seed import seed_db

client = TestClient(app)


@pytest.fixture(scope="module")
def db() -> Session:
    init_db()
    session = SessionLocal()
    seed_db(session)
    yield session
    session.close()


def test_ivr_recommendation_matches_web(db: Session):
    from app.api.v1.auth import create_access_token
    token = create_access_token(data={"sub": "testuser", "user_id": 1, "role": "FARMER"})
    headers = {"Authorization": f"Bearer {token}"}

    # Fetch Web Recommendation response
    web_res = client.post("/api/v1/recommendations", json={"farm_id": 1}, headers=headers)
    assert web_res.status_code == 200
    web_data = web_res.json()

    # Fetch IVR Recommendation response
    ivr_res = client.post("/api/v1/ivr/recommendation", json={"farmer_id": 1})
    assert ivr_res.status_code == 200
    ivr_data = ivr_res.json()

    # Verify matching recommendation
    assert ivr_data["verified"] is True
    assert ivr_data["farmer_name"] == "Raju Naik"
    
    rec_web = web_data
    rec_ivr = ivr_data["recommendation"]
    
    assert rec_ivr["recommended_crop"] == rec_web["recommended_crop"]
    assert rec_ivr["safety_score"] == rec_web["safety_score"]
    assert rec_ivr["profit_difference"] == rec_web["profit_difference"]


def test_ivr_voice_script_format():
    ivr_res = client.post("/api/v1/ivr/recommendation", json={"farmer_id": 1})
    assert ivr_res.status_code == 200
    ivr_data = ivr_res.json()
    
    script = ivr_data["voice_script"]
    assert script is not None
    assert "Namaste Raju Naik" in script
    assert "groundnut" in script.lower()
    
    # Check natural numbers spelling instead of digits
    assert "eighty two" in script.lower()
    assert "nine thousand" in script.lower()
    assert "one" in script.lower()
    
    # Check under 45 words
    words = script.split()
    assert len(words) <= 45


def test_ivr_unknown_farmer():
    res = client.post("/api/v1/ivr/recommendation", json={"farmer_id": 9999})
    assert res.status_code == 200
    data = res.json()
    
    assert data["verified"] is False
    assert data["recommendation"] is None
    assert "could not verify" in data["voice_script"].lower()

def test_ivr_webhook_incoming():
    res = client.post("/api/v1/ivr/webhook/incoming", data={"CallSid": "test1234", "From": "+919999999999"})
    assert res.status_code == 200
    assert res.headers["content-type"] == "text/xml; charset=utf-8"
    xml = res.text
    assert "<Response>" in xml
    assert "Gather" in xml
    assert "namaste" in xml.lower() or "swagat" in xml.lower() or "kare" in xml.lower()

def test_ivr_webhook_menu_digit_1():
    client.post("/api/v1/ivr/webhook/incoming", data={"CallSid": "test1234", "From": "+919999999999"})
    res = client.post("/api/v1/ivr/webhook/menu", data={"CallSid": "test1234", "From": "+919999999999", "Digits": "1"})
    assert res.status_code == 200
    xml = res.text
    assert "groundnut" in xml.lower() or "shifaris" in xml.lower()

def test_ivr_webhook_menu_digit_2():
    res = client.post("/api/v1/ivr/webhook/menu", data={"CallSid": "test1234", "From": "+919999999999", "Digits": "2"})
    assert res.status_code == 200
    xml = res.text
    assert "6200" in xml or "mandi" in xml.lower() or "market" in xml.lower()


def test_ivr_webhook_menu_language_selection():
    res = client.post("/api/v1/ivr/webhook/menu", data={"CallSid": "test1234", "From": "+919999999999", "Digits": "8"})
    assert res.status_code == 200
    xml = res.text
    assert "hindi" in xml.lower()
    assert "english" in xml.lower()

def test_ivr_webhook_menu_repeat():
    res = client.post("/api/v1/ivr/webhook/menu", data={"CallSid": "test1234", "From": "+919999999999", "Digits": "9"})
    assert res.status_code == 200
    xml = res.text
    assert "namaste" in xml.lower() or "swagat" in xml.lower() or "welcome" in xml.lower()

def test_ivr_webhook_menu_exit():
    res = client.post("/api/v1/ivr/webhook/menu", data={"CallSid": "test1234", "From": "+919999999999", "Digits": "0"})
    assert res.status_code == 200
    xml = res.text
    assert "<Hangup/>" in xml

def test_ivr_webhook_menu_unknown_digit():
    res = client.post("/api/v1/ivr/webhook/menu", data={"CallSid": "test1234", "From": "+919999999999", "Digits": "5"})
    assert res.status_code == 200
    xml = res.text
    assert "asatyapith" in xml.lower() or "invalid" in xml.lower() or "anya chayan" in xml.lower()

def test_ivr_webhook_missing_data():
    res = client.post("/api/v1/ivr/webhook/incoming", data={"From": "+919999999999"})
    assert res.status_code == 422

def test_ivr_webhook_absolute_url(monkeypatch):
    from app.config import settings
    monkeypatch.setattr(settings, "IVR_BASE_URL", "https://cropshift-demo.ngrok-free.app")
    res = client.post("/api/v1/ivr/webhook/incoming", data={"CallSid": "abs_test_123", "From": "+919999999999"})
    assert res.status_code == 200
    xml = res.text
    assert 'action="https://cropshift-demo.ngrok-free.app/api/v1/ivr/webhook/menu"' in xml

def test_ivr_webhook_multilingual_responses():
    # 1. Initialize session with Hindi
    client.post("/api/v1/ivr/webhook/incoming", data={"CallSid": "multi_lang_sid", "From": "+919999999999"})
    
    # 2. Select Kannada via Language Menu (Digit 8 -> Digit 2)
    client.post("/api/v1/ivr/webhook/menu", data={"CallSid": "multi_lang_sid", "From": "+919999999999", "Digits": "8"})
    res_kn = client.post("/api/v1/ivr/webhook/menu", data={"CallSid": "multi_lang_sid", "From": "+919999999999", "Digits": "2"})
    assert res_kn.status_code == 200
    assert 'language="kn-IN"' in res_kn.text
    assert "CropShift" in res_kn.text
    
    # 3. Select English via Language Menu (Digit 8 -> Digit 3)
    client.post("/api/v1/ivr/webhook/menu", data={"CallSid": "multi_lang_sid", "From": "+919999999999", "Digits": "8"})
    res_en = client.post("/api/v1/ivr/webhook/menu", data={"CallSid": "multi_lang_sid", "From": "+919999999999", "Digits": "3"})
    assert res_en.status_code == 200
    assert 'language="en-IN"' in res_en.text
    assert "Welcome" in res_en.text

def test_ivr_demo_predefined_responses():
    # Setup session with English language
    client.post("/api/v1/ivr/webhook/incoming", data={"CallSid": "demo_test_sid", "From": "+919999999999"})
    client.post("/api/v1/ivr/webhook/menu", data={"CallSid": "demo_test_sid", "From": "+919999999999", "Digits": "8"})
    client.post("/api/v1/ivr/webhook/menu", data={"CallSid": "demo_test_sid", "From": "+919999999999", "Digits": "3"})
    
    # Digit 1: Predefined Recommendation
    r1 = client.post("/api/v1/ivr/webhook/menu", data={"CallSid": "demo_test_sid", "From": "+919999999999", "Digits": "1"})
    assert "100 to 120 days" in r1.text
    
    # Digit 2: Predefined Market Price
    r2 = client.post("/api/v1/ivr/webhook/menu", data={"CallSid": "demo_test_sid", "From": "+919999999999", "Digits": "2"})
    assert "6200 rupees per quintal" in r2.text
    
    # Digit 3: Predefined Subsidy
    r3 = client.post("/api/v1/ivr/webhook/menu", data={"CallSid": "demo_test_sid", "From": "+919999999999", "Digits": "3"})
    assert "PM-KISAN" in r3.text


