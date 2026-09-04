import app.patch_bcrypt
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.api.v1.auth import get_current_user, create_access_token, get_password_hash
from app.models.user import User, UserRole
from app.database.session import SessionLocal, engine
from app.database.base import Base

def override_get_current_user():
    return User(id=1, username="testuser", email="test@example.com", role=UserRole.FARMER)

app.dependency_overrides[get_current_user] = override_get_current_user


@pytest.fixture(autouse=True)
def reset_default_auth_override():
    """Ensure default test user override is active for general endpoints unless explicitly cleared by a test fixture."""
    app.dependency_overrides[get_current_user] = override_get_current_user


@pytest.fixture(scope="module")
def client():
    """Pytest fixture to provide a FastAPI TestClient."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def db_session():
    """Provides a database session for testing with strict transactional rollback."""
    connection = engine.connect()
    transaction = connection.begin()
    session = SessionLocal(bind=connection)
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def farmer_user_token(db_session):
    user = db_session.query(User).filter(User.username == "test_farmer_user").first()
    if not user:
        user = User(
            username="test_farmer_user",
            email="farmer_test@example.com",
            hashed_password=get_password_hash("password123"),
            role=UserRole.FARMER,
            is_active=True
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
    token = create_access_token(data={"sub": user.username, "role": user.role.value})
    return {"token": token, "user": user}
