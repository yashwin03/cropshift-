"""
Explainability layer for CropShift.
Converts decision factors into farmer-readable explanations.
"""
from typing import List, Tuple

def generate_explanations(
    decision: str,
    suitability_score: int,
    profitability_score: int,
    market_score: int,
    risk_score: int,
    profit_diff: float,
    current_crop_profit: float,
    expected_profit: float,
    alt_crop_name: str,
    water_requirement: str,
    water_availability: bool,
    trend: str | None,
    distance_km: float | None,
    notes: List[str]
) -> Tuple[List[str], List[str]]:
    """
    Generate dynamic farmer-friendly explanations (reasons and risks)
    based on computed scores, decision types, and missing data notes.
    """
    reasons = []

    # 1. Generate reasons based on decision type
    core_reasons = []
    if decision == "SWITCH":
        core_reasons.append(f"Expected profit is ₹{profit_diff:,.0f}/acre higher than your current crop.")
        core_reasons.append(f"Crop suitability is high at {suitability_score}/100 for your district.")
        core_reasons.append(f"Market intelligence score is strong at {market_score}/100.")
        core_reasons.append("Overall safety score indicates a switch is highly recommended.")
    elif decision == "CAUTION":
        core_reasons.append(f"Mixed signals: crop suitability is good ({suitability_score}/100), but there is moderate risk (Risk Score: {risk_score}/100).")
        core_reasons.append(f"Expected profit is ₹{profit_diff:,.0f}/acre higher, but caution is advised due to risk elements.")
        core_reasons.append(f"Market conditions are favorable ({market_score}/100), but water or suitability constraints suggest caution.")
    else: # DONT_SWITCH
        core_reasons.append(f"We do not recommend switching to {alt_crop_name} because the safety score is low.")
        core_reasons.append(f"Expected profit difference is low or negative: ₹{profit_diff:,.0f}/acre.")
        core_reasons.append(f"Crop suitability is low or constrained: {suitability_score}/100.")
        core_reasons.append(f"Market access or price levels are weak: {market_score}/100.")

    # 2. Append confidence warning notes if any component was defaulted
    warnings = []
    for note in notes:
        note_lower = note.lower()
        if "soil" in note_lower:
            warnings.append("Soil information was not available, so a regional average was used.")
        elif "water" in note_lower:
            warnings.append("Water availability details not available, so regional default used.")
        elif "market" in note_lower or "price" in note_lower or "suitability" in note_lower:
            warnings.append("Regional market or suitability data was not available, so regional default used.")

    # Combine keeping total size <= 5, prioritizing warnings
    reasons = core_reasons + warnings
    if len(reasons) > 5:
        # Keep warnings, trim core reasons if needed
        reasons = core_reasons[:5 - len(warnings)] + warnings
    
    if len(reasons) < 3:
        reasons.append("Review local agricultural extension services for specific field guidance.")
        reasons = reasons[:5]

    # 3. Generate risks list from risk parameters
    risks = []
    
    # Yield risk
    if suitability_score < 80:
        risks.append(f"Yield risk: Suitability shortfall of {100 - suitability_score}% indicates crop is not fully suited to your soil type.")
    
    # Water risk
    req_upper = str(water_requirement).upper().strip()
    if not water_availability:
        if req_upper in ["HIGH", "MEDIUM"]:
            risks.append(f"High water risk: Crop requires {water_requirement} water but farm has no water available.")
    else:
        if req_upper in ["HIGH", "MEDIUM"]:
            risks.append(f"Moderate water risk: Crop requires {water_requirement} water; monitor local rainfall and canal schedules.")

    # Price risk
    trend_upper = str(trend).upper().strip() if trend else "UNKNOWN"
    if trend_upper == "FALLING":
        risks.append("High price risk: Market price trend is FALLING.")
    elif trend_upper == "STABLE":
        risks.append("Moderate price risk: Market price trend is STABLE.")

    # Market access distance
    if distance_km is not None and distance_km > 25.0:
        risks.append(f"Market access risk: Crop must be transported {distance_km:.2f} km to the nearest market.")

    # Clamp risks to 1-4 items; ensure it is never empty
    if not risks:
        risks.append("Baseline risk: Shifting crops carries inherent transition and technique risks.")
    
    risks = risks[:4]

    return reasons, risks
