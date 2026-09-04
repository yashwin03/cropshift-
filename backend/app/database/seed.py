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
    (1,  1, "Tumkur",  20.0, "Quintal / acre", 18000.0, 2550.0, "STATIC",    "Agmarknet / ICAR snapshot"),
    (2,  1, "Haveri",  22.0, "Quintal / acre", 18500.0, 2600.0, "STATIC",    "Agmarknet / ICAR snapshot"),
    (3,  2, "Tumkur",  10.0, "Quintal / acre", 12000.0, 5400.0, "ESTIMATED", "Agmarknet / ICAR snapshot"),
    (4,  2, "Dharwad", 10.5, "Quintal / acre", 12200.0, 5500.0, "ESTIMATED", "Agmarknet / ICAR snapshot"),
    (5,  3, "Dharwad", 8.0,  "Quintal / acre", 10000.0, 4900.0, "ESTIMATED", "Agmarknet / ICAR snapshot"),
    (6,  3, "Haveri",  8.5,  "Quintal / acre", 10200.0, 5000.0, "ESTIMATED", "Agmarknet / ICAR snapshot"),
    (7,  4, "Haveri",  8.0,  "Quintal / acre", 11000.0, 4750.0, "ESTIMATED", "Agmarknet / ICAR snapshot"),
    (8,  4, "Dharwad", 8.5,  "Quintal / acre", 11200.0, 4800.0, "ESTIMATED", "Agmarknet / ICAR snapshot"),
    (9,  5, "Dharwad", 6.0,  "Quintal / acre", 8000.0,  5150.0, "ESTIMATED", "Agmarknet / ICAR snapshot"),
    (10, 5, "Tumkur",  6.5,  "Quintal / acre", 8200.0,  5200.0, "ESTIMATED", "Agmarknet / ICAR snapshot"),
    (11, 6, "Tumkur",  4.0,  "Quintal / acre", 7000.0,  6900.0, "ESTIMATED", "Agmarknet / ICAR snapshot"),
    (12, 6, "Dharwad", 4.5,  "Quintal / acre", 7200.0,  7000.0, "ESTIMATED", "Agmarknet / ICAR snapshot"),
    (13, 7, "Haveri",  25.0, "Quintal / acre", 15000.0, 1550.0, "STATIC",    "Agmarknet / ICAR snapshot"),
    (14, 7, "Tumkur",  24.0, "Quintal / acre", 14800.0, 1500.0, "STATIC",    "Agmarknet / ICAR snapshot"),
    (15, 8, "Tumkur",  7.0,  "Quintal / acre", 9000.0,  5700.0, "ESTIMATED", "Agmarknet / ICAR snapshot"),
    (16, 8, "Dharwad", 7.5,  "Quintal / acre", 9200.0,  5800.0, "ESTIMATED", "Agmarknet / ICAR snapshot"),
    (17, 9, "Tumkur",  4.5,  "Quintal / acre", 6500.0,  6300.0, "ESTIMATED", "Agmarknet / ICAR snapshot"),
    (18, 9, "Haveri",  5.0,  "Quintal / acre", 6700.0,  6400.0, "ESTIMATED", "Agmarknet / ICAR snapshot"),
    (19, 10, "Dharwad", 12.0, "Quintal / acre", 11000.0, 5900.0, "ESTIMATED", "Agmarknet / ICAR snapshot"),
    (20, 10, "Tumkur",  12.5, "Quintal / acre", 11200.0, 6000.0, "ESTIMATED", "Agmarknet / ICAR snapshot"),
    (21, 11, "Haveri",  5.5,  "Quintal / acre", 7500.0,  5500.0, "ESTIMATED", "Agmarknet / ICAR snapshot"),
    (22, 11, "Dharwad", 6.0,  "Quintal / acre", 7700.0,  5600.0, "ESTIMATED", "Agmarknet / ICAR snapshot"),
    (23, 12, "Tumkur",  4.2,  "Quintal / acre", 7200.0,  7600.0, "ESTIMATED", "Agmarknet / ICAR snapshot"),
    (24, 12, "Dharwad", 4.6,  "Quintal / acre", 7400.0,  7700.0, "ESTIMATED", "Agmarknet / ICAR snapshot"),
]

