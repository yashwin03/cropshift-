"""
telephony_service.py -- Telephony webhook processing and multi-lingual voice script engine.
Integrates with CropShift decision engine, market service, subsidy service, and PostGIS.
"""
from typing import Dict, Optional, Tuple, Any
import html
import time
from sqlalchemy.orm import Session

from app.models.farmer import Farmer
from app.models.farm import Farm
from app.models.crop import Crop
from app.decision_engine.recommendation import generate_recommendation
from app.services.market_service import get_best_market_for_crop
from app.services.subsidy_service import get_subsidies_for_farm
from app.ivr.service import number_to_words
from app.ivr.demo_data import (
    DEMO_FARMER_NAME,
    DEMO_RECOMMENDATION_PROMPTS,
    DEMO_MARKET_PROMPTS,
    DEMO_SUBSIDY_PROMPTS,
)


# ---------------------------------------------------------------------------
# In-Memory Ephemeral Session Store (CallSid -> Session Dict)
# ---------------------------------------------------------------------------
_sessions: Dict[str, Dict[str, Any]] = {}

def get_or_create_session(call_sid: str, phone: str) -> Dict[str, Any]:
    """Retrieve existing call session or initialize a new one."""
    if call_sid not in _sessions:
        _sessions[call_sid] = {
            "call_sid": call_sid,
            "phone": phone,
            "farmer_id": None,
            "farm_id": None,
            "farmer_name": None,
            "language": "hi",
            "current_step": "MAIN_MENU",
            "created_at": time.time(),
        }
    return _sessions[call_sid]

def update_session(call_sid: str, **kwargs) -> Dict[str, Any]:
    sess = _sessions.get(call_sid, {})
    sess.update(kwargs)
    _sessions[call_sid] = sess
    return sess

def clear_session(call_sid: str):
    _sessions.pop(call_sid, None)


