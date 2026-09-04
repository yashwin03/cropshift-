"""Subsidy model -- A1 spec entity."""
from sqlalchemy import Column, Integer, String, Boolean, JSON

from ..database.base import Base


class Subsidy(Base):
    __tablename__ = "subsidy"

    id = Column(Integer, primary_key=True, index=True)
    scheme_id = Column(String, nullable=False, unique=True)   # official scheme code
    scheme_name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    applicable_crop_types = Column(JSON, nullable=True)       # list of CropType strings
    applicable_states = Column(JSON, nullable=True)           # list of state names
    eligibility_factors = Column(JSON, nullable=True)         # structured eligibility dict
    required_information = Column(JSON, nullable=True)        # docs/info needed
    support_information = Column(String, nullable=True)       # contact / helpline
    verification_required = Column(Boolean, nullable=False, default=True)
    data_source = Column(String, nullable=True)
