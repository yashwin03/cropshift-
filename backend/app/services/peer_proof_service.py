"""
peer_proof_service.py -- Pure data access & aggregation service for Peer Proof / Farmer Network.
"""
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.peer_proof import PeerProof
from app.models.crop import Crop
from app.models.farm import Farm
from app.utils.geo import haversine_distance

MIN_COHORT_SIZE = 1

DISTRICT_COORDINATES: Dict[str, tuple[float, float]] = {
    "dharwad": (15.4589, 75.0078),
    "haveri": (14.7960, 75.4000),
    "tumkur": (13.3409, 77.1025),
    "tumakuru": (13.3409, 77.1025),
    "belagavi": (15.8497, 74.5085),
    "shivamogga": (13.9299, 75.5680),
    "hassan": (13.0033, 76.1004),
    "mysuru": (12.2958, 76.6394),
    "mysore": (12.2958, 76.6394),
    "raichur": (16.2076, 77.3557),
    "ballari": (15.1394, 76.9214),
    "gadag": (15.4290, 75.6260),
    "davanagere": (14.4644, 75.9220),
    "chikkamagaluru": (13.3161, 75.7720),
    "mandya": (12.5218, 76.8951),
    "bengaluru rural": (13.2257, 77.5750),
    "chitradurga": (14.2251, 76.3980),
    "vijayapura": (16.8302, 75.7100),
    "bijapur": (16.8302, 75.7100),
}


