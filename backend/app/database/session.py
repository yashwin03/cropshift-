from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings

# SQLAlchemy create_engine is lazy by default (does not connect on instantiation).
# It will connect only when the pool is first accessed.
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True  # Enables check to see if database connection is alive
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_db():
    """FastAPI dependency to yield a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
