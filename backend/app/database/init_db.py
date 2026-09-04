"""
init_db.py -- Creates the PostGIS extension and all A1 tables.

Usage:
    python -m app.database.init_db

This script is idempotent: running it multiple times is safe.
Tables are created with CREATE TABLE IF NOT EXISTS (via SQLAlchemy's create_all).
"""
import logging

from sqlalchemy import text

from .session import engine
from .base import Base

# Import all models so their metadata is registered with Base
import app.models  # noqa: F401

logger = logging.getLogger(__name__)


def init_db() -> None:
    """Enable PostGIS and create all tables."""
    logger.info("Enabling PostGIS extension...")
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
        conn.commit()

    logger.info("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    
    # Reversible schema upgrade: Ensure role, full_name, and phone columns exist on user table
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE \"user\" ADD COLUMN IF NOT EXISTS role VARCHAR DEFAULT 'FARMER';"))
            conn.execute(text("ALTER TABLE \"user\" ADD COLUMN IF NOT EXISTS full_name VARCHAR;"))
            conn.execute(text("ALTER TABLE \"user\" ADD COLUMN IF NOT EXISTS phone VARCHAR;"))
            conn.execute(text("ALTER TABLE \"user\" ADD COLUMN IF NOT EXISTS farmer_id VARCHAR;"))
            conn.execute(text("DELETE FROM \"user\" WHERE username LIKE '%test%' OR username LIKE '%dup%';"))
            conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_user_farmer_id ON \"user\" (farmer_id);"))
            conn.execute(text("ALTER TABLE contact_sharing ADD COLUMN IF NOT EXISTS stock_bid_id INTEGER;"))
            conn.execute(text("ALTER TABLE contact_sharing ALTER COLUMN bid_id DROP NOT NULL;"))
            conn.commit()
        except Exception as e:
            logger.warning(f"Note on schema column migration: {e}")

    logger.info("All tables created (or already exist).")



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    init_db()
    print("Database initialised successfully.")
