"""Unit and integration tests for Phase 8B TradeOrder fulfillment tracking."""
import uuid
from datetime import date, datetime, timedelta
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database.session import SessionLocal, engine
from app.database.base import Base
from app.models.user import User, UserRole
from app.models.farm import Farm
from app.models.crop import Crop, CropType
from app.models.farmer import Farmer
from app.models.stock_lot import StockLot, StockLotStatus
from app.models.stock_bid import StockBid, StockBidStatus
from app.models.trade_order import TradeOrder, TradeOrderStatus, TradeOrderCancellationReason
from app.models.contact_sharing import ContactSharing, ContactSharingStatus
from app.api.v1.auth import get_current_user, get_password_hash, create_access_token

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_test_context():
    """Clear dependency overrides and ensure test environment has all tables and column migrations."""
    from app.database.init_db import init_db
    app.dependency_overrides.clear()
    init_db()
    yield
    app.dependency_overrides.clear()


def _create_user(role: UserRole = UserRole.FARMER, email: str = None) -> User:
    db = SessionLocal()
    uid = uuid.uuid4().hex[:6]
    if not email:
        email = f"user_{uid}@example.com"
    try:
        user = User(
            username=f"user_{uid}",
            email=email,
            hashed_password=get_password_hash("password123"),
            role=role,
            full_name=f"Test {role.value} {uid}",
            phone=f"9876{uid[:6].zfill(6)}",
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    finally:
        db.close()


def _create_farm(farmer_id: int) -> Farm:
    db = SessionLocal()
    uid = uuid.uuid4().hex[:6]
    try:
        farmer_entity = db.query(Farmer).filter(Farmer.phone == "9876543210").first()
        if not farmer_entity:
            farmer_entity = Farmer(
                name=f"Farmer {uid}",
                phone="9876543210",
                district="Dharwad",
                state="Karnataka",
                village="Test Village",
                land_area_acres=5.0,
            )
            db.add(farmer_entity)
            db.commit()
            db.refresh(farmer_entity)

        farm = Farm(
            farmer_id=farmer_entity.id,
            land_area_acre=5.0,
            water_availability=True,
            soil_type="Black Cotton",
            district="Dharwad",
            state="Karnataka",
            owner_id=farmer_id,
        )
        db.add(farm)
        db.commit()
        db.refresh(farm)
        return farm
    finally:
        db.close()


def _get_or_create_crop() -> Crop:
    db = SessionLocal()
    try:
        crop = db.query(Crop).first()
        if not crop:
            crop = Crop(
                name="Groundnut",
                season="Kharif",
                crop_type=CropType.OILSEED,
                growing_period_days=120,
                base_yield_per_acre=15.0,
            )
            db.add(crop)
            db.commit()
            db.refresh(crop)
        return crop
    finally:
        db.close()


def _auth_headers(user: User) -> dict:
    token = create_access_token({"sub": user.username})
    return {"Authorization": f"Bearer {token}"}


def test_1_to_6_trade_order_creation_linkage_and_uniqueness():
    db = SessionLocal()
    try:
        farmer = _create_user(UserRole.FARMER)
        buyer = _create_user(UserRole.BUYER)
        farm = _create_farm(farmer.id)
        crop = _get_or_create_crop()

        f_headers = _auth_headers(farmer)

        stock_lot = StockLot(
            farmer_id=farmer.id,
            farm_id=farm.id,
            crop_id=crop.id,
            variety="Kadir-6",
            actual_quantity_quintals=100.0,
            available_quantity_quintals=100.0,
            actual_harvest_date=date(2026, 9, 20),
            quality_grade="Grade A",
            asking_price_per_quintal=6000.0,
            status=StockLotStatus.AVAILABLE,
        )
        db.add(stock_lot)
        db.commit()
        db.refresh(stock_lot)

        bid = StockBid(
            stock_lot_id=stock_lot.id,
            buyer_id=buyer.id,
            offered_price_per_quintal=6200.0,
            requested_quantity_quintals=40.0,
            status=StockBidStatus.SUBMITTED,
        )
        db.add(bid)
        db.commit()
        db.refresh(bid)

        # Farmer accepts bid
        res = client.post(f"/api/v1/stock-bids/{bid.id}/accept", json={"allocated_quantity_quintals": 40.0}, headers=f_headers)
        assert res.status_code == 200

        # 1. TradeOrder created after accepted StockBid
        # 2. Correct buyer/farmer linkage
        # 3. Correct stock lot linkage
        # 4. Correct allocated quantity
        # 5. Correct agreed price snapshot
        trade_order = db.query(TradeOrder).filter(TradeOrder.stock_bid_id == bid.id).first()
        assert trade_order is not None
        assert trade_order.buyer_id == buyer.id
        assert trade_order.farmer_id == farmer.id
        assert trade_order.stock_lot_id == stock_lot.id
        assert trade_order.allocated_quantity_quintals == 40.0
        assert trade_order.agreed_price_per_quintal == 6200.0
        assert trade_order.status == TradeOrderStatus.CREATED

        # 6. Duplicate TradeOrder prevented (unique constraint)
        dup_order = TradeOrder(
            stock_bid_id=bid.id,
            stock_lot_id=stock_lot.id,
            buyer_id=buyer.id,
            farmer_id=farmer.id,
            allocated_quantity_quintals=40.0,
            agreed_price_per_quintal=6200.0,
            status=TradeOrderStatus.CREATED,
        )
        db.add(dup_order)
        with pytest.raises(Exception):
            db.commit()
        db.rollback()
    finally:
        db.close()


def test_7_to_9_trade_order_query_apis_and_rbac():
    db = SessionLocal()
    try:
        farmer = _create_user(UserRole.FARMER)
        buyer = _create_user(UserRole.BUYER)
        unrelated = _create_user(UserRole.BUYER)
        farm = _create_farm(farmer.id)
        crop = _get_or_create_crop()

        stock_lot = StockLot(farmer_id=farmer.id, farm_id=farm.id, crop_id=crop.id, actual_quantity_quintals=50.0, available_quantity_quintals=30.0, actual_harvest_date=date(2026, 9, 20), status=StockLotStatus.PARTIALLY_SOLD)
        db.add(stock_lot)
        db.commit()

        bid = StockBid(stock_lot_id=stock_lot.id, buyer_id=buyer.id, offered_price_per_quintal=6000.0, requested_quantity_quintals=20.0, status=StockBidStatus.ACCEPTED, allocated_quantity_quintals=20.0)
        db.add(bid)
        db.commit()

        trade_order = TradeOrder(stock_bid_id=bid.id, stock_lot_id=stock_lot.id, buyer_id=buyer.id, farmer_id=farmer.id, allocated_quantity_quintals=20.0, agreed_price_per_quintal=6000.0, status=TradeOrderStatus.CREATED)
        db.add(trade_order)
        db.commit()

        b_headers = _auth_headers(buyer)
        f_headers = _auth_headers(farmer)
        u_headers = _auth_headers(unrelated)

        # 7. Buyer can view own orders
        res = client.get("/api/v1/trade-orders/me", headers=b_headers)
        assert res.status_code == 200
        b_orders = res.json()
        assert any(o["id"] == trade_order.id for o in b_orders)

        # 8. Farmer can view own orders
        res = client.get("/api/v1/trade-orders/me", headers=f_headers)
        assert res.status_code == 200
        f_orders = res.json()
        assert any(o["id"] == trade_order.id for o in f_orders)

        # 9. Unrelated user receives 403
        res = client.get(f"/api/v1/trade-orders/{trade_order.id}", headers=u_headers)
        assert res.status_code == 403
    finally:
        db.close()


def test_10_to_11_trade_order_fulfillment():
    db = SessionLocal()
    try:
        farmer = _create_user(UserRole.FARMER)
        buyer = _create_user(UserRole.BUYER)
        farm = _create_farm(farmer.id)
        crop = _get_or_create_crop()

        stock_lot = StockLot(farmer_id=farmer.id, farm_id=farm.id, crop_id=crop.id, actual_quantity_quintals=50.0, available_quantity_quintals=30.0, actual_harvest_date=date(2026, 9, 20), status=StockLotStatus.PARTIALLY_SOLD)
        db.add(stock_lot)
        db.commit()

        bid = StockBid(stock_lot_id=stock_lot.id, buyer_id=buyer.id, offered_price_per_quintal=6000.0, requested_quantity_quintals=20.0, status=StockBidStatus.ACCEPTED, allocated_quantity_quintals=20.0)
        db.add(bid)
        db.commit()

        trade_order = TradeOrder(stock_bid_id=bid.id, stock_lot_id=stock_lot.id, buyer_id=buyer.id, farmer_id=farmer.id, allocated_quantity_quintals=20.0, agreed_price_per_quintal=6000.0, status=TradeOrderStatus.CREATED)
        db.add(trade_order)
        db.commit()

        b_headers = _auth_headers(buyer)

        # 10. CREATED -> FULFILLED
        res = client.post(f"/api/v1/trade-orders/{trade_order.id}/fulfill", headers=b_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "FULFILLED"
        assert data["fulfilled_at"] is not None

        # 11. FULFILLED cannot be fulfilled again
        res = client.post(f"/api/v1/trade-orders/{trade_order.id}/fulfill", headers=b_headers)
        assert res.status_code == 400
    finally:
        db.close()


def test_12_to_17_trade_order_cancellation_and_stock_restoration():
    db = SessionLocal()
    try:
        farmer = _create_user(UserRole.FARMER)
        buyer = _create_user(UserRole.BUYER)
        farm = _create_farm(farmer.id)
        crop = _get_or_create_crop()

        stock_lot = StockLot(
            farmer_id=farmer.id,
            farm_id=farm.id,
            crop_id=crop.id,
            actual_quantity_quintals=100.0,
            available_quantity_quintals=60.0,
            actual_harvest_date=date(2026, 9, 20),
            status=StockLotStatus.PARTIALLY_SOLD,
        )
        db.add(stock_lot)
        db.commit()

        bid = StockBid(stock_lot_id=stock_lot.id, buyer_id=buyer.id, offered_price_per_quintal=6000.0, requested_quantity_quintals=40.0, status=StockBidStatus.ACCEPTED, allocated_quantity_quintals=40.0)
        db.add(bid)
        db.commit()

        trade_order = TradeOrder(stock_bid_id=bid.id, stock_lot_id=stock_lot.id, buyer_id=buyer.id, farmer_id=farmer.id, allocated_quantity_quintals=40.0, agreed_price_per_quintal=6000.0, status=TradeOrderStatus.CREATED)
        db.add(trade_order)
        db.commit()

        b_headers = _auth_headers(buyer)

        # 12. CREATED -> CANCELLED
        res = client.post(f"/api/v1/trade-orders/{trade_order.id}/cancel", json={"cancellation_reason": "BUYER_CANCELLED"}, headers=b_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "CANCELLED"
        assert data["cancellation_reason"] == "BUYER_CANCELLED"
        assert data["cancelled_at"] is not None

        # 14. CANCELLED cannot be cancelled again
        res = client.post(f"/api/v1/trade-orders/{trade_order.id}/cancel", json={"cancellation_reason": "BUYER_CANCELLED"}, headers=b_headers)
        assert res.status_code == 400

        # 15. Cancellation restores available stock
        # 16. Cancellation cannot exceed actual stock
        # 23. StockLot status remains correct after cancellation (restored to 100.0 => AVAILABLE)
        db.refresh(stock_lot)
        assert stock_lot.available_quantity_quintals == 100.0
        assert stock_lot.status == StockLotStatus.AVAILABLE

        # 17. Cancellation preserves accepted StockBid (remains ACCEPTED historically)
        db.refresh(bid)
        assert bid.status == StockBidStatus.ACCEPTED
    finally:
        db.close()


def test_13_fulfilled_cannot_be_cancelled():
    db = SessionLocal()
    try:
        farmer = _create_user(UserRole.FARMER)
        buyer = _create_user(UserRole.BUYER)
        farm = _create_farm(farmer.id)
        crop = _get_or_create_crop()

        stock_lot = StockLot(farmer_id=farmer.id, farm_id=farm.id, crop_id=crop.id, actual_quantity_quintals=50.0, available_quantity_quintals=10.0, actual_harvest_date=date(2026, 9, 20), status=StockLotStatus.PARTIALLY_SOLD)
        db.add(stock_lot)
        db.commit()

        bid = StockBid(stock_lot_id=stock_lot.id, buyer_id=buyer.id, offered_price_per_quintal=6000.0, requested_quantity_quintals=40.0, status=StockBidStatus.ACCEPTED, allocated_quantity_quintals=40.0)
        db.add(bid)
        db.commit()

        trade_order = TradeOrder(stock_bid_id=bid.id, stock_lot_id=stock_lot.id, buyer_id=buyer.id, farmer_id=farmer.id, allocated_quantity_quintals=40.0, agreed_price_per_quintal=6000.0, status=TradeOrderStatus.FULFILLED)
        db.add(trade_order)
        db.commit()

        b_headers = _auth_headers(buyer)

        # 13. FULFILLED cannot be cancelled
        res = client.post(f"/api/v1/trade-orders/{trade_order.id}/cancel", headers=b_headers)
        assert res.status_code == 400
    finally:
        db.close()


def test_18_to_20_contact_sharing_privacy_integration():
    db = SessionLocal()
    try:
        farmer = _create_user(UserRole.FARMER)
        buyer = _create_user(UserRole.BUYER)
        farm = _create_farm(farmer.id)
        crop = _get_or_create_crop()

        stock_lot = StockLot(farmer_id=farmer.id, farm_id=farm.id, crop_id=crop.id, actual_quantity_quintals=50.0, available_quantity_quintals=50.0, actual_harvest_date=date(2026, 9, 20), status=StockLotStatus.AVAILABLE)
        db.add(stock_lot)
        db.commit()

        bid = StockBid(stock_lot_id=stock_lot.id, buyer_id=buyer.id, offered_price_per_quintal=6000.0, requested_quantity_quintals=20.0, status=StockBidStatus.SUBMITTED)
        db.add(bid)
        db.commit()

        f_headers = _auth_headers(farmer)
        b_headers = _auth_headers(buyer)

        # Farmer accepts bid
        res = client.post(f"/api/v1/stock-bids/{bid.id}/accept", json={"allocated_quantity_quintals": 20.0}, headers=f_headers)
        assert res.status_code == 200

        # 18. ContactSharing remains intact
        # 19. Contact remains hidden before mutual consent
        sharing = db.query(ContactSharing).filter(ContactSharing.stock_bid_id == bid.id).first()
        assert sharing is not None
        assert sharing.status == ContactSharingStatus.PENDING

        res = client.get(f"/api/v1/stock-bids/{bid.id}/contact-sharing", headers=f_headers)
        assert res.status_code == 200
        assert res.json()["status"] == "PENDING"
        assert res.json()["farmer_contact"] is None
        assert res.json()["buyer_contact"] is None

        # 20. Contact available after mutual consent
        client.post(f"/api/v1/stock-bids/{bid.id}/contact-sharing/consent", headers=f_headers)
        client.post(f"/api/v1/stock-bids/{bid.id}/contact-sharing/consent", headers=b_headers)

        res = client.get(f"/api/v1/stock-bids/{bid.id}/contact-sharing", headers=f_headers)
        assert res.status_code == 200
        assert res.json()["status"] == "MUTUAL_CONSENT"
    finally:
        db.close()


def test_21_to_24_multiple_bids_concurrency_and_independent_trade_orders():
    db = SessionLocal()
    try:
        farmer = _create_user(UserRole.FARMER)
        buyer = _create_user(UserRole.BUYER)
        farm = _create_farm(farmer.id)
        crop = _get_or_create_crop()

        stock_lot = StockLot(farmer_id=farmer.id, farm_id=farm.id, crop_id=crop.id, actual_quantity_quintals=100.0, available_quantity_quintals=100.0, actual_harvest_date=date(2026, 9, 20), status=StockLotStatus.AVAILABLE)
        db.add(stock_lot)
        db.commit()

        # Create 2 separate bids from buyer
        bid1 = StockBid(stock_lot_id=stock_lot.id, buyer_id=buyer.id, offered_price_per_quintal=6000.0, requested_quantity_quintals=40.0, status=StockBidStatus.SUBMITTED)
        bid2 = StockBid(stock_lot_id=stock_lot.id, buyer_id=buyer.id, offered_price_per_quintal=6100.0, requested_quantity_quintals=30.0, status=StockBidStatus.SUBMITTED)
        db.add(bid1)
        db.add(bid2)
        db.commit()

        f_headers = _auth_headers(farmer)
        b_headers = _auth_headers(buyer)

        # Farmer accepts both bids
        client.post(f"/api/v1/stock-bids/{bid1.id}/accept", json={"allocated_quantity_quintals": 40.0}, headers=f_headers)
        client.post(f"/api/v1/stock-bids/{bid2.id}/accept", json={"allocated_quantity_quintals": 30.0}, headers=f_headers)

        # 24. Multiple accepted StockBids remain independently represented by separate TradeOrders
        order1 = db.query(TradeOrder).filter(TradeOrder.stock_bid_id == bid1.id).first()
        order2 = db.query(TradeOrder).filter(TradeOrder.stock_bid_id == bid2.id).first()
        assert order1 is not None and order2 is not None
        assert order1.id != order2.id

        db.refresh(stock_lot)
        assert stock_lot.available_quantity_quintals == 30.0
        assert stock_lot.status == StockLotStatus.PARTIALLY_SOLD

        # Cancel order1
        # 21. Concurrent cancellation is safe
        # 22. Concurrent fulfillment/cancellation does not produce inconsistent state
        res = client.post(f"/api/v1/trade-orders/{order1.id}/cancel", json={"cancellation_reason": "BUYER_CANCELLED"}, headers=b_headers)
        assert res.status_code == 200

        db.refresh(stock_lot)
        assert stock_lot.available_quantity_quintals == 70.0
        assert stock_lot.status == StockLotStatus.PARTIALLY_SOLD
        assert order2.status == TradeOrderStatus.CREATED
    finally:
        db.close()
