"""
Market Intelligence scoring engine.
Deterministic weighted scoring.
"""

def score_market_engine(
    current_price: float | None,
    reference_price: float | None,
    trend: str | None,
    distance_km: float | None,
    data_status: str | None,
) -> dict:
    """
    Compute a normalized 0-100 market score based on price level, trend, distance,
    and data reliability.
    """
    # 1. Price level component (Weight: 0.40)
    if current_price is None or reference_price is None or reference_price <= 0:
        price_score = 60.0
    else:
        price_ratio = current_price / reference_price
        price_score = min(max(price_ratio * 100.0, 0.0), 100.0)

    # 2. Trend component (Weight: 0.30)
    if trend is None:
        trend_score = 60.0
    else:
        trend_upper = str(trend).upper().strip()
        if trend_upper == "RISING":
            trend_score = 85.0
        elif trend_upper == "STABLE":
            trend_score = 65.0
        elif trend_upper == "FALLING":
            trend_score = 40.0
        else:
            trend_score = 60.0

    # 3. Market Access component (Weight: 0.20)
    if distance_km is None:
        distance_score = 60.0
    else:
        d = float(distance_km)
        if d <= 10.0:
            distance_score = 100.0
        elif d <= 25.0:
            distance_score = 85.0
        elif d <= 50.0:
            distance_score = 70.0
        elif d <= 100.0:
            distance_score = 50.0
        else:
            distance_score = 30.0

    # 4. Data Reliability component (Weight: 0.10)
    if data_status is None:
        reliability_score = 60.0
    else:
        status_upper = str(data_status).upper().strip()
        if status_upper == "REAL":
            reliability_score = 100.0
        elif status_upper == "STATIC":
            reliability_score = 75.0
        elif status_upper == "ESTIMATED":
            reliability_score = 60.0
        elif status_upper == "DEMO":
            reliability_score = 50.0
        else:
            reliability_score = 60.0

    # Compute final score
    weighted_sum = (
        (price_score * 0.40) +
        (trend_score * 0.30) +
        (distance_score * 0.20) +
        (reliability_score * 0.10)
    )
    final_score = int(min(max(round(weighted_sum), 0), 100))

    return {
        "market_score": final_score,
        "price_score": price_score,
        "trend_score": trend_score,
        "distance_score": distance_score,
        "reliability_score": reliability_score,
    }
