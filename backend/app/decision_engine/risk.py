"""
Risk factor definition and risk calculation engine for CropShift.
"""
from dataclasses import dataclass

@dataclass
class RiskFactor:
    name: str
    raw_risk_level: float  # 0.0 to 1.0 (where 1.0 is extreme hazard)
    weight: float          # 0.0 to 1.0

def calculate_risk_score(
    suitability_score: float,
    trend: str | None,
    water_availability: bool,
    water_requirement: str,
    distance_km: float | None
) -> int:
    """
    Calculate a 0-100 risk score based on price, yield, water, and market access risks.
    Weights: Price (30%), Yield (30%), Water (25%), Market (15%).
    """
    # 1. Price risk (Weight: 0.30)
    if trend is None:
        price_risk = 0.30
    else:
        trend_upper = str(trend).upper().strip()
        if trend_upper == "RISING":
            price_risk = 0.10
        elif trend_upper == "STABLE":
            price_risk = 0.30
        elif trend_upper == "FALLING":
            price_risk = 0.70
        else:
            price_risk = 0.30

    # 2. Yield risk (Weight: 0.30)
    yield_risk = (100.0 - float(suitability_score)) / 100.0
    yield_risk = min(max(yield_risk, 0.0), 1.0)

    # 3. Water risk (Weight: 0.25)
    req_upper = str(water_requirement).upper().strip()
    if water_availability:
        if req_upper == "HIGH":
            water_risk = 0.70
        elif req_upper == "MEDIUM":
            water_risk = 0.56
        else: # LOW
            water_risk = 0.0
    else:
        if req_upper == "HIGH":
            water_risk = 0.95
        elif req_upper == "MEDIUM":
            water_risk = 0.80
        else: # LOW
            water_risk = 0.30

    # 4. Market risk (Weight: 0.15)
    if distance_km is None:
        market_risk = 0.50
    else:
        d = float(distance_km)
        market_risk = min((d / 100.0) + 0.50, 1.0)

    # Aggregate weighted risk
    weighted_sum = (
        price_risk * 0.30 +
        yield_risk * 0.30 +
        water_risk * 0.25 +
        market_risk * 0.15
    )
    
    risk_score = int(min(max(round(weighted_sum * 100.0), 0), 100))
    return risk_score
