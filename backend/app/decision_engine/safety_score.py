"""
Safety score calculation engine.
Deterministic inverse scoring of aggregated risk factors.
"""
from dataclasses import dataclass, field
from typing import List
from app.decision_engine.risk import RiskFactor

@dataclass
class SafetyResult:
    safety_score: int
    weighted_risk: float
    factors: List[RiskFactor] = field(default_factory=list)
    confidence: str = "HIGH"
    notes: List[str] = field(default_factory=list)

def clamp(val: float, min_val: float, max_val: float) -> int:
    return int(max(min_val, min(max_val, val)))

def calculate_safety_score(risk_factors: list[RiskFactor]) -> SafetyResult:
    """
    Calculate safety score based on risk factors.
    Deterministic weighted scoring.
    """
    if not risk_factors:
        return SafetyResult(
            safety_score=100,
            weighted_risk=0.0,
            factors=[],
            confidence="MEDIUM",
            notes=["No hazards were assessed."]
        )

    sum_weighted_risk = 0.0
    sum_weights = 0.0

    for rf in risk_factors:
        sum_weighted_risk += rf.raw_risk_level * rf.weight
        sum_weights += rf.weight

    if sum_weights == 0.0:
        weighted_risk = 0.0
    else:
        weighted_risk = sum_weighted_risk / sum_weights

    safety_score = clamp(round((1.0 - weighted_risk) * 100.0), 0, 100)

    # Determine confidence (default to HIGH since data is present)
    confidence = "HIGH"

    return SafetyResult(
        safety_score=safety_score,
        weighted_risk=weighted_risk,
        factors=risk_factors,
        confidence=confidence,
        notes=[]
    )

@dataclass
class SafetyScoreResult:
    safety_score: int
    decision: str
    components: dict
    weights: dict
    thresholds: dict
    confidence: str
    notes: List[str]

def calculate_headline_safety_score(
    suitability: float | None,
    profitability: float | None,
    market: float | None,
    risk: float | None
) -> SafetyScoreResult:
    """
    Calculate the headline safety score based on:
      - Suitability (Weight: 0.35)
      - Profitability (Weight: 0.30)
      - Market (Weight: 0.20)
      - Risk Inverse (Weight: 0.15), where Risk Inverse = 100 - Risk

    All weights, components, and missing-data substitutions are fully documented.
    Compute in float, round once at the end, and clamp to [0, 100].
    """
    weights = {
        "suitability": 0.35,
        "profitability": 0.30,
        "market": 0.20,
        "risk_inverse": 0.15
    }

    thresholds = {
        "SWITCH": (80, 100),
        "CAUTION": (60, 79),
        "DONT_SWITCH": (0, 59)
    }

    notes = []
    defaults_count = 0

    # 1. Resolve Suitability
    if suitability is None:
        eff_suitability = 60.0
        defaults_count += 1
        notes.append("Suitability score unavailable; neutral default of 60 used.")
    else:
        eff_suitability = float(suitability)

    # 2. Resolve Profitability
    if profitability is None:
        eff_profitability = 60.0
        defaults_count += 1
        notes.append("Profitability score unavailable; neutral default of 60 used.")
    else:
        eff_profitability = float(profitability)

    # 3. Resolve Market
    if market is None:
        eff_market = 60.0
        defaults_count += 1
        notes.append("Market score unavailable; neutral default of 60 used.")
    else:
        eff_market = float(market)

    # 4. Resolve Risk and compute Risk Inverse
    if risk is None:
        eff_risk_inverse = 60.0
        defaults_count += 1
        notes.append("Risk score unavailable; neutral default of 60 used for Risk Inverse.")
    else:
        eff_risk_inverse = 100.0 - float(risk)

    # Compute weighted score
    contrib_suitability = eff_suitability * weights["suitability"]
    contrib_profitability = eff_profitability * weights["profitability"]
    contrib_market = eff_market * weights["market"]
    contrib_risk_inverse = eff_risk_inverse * weights["risk_inverse"]

    weighted_sum = (
        contrib_suitability +
        contrib_profitability +
        contrib_market +
        contrib_risk_inverse
    )

    safety_score = clamp(round(weighted_sum), 0, 100)

    # Determine Decision
    if safety_score >= 80:
        decision = "SWITCH"
    elif safety_score >= 60:
        decision = "CAUTION"
    else:
        decision = "DONT_SWITCH"

    # Determine Confidence
    if defaults_count == 0:
        confidence = "HIGH"
    elif defaults_count == 1:
        confidence = "MEDIUM"
    else:
        confidence = "LOW"

    components = {
        "suitability": {
            "value": eff_suitability,
            "weight": weights["suitability"],
            "contribution": contrib_suitability
        },
        "profitability": {
            "value": eff_profitability,
            "weight": weights["profitability"],
            "contribution": contrib_profitability
        },
        "market": {
            "value": eff_market,
            "weight": weights["market"],
            "contribution": contrib_market
        },
        "risk_inverse": {
            "value": eff_risk_inverse,
            "weight": weights["risk_inverse"],
            "contribution": contrib_risk_inverse
        }
    }

    return SafetyScoreResult(
        safety_score=safety_score,
        decision=decision,
        components=components,
        weights=weights,
        thresholds=thresholds,
        confidence=confidence,
        notes=notes
    )
