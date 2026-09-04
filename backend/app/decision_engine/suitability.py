"""
Deterministic weighted rule-based scoring engine for crop suitability.
"""
from dataclasses import dataclass
from typing import List, Any
from app.utils.missing_data import DataConfidence

@dataclass
class Factor:
    name: str
    value: float
    weight: float
    contribution: float
    explanation: str

@dataclass
class SuitabilityResult:
    score: int
    factors: List[Factor]
    confidence: str
    notes: List[str]

def clamp(val: float, min_val: float, max_val: float) -> int:
    return int(max(min_val, min(max_val, val)))

def score_suitability(
    farm_conditions: dict,
    crop: dict,
    suitability_row: Any | None
) -> SuitabilityResult:
    """
    Calculate suitability score based on regional, water, soil, and climate factors.
    Deterministic weighted rule-based scoring.
    """
    dc = DataConfidence()
    notes = []
    
    # Base score selection (default to 60 if suitability_row is missing)
    base_score = 60.0
    if suitability_row is None:
        dc.record_default("suitability_row", "Regional suitability data not found.")
        notes.append("Regional suitability data not found; neutral default used.")
    else:
        # Extract base score from suitability_row (can be dict or object)
        if isinstance(suitability_row, dict):
            row_base = suitability_row.get("suitability_base_score")
        else:
            row_base = getattr(suitability_row, "suitability_base_score", None)
            
        if row_base is None:
            dc.record_default("suitability_base_score", "Suitability base score not specified.")
            notes.append("Regional suitability base score not found; neutral default used.")
        else:
            base_score = float(row_base)
            
    factors = []
    
    # A. Regional Suitability (Weight: 0.30)
    reg_val = base_score
    if suitability_row is None or (isinstance(suitability_row, dict) and suitability_row.get("suitability_base_score") is None) or (not isinstance(suitability_row, dict) and getattr(suitability_row, "suitability_base_score", None) is None):
        reg_explanation = "Regional suitability data is missing; fallback to neutral default."
    else:
        reg_explanation = "Crop is regionally suitable based on district/state records."
    
    reg_contrib = reg_val * 0.30
    factors.append(Factor(
        name="Regional suitability",
        value=reg_val,
        weight=0.30,
        contribution=reg_contrib,
        explanation=reg_explanation
    ))

    # B. Water Compatibility (Weight: 0.30)
    water_avail = farm_conditions.get("water_availability")
    water_req = crop.get("water_requirement")
    
    if water_avail is None or water_req is None:
        dc.record_default("water_compatibility", "Water compatibility data missing.")
        notes.append("Water compatibility details not available; neutral default used.")
        water_val = 60.0
        water_explanation = "Water data is missing; fallback to neutral default."
    else:
        if water_avail:
            water_val = base_score
            water_explanation = "Water availability matches or exceeds crop water requirement."
        else:
            req_upper = str(water_req).upper()
            if req_upper == "LOW":
                water_val = base_score * 0.8
                water_explanation = "Farm has no water, but crop has low water requirement."
            elif req_upper == "MEDIUM":
                water_val = base_score * 0.5
                water_explanation = "Farm has no water, and crop has medium water requirement."
            else:  # HIGH
                water_val = base_score * 0.2
                water_explanation = "Farm has no water, while crop has high water requirement."
                
    water_contrib = water_val * 0.30
    factors.append(Factor(
        name="Water compatibility",
        value=water_val,
        weight=0.30,
        contribution=water_contrib,
        explanation=water_explanation
    ))

    # C. Soil Compatibility (Weight: 0.25)
    farm_soil = farm_conditions.get("soil_type")
    pref_soil = None
    if suitability_row is not None:
        if isinstance(suitability_row, dict):
            pref_soil = suitability_row.get("soil_type")
        else:
            pref_soil = getattr(suitability_row, "soil_type", None)
            
    if farm_soil is None or pref_soil is None:
        dc.record_default("soil_compatibility", "Soil compatibility data missing.")
        notes.append("Soil compatibility details not available; neutral default used.")
        soil_val = 60.0
        soil_explanation = "Soil type data is missing; fallback to neutral default."
    else:
        if str(farm_soil).lower().strip() == str(pref_soil).lower().strip():
            soil_val = base_score
            soil_explanation = f"Farm soil type '{farm_soil}' matches crop preferred soil."
        else:
            soil_val = base_score * 0.4
            soil_explanation = f"Farm soil type '{farm_soil}' does not match crop preferred soil '{pref_soil}'."
            
    soil_contrib = soil_val * 0.25
    factors.append(Factor(
        name="Soil compatibility",
        value=soil_val,
        weight=0.25,
        contribution=soil_contrib,
        explanation=soil_explanation
    ))

    # D. Climate/Season Fit (Weight: 0.15)
    crop_season = crop.get("season")
    if crop_season is None:
        dc.record_default("climate_fit", "Climate fit data missing.")
        notes.append("Climate/season details not available; neutral default used.")
        climate_val = 60.0
        climate_explanation = "Climate/season data is missing; fallback to neutral default."
    else:
        climate_val = base_score
        climate_explanation = f"Crop season '{crop_season}' is suitable for the regional climate window."
        
    climate_contrib = climate_val * 0.15
    factors.append(Factor(
        name="Climate/season fit",
        value=climate_val,
        weight=0.15,
        contribution=climate_contrib,
        explanation=climate_explanation
    ))

    # Sum contributions
    total_score = reg_contrib + water_contrib + soil_contrib + climate_contrib
    final_score = clamp(round(total_score), 0, 100)
    
    # Collect notes from DataConfidence
    for default_note in dc.notes:
        if default_note not in notes:
            notes.append(default_note)
            
    return SuitabilityResult(
        score=final_score,
        factors=factors,
        confidence=dc.level,
        notes=notes
    )
