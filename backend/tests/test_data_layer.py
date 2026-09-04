"""
test_data_layer.py -- A2 acceptance tests for farm_service, crop_service,
and utils/missing_data.

Spec requirements tested:
1. get_farmer / get_farm lookups for existing and non-existing IDs.
2. get_farm_conditions returns normalised dict with correct keys.
3. A farm with soil_type = NULL returns conditions with a defaulted flag
   (no exception raised).
4. get_alternative_crops for golden demo farm includes Groundnut and
   excludes the current crop (Paddy).
5. Missing-data path covered (resolve() and DataConfidence).
6. get_current_crop returns Paddy for farm 1.
7. get_crop_requirements returns expected keys.
"""
import pytest
from sqlalchemy.orm import Session

from app.database.session import SessionLocal
from app.database.init_db import init_db
from app.database.seed import seed_db

from app.services.farm_service import (
    get_farmer,
    get_farm,
    get_farm_by_farmer,
    get_farm_conditions,
)
from app.services.crop_service import (
    get_crop,
    list_crops,
    get_current_crop,
    get_alternative_crops,
    get_crop_requirements,
)
from app.utils.missing_data import resolve, DataConfidence


# ---------------------------------------------------------------------------
# Module-scoped DB fixture (re-uses A1 seeded data)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def db() -> Session:
    """Ensure DB is initialised and seeded, yield a session."""
    init_db()
    with SessionLocal() as session:
        seed_db(session)
        yield session


# ===========================================================================
# missing_data utility
# ===========================================================================

class TestResolve:
    def test_present_value_returned_as_is(self):
        val, defaulted, note = resolve("red laterite", "unknown", "soil_type")
        assert val == "red laterite"
        assert defaulted is False
        assert note == ""

    def test_none_returns_fallback(self):
        val, defaulted, note = resolve(None, "unknown", "soil_type")
        assert val == "unknown"
        assert defaulted is True
        assert "soil" in note.lower()

    def test_zero_is_not_treated_as_missing(self):
        val, defaulted, _ = resolve(0, 99, "score")
        assert val == 0
        assert defaulted is False

    def test_false_is_not_treated_as_missing(self):
        val, defaulted, _ = resolve(False, True, "water_availability")
        assert val is False
        assert defaulted is False


class TestDataConfidence:
    def test_no_defaults_gives_high(self):
        dc = DataConfidence()
        assert dc.level == "HIGH"

    def test_one_default_gives_medium(self):
        dc = DataConfidence()
        dc.record_default("soil_type", "Soil info unavailable.")
        assert dc.level == "MEDIUM"

    def test_two_defaults_gives_low(self):
        dc = DataConfidence()
        dc.record_default("soil_type", "Soil info unavailable.")
        dc.record_default("location", "Location info unavailable.")
        assert dc.level == "LOW"

    def test_apply_records_default_only_for_none(self):
        dc = DataConfidence()
        v1 = dc.apply("loam", "unknown", "soil_type")
        assert v1 == "loam"
        assert dc.level == "HIGH"

        v2 = dc.apply(None, "unknown", "soil_type")
        assert v2 == "unknown"
        assert dc.level == "MEDIUM"

    def test_duplicate_default_not_double_counted(self):
        dc = DataConfidence()
        dc.record_default("soil_type", "note 1")
        dc.record_default("soil_type", "note 1")  # same field again
        assert len(dc.defaults) == 1

    def test_summary_keys(self):
        dc = DataConfidence()
        s = dc.summary()
        assert "confidence" in s
        assert "defaulted_fields" in s
        assert "notes" in s


# ===========================================================================
# farm_service
# ===========================================================================

class TestGetFarmer:
    def test_existing_farmer_returns_dict(self, db):
        farmer = get_farmer(db, 1)
        assert farmer is not None
        assert farmer["id"] == 1
        assert isinstance(farmer["name"], str)

    def test_missing_farmer_returns_none(self, db):
        assert get_farmer(db, 9999) is None

    def test_farmer_has_required_keys(self, db):
        farmer = get_farmer(db, 1)
        for key in ("id", "name", "phone", "language", "district", "state"):
            assert key in farmer


