"""Pydantic schemas for ContactSharing validation and serialization."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from ..models.contact_sharing import ContactSharingStatus


class ContactDetails(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    business_name: Optional[str] = None

    class Config:
        from_attributes = True


class ContactSharingResponse(BaseModel):
    id: int
    bid_id: int
    status: ContactSharingStatus
    farmer_consented: bool
    farmer_consented_at: Optional[datetime] = None
    buyer_consented: bool
    buyer_consented_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    farmer_contact: Optional[ContactDetails] = None
    buyer_contact: Optional[ContactDetails] = None

    class Config:
        from_attributes = True
