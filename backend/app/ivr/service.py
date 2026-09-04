from sqlalchemy.orm import Session
from typing import Optional, Dict, Any

from app.models.farmer import Farmer
from app.models.farm import Farm
from app.models.crop import Crop
from app.decision_engine.recommendation import generate_recommendation

def number_to_words(n: int) -> str:
    """Convert integers to their spoken English counterparts."""
    if n < 0:
        return "negative " + number_to_words(abs(n))
    
    ones = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", 
            "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"]
    tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]
    
    if n < 20:
        return ones[n]
    if n < 100:
        div, mod = divmod(n, 10)
        return tens[div] + (" " + ones[mod] if mod != 0 else "")
    if n == 100:
        return "one hundred"
    
    if n >= 1000:
        thousands = n // 1000
        remainder = n % 1000
        t_str = number_to_words(thousands) + " thousand"
        if remainder > 0:
            t_str += " " + number_to_words(remainder)
        return t_str
        
    return str(n)


def generate_ivr_response(db: Session, farmer_id: int, language: str = "en") -> Dict[str, Any]:
    """Generate a voice-compatible response for IVR flow."""
    farmer = db.get(Farmer, farmer_id)
    if not farmer:
        return {
            "farmer_name": None,
            "verified": False,
            "voice_script": "Namaste. We could not verify your farmer ID. Please contact support or try again.",
            "recommendation": None,
            "language": language
        }

    # Fetch farmer's primary farm
    farm = db.query(Farm).filter(Farm.farmer_id == farmer_id, Farm.current_crop_id.isnot(None)).order_by(Farm.id.asc()).first()
    if not farm:
        farm = db.query(Farm).filter(Farm.farmer_id == farmer_id).order_by(Farm.id.asc()).first()
    if not farm:
        return {
            "farmer_name": farmer.name,
            "verified": True,
            "voice_script": f"Namaste {farmer.name}. We verified your ID, but could not find a farm associated with your profile.",
            "recommendation": None,
            "language": language
        }

    rec = generate_recommendation(db, farm.id)
    if not rec:
        return {
            "farmer_name": farmer.name,
            "verified": True,
            "voice_script": f"Namaste {farmer.name}. We verified your ID, but recommendation generation failed.",
            "recommendation": None,
            "language": language
        }

    crop = db.get(Crop, rec.recommended_crop_id)
    crop_name = crop.name if crop else "Unknown"

    # Convert numeric scores/profits to words
    land_area = int(farm.land_area_acre)
    land_area_words = number_to_words(land_area) if land_area > 0 else "zero"
    
    safety_score = int(rec.safety_score)
    safety_score_words = number_to_words(safety_score)
    
    profit_diff = int(rec.profit_difference)
    profit_words = number_to_words(profit_diff)

    # Voice script text under 45 words:
    # "Namaste <name>. For your <land_area> acre farm, <crop_name> is recommended. Safety score <safety_score_words> out of one hundred. Expected profit is higher by <profit_words> rupees per acre. Market prices may change."
    voice_script = (
        f"Namaste {farmer.name}. For your {land_area_words} acre farm, {crop_name.lower()} is recommended. "
        f"Safety score {safety_score_words} out of one hundred. "
        f"Expected profit is higher by {profit_words} rupees per acre. Market prices may change."
    )

    rec_data = {
        "recommended_crop": crop_name,
        "suitability_score": int(rec.suitability_score),
        "profitability_score": int(rec.profitability_score),
        "market_score": int(rec.market_score),
        "risk_score": int(rec.risk_score),
        "safety_score": int(rec.safety_score),
        "decision": rec.decision,
        "expected_profit": float(rec.expected_profit),
        "current_crop_profit": float(rec.current_crop_profit),
        "profit_difference": float(rec.profit_difference),
        "reasons": rec.reasons or [],
        "risks": rec.risks or []
    }

    return {
        "farmer_name": farmer.name,
        "verified": True,
        "voice_script": voice_script,
        "recommendation": rec_data,
        "language": language
    }