CROP_SUITABILITIES = [
    (1,  1, "Tumkur",  "red laterite",  "HIGH",   75.0, "Suitable with irrigation"),
    (2,  1, "Haveri",  "black cotton",  "HIGH",   80.0, "Good canal irrigation"),
    (3,  2, "Tumkur",  "red laterite",  "MEDIUM", 87.0, "Excellent fit"),
    (4,  2, "Dharwad", "red laterite",  "MEDIUM", 85.0, "Good oilseed region"),
    (5,  3, "Dharwad", "black cotton",  "MEDIUM", 82.0, "Rabi season suitable"),
    (6,  3, "Haveri",  "black cotton",  "MEDIUM", 79.0, "Good yield potential"),
    (7,  4, "Haveri",  "black cotton",  "MEDIUM", 80.0, "Kharif soybean belt"),
    (8,  4, "Dharwad", "red laterite",  "MEDIUM", 76.0, "Moderate suitability"),
    (9,  5, "Dharwad", "red laterite",  "LOW",    78.0, "Rabi mustard ok"),
    (10, 5, "Tumkur",  "red laterite",  "LOW",    72.0, "Dryland suitable"),
    (11, 6, "Tumkur",  "red laterite",  "LOW",    74.0, "Drought tolerant"),
    (12, 6, "Dharwad", "red laterite",  "LOW",    71.0, "Suitable"),
    (13, 7, "Haveri",  "black cotton",  "MEDIUM", 83.0, "Good maize area"),
    (14, 7, "Tumkur",  "red laterite",  "MEDIUM", 77.0, "Moderate yield"),
    (15, 8, "Tumkur",  "red laterite",  "LOW",    76.0, "Rabi suitable"),
    (16, 8, "Dharwad", "red laterite",  "LOW",    74.0, "Suitable"),
    (17, 9, "Tumkur",  "red laterite",  "LOW",    72.0, "Kharif suitable"),
    (18, 9, "Haveri",  "black cotton",  "LOW",    75.0, "Suitable"),
    (19, 10, "Dharwad", "red laterite", "MEDIUM", 80.0, "Deep soil suitable"),
    (20, 10, "Tumkur",  "red laterite", "MEDIUM", 78.0, "Good yield"),
    (21, 11, "Haveri",  "black cotton", "LOW",    73.0, "Rabi linseed"),
    (22, 11, "Dharwad", "red laterite", "LOW",    71.0, "Moderate fit"),
    (23, 12, "Tumkur",  "red laterite", "LOW",    77.0, "High value crop"),
    (24, 12, "Dharwad", "red laterite", "LOW",    75.0, "Suitable"),
]

# ---------------------------------------------------------------------------
# Peer Proofs (DEMO DATASET — minimum 6-8 farmers per oilseed crop with distinct, non-overlapping coordinates)
# ---------------------------------------------------------------------------

_PEER_SOURCE = "CropShift demo dataset"
_PEER_VERIF  = "Demo data — not real farmer verification"

# Base coordinates per district for geographic distribution
DISTRICT_LOCS = {
    "Dharwad": (15.4589, 75.0078),
    "Haveri": (14.7960, 75.4000),
    "Tumkur": (13.3409, 77.1025),
    "Belagavi": (15.8497, 74.5085),
    "Shivamogga": (13.9299, 75.5680),
    "Hassan": (13.0033, 76.1004),
    "Mysuru": (12.2958, 76.6394),
    "Davanagere": (14.4644, 75.9220),
    "Chitradurga": (14.2251, 76.3980),
    "Mandya": (12.5218, 76.8951),
}

PEER_PROOFS = []

