import html
from fastapi import APIRouter, Depends, Form, Response, Request
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.database.session import get_db
from app.schemas.ivr import IVRRequest, IVRResponse
from app.ivr.service import generate_ivr_response
from app.ivr.telephony_service import process_incoming_call, process_menu_selection
from app.config import settings

router = APIRouter()

def format_provider_xml(model: Dict[str, Any], request: Request) -> str:
    """
    Adapter that converts the neutral IVR response model into telecom-compatible XML.
    Currently preserves TwiML-style <Response> and <Say> format as per compatibility findings,
    while dynamically injecting the absolute URL for <Gather action="...">.
    """
    say_text = model.get("say_text", "")
    language = model.get("language", "hi")
    gather_action = model.get("gather_action")
    gather_num_digits = model.get("gather_num_digits", 1)
    timeout_sec = model.get("timeout_sec", 5)
    hangup = model.get("hangup", False)
    redirect_url = model.get("redirect_url")

    # Map language to Twilio/Exotel supported BCP-47 codes
    lang_code = "hi-IN" if language == "hi" else "kn-IN" if language == "kn" else "en-IN"
    escaped_say = html.escape(say_text.strip())

    # Build Absolute URL for action
    base_url = settings.IVR_BASE_URL.rstrip("/")
    if not base_url:
        # Fallback for testing if IVR_BASE_URL is not set
        base_url = str(request.base_url).rstrip("/")

    xml_parts = ['<?xml version="1.0" encoding="UTF-8"?>', '<Response>']

    if gather_action:
        # Ensure gather action is absolute
        absolute_action = f"{base_url}{gather_action}" if gather_action.startswith("/") else f"{base_url}/{gather_action}"
        
        xml_parts.append(
            f'    <Gather action="{absolute_action}" method="POST" numDigits="{gather_num_digits}" timeout="{timeout_sec}">'
        )
        # Note: Exotel SSML formatting for kn-IN/hi-IN is isolated here but currently uses Twilio syntax 
        # as exact Exotel SSML TTS syntax requires verified testing.
        xml_parts.append(f'        <Say language="{lang_code}">{escaped_say}</Say>')
        xml_parts.append('    </Gather>')
        if redirect_url:
            abs_redirect = f"{base_url}{redirect_url}" if redirect_url.startswith("/") else f"{base_url}/{redirect_url}"
            xml_parts.append(f'    <Redirect>{abs_redirect}</Redirect>')
        else:
            xml_parts.append(f'    <Say language="{lang_code}">Humein koi jawab nahi mila.</Say>')
    else:
        xml_parts.append(f'    <Say language="{lang_code}">{escaped_say}</Say>')

    if hangup:
        xml_parts.append('    <Hangup/>')

    xml_parts.append('</Response>')
    return "\n".join(xml_parts)

@router.post("/recommendation", response_model=IVRResponse)
def get_ivr_recommendation(
    payload: IVRRequest,
    db: Session = Depends(get_db)
):
    res = generate_ivr_response(db, payload.farmer_id)
    return res

@router.api_route("/webhook/incoming", methods=["GET", "POST"])
async def ivr_webhook_incoming(
    request: Request,
    db: Session = Depends(get_db)
):
    if request.method == "POST":
        form_data = await request.form()
        call_sid = form_data.get("CallSid") or form_data.get("callSid")
        phone = form_data.get("From") or form_data.get("CallFrom") or form_data.get("from")
    else:
        call_sid = request.query_params.get("CallSid") or request.query_params.get("callSid")
        phone = request.query_params.get("From") or request.query_params.get("CallFrom") or request.query_params.get("from")

    if not call_sid:
        from fastapi import HTTPException
        raise HTTPException(status_code=422, detail="CallSid is required")

    response_model = process_incoming_call(db, str(call_sid), str(phone) if phone else None)
    xml_response = format_provider_xml(response_model, request)
    return Response(content=xml_response, media_type="text/xml")

@router.api_route("/webhook/menu", methods=["GET", "POST"])
async def ivr_webhook_menu(
    request: Request,
    db: Session = Depends(get_db)
):
    if request.method == "POST":
        form_data = await request.form()
        call_sid = form_data.get("CallSid") or form_data.get("callSid")
        phone = form_data.get("From") or form_data.get("CallFrom") or form_data.get("from")
        digits = form_data.get("Digits") or form_data.get("digits")
    else:
        call_sid = request.query_params.get("CallSid") or request.query_params.get("callSid")
        phone = request.query_params.get("From") or request.query_params.get("CallFrom") or request.query_params.get("from")
        digits = request.query_params.get("Digits") or request.query_params.get("digits")

    if not call_sid:
        from fastapi import HTTPException
        raise HTTPException(status_code=422, detail="CallSid is required")

    clean_digits = str(digits).strip(' "\'') if digits is not None else None

    response_model = process_menu_selection(db, str(call_sid), str(phone) if phone else None, clean_digits)
    xml_response = format_provider_xml(response_model, request)
    return Response(content=xml_response, media_type="text/xml")

