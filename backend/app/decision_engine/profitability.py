"""
Deterministic profitability scoring engine.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class Factor:
    name: str
    value: float
    weight: float
    contribution: float
    explanation: str

@dataclass
class ProfitabilityResult:
    expected_yield: float
    yield_unit: str
    production_cost: int            # INR/acre
    expected_revenue: int           # INR/acre
    estimated_profit: int           # INR/acre
    current_crop_profit: int        # INR/acre
    profit_difference: int          # INR/acre
    profitability_score: int        # 0-100
    factors: List[Factor] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)
    data_status: str = "DEMO"
    disclaimer: str = ""

def clamp(val: float, min_val: float, max_val: float) -> int:
    return int(max(min_val, min(max_val, val)))

def calculate_profitability(
    farm_conditions: dict,
    current_crop_econ: dict,
    alternative_crop_econ: dict,
    land_area_acre: float = 1.0
) -> ProfitabilityResult:
    """
    Calculate crop yields, revenues, production costs, profits, and a normalized
    profitability score comparing the alternative crop to the current crop.
    Deterministic weighted decision engine (rule-based).
    """
    # Extract current crop economics
    curr_yield = float(current_crop_econ.get("expected_yield_per_acre", 0.0))
    curr_unit = current_crop_econ.get("yield_unit", "unit")
    curr_cost = float(current_crop_econ.get("production_cost_per_acre", 0.0))
    curr_price = float(current_crop_econ.get("expected_price_per_unit", 0.0))
    curr_source = current_crop_econ.get("data_source", "Unknown")
    curr_status = current_crop_econ.get("data_status", "DEMO")

    # Extract alternative crop economics
    alt_yield = float(alternative_crop_econ.get("expected_yield_per_acre", 0.0))
    alt_unit = alternative_crop_econ.get("yield_unit", "unit")
    alt_cost = float(alternative_crop_econ.get("production_cost_per_acre", 0.0))
    alt_price = float(alternative_crop_econ.get("expected_price_per_unit", 0.0))
    alt_source = alternative_crop_econ.get("data_source", "Unknown")
    alt_status = alternative_crop_econ.get("data_status", "DEMO")

    # Revenue and Profit formulas (per acre)
    curr_revenue = curr_yield * curr_price
    curr_profit = curr_revenue - curr_cost

    alt_revenue = alt_yield * alt_price
    alt_profit = alt_revenue - alt_cost

    profit_diff = alt_profit - curr_profit

    # Profitability Score Normalization
    ratio = profit_diff / max(curr_profit, 1.0)
    score = clamp(round(50.0 + ratio * 100.0), 0, 100)

    # Explanations / Factors
    factors = [
        Factor(
            name="Current crop estimated profit",
            value=curr_profit,
            weight=0.0,
            contribution=0.0,
            explanation=f"Estimated profit of current crop: {int(round(curr_profit))} INR/acre"
        ),
        Factor(
            name="Alternative crop estimated profit",
            value=alt_profit,
            weight=0.0,
            contribution=0.0,
            explanation=f"Estimated profit of alternative crop: {int(round(alt_profit))} INR/acre"
        ),
        Factor(
            name="Profit difference",
            value=profit_diff,
            weight=1.0,
            contribution=profit_diff,
            explanation=f"Potential profit difference: {int(round(profit_diff))} INR/acre"
        )
    ]

    # Collect Assumptions
    assumptions = [
        f"Region: {farm_conditions.get('district', 'Unknown')}, {farm_conditions.get('state', 'Unknown')}",
        f"Land Area: {land_area_acre} acres",
        f"Current Crop Yield Source: {curr_source} (Status: {curr_status})",
        f"Current Crop Price Source: {curr_source}",
        f"Current Crop Cost Source: {curr_source}",
        f"Alternative Crop Yield Source: {alt_source} (Status: {alt_status})",
        f"Alternative Crop Price Source: {alt_source}",
        f"Alternative Crop Cost Source: {alt_source}"
    ]

    # Data Status: use alternative's status or current status
    # Standard rule: use alternative crop economics status
    status = alt_status

    # Disclaimer
    disclaimer = f"Estimated figures based on {alt_source}. Actual results vary."

    return ProfitabilityResult(
        expected_yield=alt_yield,
        yield_unit=alt_unit,
        production_cost=int(round(alt_cost)),
        expected_revenue=int(round(alt_revenue)),
        estimated_profit=int(round(alt_profit)),
        current_crop_profit=int(round(curr_profit)),
        profit_difference=int(round(profit_diff)),
        profitability_score=score,
        factors=factors,
        assumptions=assumptions,
        data_status=status,
        disclaimer=disclaimer
    )