def _gen_peers():
    pid = 1
    # Oilseed crops: 2 (Groundnut), 3 (Sunflower), 4 (Soybean), 5 (Mustard), 6 (Sesame), 8 (Safflower), 9 (Niger), 10 (Castor), 11 (Linseed), 12 (Sesame Black)
    oilseed_specs = [
        (2, "Groundnut", 9.5, 5900, "Kharif 2025", "Pod Formation"),
        (3, "Sunflower", 8.2, 5250, "Rabi 2025", "Head Development"),
        (4, "Soybean", 8.4, 4900, "Kharif 2025", "Pod Filling"),
        (5, "Mustard", 6.2, 5400, "Rabi 2025", "Pod Development"),
        (6, "Sesame", 4.3, 7250, "Kharif 2025", "Capsule Formation"),
        (8, "Safflower", 7.1, 5650, "Rabi 2025", "Maturity"),
        (9, "Niger", 4.8, 6350, "Kharif 2025", "Flowering"),
        (10, "Castor", 12.5, 5950, "Kharif 2025", "Spike Development"),
        (11, "Linseed", 5.8, 5550, "Rabi 2025", "Pod Maturity"),
        (12, "Sesame (Black)", 4.5, 7650, "Kharif 2025", "Capsule Maturity"),
    ]

    districts = list(DISTRICT_LOCS.keys())

    for crop_id, crop_name, base_yield, base_price, season, stage in oilseed_specs:
        # Create 7 distinct demo farmers per crop distributed across Karnataka
        for i in range(7):
            dist_name = districts[i % len(districts)]
            base_lat, base_lon = DISTRICT_LOCS[dist_name]
            
            # Offset lat/lon slightly so markers do NOT overlap
            offset_lat = base_lat + ((i * 0.035) - 0.1)
            offset_lon = base_lon + (((i % 3) * 0.04) - 0.06)

            acres = round(1.5 + (i * 0.5), 1)
            y_val = round(base_yield + ((i * 0.2) - 0.4), 1)
            p_val = round(base_price + ((i * 50) - 100), 1)
            cost = round(acres * 4000 + 3000, 1)
            net_val = round(y_val * p_val - cost, 1)

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
                latitude=offset_lat,
                longitude=offset_lon,
                crop_stage=stage,
                expected_harvest="Oct 2025" if "Kharif" in season else "Feb 2026",
                soil_type="Red Laterite" if i % 2 == 0 else "Black Cotton",
                water_source="Borewell" if i % 2 == 0 else "Canal Irrigation",
                source_type=_PEER_SOURCE,
                verification_status=_PEER_VERIF,
                peer_visibility="CONTACTABLE" if i == 0 else "VERIFIED" if i == 1 else "ANONYMOUS",
                contactable=(i == 0),
                farmer_display_name=f"CropShift Demo Farmer #{pid}" if i != 0 else f"Demonstration Farmer #{pid} ({dist_name})",
                contact_phone="98765000" + str(pid).zfill(2) if i == 0 else None,
                contact_email=f"demo_farmer_{pid}@cropshift.com" if i == 0 else None,
            ))
            pid += 1

_gen_peers()

MARKETS = [
    dict(id=1, name="Tumkur APMC",          district="Tumkur",     state="Karnataka", location=_point(77.1000, 13.3400), market_type="APMC"),
    dict(id=2, name="Haveri APMC",          district="Haveri",     state="Karnataka", location=_point(75.3980, 14.7950), market_type="APMC"),
    dict(id=3, name="Dharwad APMC",         district="Dharwad",    state="Karnataka", location=_point(75.0100, 15.4600), market_type="APMC"),
    dict(id=4, name="Bengaluru APMC",       district="Bengaluru",  state="Karnataka", location=_point(77.5946, 12.9716), market_type="APMC"),
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
        session.execute(text(f"SELECT setval('{t}_id_seq', (SELECT COALESCE(MAX(id), 1) FROM \"{t}\"));"))
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