def get_peer_proof_for_crop(
    db: Session,
    crop_id: int,
    district: Optional[str] = "Dharwad",
    land_area_acres: float = 1.0,
    radius_km: float = 50.0,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    farm_id: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Fetch distance-filtered peer proof records for a given crop and location.
    Calculates backend distance_km and filters by radius_km (50 or 100).
    """
    crop = db.get(Crop, crop_id)
    crop_name = crop.name if crop else "Oilseed Crop"

    center_lat: Optional[float] = latitude
    center_lon: Optional[float] = longitude

    if (center_lat is None or center_lon is None) and farm_id:
        farm = db.get(Farm, farm_id)
        if farm:
            if hasattr(farm, 'latitude') and farm.latitude and hasattr(farm, 'longitude') and farm.longitude:
                center_lat = float(farm.latitude)
                center_lon = float(farm.longitude)

    if (center_lat is None or center_lon is None) and district:
        dist_key = district.lower().strip()
        if dist_key in DISTRICT_COORDINATES:
            center_lat, center_lon = DISTRICT_COORDINATES[dist_key]

    if center_lat is None or center_lon is None:
        center_lat, center_lon = 15.4589, 75.0078  # Default Dharwad coordinates

    all_crop_records = (
        db.query(PeerProof)
        .filter(PeerProof.crop_id == crop_id)
        .all()
    )

    all_peers_calculated = []
    peers_with_dist = []
    for r in all_crop_records:
        r_lat = r.latitude
        r_lon = r.longitude

        if r_lat is None or r_lon is None:
            dist_key = (r.district or "").lower().strip()
            if dist_key in DISTRICT_COORDINATES:
                r_lat, r_lon = DISTRICT_COORDINATES[dist_key]
            else:
                r_lat, r_lon = center_lat + 0.1, center_lon + 0.1

        dist = haversine_distance(center_lat, center_lon, float(r_lat), float(r_lon))
        dist_km = round(dist, 1)

        item_tuple = (r, dist_km, float(r_lat), float(r_lon))
        all_peers_calculated.append(item_tuple)
        if dist_km <= radius_km:
            peers_with_dist.append(item_tuple)

    all_peers_calculated.sort(key=lambda x: x[1])
    peers_with_dist.sort(key=lambda x: x[1])

    is_fallback = False
    if len(peers_with_dist) == 0 and len(all_peers_calculated) > 0:
        peers_with_dist = all_peers_calculated
        is_fallback = True

    cohort_count = len(peers_with_dist)
    if cohort_count == 0:
        return {
            "available": False,
            "crop_id": crop_id,
            "crop_name": crop_name,
            "radius_km": radius_km,
            "cohort_count": 0,
            "total_farmers": 0,
            "total_districts": 0,
            "regions": [],
            "center_latitude": center_lat,
            "center_longitude": center_lon,
            "geographic_scope": f"Within {int(radius_km)} km radius",
            "message": f"No verified peer records found for {crop_name} within {int(radius_km)} km.",
            "data_source": "CropShift demo dataset",
            "verification_status": "Demo data — not real farmer verification",
            "peers": []
        }

    matched_records = [item[0] for item in peers_with_dist]
    avg_yield = sum(r.yield_quintals_per_acre for r in matched_records) / cohort_count
    avg_price = sum(r.selling_price_per_quintal for r in matched_records) / cohort_count

    net_realizations = [
        r.net_realization_per_acre
        if r.net_realization_per_acre is not None
        else (r.selling_price_per_quintal * r.yield_quintals_per_acre - (r.cultivation_cost_per_acre or 0.0))
        for r in matched_records
    ]
    avg_net_realization = sum(net_realizations) / cohort_count

    seasons = list(set(r.season for r in matched_records if r.season))
    season_str = seasons[0] if seasons else "Kharif 2025"

    min_area = min(r.cultivated_area_acres for r in matched_records)
    max_area = max(r.cultivated_area_acres for r in matched_records)
    farm_size_range = f"{min_area:.1f} - {max_area:.1f} acres"

    # Compute district regional aggregation
    district_counts: Dict[str, int] = {}
    for r, dist_km, r_lat, r_lon in peers_with_dist:
        d_name = r.district or "Karnataka"
        district_counts[d_name] = district_counts.get(d_name, 0) + 1

    regions_summary = [
        {"district": d_name, "farmer_count": count}
        for d_name, count in sorted(district_counts.items(), key=lambda x: x[1], reverse=True)
    ]

    peers_list = []
    for r, dist_km, r_lat, r_lon in peers_with_dist:
        peers_list.append({
            "id": r.id,
            "peer_display_id": r.farmer_display_name or f"CropShift Demo Farmer #{r.id}",
            "crop_id": r.crop_id,
            "crop_name": crop_name,
            "district": r.district,
            "state": r.state,
            "distance_km": dist_km,
            "latitude": r_lat,
            "longitude": r_lon,
            "acres": r.cultivated_area_acres,
            "yield_per_acre": r.yield_quintals_per_acre,
            "selling_price": r.selling_price_per_quintal,
            "net_realization": r.net_realization_per_acre,
            "crop_stage": r.crop_stage or "Pod Formation",
            "expected_harvest": r.expected_harvest or "Oct 2025",
            "soil_type": r.soil_type or "Red Laterite",
            "water_source": r.water_source or "Borewell",
            "contactable": r.contactable,
            "verification_status": r.verification_status or "Demo data — not real farmer verification",
            "label": "CropShift Demo Farmer",
        })

    return {
        "available": True,
        "crop_id": crop_id,
        "crop_name": crop_name,
        "radius_km": radius_km,
        "cohort_count": cohort_count,
        "total_farmers": cohort_count,
        "total_districts": len(regions_summary),
        "regions": regions_summary,
        "center_latitude": center_lat,
        "center_longitude": center_lon,
        "geographic_scope": f"Within {int(radius_km)} km radius" if not is_fallback else f"Regional Karnataka peer network ({int(radius_km)} km expanded)",
        "season": season_str,
        "farm_size_range": farm_size_range,
        "average_yield_quintals_per_acre": round(avg_yield, 2),
        "average_selling_price_per_quintal": round(avg_price, 2),
        "average_net_realization_per_acre": round(avg_net_realization, 2),
        "data_source": "CropShift demo dataset",
        "verification_status": "Demo data — not real farmer verification",
        "peers": peers_list
    }


def request_peer_contact(
    db: Session,
    peer_proof_id: int
) -> Optional[Dict[str, Any]]:
    """
    Request contact info for an opted-in contactable peer.
    Ensures contactable == True before returning details.
    """
    record = db.get(PeerProof, peer_proof_id)
    if not record or not record.contactable:
        return None

    return {
        "id": record.id,
        "farmer_display_name": record.farmer_display_name or f"CropShift Demo Farmer #{record.id}",
        "district": record.district,
        "state": record.state,
        "phone": record.contact_phone or "9876500000",
        "email": record.contact_email or "peer@cropshift.com",
        "contactable": True,
        "verification_status": record.verification_status
    }

