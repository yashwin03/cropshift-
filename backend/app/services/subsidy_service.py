"""
Subsidy Matcher service for CropShift.
Matches real verified agricultural schemes based on farm conditions and crops.
"""
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.models.crop import Crop
from app.services.farm_service import get_farm_conditions

def match_subsidies(
    db: Session,
    farm_id: int,
    has_land_proof: bool = False,
    has_soil_health_card: bool = False,
    recommended_crop_id: int | None = None
) -> List[Dict[str, Any]]:
    """
    Match verified agricultural schemes to the given farm.
    Always returns exactly 9 specified fields per scheme.
    Does not fabricate eligibility: defaults to VERIFICATION_REQUIRED if land proof is missing.
    """
    farm_cond = get_farm_conditions(db, farm_id)
    if not farm_cond:
        return []

    # Determine if recommended crop is an oilseed
    is_oilseed = False
    rec_crop_name = None
    if recommended_crop_id is not None:
        crop = db.get(Crop, recommended_crop_id)
        if crop:
            rec_crop_name = crop.name
            is_oilseed = crop.name.strip().lower() in ["groundnut", "sunflower", "mustard", "sesame"]

    schemes = []

    # 1. National Mission on Edible Oils — Oilseeds (NMEO-OS)
    farm_state = farm_cond.get('state') or 'Unknown'
    farm_district = farm_cond.get('district') or 'Unknown'
    farm_soil = farm_cond.get('soil_type') or 'Unknown'

    nmeo_factors = [
        f"Recommended crop: {rec_crop_name or 'None'} (Oilseed: {is_oilseed})",
        f"Farm state: {farm_state}",
        f"Land ownership proof provided: {has_land_proof}"
    ]
    if is_oilseed:
        nmeo_relevance = "HIGH"
    else:
        nmeo_relevance = "MEDIUM" if (farm_cond.get("state") or "") == "Karnataka" else "LOW"

    if not has_land_proof:
        nmeo_eligibility = "VERIFICATION_REQUIRED"
        nmeo_verification = True
        nmeo_req_info = ["Land ownership certificate (RoR/Patta)", "Aadhaar card linked to land records"]
    else:
        if is_oilseed:
            nmeo_eligibility = "LIKELY_ELIGIBLE"
            nmeo_verification = False
            nmeo_req_info = []
        else:
            nmeo_eligibility = "LIKELY_NOT_ELIGIBLE"
            nmeo_verification = False
            nmeo_req_info = ["Proof of oilseed cultivation intent"]

    schemes.append({
        "scheme_id": "nmeo_os",
        "scheme_name": "National Mission on Edible Oils — Oilseeds (NMEO-OS)",
        "relevance": nmeo_relevance,
        "eligibility_status": nmeo_eligibility,
        "eligibility_factors": nmeo_factors,
        "required_information": nmeo_req_info,
        "support_information": "Subsidies for high-yielding oilseed seed distribution, farm toolkits, and cultivator training.",
        "verification_required": nmeo_verification,
        "data_source": "Ministry of Agriculture & Farmers Welfare, Government of India"
    })

    # 2. PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)
    land_area = farm_cond.get("land_area_acre") or 0.0
    pm_kisan_factors = [
        f"Land area: {land_area} acres (Marginal/Small: {land_area <= 5.0})",
        f"Land ownership proof provided: {has_land_proof}"
    ]
    pm_kisan_relevance = "HIGH" if land_area <= 5.0 else "MEDIUM"

    if not has_land_proof:
        pm_kisan_eligibility = "VERIFICATION_REQUIRED"
        pm_kisan_verification = True
        pm_kisan_req_info = ["Landholding registration documents", "Aadhaar Card", "Bank Account passbook copy"]
    else:
        pm_kisan_eligibility = "LIKELY_ELIGIBLE"
        pm_kisan_verification = False
        pm_kisan_req_info = []

    schemes.append({
        "scheme_id": "pm_kisan",
        "scheme_name": "PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)",
        "relevance": pm_kisan_relevance,
        "eligibility_status": pm_kisan_eligibility,
        "eligibility_factors": pm_kisan_factors,
        "required_information": pm_kisan_req_info,
        "support_information": "Income support of ₹6,000 per year in three equal installments to all landholding farmer families.",
        "verification_required": pm_kisan_verification,
        "data_source": "pmkisan.gov.in (Official PM-KISAN Portal)"
    })

    # 3. Pradhan Mantri Fasal Bima Yojana (PMFBY)
    pmfby_factors = [
        f"Recommended crop: {rec_crop_name or 'None'} (Oilseed: {is_oilseed})",
        f"District: {farm_district}",
        f"Land ownership proof provided: {has_land_proof}"
    ]
    pmfby_relevance = "HIGH" if is_oilseed else "MEDIUM"

    if not has_land_proof:
        pmfby_eligibility = "VERIFICATION_REQUIRED"
        pmfby_verification = True
        pmfby_req_info = ["Sowing certificate issued by local revenue/agricultural officer", "Land registration records"]
    else:
        pmfby_eligibility = "LIKELY_ELIGIBLE"
        pmfby_verification = False
        pmfby_req_info = []

    schemes.append({
        "scheme_id": "pmfby",
        "scheme_name": "Pradhan Mantri Fasal Bima Yojana (PMFBY)",
        "relevance": pmfby_relevance,
        "eligibility_status": pmfby_eligibility,
        "eligibility_factors": pmfby_factors,
        "required_information": pmfby_req_info,
        "support_information": "Low-premium crop insurance (1.5% - 2.0% farmer contribution) protecting against natural calamities and yield losses.",
        "verification_required": pmfby_verification,
        "data_source": "pmfby.gov.in (National Crop Insurance Portal)"
    })

    # 4. Soil Health Card Scheme
    shc_factors = [
        f"Existing soil type: {farm_soil}",
        f"Soil Health Card registration status: {has_soil_health_card}"
    ]
    shc_relevance = "HIGH" if farm_cond.get("soil_type") else "MEDIUM"

    if not has_soil_health_card:
        shc_eligibility = "VERIFICATION_REQUIRED"
        shc_verification = True
        shc_req_info = ["Representative soil sample from the farm plot for testing"]
    else:
        shc_eligibility = "LIKELY_ELIGIBLE"
        shc_verification = False
        shc_req_info = []

    schemes.append({
        "scheme_id": "soil_health_card",
        "scheme_name": "Soil Health Card Scheme",
        "relevance": shc_relevance,
        "eligibility_status": shc_eligibility,
        "eligibility_factors": shc_factors,
        "required_information": shc_req_info,
        "support_information": "Provides soil nutrient status cards and tailored fertilizer/macro-nutrient dosage recommendations.",
        "verification_required": shc_verification,
        "data_source": "soilhealth.dac.gov.in"
    })

    # 5. State Oilseed Support Scheme (Karnataka FRUITS/Oilseeds)
    is_karnataka = (farm_cond.get("state") or "").strip().lower() == "karnataka"
    fruits_factors = [
        f"Farm state: {farm_state}",
        f"Recommended crop: {rec_crop_name or 'None'} (Oilseed: {is_oilseed})",
        f"Land ownership proof provided: {has_land_proof}"
    ]
    if is_karnataka and is_oilseed:
        fruits_relevance = "HIGH"
    elif is_karnataka:
        fruits_relevance = "MEDIUM"
    else:
        fruits_relevance = "LOW"

    if not has_land_proof:
        fruits_eligibility = "VERIFICATION_REQUIRED"
        fruits_verification = True
        fruits_req_info = ["Karnataka FRUITS Registration ID"]
    else:
        if is_karnataka and is_oilseed:
            fruits_eligibility = "LIKELY_ELIGIBLE"
            fruits_verification = False
            fruits_req_info = []
        else:
            fruits_eligibility = "LIKELY_NOT_ELIGIBLE"
            fruits_verification = False
            fruits_req_info = ["Proof of residency in Karnataka State"]

    schemes.append({
        "scheme_id": "state_oilseed_support",
        "scheme_name": "State Oilseed Support Scheme (Karnataka FRUITS)",
        "relevance": fruits_relevance,
        "eligibility_status": fruits_eligibility,
        "eligibility_factors": fruits_factors,
        "required_information": fruits_req_info,
        "support_information": "Additional state-specific incentives and certified seed subsidies via the FRUITS database portal.",
        "verification_required": fruits_verification,
        "data_source": "fruits.karnataka.gov.in"
    })

    return schemes

get_subsidies_for_farm = match_subsidies