# ---------------------------------------------------------------------------
# Telephony XML Response Builder (Compatible with Exotel, Plivo, TwiML)
# ---------------------------------------------------------------------------
def build_xml_response(
    say_text: str,
    language: str = "hi",
    gather_action: Optional[str] = None,
    gather_num_digits: int = 1,
    timeout_sec: int = 5,
    hangup: bool = False,
    redirect_url: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Construct provider-independent response representation.
    """
    return {
        "say_text": say_text,
        "language": language,
        "gather_action": gather_action,
        "gather_num_digits": gather_num_digits,
        "timeout_sec": timeout_sec,
        "hangup": hangup,
        "redirect_url": redirect_url,
    }


# ---------------------------------------------------------------------------
# Multi-Lingual Prompt Templates
# ---------------------------------------------------------------------------
MENU_PROMPTS = {
    "hi": (
        "Namaste {name}. CropShift Helpline mein aapka swagat hai. "
        "Fasal badlav salah ke liye 1 dabayein. "
        "Mandi ke taaza bhav ke liye 2 dabayein. "
        "Sarkari yojnaon ke liye 3 dabayein. "
        "Bhasha badalne ke liye 8 dabayein. "
        "Menoo dobara sunne ke liye 9 dabayein. "
        "Call samapt karne ke liye 0 dabayein."
    ),
    "kn": (
        "Namaskara {name}. CropShift Sahayavaniyalli swagatha. "
        "Bele badalavanege 1 otti. "
        "Market bele tilidukollalu 2 otti. "
        "Sarkari yojanegalige 3 otti. "
        "Bhashe badalisalu 8 otti. "
        "Mattonme kelalu 9 otti. "
        "Kare mugiyalu 0 otti."
    ),
    "en": (
        "Welcome to CropShift Voice Helpline, {name}. "
        "Press 1 for crop shift recommendation. "
        "Press 2 for nearby market mandi prices. "
        "Press 3 for government subsidies. "
        "Press 8 to change language. "
        "Press 9 to repeat this menu. "
        "Press 0 to end call."
    ),
}

LANG_SELECT_PROMPT = (
    "Hindi ke liye 1 dabayein. "
    "Kannada ge 2 otti. "
    "For English press 3."
)


# ---------------------------------------------------------------------------
# Farmer & Farm Context Resolver
# ---------------------------------------------------------------------------
def resolve_farmer_context(db: Session, phone: Optional[str]) -> Tuple[Optional[Farmer], Optional[Farm]]:
    """Lookup farmer and their primary farm by phone number."""
    if not phone:
        return None, None

    clean_phone = phone.replace("+91", "").replace("-", "").strip()

    farmer = db.query(Farmer).filter(
        (Farmer.phone == phone) | (Farmer.phone == clean_phone) | (Farmer.phone.endswith(clean_phone[-10:]))
    ).first()

    if not farmer:
        # Fallback to demo farmer ID 1 if not matched
        farmer = db.get(Farmer, 1)

    farm = None
    if farmer:
        farm = db.query(Farm).filter(Farm.farmer_id == farmer.id).first()

    if not farm:
        farm = db.get(Farm, 1)

    return farmer, farm


# ---------------------------------------------------------------------------
# Webhook Event Handlers
# ---------------------------------------------------------------------------
def process_incoming_call(db: Session, call_sid: str, phone: Optional[str]) -> Dict[str, Any]:
    """
    Handle initial incoming call webhook (INVOKE on call connect).
    Identifies caller, initializes session, and returns Main Menu audio prompt.
    """
    session = get_or_create_session(call_sid, phone or "unknown")
    farmer, farm = resolve_farmer_context(db, phone)

    if farmer:
        farmer_name = farmer.name
        language = farmer.language or "hi"
        if language not in ("hi", "kn", "en"):
            language = "hi"
        update_session(
            call_sid,
            farmer_id=farmer.id,
            farm_id=farm.id if farm else 1,
            farmer_name=farmer_name,
            language=language,
            current_step="MAIN_MENU",
        )
    else:
        farmer_name = "Kisan Bhai"
        language = "hi"
        update_session(
            call_sid,
            farmer_name=farmer_name,
            farm_id=1,
            language=language,
            current_step="MAIN_MENU",
        )

    menu_template = MENU_PROMPTS.get(language, MENU_PROMPTS["hi"])
    prompt = menu_template.format(name=farmer_name)

    return build_xml_response(
        say_text=prompt,
        language=language,
        gather_action="/api/v1/ivr/webhook/menu",
        gather_num_digits=1,
        timeout_sec=8,
    )


def process_menu_selection(
    db: Session, call_sid: str, phone: Optional[str], digits: Optional[str]
) -> Dict[str, Any]:
    """
    Handle DTMF digit webhook callbacks (farmer presses 1, 2, 3, 8, 9, 0).
    """
    session = get_or_create_session(call_sid, phone or "unknown")
    language = session.get("language", "hi")
    farmer_name = session.get("farmer_name", "Kisan")
    farm_id = session.get("farm_id") or 1
    current_step = session.get("current_step", "MAIN_MENU")

    digit = (digits or "").strip()

    # Step: Language Selection Submenu
    if current_step == "LANG_SELECT":
        if digit == "1":
            language = "hi"
        elif digit == "2":
            language = "kn"
        elif digit == "3":
            language = "en"
        else:
            language = "hi"

        update_session(call_sid, language=language, current_step="MAIN_MENU")
        menu_template = MENU_PROMPTS.get(language, MENU_PROMPTS["hi"])
        prompt = menu_template.format(name=farmer_name)
        return build_xml_response(
            say_text=prompt,
            language=language,
            gather_action="/api/v1/ivr/webhook/menu",
            gather_num_digits=1,
        )

    # Step: Main Menu Actions
    if digit == "1":
        # 1: Crop Shift Recommendation (Deterministic Demo Response)
        advice = DEMO_RECOMMENDATION_PROMPTS.get(language, DEMO_RECOMMENDATION_PROMPTS["hi"])
        return build_xml_response(
            say_text=advice,
            language=language,
            gather_action="/api/v1/ivr/webhook/menu",
            gather_num_digits=1,
            timeout_sec=10,
        )

    elif digit == "2":
        # 2: Mandi Market Prices (Deterministic Demo Response)
        market_text = DEMO_MARKET_PROMPTS.get(language, DEMO_MARKET_PROMPTS["hi"])
        return build_xml_response(
            say_text=market_text,
            language=language,
            gather_action="/api/v1/ivr/webhook/menu",
            gather_num_digits=1,
            timeout_sec=10,
        )

    elif digit == "3":
        # 3: Government Subsidies & Schemes (Deterministic Demo Response)
        sub_text = DEMO_SUBSIDY_PROMPTS.get(language, DEMO_SUBSIDY_PROMPTS["hi"])
        return build_xml_response(
            say_text=sub_text,
            language=language,
            gather_action="/api/v1/ivr/webhook/menu",
            gather_num_digits=1,
            timeout_sec=10,
        )


    elif digit == "8":
        # 8: Change Language
        update_session(call_sid, current_step="LANG_SELECT")
        return build_xml_response(
            say_text=LANG_SELECT_PROMPT,
            language="hi",
            gather_action="/api/v1/ivr/webhook/menu",
            gather_num_digits=1,
            timeout_sec=6,
        )

    elif digit == "9":
        # 9: Repeat Main Menu
        update_session(call_sid, current_step="MAIN_MENU")
        menu_template = MENU_PROMPTS.get(language, MENU_PROMPTS["hi"])
        prompt = menu_template.format(name=farmer_name)
        return build_xml_response(
            say_text=prompt,
            language=language,
            gather_action="/api/v1/ivr/webhook/menu",
            gather_num_digits=1,
        )

    elif digit == "0":
        # 0: End Call / Hangup
        farewell = (
            "Dhanyavad. CropShift se judne ke liye aabhar. Shubh din!"
            if language == "hi"
            else "Dhanyavadagalu. CropShift samparkisiddakke aabhari. Shubhadina!"
            if language == "kn"
            else "Thank you for calling CropShift. Have a great day!"
        )
        clear_session(call_sid)
        return build_xml_response(say_text=farewell, language=language, hangup=True)

    else:
        # Invalid selection -> Prompt retry
        retry_msg = (
            "Anya chayan asatyapith hai. Kripya sahi vikalp chunein. "
            + MENU_PROMPTS.get(language, MENU_PROMPTS["hi"]).format(name=farmer_name)
        )
        return build_xml_response(
            say_text=retry_msg,
            language=language,
            gather_action="/api/v1/ivr/webhook/menu",
            gather_num_digits=1,
        )
