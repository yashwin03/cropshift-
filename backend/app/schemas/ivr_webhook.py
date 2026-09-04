"""
ivr_webhook.py -- Pydantic schemas for Telephony Provider Webhook integration.
"""
from typing import Optional
from pydantic import BaseModel, Field


class IVRWebhookInput(BaseModel):
    """Payload received from telephony providers (e.g. Exotel, Plivo, Twilio)."""
    CallSid: Optional[str] = Field(None, description="Unique call session ID from telecom provider")
    From: Optional[str] = Field(None, description="Caller phone number (farmer)")
    To: Optional[str] = Field(None, description="Dialed virtual / toll-free number")
    Digits: Optional[str] = Field(None, description="DTMF digit pressed by farmer (0-9, *, #)")
    CallType: Optional[str] = Field(None, description="Call direction/type (inbound, outbound)")
    DialCallStatus: Optional[str] = Field(None, description="Call status")


class IVRSessionData(BaseModel):
    """Internal session state model for multi-turn IVR interactions."""
    call_sid: str
    phone: str
    farmer_id: Optional[int] = None
    farm_id: Optional[int] = None
    language: str = "hi"
    current_step: str = "MAIN_MENU"
