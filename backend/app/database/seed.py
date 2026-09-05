"""
seed.py -- Deterministic, idempotent seed data for CropShift A1.

Seed strategy: use INSERT ... ON CONFLICT DO NOTHING (via SQLAlchemy merge-by-pk).
Running this script twice yields identical row counts.

DATA STATUS: DEMO -- all numeric values are hand-authored for demonstration purposes.
Sources: ICAR crop guides, Karnataka state agriculture department references (STATIC).

Usage:
    python -m app.database.seed
"""

import app.patch_bcrypt
import datetime
import logging

from geoalchemy2.elements import WKTElement
from sqlalchemy.orm import Session

from .session import engine
from .init_db import init_db
from ..models import (
    Farmer,
    Farm,
    Crop,
    CropType,
    CropEconomics,
    CropSuitability,
    Market,
    MarketPrice,
    Subsidy,
    RiskScenario,
    RiskCode,
    User,
    UserRole,
    PeerProof,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _point(lon: float, lat: float) -> WKTElement:
    """Return a PostGIS POINT geometry in SRID 4326."""
    return WKTElement(f"POINT({lon} {lat})", srid=4326)


def _get_or_create(session: Session, model, pk_value: int, **kwargs):
    """Fetch by pk or username/name; if missing, create and add to session."""
    obj = session.get(model, pk_value)
    if obj is None and "username" in kwargs:
        obj = session.query(model).filter_by(username=kwargs["username"]).first()
    if obj is None and "name" in kwargs:
        obj = session.query(model).filter_by(name=kwargs["name"]).first()
    if obj is None:
        obj = model(id=pk_value, **kwargs)
        session.add(obj)
    return obj


# ---------------------------------------------------------------------------
# Seed users
# ---------------------------------------------------------------------------
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

USERS = [
    dict(id=1, username="demo", email="demo@cropshift.com", hashed_password=pwd_context.hash("password123"), role=UserRole.FARMER, is_active=True),
    dict(id=2, username="buyer_demo", email="buyer@cropshift.com", hashed_password=pwd_context.hash("password123"), role=UserRole.BUYER, is_active=True),

    # 8 Persistent Farmer Hackathon Accounts
    dict(id=101, username="Farmer 1 (Raju Naik)", email="farmer1@cropshift.com", hashed_password=pwd_context.hash("password123"), role=UserRole.FARMER, is_active=True),
    dict(id=102, username="Farmer 2 (Suresh Gowda)", email="farmer2@cropshift.com", hashed_password=pwd_context.hash("password123"), role=UserRole.FARMER, is_active=True),
    dict(id=103, username="Farmer 3 (Ramesh Patil)", email="farmer3@cropshift.com", hashed_password=pwd_context.hash("password123"), role=UserRole.FARMER, is_active=True),
    dict(id=104, username="Farmer 4 (Venkatesh Rao)", email="farmer4@cropshift.com", hashed_password=pwd_context.hash("password123"), role=UserRole.FARMER, is_active=True),
    dict(id=105, username="Farmer 5 (Mallikarjun B)", email="farmer5@cropshift.com", hashed_password=pwd_context.hash("password123"), role=UserRole.FARMER, is_active=True),
    dict(id=106, username="Farmer 6 (Anand Hegde)", email="farmer6@cropshift.com", hashed_password=pwd_context.hash("password123"), role=UserRole.FARMER, is_active=True),
    dict(id=107, username="Farmer 7 (Basavaraj K)", email="farmer7@cropshift.com", hashed_password=pwd_context.hash("password123"), role=UserRole.FARMER, is_active=True),
    dict(id=108, username="Farmer 8 (Chandrashekar M)", email="farmer8@cropshift.com", hashed_password=pwd_context.hash("password123"), role=UserRole.FARMER, is_active=True),

    # 8 Persistent Buyer Hackathon Accounts
    dict(id=201, username="Buyer 1 (Karnataka Oil Processing Ltd)", email="buyer1@cropshift.com", hashed_password=pwd_context.hash("password123"), role=UserRole.BUYER, is_active=True),
    dict(id=202, username="Buyer 2 (Deccan Agri Procurements)", email="buyer2@cropshift.com", hashed_password=pwd_context.hash("password123"), role=UserRole.BUYER, is_active=True),
    dict(id=203, username="Buyer 3 (Southern Oilseed Millers Co)", email="buyer3@cropshift.com", hashed_password=pwd_context.hash("password123"), role=UserRole.BUYER, is_active=True),
    dict(id=204, username="Buyer 4 (Apex Agro Exports)", email="buyer4@cropshift.com", hashed_password=pwd_context.hash("password123"), role=UserRole.BUYER, is_active=True),
    dict(id=205, username="Buyer 5 (GreenValley BioRefineries)", email="buyer5@cropshift.com", hashed_password=pwd_context.hash("password123"), role=UserRole.BUYER, is_active=True),
    dict(id=206, username="Buyer 6 (Challakere Oil Industries)", email="buyer6@cropshift.com", hashed_password=pwd_context.hash("password123"), role=UserRole.BUYER, is_active=True),
    dict(id=207, username="Buyer 7 (Malnad Solvent Extractors)", email="buyer7@cropshift.com", hashed_password=pwd_context.hash("password123"), role=UserRole.BUYER, is_active=True),
    dict(id=208, username="Buyer 8 (Dharwad Agro Trading)", email="buyer8@cropshift.com", hashed_password=pwd_context.hash("password123"), role=UserRole.BUYER, is_active=True),
]

CROPS = [
    # 1. Paddy (non-oilseed baseline shift source)
    dict(id=1, name="Paddy", crop_type=CropType.CEREAL, season="Kharif", expected_yield_range="18 - 25 Quintal / acre", water_requirement_level="HIGH"),
    # 9 Primary Oilseeds + Safflower + Niger + Linseed + Sesame Black
    dict(id=2, name="Groundnut", crop_type=CropType.OILSEED, season="Kharif / Rabi", expected_yield_range="8 - 12 Quintal / acre", water_requirement_level="MEDIUM"),
    dict(id=3, name="Sunflower", crop_type=CropType.OILSEED, season="Rabi", expected_yield_range="6 - 10 Quintal / acre", water_requirement_level="MEDIUM"),
    dict(id=4, name="Soybean", crop_type=CropType.OILSEED, season="Kharif", expected_yield_range="7 - 10 Quintal / acre", water_requirement_level="MEDIUM"),
    dict(id=5, name="Mustard", crop_type=CropType.OILSEED, season="Rabi", expected_yield_range="5 - 8 Quintal / acre", water_requirement_level="LOW"),
    dict(id=6, name="Sesame", crop_type=CropType.OILSEED, season="Kharif / Summer", expected_yield_range="3 - 6 Quintal / acre", water_requirement_level="LOW"),
    dict(id=7, name="Maize", crop_type=CropType.CEREAL, season="Kharif", expected_yield_range="20 - 30 Quintal / acre", water_requirement_level="MEDIUM"),
    dict(id=8, name="Safflower", crop_type=CropType.OILSEED, season="Rabi", expected_yield_range="5 - 9 Quintal / acre", water_requirement_level="LOW"),
    dict(id=9, name="Niger", crop_type=CropType.OILSEED, season="Kharif", expected_yield_range="3 - 5 Quintal / acre", water_requirement_level="LOW"),
    dict(id=10, name="Castor", crop_type=CropType.OILSEED, season="Kharif / Rabi", expected_yield_range="10 - 15 Quintal / acre", water_requirement_level="MEDIUM"),
    dict(id=11, name="Linseed", crop_type=CropType.OILSEED, season="Rabi", expected_yield_range="4 - 7 Quintal / acre", water_requirement_level="LOW"),
    dict(id=12, name="Sesame (Black)", crop_type=CropType.OILSEED, season="Kharif", expected_yield_range="3 - 6 Quintal / acre", water_requirement_level="LOW"),
]

FARMERS = [
    dict(id=1, user_id=1, district="Dharwad", state="Karnataka", phone="9876543210"),
]

FARMS = [
    dict(id=1, farmer_id=1, name="Green Field Farm", land_area_acre=2.5, location=_point(75.0078, 15.4589), district="Dharwad", state="Karnataka", water_availability=True, soil_type="Red Laterite"),
]

CROP_ECONOMICS = [
    # (id, crop_id, region, expected_yield_per_acre, yield_unit, production_cost_per_acre, expected_price_per_unit, status, source)
    (1,  1, "Tumkur",     20.0, "Quintal / acre", 18000.0, 2550.0, "STATIC",    "Agmarknet / ICAR snapshot"),
    (2,  1, "Haveri",     22.0, "Quintal / acre", 18500.0, 2600.0, "STATIC",    "Agmarknet / ICAR snapshot"),
    (3,  2, "Tumkur",      9.5, "Quintal / acre", 13000.0, 5600.0, "ESTIMATED", "Agmarknet / ICAR snapshot"),
    (4,  2, "Dharwad",    10.0, "Quintal / acre", 13200.0, 5700.0, "ESTIMATED", "Agmarknet / ICAR snapshot"),
    (5,  3, "Dharwad",     9.0, "Quintal / acre", 11000.0, 5400.0, "ESTIMATED", "Agmarknet / ICAR snapshot"),
    (6,  3, "Haveri",      9.5, "Quintal / acre", 11200.0, 5500.0, "ESTIMATED", "Agmarknet / ICAR snapshot"),
    (7,  4, "Haveri",      8.5, "Quintal / acre", 11500.0, 4850.0, "ESTIMATED", "Agmarknet / ICAR snapshot"),
    (8,  4, "Dharwad",     8.8, "Quintal / acre", 11800.0, 4900.0, "ESTIMATED", "Agmarknet / ICAR snapshot"),
    (9,  5, "Dharwad",     7.2, "Quintal / acre",  8500.0, 5450.0, "ESTIMATED", "Agmarknet / ICAR snapshot"),
    (10, 5, "Tumkur",      7.5, "Quintal / acre",  8700.0, 5500.0, "ESTIMATED", "Agmarknet / ICAR snapshot"),
    (11, 6, "Tumkur",      5.2, "Quintal / acre",  7500.0, 7400.0, "ESTIMATED", "Agmarknet / ICAR snapshot"),
    (12, 6, "Dharwad",     5.5, "Quintal / acre",  7700.0, 7500.0, "ESTIMATED", "Agmarknet / ICAR snapshot"),
    (13, 7, "Haveri",     25.0, "Quintal / acre", 15000.0, 1550.0, "STATIC",    "Agmarknet / ICAR snapshot"),
    (14, 7, "Tumkur",     24.0, "Quintal / acre", 14800.0, 1500.0, "STATIC",    "Agmarknet / ICAR snapshot"),
    (15, 8, "Tumkur",      7.8, "Quintal / acre",  9200.0, 5800.0, "ESTIMATED", "Agmarknet / ICAR snapshot"),
    (16, 8, "Dharwad",     8.0, "Quintal / acre",  9400.0, 5900.0, "ESTIMATED", "Agmarknet / ICAR snapshot"),
    (17, 9, "Tumkur",      5.0, "Quintal / acre",  6800.0, 6500.0, "ESTIMATED", "Agmarknet / ICAR snapshot"),
    (18, 9, "Haveri",      5.3, "Quintal / acre",  7000.0, 6600.0, "ESTIMATED", "Agmarknet / ICAR snapshot"),
    (19, 10, "Dharwad",    9.8, "Quintal / acre", 11500.0, 5850.0, "ESTIMATED", "Agmarknet / ICAR snapshot"),
    (20, 10, "Tumkur",    10.0, "Quintal / acre", 11800.0, 5900.0, "ESTIMATED", "Agmarknet / ICAR snapshot"),
    (21, 11, "Haveri",     6.0, "Quintal / acre",  7800.0, 5600.0, "ESTIMATED", "Agmarknet / ICAR snapshot"),
    (22, 11, "Dharwad",    6.2, "Quintal / acre",  8000.0, 5700.0, "ESTIMATED", "Agmarknet / ICAR snapshot"),
    (23, 12, "Tumkur",     4.8, "Quintal / acre",  7600.0, 7800.0, "ESTIMATED", "Agmarknet / ICAR snapshot"),
    (24, 12, "Dharwad",    5.0, "Quintal / acre",  7800.0, 7900.0, "ESTIMATED", "Agmarknet / ICAR snapshot"),
]

CROP_SUITABILITIES = [
    # (id, crop_id, region, soil_type, water_req, base_score, notes)
    (1,  1, "Tumkur",     "red laterite",  "HIGH",   75.0, "Suitable with irrigation"),
    (2,  1, "Haveri",      "black cotton",  "HIGH",   80.0, "Good canal irrigation"),
    
    # Groundnut (Crop 2)
    (3,  2, "Tumkur",     "red laterite",  "MEDIUM", 87.0, "Excellent red soil fit"),
    (4,  2, "Dharwad",    "red laterite",  "MEDIUM", 85.0, "Good oilseed region"),
    (5,  2, "Haveri",     "red laterite",  "MEDIUM", 84.0, "High potential"),
    (6,  2, "Belagavi",   "red laterite",  "MEDIUM", 82.0, "Suitable"),

    # Sunflower (Crop 3)
    (7,  3, "Dharwad",    "black cotton",  "MEDIUM", 88.0, "Rabi season black soil prime fit"),
    (8,  3, "Haveri",     "black cotton",  "MEDIUM", 86.0, "Excellent black soil yield"),
    (9,  3, "Belagavi",   "black cotton",  "MEDIUM", 85.0, "Good yield potential"),
    (10, 3, "Tumkur",     "red laterite",  "MEDIUM", 78.0, "Moderate fit"),

    # Soybean (Crop 4)
    (11, 4, "Haveri",     "black cotton",  "MEDIUM", 87.0, "Kharif soybean belt"),
    (12, 4, "Dharwad",    "black cotton",  "MEDIUM", 85.0, "Black soil optimal"),
    (13, 4, "Belagavi",   "black cotton",  "MEDIUM", 84.0, "Good Kharif fit"),

    # Mustard (Crop 5) — Dryland low-water fit
    (14, 5, "Dharwad",    "red laterite",  "LOW",    86.0, "Excellent low water dryland fit"),
    (15, 5, "Tumkur",     "red laterite",  "LOW",    85.0, "Top dryland crop"),
    (16, 5, "Haveri",     "red laterite",  "LOW",    82.0, "Suitable for dry season"),

    # Sesame (Crop 6) — Low water / high value
    (17, 6, "Tumkur",     "red laterite",  "LOW",    88.0, "Drought tolerant high value"),
    (18, 6, "Dharwad",    "red laterite",  "LOW",    84.0, "Low water high market value"),
    (19, 6, "Haveri",     "red laterite",  "LOW",    82.0, "Summer/Kharif suitable"),

    # Maize (Crop 7)
    (20, 7, "Haveri",     "black cotton",  "MEDIUM", 83.0, "Good maize area"),
    (21, 7, "Tumkur",     "red laterite",  "MEDIUM", 77.0, "Moderate yield"),

    # Safflower (Crop 8) — Rabi low water
    (22, 8, "Tumkur",     "black cotton",  "LOW",    87.0, "Rabi drought resistant prime fit"),
    (23, 8, "Dharwad",    "black cotton",  "LOW",    85.0, "Deep black soil rabi fit"),

    # Niger (Crop 9)
    (24, 9, "Tumkur",     "red laterite",  "LOW",    81.0, "Kharif dryland crop"),
    (25, 9, "Haveri",     "black cotton",  "LOW",    80.0, "Suitable"),

    # Castor (Crop 10)
    (26, 10, "Dharwad",   "red laterite",  "MEDIUM", 81.0, "Deep soil suitable"),
    (27, 10, "Tumkur",    "red laterite",  "MEDIUM", 80.0, "Good yield"),
    (28, 10, "Haveri",    "red laterite",  "MEDIUM", 79.0, "Moderate fit"),

    # Linseed (Crop 11)
    (29, 11, "Haveri",    "black cotton",  "LOW",    82.0, "Rabi linseed fit"),
    (30, 11, "Dharwad",   "red laterite",  "LOW",    80.0, "Moderate fit"),

    # Sesame Black (Crop 12)
    (31, 12, "Tumkur",    "red laterite",  "LOW",    86.0, "High value specialty oilseed"),
    (32, 12, "Dharwad",   "red laterite",  "LOW",    83.0, "Suitable for dryland"),
]

# ---------------------------------------------------------------------------
# Peer Proofs (DEMO DATASET — Dense, accurate spatial coverage per crop)
# ---------------------------------------------------------------------------

_PEER_SOURCE = "CropShift demo dataset"
_PEER_VERIF  = "Demo data — not real farmer verification"

# Base coordinates per district for geographic distribution
DISTRICT_LOCS = {
    "Dharwad": (15.4589, 75.0078),
    "Haveri": (14.7960, 75.4000),       # ~80 km from Dharwad
    "Belagavi": (15.8497, 74.5085),     # ~70 km from Dharwad
    "Gadag": (15.4290, 75.6260),        # ~67 km from Dharwad
    "Tumkur": (13.3409, 77.1025),       # ~300 km
    "Davanagere": (14.4644, 75.9220),   # ~150 km
    "Shivamogga": (13.9299, 75.5680),   # ~190 km
    "Chitradurga": (14.2251, 76.3980),  # ~210 km
    "Mysuru": (12.2958, 76.6394),       # ~390 km
}

PEER_PROOFS = []

def _gen_peers():
    pid = 1
    # Oilseed crops specs: (crop_id, crop_name, base_yield, base_price, season, stage)
    oilseed_specs = [
        (2, "Groundnut", 9.5, 5700, "Kharif 2025", "Pod Formation"),
        (3, "Sunflower", 8.8, 5450, "Rabi 2025", "Head Development"),
        (4, "Soybean", 8.5, 4900, "Kharif 2025", "Pod Filling"),
        (5, "Mustard", 7.2, 5450, "Rabi 2025", "Pod Development"),
        (6, "Sesame", 5.2, 7450, "Kharif 2025", "Capsule Formation"),
        (8, "Safflower", 7.8, 5800, "Rabi 2025", "Maturity"),
        (9, "Niger", 5.0, 6500, "Kharif 2025", "Flowering"),
        (10, "Castor", 9.8, 5850, "Kharif 2025", "Spike Development"),
        (11, "Linseed", 6.0, 5600, "Rabi 2025", "Pod Maturity"),
        (12, "Sesame (Black)", 4.8, 7850, "Kharif 2025", "Capsule Maturity"),
    ]

    for crop_id, crop_name, base_yield, base_price, season, stage in oilseed_specs:
        # Generate 12 records per crop:
        # - 4 records in Dharwad hub (< 40 km radius)
        # - 3 records in Haveri hub (~70-90 km radius)
        # - 3 records in Belagavi / Gadag hubs (~65-85 km radius)
        # - 2 records in Tumkur hub (~300 km)
        clusters = [
            ("Dharwad", 15.4589, 75.0078, 4),
            ("Haveri", 14.7960, 75.4000, 3),
            ("Belagavi", 15.8497, 74.5085, 2),
            ("Gadag", 15.4290, 75.6260, 1),
            ("Tumkur", 13.3409, 77.1025, 2),
        ]

        for dist_name, base_lat, base_lon, count in clusters:
            for i in range(count):
                # Tight offsets within ~10-30 km of district center
                offset_lat = base_lat + ((i * 0.08) - 0.04)
                offset_lon = base_lon + (((i % 2) * 0.09) - 0.045)

                acres = round(1.5 + (i * 0.5), 1)
                y_val = round(base_yield + ((i * 0.2) - 0.3), 1)
                p_val = round(base_price + ((i * 40) - 60), 1)
                cost = round(acres * 3800 + 2500, 1)
                net_val = round(y_val * p_val - cost, 1)

                is_contactable = (i == 0 and dist_name == "Dharwad")

                PEER_PROOFS.append(dict(
                    id=pid,
                    crop_id=crop_id,
                    season=season,
                    cultivated_area_acres=acres,
                    yield_quintals_per_acre=y_val,
                    selling_price_per_quintal=p_val,
                    cultivation_cost_per_acre=cost,
                    net_realization_per_acre=net_val,
                    district=dist_name,
                    state="Karnataka",
                    latitude=round(offset_lat, 4),
                    longitude=round(offset_lon, 4),
                    crop_stage=stage,
                    expected_harvest="Oct 2025" if "Kharif" in season else "Feb 2026",
                    soil_type="Red Laterite" if i % 2 == 0 else "Black Cotton",
                    water_source="Borewell" if i % 2 == 0 else "Canal Irrigation",
                    source_type=_PEER_SOURCE,
                    verification_status=_PEER_VERIF,
                    peer_visibility="CONTACTABLE" if is_contactable else "VERIFIED" if i == 1 else "ANONYMOUS",
                    contactable=is_contactable,
                    farmer_display_name=f"CropShift Demo Farmer #{pid} ({dist_name})" if not is_contactable else f"Demonstration Farmer #{pid} ({dist_name})",
                    contact_phone="98765000" + str(pid).zfill(2) if is_contactable else None,
                    contact_email=f"demo_farmer_{pid}@cropshift.com" if is_contactable else None,
                ))
                pid += 1

_gen_peers()

MARKETS = [
    dict(id=1, name="Tumkur APMC",          district="Tumkur",     state="Karnataka", location=_point(77.1000, 13.3400), market_type="APMC"),
    dict(id=2, name="Haveri APMC",          district="Haveri",     state="Karnataka", location=_point(75.3980, 14.7950), market_type="APMC"),
    dict(id=3, name="Dharwad APMC",         district="Dharwad",    state="Karnataka", location=_point(75.0100, 15.4600), market_type="APMC"),
    dict(id=4, name="Bengaluru APMC Yeshwanthpur", district="Bengaluru", state="Karnataka", location=_point(77.5946, 12.9716), market_type="APMC"),
    dict(id=5, name="Shivamogga APMC",      district="Shivamogga", state="Karnataka", location=_point(75.5680, 13.9299), market_type="APMC"),
    dict(id=6, name="Bhadravathi Sub-Yard", district="Shivamogga", state="Karnataka", location=_point(75.7140, 13.8430), market_type="SUB_YARD"),
    dict(id=7, name="Sagar APMC",           district="Shivamogga", state="Karnataka", location=_point(75.0310, 14.1670), market_type="APMC"),
    dict(id=8, name="Raichur APMC",         district="Raichur",    state="Karnataka", location=_point(77.3560, 16.2070), market_type="APMC"),
    dict(id=9, name="Manvi Sub-Yard",       district="Raichur",    state="Karnataka", location=_point(77.0500, 15.9890), market_type="SUB_YARD"),
    dict(id=10, name="Sindhanur APMC",      district="Raichur",    state="Karnataka", location=_point(76.7600, 15.7760), market_type="APMC"),
    dict(id=11, name="Hubballi APMC",       district="Dharwad",    state="Karnataka", location=_point(75.1240, 15.3647), market_type="APMC"),
    dict(id=12, name="Gadag APMC",          district="Gadag",      state="Karnataka", location=_point(75.6260, 15.4290), market_type="APMC"),
    dict(id=13, name="Davanagere APMC",     district="Davanagere", state="Karnataka", location=_point(75.9220, 14.4640), market_type="APMC"),
    dict(id=14, name="Belagavi APMC",       district="Belagavi",   state="Karnataka", location=_point(74.5080, 15.8490), market_type="APMC"),
    dict(id=15, name="Ballari APMC",        district="Ballari",    state="Karnataka", location=_point(76.9210, 15.1390), market_type="APMC"),
    dict(id=16, name="Chitradurga APMC",    district="Chitradurga",state="Karnataka", location=_point(76.3980, 14.2250), market_type="APMC"),
    dict(id=17, name="Kalaburagi APMC",     district="Kalaburagi", state="Karnataka", location=_point(76.8343, 17.3297), market_type="APMC"),
    dict(id=18, name="Vijayapura APMC",     district="Vijayapura", state="Karnataka", location=_point(75.7100, 16.8302), market_type="APMC"),
    dict(id=19, name="Bagalkot APMC",       district="Bagalkot",   state="Karnataka", location=_point(75.6960, 16.1850), market_type="APMC"),
    dict(id=20, name="Mysuru APMC Bandipalya", district="Mysuru", state="Karnataka", location=_point(76.6394, 12.2958), market_type="APMC"),
    dict(id=21, name="Mandya APMC",          district="Mandya",     state="Karnataka", location=_point(76.8951, 12.5218), market_type="APMC"),
    dict(id=22, name="Hassan APMC",          district="Hassan",     state="Karnataka", location=_point(76.1004, 13.0033), market_type="APMC"),
    dict(id=23, name="Chikmagalur APMC",    district="Chikmagalur",state="Karnataka", location=_point(75.7720, 13.3161), market_type="APMC"),
    dict(id=24, name="Kolar APMC",           district="Kolar",      state="Karnataka", location=_point(78.1290, 13.1360), market_type="APMC"),
    dict(id=25, name="Chintamani APMC",      district="Chikkaballapur", state="Karnataka", location=_point(78.0600, 13.4000), market_type="APMC"),
    dict(id=26, name="Ranebennur APMC",      district="Haveri",     state="Karnataka", location=_point(75.6210, 14.6230), market_type="APMC"),
    dict(id=27, name="Laxmeshwar Sub-Yard",  district="Gadag",      state="Karnataka", location=_point(75.4740, 15.1260), market_type="SUB_YARD"),
    dict(id=28, name="Gokak APMC",           district="Belagavi",   state="Karnataka", location=_point(74.8330, 16.1670), market_type="APMC"),
]

_PRICE_DATE = datetime.date(2024, 10, 1)

MARKET_PRICES = [
    (1,  1, 1, 2550.0, "STABLE"),
    (2,  2, 1, 2600.0, "STABLE"),
    (3,  1, 2, 5400.0, "RISING"),
    (4,  2, 2, 5500.0, "RISING"),
    (5,  3, 3, 4900.0, "STABLE"),
    (6,  4, 3, 5100.0, "STABLE"),
    (7,  2, 4, 4750.0, "STABLE"),
    (8,  3, 4, 4800.0, "STABLE"),
    (9,  3, 5, 5150.0, "RISING"),
    (10, 4, 5, 5200.0, "RISING"),
    (11, 1, 6, 6900.0, "STABLE"),
    (12, 4, 6, 7000.0, "STABLE"),
    (13, 2, 7, 1550.0, "FALLING"),
    (14, 4, 7, 1600.0, "STABLE"),
    (15, 5, 2, 6350.0, "RISING"),
    (16, 6, 2, 6200.0, "STABLE"),
    (17, 7, 3, 5100.0, "RISING"),
    (18, 8, 2, 6420.0, "RISING"),
    (19, 9, 2, 6180.0, "STABLE"),
    (20, 10, 3, 5050.0, "RISING"),
    (21, 11, 3, 7100.0, "STABLE"),
    (22, 12, 6, 9800.0, "RISING"),
    (23, 13, 4, 4950.0, "FALLING"),
    (24, 14, 4, 5020.0, "RISING"),
    (25, 15, 2, 6100.0, "STABLE"),
    (26, 16, 2, 5950.0, "STABLE"),
    (27, 17, 5, 5300.0, "RISING"),
    (28, 18, 8, 5750.0, "RISING"),
    (29, 19, 2, 6050.0, "STABLE"),
    (30, 20, 2, 6250.0, "RISING"),
    (31, 21, 3, 5050.0, "STABLE"),
    (32, 22, 2, 6120.0, "STABLE"),
    (33, 26, 2, 6080.0, "RISING"),
    (34, 27, 6, 9600.0, "STABLE"),
    (35, 28, 2, 6150.0, "RISING"),
]

RISK_SCENARIOS = [
    dict(id=1, code=RiskCode.BASELINE, name="Baseline", description="Normal conditions. No stress applied.", price_multiplier=1.0, yield_multiplier=1.0, water_penalty=0.0),
    dict(id=2, code=RiskCode.PRICE_DOWN, name="Price Drop 20%", description="Market price falls 20% below reference. Yield unchanged.", price_multiplier=0.8, yield_multiplier=1.0, water_penalty=0.0),
    dict(id=3, code=RiskCode.YIELD_DOWN, name="Yield Drop 30%", description="Crop yield drops 30% due to pest, disease, or weather. Price unchanged.", price_multiplier=1.0, yield_multiplier=0.7, water_penalty=0.0),
    dict(id=4, code=RiskCode.WATER_RISK, name="Water Scarcity", description="Irrigation unavailable. Score penalty applied for high-water crops.", price_multiplier=1.0, yield_multiplier=1.0, water_penalty=25.0),
]

SUBSIDIES = [
    dict(
        id=1,
        scheme_id="PM-KISAN",
        scheme_name="PM Kisan Samman Nidhi",
        description="Direct income support of INR 6,000/year to eligible farmer families.",
        applicable_crop_types=["CEREAL", "OILSEED", "PULSE", "OTHER"],
        applicable_states=["Karnataka", "All States"],
        eligibility_factors={"land_ownership": True, "small_marginal": True},
        required_information=["Aadhaar", "Land records", "Bank account"],
        support_information="Toll-free: 155261",
        verification_required=True,
        data_source="pmkisan.gov.in (STATIC)",
    ),
    dict(
        id=2,
        scheme_id="NMOOP",
        scheme_name="National Mission on Oilseeds and Oil Palm",
        description="Subsidy and technical support to boost oilseed production.",
        applicable_crop_types=["OILSEED"],
        applicable_states=["Karnataka", "All States"],
        eligibility_factors={"crop_type": "OILSEED"},
        required_information=["Land records", "Crop sown certificate"],
        support_information="Contact district agriculture office",
        verification_required=True,
        data_source="nfsm.gov.in (STATIC)",
    ),
]


def seed_db(session: Session) -> None:
    logger.info("Seeding users...")
    for u in USERS:
        _get_or_create(session, User, u["id"], **{k: v for k, v in u.items() if k != "id"})

    logger.info("Seeding crops...")
    for c in CROPS:
        _get_or_create(session, Crop, c["id"], **{k: v for k, v in c.items() if k != "id"})

    logger.info("Seeding farmers...")
    for f in FARMERS:
        _get_or_create(session, Farmer, f["id"], **{k: v for k, v in f.items() if k != "id"})

    logger.info("Seeding farms...")
    for f in FARMS:
        _get_or_create(session, Farm, f["id"], **{k: v for k, v in f.items() if k != "id"})

    logger.info("Seeding crop economics...")
    for row in CROP_ECONOMICS:
        (eid, crop_id, region, yield_per_acre, yield_unit,
         prod_cost, price_per_unit, status, source) = row
        _get_or_create(
            session, CropEconomics, eid,
            crop_id=crop_id,
            region=region,
            expected_yield_per_acre=yield_per_acre,
            yield_unit=yield_unit,
            production_cost_per_acre=prod_cost,
            expected_price_per_unit=price_per_unit,
            data_status=status,
            data_source=source,
        )

    logger.info("Seeding crop suitabilities...")
    for row in CROP_SUITABILITIES:
        (sid, crop_id, region, soil, water_level, base_score, notes) = row
        _get_or_create(
            session, CropSuitability, sid,
            crop_id=crop_id,
            region=region,
            soil_type=soil,
            water_requirement_level=water_level,
            suitability_base_score=base_score,
            notes=notes,
        )

    logger.info("Seeding markets...")
    for m in MARKETS:
        _get_or_create(session, Market, m["id"], **{k: v for k, v in m.items() if k != "id"})

    logger.info("Seeding market prices...")
    for row in MARKET_PRICES:
        (pid, market_id, crop_id, price, trend) = row
        _get_or_create(
            session, MarketPrice, pid,
            market_id=market_id,
            crop_id=crop_id,
            price=price,
            price_unit="quintal",
            price_date=_PRICE_DATE,
            trend=trend,
            data_status="DEMO",
            data_source="Agmarknet snapshot basis (DEMO)",
        )

    logger.info("Seeding risk scenarios...")
    for r in RISK_SCENARIOS:
        _get_or_create(session, RiskScenario, r["id"], **{k: v for k, v in r.items() if k != "id"})

    logger.info("Seeding subsidies...")
    for s in SUBSIDIES:
        _get_or_create(session, Subsidy, s["id"], **{k: v for k, v in s.items() if k != "id"})

    logger.info("Seeding peer proofs (using merge for full dataset synchronization)...")
    # Clear existing synthetic peer proof records so updated multi-crop dataset applies cleanly
    session.query(PeerProof).delete()
    session.commit()

    for p in PEER_PROOFS:
        peer_obj = PeerProof(**p)
        session.add(peer_obj)

    session.commit()
    
    # Sync sequences to max id to prevent duplicate key errors during registration/creation
    from sqlalchemy import text
    tables = ['user', 'crop', 'farmer', 'farm', 'market', 'subsidy', 'peer_proof']
    for t in tables:
        try:
            session.execute(text(f"SELECT setval(pg_get_serial_sequence('\"{t}\"', 'id'), (SELECT COALESCE(MAX(id), 1) FROM \"{t}\"));"))
        except Exception as seq_err:
            logger.warning(f"Sequence sync note for {t}: {seq_err}")
    session.commit()

    logger.info("Seed complete.")


def run_seed() -> None:
    """Entry point: initialise DB then seed."""
    from .session import SessionLocal
    init_db()
    with SessionLocal() as session:
        seed_db(session)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_seed()
    print("Seed data inserted successfully.")
