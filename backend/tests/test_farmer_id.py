import pytest
from app.models.user import User, UserRole
from app.api.v1.auth import get_password_hash

def test_farmer_id_generation_and_persistence(db_session):
    db_session.query(User).filter(User.username.in_(["farmer_test_id", "buyer_test_id", "farmer_dup_1", "farmer_dup_2"])).delete(synchronize_session=False)
    db_session.commit()

    user = User(
        username="farmer_test_id",
        email="farmer_test_id@cropshift.com",
        hashed_password=get_password_hash("password123"),
        role=UserRole.FARMER
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # Assign farmer_id
    user.farmer_id = f"FS-{user.id:06d}"
    db_session.commit()
    db_session.refresh(user)

    assert user.farmer_id == f"FS-{user.id:06d}"
    assert user.farmer_id.startswith("FS-")

    # Verify same account retains same Farmer ID
    same_user = db_session.query(User).filter(User.username == "farmer_test_id").first()
    assert same_user.farmer_id == user.farmer_id

def test_buyer_does_not_have_farmer_id_by_default(db_session):
    buyer = User(
        username="buyer_test_id",
        email="buyer_test_id@cropshift.com",
        hashed_password=get_password_hash("password123"),
        role=UserRole.BUYER
    )
    db_session.add(buyer)
    db_session.commit()
    db_session.refresh(buyer)

    assert buyer.farmer_id is None

def test_duplicate_farmer_id_fails(db_session):
    user1 = User(
        username="farmer_dup_1",
        email="farmer_dup_1@cropshift.com",
        hashed_password=get_password_hash("password123"),
        role=UserRole.FARMER,
        farmer_id="FS-999999"
    )
    db_session.add(user1)
    db_session.commit()

    user2 = User(
        username="farmer_dup_2",
        email="farmer_dup_2@cropshift.com",
        hashed_password=get_password_hash("password123"),
        role=UserRole.FARMER,
        farmer_id="FS-999999"
    )
    db_session.add(user2)
    with pytest.raises(Exception):
        db_session.commit()
    db_session.rollback()
