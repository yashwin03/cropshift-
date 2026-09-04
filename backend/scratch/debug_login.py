import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import app.patch_bcrypt
import urllib.request
import urllib.parse
import json

def test_backend():
    print("=== 1. VERIFY BACKEND REACHABILITY ===")
    endpoints = [
        "http://127.0.0.1:8000/health",
        "http://localhost:8000/health",
        "http://127.0.0.1:8000/docs",
        "http://localhost:8000/docs",
    ]
    for url in endpoints:
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=3) as resp:
                body = resp.read().decode('utf-8')
                print(f"GET {url} -> Status: {resp.status}, Response: {body[:100]}")
        except urllib.error.HTTPError as e:
            body = e.read().decode('utf-8')
            print(f"GET {url} -> Status: {e.code}, Response: {body[:100]}")
        except Exception as e:
            print(f"GET {url} -> ERROR: {e}")

def test_demo_user_db():
    print("\n=== 6. VERIFY DEMO USER IN DATABASE ===")
    from app.database.session import SessionLocal
    from app.models.user import User, UserRole
    from app.api.v1.auth import verify_password, get_password_hash

    db = SessionLocal()
    try:
        farmer = db.query(User).filter(User.username == "demo").first()
        if farmer:
            print(f"Farmer 'demo' found in DB: id={farmer.id}, username={farmer.username}, role={farmer.role}, farmer_id={farmer.farmer_id}")
            valid_pw = verify_password("password123", farmer.hashed_password)
            print(f"Password 'password123' verification result: {valid_pw}")
            if not valid_pw:
                print("Resetting 'demo' password hash to 'password123'...")
                farmer.hashed_password = get_password_hash("password123")
                db.commit()
                print("Updated 'demo' password hash.")
        else:
            print("Farmer 'demo' NOT found in DB. Creating 'demo' user...")
            new_farmer = User(
                username="demo",
                email="demo@cropshift.com",
                hashed_password=get_password_hash("password123"),
                role=UserRole.FARMER,
                farmer_id="FS-000001"
            )
            db.add(new_farmer)
            db.commit()
            print("Created farmer 'demo' in DB.")

        buyer = db.query(User).filter(User.username == "buyer_demo").first()
        if buyer:
            print(f"Buyer 'buyer_demo' found in DB: id={buyer.id}, username={buyer.username}, role={buyer.role}")
            valid_pw = verify_password("password123", buyer.hashed_password)
            print(f"Password 'password123' verification result: {valid_pw}")
            if not valid_pw:
                print("Resetting 'buyer_demo' password hash to 'password123'...")
                buyer.hashed_password = get_password_hash("password123")
                db.commit()
                print("Updated 'buyer_demo' password hash.")
        else:
            print("Buyer 'buyer_demo' NOT found in DB. Creating 'buyer_demo' user...")
            new_buyer = User(
                username="buyer_demo",
                email="buyer_demo@cropshift.com",
                hashed_password=get_password_hash("password123"),
                role=UserRole.BUYER
            )
            db.add(new_buyer)
            db.commit()
            print("Created buyer 'buyer_demo' in DB.")
    finally:
        db.close()

def test_login_endpoint(base="http://127.0.0.1:8000"):
    print(f"\n=== 4. TEST BACKEND TOKEN ENDPOINT ({base}) ===")
    url = f"{base}/api/v1/auth/token"
    payload = urllib.parse.urlencode({"username": "demo", "password": "password123"}).encode('utf-8')
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    try:
        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=5) as resp:
            body = resp.read().decode('utf-8')
            print(f"POST {url} -> Status: {resp.status}")
            print(f"Response Body: {body}")
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8')
        print(f"POST {url} -> Status: {e.code}, Response: {body}")
    except Exception as e:
        print(f"POST {url} -> ERROR: {e}")

if __name__ == "__main__":
    test_backend()
    test_demo_user_db()
    test_login_endpoint("http://127.0.0.1:8000")
    test_login_endpoint("http://localhost:8000")
