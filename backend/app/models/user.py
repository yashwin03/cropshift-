import enum
from sqlalchemy import Column, Integer, String, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from ..database.base import Base

class UserRole(str, enum.Enum):
    FARMER = "FARMER"
    BUYER = "BUYER"

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
    role = Column(SQLEnum(UserRole, native_enum=False), nullable=False, default=UserRole.FARMER)
    full_name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    farmer_id = Column(String, nullable=True, unique=True, index=True)
    partner_code = Column(String, nullable=True, unique=True, index=True)
    is_active = Column(Boolean, default=True)

    farms = relationship("Farm", back_populates="owner")