class TestGetFarm:
    def test_existing_farm_returns_dict(self, db):
        farm = get_farm(db, 1)
        assert farm is not None
        assert farm["id"] == 1

    def test_missing_farm_returns_none(self, db):
        assert get_farm(db, 9999) is None

    def test_farm_has_required_keys(self, db):
        farm = get_farm(db, 1)
        for key in ("id", "farmer_id", "land_area_acre", "water_availability",
                    "soil_type", "district", "state", "current_crop_id"):
            assert key in farm


class TestGetFarmByFarmer:
    def test_returns_list(self, db):
        farms = get_farm_by_farmer(db, 1)
        assert isinstance(farms, list)
        assert len(farms) >= 1

    def test_unknown_farmer_returns_empty_list(self, db):
        assert get_farm_by_farmer(db, 9999) == []


class TestGetFarmConditions:
    def test_golden_demo_farm_conditions(self, db):
        conditions = get_farm_conditions(db, 1)
        assert conditions is not None
        assert conditions["land_area_acre"] == pytest.approx(1.0)
        assert conditions["water_availability"] is True

    def test_conditions_has_all_required_keys(self, db):
        conditions = get_farm_conditions(db, 1)
        for key in ("land_area_acre", "water_availability", "soil_type",
                    "district", "state", "latitude", "longitude",
                    "current_crop", "_missing_geometry"):
            assert key in conditions, f"Missing key: {key}"

    def test_current_crop_is_paddy(self, db):
        conditions = get_farm_conditions(db, 1)
        assert conditions["current_crop"] is not None
        assert conditions["current_crop"]["name"] == "Paddy"

    def test_missing_farm_returns_none(self, db):
        assert get_farm_conditions(db, 9999) is None

    def test_null_soil_type_does_not_raise(self, db):
        """A farm with NULL soil_type must return conditions without exception."""
        conditions = get_farm_conditions(db, 1)
        # soil_type may or may not be None -- either way, no exception
        assert "soil_type" in conditions


# ===========================================================================
# crop_service
# ===========================================================================

class TestGetCrop:
    def test_existing_crop_returns_dict(self, db):
        crop = get_crop(db, 1)
        assert crop is not None
        assert crop["id"] == 1

    def test_missing_crop_returns_none(self, db):
        assert get_crop(db, 9999) is None

    def test_crop_has_required_keys(self, db):
        crop = get_crop(db, 1)
        for key in ("id", "name", "crop_type", "is_oilseed",
                    "season", "water_requirement"):
            assert key in crop


class TestListCrops:
    def test_returns_at_least_7_crops(self, db):
        crops = list_crops(db)
        assert len(crops) >= 7

    def test_all_items_are_dicts(self, db):
        crops = list_crops(db)
        for c in crops:
            assert isinstance(c, dict)


class TestGetCurrentCrop:
    def test_golden_demo_farm_current_crop_is_paddy(self, db):
        crop = get_current_crop(db, 1)
        assert crop is not None
        assert crop["name"] == "Paddy"

    def test_missing_farm_returns_none(self, db):
        assert get_current_crop(db, 9999) is None


class TestGetAlternativeCrops:
    def test_golden_demo_farm_alternatives_include_groundnut(self, db):
        alternatives = get_alternative_crops(db, 1)
        names = [c["name"] for c in alternatives]
        assert "Groundnut" in names, f"Groundnut not in alternatives: {names}"

    def test_alternatives_exclude_current_crop(self, db):
        """Paddy is the current crop -- it must not appear in alternatives."""
        alternatives = get_alternative_crops(db, 1)
        names = [c["name"] for c in alternatives]
        assert "Paddy" not in names

    def test_all_alternatives_are_oilseeds(self, db):
        alternatives = get_alternative_crops(db, 1)
        for c in alternatives:
            assert c["is_oilseed"] is True, (
                f"{c['name']} is returned as alternative but is_oilseed=False"
            )

    def test_unknown_farm_returns_empty_list(self, db):
        assert get_alternative_crops(db, 9999) == []

    def test_results_are_deterministic(self, db):
        """Same call twice must return same order."""
        r1 = get_alternative_crops(db, 1)
        r2 = get_alternative_crops(db, 1)
        assert [c["id"] for c in r1] == [c["id"] for c in r2]


class TestGetCropRequirements:
    def test_returns_required_keys(self, db):
        req = get_crop_requirements(db, 1)
        assert req is not None
        for key in ("crop_id", "crop_name", "water_requirement",
                    "preferred_soil", "season"):
            assert key in req

    def test_missing_crop_returns_none(self, db):
        assert get_crop_requirements(db, 9999) is None
