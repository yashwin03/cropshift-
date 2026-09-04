"""
peer_proof.py -- PeerProof model for farmer crop outcome evidence.
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database.base import Base


class PeerProof(Base):
    __tablename__ = "peer_proof"

    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("user.id"), nullable=True)
    crop_id = Column(Integer, ForeignKey("crop.id"), nullable=False)

    season = Column(String, nullable=False, default="Kharif 2025")
    cultivated_area_acres = Column(Float, nullable=False, default=2.0)
    yield_quintals_per_acre = Column(Float, nullable=False)
    selling_price_per_quintal = Column(Float, nullable=False)
    cultivation_cost_per_acre = Column(Float, nullable=True)
    net_realization_per_acre = Column(Float, nullable=True)

    district = Column(String, nullable=False)
    state = Column(String, nullable=False, default="Karnataka")

    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    crop_stage = Column(String, nullable=True)
    expected_harvest = Column(String, nullable=True)
    soil_type = Column(String, nullable=True)
    water_source = Column(String, nullable=True)

    source_type = Column(String, nullable=False, default="CropShift demo dataset")
    verification_status = Column(String, nullable=False, default="Self-reported & Verified")
    peer_visibility = Column(String, nullable=False, default="ANONYMOUS")  # ANONYMOUS, VERIFIED, CONTACTABLE
    contactable = Column(Boolean, nullable=False, default=False)
    contact_phone = Column(String, nullable=True)
    contact_email = Column(String, nullable=True)
    farmer_display_name = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    crop = relationship("Crop")
    farmer = relationship("User")
