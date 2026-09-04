# Graph Report - CropShift Sqlx  (2026-08-30)

## Corpus Check
- Large corpus: 1329 files · ~5,887,572 words. Semantic extraction will be expensive (many Claude tokens). Consider running on a subfolder.

## Summary
- 2303 nodes · 3833 edges · 207 communities (183 shown, 24 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 66 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- ProjJSON CRS Schema
- Frontend Mock Data & Fixtures
- Decision Engine Core
- API Error Handling
- Database Init & Seeding
- Crop Data Services
- Auth & API Routing
- Geospatial Services
- ProjJSON Direction Schema
- Suitability Engine
- Frontend App Layout
- Farm Info Wizard
- UI Common Components
- Risk Simulation API
- Map Visualization
- Proj Triangulation Schema
- Proj Coordinate Systems
- Risk & Safety Scoring
- Market Intelligence Engine
- Score Display Components
- Frontend TS App Config
- Proj CRS Definitions
- Seed Data Tests
- IVR & Recommendations API
- Proj Derived CRS Schema
- Common UI Primitives
- GDAL Info Schema
- OGR Info Schema
- Frontend TS Node Config
- Proj Triangulation Data
- PostGIS Component 30
- PostGIS Component 31
- PostGIS Component 32
- PostGIS Component 33
- PostGIS Component 34
- PostGIS Component 35
- PostGIS Component 36
- PostGIS Component 37
- PostGIS Component 38
- PostGIS Component 39
- PostGIS Component 40
- PostGIS Component 41
- PostGIS Component 42
- Frontend Module 43
- Frontend Module 44
- Backend Module 45
- PostGIS Component 46
- PostGIS Component 47
- PostGIS Component 48
- PostGIS Component 49
- PostGIS Component 50
- PostGIS Component 51
- PostGIS Component 52
- PostGIS Component 53
- PostGIS Component 54
- PostGIS Component 55
- PostGIS Component 56
- PostGIS Component 57
- PostGIS Component 58
- PostGIS Component 59
- PostGIS Component 60
- PostGIS Component 61
- PostGIS Component 62
- PostGIS Component 63
- PostGIS Component 64
- PostGIS Component 65
- PostGIS Component 66
- PostGIS Component 67
- PostGIS Component 68
- PostGIS Component 69
- Backend Module 70
- PostGIS Component 71
- PostGIS Component 72
- PostGIS Component 73
- PostGIS Component 74
- Backend Module 75
- PostGIS Component 76
- PostGIS Component 77
- PostGIS Component 78
- PostGIS Component 79
- PostGIS Component 80
- PostGIS Component 81
- PostGIS Component 82
- PostGIS Component 83
- PostGIS Component 84
- PostGIS Component 85
- PostGIS Component 86
- PostGIS Component 87
- PostGIS Component 88
- Frontend Module 89
- PostGIS Component 90
- PostGIS Component 91
- PostGIS Component 92
- PostGIS Component 93
- PostGIS Component 94
- PostGIS Component 95
- PostGIS Component 96
- PostGIS Component 97
- PostGIS Component 98
- PostGIS Component 99
- PostGIS Component 100
- PostGIS Component 101
- PostGIS Component 102
- PostGIS Component 103
- PostGIS Component 104
- PostGIS Component 105
- PostGIS Component 106
- PostGIS Component 107
- PostGIS Component 108
- PostGIS Component 109
- PostGIS Component 110
- PostGIS Component 111
- PostGIS Component 112
- PostGIS Component 113
- PostGIS Component 114
- PostGIS Component 115
- PostGIS Component 116
- PostGIS Component 117
- PostGIS Component 118
- Frontend Module 119
- Backend Module 120
- PostGIS Component 121
- PostGIS Component 122
- PostGIS Component 123
- PostGIS Component 124
- PostGIS Component 125
- PostGIS Component 126
- PostGIS Component 127
- PostGIS Component 128
- PostGIS Component 129
- PostGIS Component 130
- PostGIS Component 131
- PostGIS Component 132
- PostGIS Component 133
- PostGIS Component 134
- PostGIS Component 135
- Backend Module 136
- Frontend Module 137
- Frontend Module 138
- Backend Module 139
- Backend Module 140
- Frontend Module 141
- Backend Module 142
- PostGIS Component 143
- PostGIS Component 144
- PostGIS Component 145
- PostGIS Component 146
- PostGIS Component 147
- PostGIS Component 148
- PostGIS Component 149
- PostGIS Component 150
- PostGIS Component 151
- PostGIS Component 152
- Backend Module 153
- Backend Module 154
- PostGIS Component 155
- PostGIS Component 156
- PostGIS Component 157
- PostGIS Component 158
- PostGIS Component 159
- PostGIS Component 160
- PostGIS Component 161
- PostGIS Component 162
- PostGIS Component 163
- PostGIS Component 164
- PostGIS Component 165
- PostGIS Component 166
- PostGIS Component 167
- Frontend Module 168
- Frontend Module 169
- PostGIS Component 170
- PostGIS Component 171
- Frontend Module 172
- Frontend Module 173
- Frontend Module 174
- Frontend Module 175
- Frontend Module 176
- Frontend Module 177
- Frontend Module 178
- Backend Module 189
- Backend Module 190
- Backend Module 191
- Backend Module 192
- Backend Module 193
- PostGIS Component 195
- Frontend Module 197
- Frontend Module 198
- Frontend Module 199

## God Nodes (most connected - your core abstractions)
1. `react` - 50 edges
2. `enum` - 41 edges
3. `generate_recommendation()` - 27 edges
4. `Crop` - 25 edges
5. `Farm` - 25 edges
6. `definitions` - 25 edges
7. `seed_db()` - 22 edges
8. `enum` - 22 edges
9. `ids` - 21 edges
10. `init_db()` - 20 edges

## Surprising Connections (you probably didn't know these)
- `Backend Environment Config` --semantically_similar_to--> `Frontend Environment Variables`  [INFERRED] [semantically similar]
  backend/docs_for_integration/ENVIRONMENT.md → frontend/docs_for_integration/ENVIRONMENT.md
- `test_distance_haversine()` --calls--> `haversine_distance()`  [INFERRED]
  backend/tests/test_market_service.py → backend/app/utils/geo.py
- `get_market_info()` --uses--> `Crop`  [INFERRED]
  backend/app/api/v1/markets.py → backend/app/models/crop.py
- `get_market_info()` --uses--> `CropEconomics`  [INFERRED]
  backend/app/api/v1/markets.py → backend/app/models/crop_economics.py
- `create_recommendation()` --uses--> `Crop`  [INFERRED]
  backend/app/api/v1/recommendations.py → backend/app/models/crop.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **CropShift API Endpoint Suite** — backend_docs_for_integration_api_spec_recommendations_endpoint, backend_docs_for_integration_api_spec_profitability_endpoint, backend_docs_for_integration_api_spec_markets_endpoint, backend_docs_for_integration_api_spec_subsidies_endpoint, backend_docs_for_integration_api_spec_geospatial_endpoint, backend_docs_for_integration_api_spec_risk_simulation_endpoint, backend_docs_for_integration_api_spec_ivr_endpoint [EXTRACTED 1.00]
- **Safety Score Computation Pipeline** — backend_docs_for_integration_golden_demo_safety_score, backend_docs_for_integration_golden_demo_weighted_components, backend_docs_for_integration_golden_demo_decision_thresholds, backend_docs_for_integration_judge_qa_deterministic_engine [EXTRACTED 1.00]
- **Frontend-Backend Integration Layer** — frontend_docs_for_integration_api_mapping_service_methods, frontend_docs_for_integration_environment_mock_toggle, backend_docs_for_integration_api_spec_cropshift_api [INFERRED 0.85]

## Communities (207 total, 24 thin omitted)

### Community 0 - "ProjJSON CRS Schema"
Cohesion: 0.07
Nodes (88): type, properties, type, type, items, properties, type, $ref (+80 more)

### Community 1 - "Frontend Mock Data & Fixtures"
Cohesion: 0.09
Nodes (48): SubsidyCardProps, CAUTION_RECOMMENDATION, DONT_SWITCH_RECOMMENDATION, GOLDEN_DEMO_RECOMMENDATION, GOLDEN_DEMO_GEOSPATIAL, delay(), USE_MOCKS, GOLDEN_DEMO_IVR (+40 more)

### Community 2 - "Decision Engine Core"
Cohesion: 0.07
Nodes (44): get_profitability(), get, Session, generate_recommendation(), Session, Recommendation engine for CropShift. Orchestrates suitability, profitability,…, Orchestrate the full pipeline to evaluate alternative crops and select the best…, Crop (+36 more)

### Community 3 - "API Error Handling"
Cohesion: 0.05
Nodes (33): _error_envelope(), _json(), Any, app/api/errors.py — A14 Global Exception Handlers and Error Envelope. Produces…, Return the canonical error envelope., Register all A14 global exception handlers onto the FastAPI app., register_exception_handlers(), get_health() (+25 more)

### Community 4 - "Database Init & Seeding"
Cohesion: 0.06
Nodes (45): init_db(), init_db.py -- Creates the PostGIS extension and all A1 tables. Usage: python -m…, Enable PostGIS and create all tables., _get_or_create(), _point(), Session, seed.py -- Deterministic, idempotent seed data for CropShift A1. Seed strategy:…, Insert all seed records. Idempotent -- skips existing rows by primary key. (+37 more)

### Community 5 - "Crop Data Services"
Cohesion: 0.06
Nodes (30): get_alternative_crops(), get_crop(), get_crop_economics(), get_crop_requirements(), list_crops(), Session, Return economics row for a crop in the specified region. Falls back to the…, Return a plain dict for the requested crop, or None if not found. (+22 more)

### Community 6 - "Auth & API Routing"
Cohesion: 0.07
Nodes (36): Config, create_access_token(), get_current_user(), get_password_hash(), login_for_access_token(), BaseModel, get, post (+28 more)

### Community 7 - "Geospatial Services"
Cohesion: 0.09
Nodes (38): get_geospatial(), get, Session, distance_km(), get_farm_location(), get_geographic_context(), get_nearby_markets(), Any (+30 more)

### Community 8 - "ProjJSON Direction Schema"
Cohesion: 0.05
Nodes (43): enum, type, direction, aft, awayFrom, clockwise, columnNegative, columnPositive (+35 more)

### Community 9 - "Suitability Engine"
Cohesion: 0.08
Nodes (25): clamp(), Factor, Any, Deterministic weighted rule-based scoring engine for crop suitability., Calculate suitability score based on regional, water, soil, and climate…, score_suitability(), SuitabilityResult, DataConfidence (+17 more)

### Community 10 - "Frontend App Layout"
Cohesion: 0.16
Nodes (21): App(), EmptyState(), EmptyStateProps, Props, State, ErrorState(), ErrorStateProps, Spinner() (+13 more)

### Community 11 - "Farm Info Wizard"
Cohesion: 0.09
Nodes (25): FarmDetails, CROP_OPTIONS, FarmInfoPage(), FormErrors, FormValues, INITIAL_FORM, SOIL_OPTIONS, validateStep() (+17 more)

### Community 12 - "UI Common Components"
Cohesion: 0.10
Nodes (26): Badge(), BadgeProps, StatusBadge(), StatusBadgeProps, MarketCard(), MarketCardProps, TrendIndicator(), TrendIndicatorProps (+18 more)

### Community 13 - "Risk Simulation API"
Cohesion: 0.12
Nodes (19): evaluate_scenario(), post, Session, simulate_risk(), calculate_risk_score(), Calculate a 0-100 risk score based on price, yield, water, and market access…, Farm model -- A1 spec entity., Farmer (+11 more)

### Community 14 - "Map Visualization"
Cohesion: 0.11
Nodes (21): farmIcon, FarmMap(), FarmMapProps, marketIcon, ProfitChart(), ProfitChartProps, formatINR(), ProfitComparison() (+13 more)

### Community 15 - "Proj Triangulation Schema"
Cohesion: 0.07
Nodes (28): description, type, description, $ref, enum, type, description, $ref (+20 more)

### Community 16 - "Proj Coordinate Systems"
Cohesion: 0.07
Nodes (27): additionalProperties, allOf, required, type, coordinate_system, enum, AbridgedTransformation, Axis (+19 more)

### Community 17 - "Risk & Safety Scoring"
Cohesion: 0.16
Nodes (22): Risk factor definition and risk calculation engine for CropShift., RiskFactor, calculate_headline_safety_score(), calculate_safety_score(), clamp(), Safety score calculation engine. Deterministic inverse scoring of aggregated…, Calculate safety score based on risk factors. Deterministic weighted scoring., Calculate the headline safety score based on: - Suitability (Weight: 0.35) -… (+14 more)

### Community 18 - "Market Intelligence Engine"
Cohesion: 0.13
Nodes (21): Market Intelligence scoring engine. Deterministic weighted scoring., Compute a normalized 0-100 market score based on price level, trend, distance,…, score_market_engine(), MarketPrice, Base, MarketPrice model -- A1 spec entity., get_best_market_for_crop(), Session (+13 more)

### Community 19 - "Score Display Components"
Cohesion: 0.14
Nodes (14): DECISION_MAP, DecisionBadge(), DecisionBadgeProps, SafetyScoreGauge(), SafetyScoreGaugeProps, ScoreBreakdown(), ScoreBreakdownProps, ScoreItemConfig (+6 more)

### Community 20 - "Frontend TS App Config"
Cohesion: 0.08
Nodes (24): compilerOptions, allowArbitraryExtensions, allowImportingTsExtensions, erasableSyntaxOnly, jsx, lib, module, moduleDetection (+16 more)

### Community 21 - "Proj CRS Definitions"
Cohesion: 0.08
Nodes (24): oneOf, oneOf, definitions, crs, datum, derived_engineering_crs, derived_parametric_crs, derived_projected_crs (+16 more)

### Community 22 - "Seed Data Tests"
Cohesion: 0.18
Nodes (23): _count(), db_session(), fixture, Session, test_seed.py — A1: integration tests against the live cropshift DB. Requires…, Create tables, seed once, then yield a session. Tear down after module., test_all_tables_exist(), test_golden_demo_farm_current_crop_is_paddy() (+15 more)

### Community 23 - "IVR & Recommendations API"
Cohesion: 0.11
Nodes (20): get_ivr_recommendation(), post, Session, create_recommendation(), post, Session, User, generate_ivr_response() (+12 more)

### Community 24 - "Proj Derived CRS Schema"
Cohesion: 0.14
Nodes (21): derived_geodetic_crs, derived_temporal_crs, derived_vertical_crs, required, additionalProperties, allOf, required, type (+13 more)

### Community 25 - "Common UI Primitives"
Cohesion: 0.18
Nodes (14): Button(), ButtonProps, Card(), CardProps, LoadingCard(), LoadingCardProps, AuthContext, AuthContextType (+6 more)

### Community 26 - "GDAL Info Schema"
Cohesion: 0.10
Nodes (20): $ref, $ref, properties, type, type, type, items, type (+12 more)

### Community 27 - "OGR Info Schema"
Cohesion: 0.10
Nodes (20): type, type, type, type, properties, type, alias, comment (+12 more)

### Community 28 - "Frontend TS Node Config"
Cohesion: 0.10
Nodes (19): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, lib, module, moduleDetection, noEmit, noFallthroughCasesInSwitch (+11 more)

### Community 29 - "Proj Triangulation Data"
Cohesion: 0.11
Nodes (19): type, triangles, triangles_columns, vertices, vertices_columns, description, items, minItems (+11 more)

### Community 30 - "PostGIS Component 30"
Cohesion: 0.11
Nodes (17): additionalProperties, type, format, pattern, type, definitions, crs, datetime (+9 more)

### Community 31 - "PostGIS Component 31"
Cohesion: 0.11
Nodes (18): description, type, additionalProperties, description, properties, required, type, description (+10 more)

### Community 32 - "PostGIS Component 32"
Cohesion: 0.12
Nodes (17): type, additionalProperties, properties, required, type, type, coordinateSystem, dataAxisToSRSAxisMapping (+9 more)

### Community 33 - "PostGIS Component 33"
Cohesion: 0.12
Nodes (17): stac, $ref, oneOf, title, items, oneOf, title, type (+9 more)

### Community 34 - "PostGIS Component 34"
Cohesion: 0.12
Nodes (17): properties, $ref, $ref, $comment, type, any, $comment, any (+9 more)

### Community 35 - "PostGIS Component 35"
Cohesion: 0.12
Nodes (17): items, type, description, $ref, $ref, properties, components, definition_crs (+9 more)

### Community 36 - "PostGIS Component 36"
Cohesion: 0.12
Nodes (17): additionalProperties, properties, required, type, bbox, type, type, east_longitude (+9 more)

### Community 37 - "PostGIS Component 37"
Cohesion: 0.12
Nodes (16): properties, $ref, type, type, type, type, type, type (+8 more)

### Community 38 - "PostGIS Component 38"
Cohesion: 0.12
Nodes (15): anyOf, anyOf, anyOf, anyOf, definitions, attribute, attributes, datatype (+7 more)

### Community 39 - "PostGIS Component 39"
Cohesion: 0.12
Nodes (16): additionalProperties, properties, type, $ref, array, $ref, datatype, nodata_value (+8 more)

### Community 40 - "PostGIS Component 40"
Cohesion: 0.12
Nodes (16): $ref, $ref, group, $ref, type, additionalProperties, properties, type (+8 more)

### Community 41 - "PostGIS Component 41"
Cohesion: 0.12
Nodes (15): definitions, domains, fieldType, keyValueDict, metadataDomain, description, additionalProperties, patternProperties (+7 more)

### Community 42 - "PostGIS Component 42"
Cohesion: 0.12
Nodes (16): description, format, type, properties, bbox, href, rel, title (+8 more)

### Community 43 - "Frontend Module 43"
Cohesion: 0.13
Nodes (15): autoprefixer, devDependencies, autoprefixer, tailwindcss, @testing-library/react, @types/react, typescript, vite (+7 more)

### Community 44 - "Frontend Module 44"
Cohesion: 0.13
Nodes (15): axios, dependencies, axios, leaflet, react, react-dom, react-leaflet, react-router-dom (+7 more)

### Community 45 - "Backend Module 45"
Cohesion: 0.22
Nodes (13): calculate_profitability(), clamp(), Factor, ProfitabilityResult, Deterministic profitability scoring engine., Calculate crop yields, revenues, production costs, profits, and a normalized…, test_profitability_negative_profit(), test_profitability_zero_land_area() (+5 more)

### Community 46 - "PostGIS Component 46"
Cohesion: 0.13
Nodes (14): definitions, keyValueDict, metadata, metadataDomain, description, patternProperties, type, $comment (+6 more)

### Community 47 - "PostGIS Component 47"
Cohesion: 0.14
Nodes (15): items, type, additionalProperties, properties, type, compound_datatype, additionalProperties, properties (+7 more)

### Community 48 - "PostGIS Component 48"
Cohesion: 0.13
Nodes (15): type, additionalProperties, properties, required, type, type, coordinateSystem, dataAxisToSRSAxisMapping (+7 more)

### Community 49 - "PostGIS Component 49"
Cohesion: 0.13
Nodes (15): type, null, items, type, items, type, left_mapping_table_fields, left_table_fields (+7 more)

### Community 50 - "PostGIS Component 50"
Cohesion: 0.13
Nodes (15): description, type, properties, description, format, type, description, type (+7 more)

### Community 51 - "PostGIS Component 51"
Cohesion: 0.14
Nodes (15): additionalProperties, allOf, required, type, compound_crs, dynamic_vertical_reference_frame, required, additionalProperties (+7 more)

### Community 52 - "PostGIS Component 52"
Cohesion: 0.21
Nodes (14): items, type, items, type, items, arrayOfTwoIntegers, arrayOfTwoNumbers, items (+6 more)

### Community 53 - "PostGIS Component 53"
Cohesion: 0.14
Nodes (14): Float32, Int16, enum, Byte, CFloat32, CFloat64, CInt16, CInt32 (+6 more)

### Community 54 - "PostGIS Component 54"
Cohesion: 0.14
Nodes (14): enum, type, enum, type, horizontal_offset_unit, horizontal_uncertainty_unit, vertical_offset_unit, vertical_uncertainty_unit (+6 more)

### Community 55 - "PostGIS Component 55"
Cohesion: 0.15
Nodes (14): additionalProperties, allOf, required, type, additionalProperties, allOf, required, type (+6 more)

### Community 56 - "PostGIS Component 56"
Cohesion: 0.15
Nodes (13): type, type, type, type, backward_path_label, forward_path_label, left_table_name, mapping_table_name (+5 more)

### Community 57 - "PostGIS Component 57"
Cohesion: 0.15
Nodes (13): type, oneOf, properties, type, type, coordinatePrecisionFormatSpecificOptions, coordinateSystem, mCoordinateResolution (+5 more)

### Community 58 - "PostGIS Component 58"
Cohesion: 0.15
Nodes (13): additionalProperties, required, type, dataset, layer, additionalProperties, required, type (+5 more)

### Community 59 - "PostGIS Component 59"
Cohesion: 0.15
Nodes (13): properties, type, $ref, type, type, description, domains, driverLongName (+5 more)

### Community 60 - "PostGIS Component 60"
Cohesion: 0.15
Nodes (13): enum, Integer, String, Binary, Date, DateTime, Integer64, Integer64List (+5 more)

### Community 61 - "PostGIS Component 61"
Cohesion: 0.15
Nodes (13): description, type, description, enum, type, description, type, filename (+5 more)

### Community 62 - "PostGIS Component 62"
Cohesion: 0.17
Nodes (12): items, type, type, properties, type, type, type, buckets (+4 more)

### Community 63 - "PostGIS Component 63"
Cohesion: 0.18
Nodes (12): field, geometryField, additionalProperties, required, type, additionalProperties, required, type (+4 more)

### Community 64 - "PostGIS Component 64"
Cohesion: 0.17
Nodes (12): relationship, additionalProperties, required, type, backward_path_label, cardinality, forward_path_label, left_table_fields (+4 more)

### Community 65 - "PostGIS Component 65"
Cohesion: 0.17
Nodes (12): properties, description, type, description, $ref, description, extent, time_function (+4 more)

### Community 66 - "PostGIS Component 66"
Cohesion: 0.17
Nodes (12): $ref, $ref, first, last, time_extent, additionalProperties, description, properties (+4 more)

### Community 67 - "PostGIS Component 67"
Cohesion: 0.17
Nodes (12): additionalProperties, allOf, required, type, additionalProperties, allOf, required, type (+4 more)

### Community 68 - "PostGIS Component 68"
Cohesion: 0.17
Nodes (12): vertical, subtype, enum, type, Cartesian, ellipsoidal, ordinal, parametric (+4 more)

### Community 69 - "PostGIS Component 69"
Cohesion: 0.17
Nodes (12): items, maxItems, minItems, type, properties, description, type, properties (+4 more)

### Community 70 - "Backend Module 70"
Cohesion: 0.17
Nodes (3): test_models.py — A1: verifies all 10 SQLAlchemy model tables are registered and…, All 10 A1 entities must be present in Base.metadata., test_all_tables_registered()

### Community 71 - "PostGIS Component 71"
Cohesion: 0.18
Nodes (11): $ref, properties, $ref, $ref, center, lowerLeft, lowerRight, upperLeft (+3 more)

### Community 72 - "PostGIS Component 72"
Cohesion: 0.18
Nodes (11): type, enum, pattern, $ref, type, Aggregation, Association, coded (+3 more)

### Community 73 - "PostGIS Component 73"
Cohesion: 0.18
Nodes (11): pattern, type, format, pattern, type, definitions, crs, datetime (+3 more)

### Community 74 - "PostGIS Component 74"
Cohesion: 0.18
Nodes (11): description, format, type, properties, href, rel, title, description (+3 more)

### Community 75 - "Backend Module 75"
Cohesion: 0.31
Nodes (8): generate_explanations(), Explainability layer for CropShift. Converts decision factors into farmer-…, Generate dynamic farmer-friendly explanations (reasons and risks) based on…, test_explainability.py -- A9 acceptance tests for Explainability engine., test_explainability_caution(), test_explainability_confidence_warnings(), test_explainability_dont_switch(), test_explainability_switch()

### Community 76 - "PostGIS Component 76"
Cohesion: 0.20
Nodes (10): dimension, additionalProperties, properties, type, type, type, type, direction (+2 more)

### Community 77 - "PostGIS Component 77"
Cohesion: 0.20
Nodes (10): type, type, items, type, properties, $ref, featureCount, fidColumnName (+2 more)

### Community 78 - "PostGIS Component 78"
Cohesion: 0.20
Nodes (10): items, type, items, type, $ref, items, type, features (+2 more)

### Community 79 - "PostGIS Component 79"
Cohesion: 0.20
Nodes (10): additionalProperties, definition, required, type, component, description, displacement_type, extent (+2 more)

### Community 80 - "PostGIS Component 80"
Cohesion: 0.20
Nodes (10): required, after_last, before_first, before_scale_factor, final_scale_factor, initial_scale_factor, model, reference_epoch (+2 more)

### Community 81 - "PostGIS Component 81"
Cohesion: 0.22
Nodes (9): additionalProperties, required, type, cornerCoordinates, center, lowerLeft, lowerRight, upperLeft (+1 more)

### Community 82 - "PostGIS Component 82"
Cohesion: 0.22
Nodes (9): integer, null, string, title, type, title, type, proj:epsg (+1 more)

### Community 83 - "PostGIS Component 83"
Cohesion: 0.22
Nodes (9): items, type, srs, data_axis_to_srs_axis_mapping, wkt, additionalProperties, properties, type (+1 more)

### Community 84 - "PostGIS Component 84"
Cohesion: 0.28
Nodes (9): items, items, type, items, type, maxItems, minItems, extent (+1 more)

### Community 85 - "PostGIS Component 85"
Cohesion: 0.22
Nodes (9): properties, items, type, items, type, type, groups, layerNames (+1 more)

### Community 86 - "PostGIS Component 86"
Cohesion: 0.22
Nodes (9): enum, mergePolicy, splitPolicy, enum, default value, duplicate, geometry ratio, geometry weighted (+1 more)

### Community 87 - "PostGIS Component 87"
Cohesion: 0.22
Nodes (9): description, type, properties, initial_scale_factor, reference_epoch, step_epoch, description, $ref (+1 more)

### Community 88 - "PostGIS Component 88"
Cohesion: 0.22
Nodes (9): enum, horizontal, vertical, transformed_components, description, items, maxItems, minItems (+1 more)

### Community 89 - "Frontend Module 89"
Cohesion: 0.22
Nodes (8): plugins, rules, react/only-export-components, react/rules-of-hooks, $schema, oxc, typescript, warn

### Community 90 - "PostGIS Component 90"
Cohesion: 0.25
Nodes (8): additionalProperties, required, type, band, type, band, band, block

### Community 91 - "PostGIS Component 91"
Cohesion: 0.25
Nodes (8): fieldSubType, enum, Float32, Int16, None, Boolean, JSON, UUID

### Community 92 - "PostGIS Component 92"
Cohesion: 0.32
Nodes (8): description, enum, type, enum, after_last, constant, linear, zero

### Community 93 - "PostGIS Component 93"
Cohesion: 0.25
Nodes (8): time_function_piecewise, additionalProperties, type, parameters, additionalProperties, description, properties, type

### Community 94 - "PostGIS Component 94"
Cohesion: 0.43
Nodes (8): required, parameters, type, required, required, required, required, required

### Community 95 - "PostGIS Component 95"
Cohesion: 0.25
Nodes (8): additionalProperties, required, type, href, description, items, type, links

### Community 96 - "PostGIS Component 96"
Cohesion: 0.25
Nodes (8): bbox, enum, exponential, GeoTIFF, piecewise, reverse_step, step, velocity

### Community 97 - "PostGIS Component 97"
Cohesion: 0.25
Nodes (8): components, file_type, format_version, source_crs, target_crs, required, definition_crs, time_extent

### Community 98 - "PostGIS Component 98"
Cohesion: 0.25
Nodes (8): file_type, format_version, required, transformed_components, triangles, triangles_columns, vertices, vertices_columns

### Community 99 - "PostGIS Component 99"
Cohesion: 0.29
Nodes (7): properties, items, type, overviews, size, $comment, $ref

### Community 100 - "PostGIS Component 100"
Cohesion: 0.29
Nodes (7): items, type, items, type, type, block_size, dimension_size

### Community 101 - "PostGIS Component 101"
Cohesion: 0.29
Nodes (7): enum, type, cardinality, ManyToMany, ManyToOne, OneToMany, OneToOne

### Community 102 - "PostGIS Component 102"
Cohesion: 0.29
Nodes (7): domain, additionalProperties, required, type, fieldType, mergePolicy, splitPolicy

### Community 103 - "PostGIS Component 103"
Cohesion: 0.29
Nodes (7): extent, additionalProperties, properties, type, type, description, type

### Community 104 - "PostGIS Component 104"
Cohesion: 0.29
Nodes (7): spatial_model, additionalProperties, description, required, type, filename, interpolation_method

### Community 105 - "PostGIS Component 105"
Cohesion: 0.29
Nodes (7): additionalProperties, allOf, required, type, datum_ensemble, accuracy, members

### Community 106 - "PostGIS Component 106"
Cohesion: 0.29
Nodes (7): additionalProperties, required, href, description, items, type, links

### Community 107 - "PostGIS Component 107"
Cohesion: 0.33
Nodes (6): Geospatial Endpoint, PostgreSQL PostGIS Setup, PostGIS Extension Bundle, GDAL Data Library, MobilityDB Extension, pgRouting Extension

### Community 108 - "PostGIS Component 108"
Cohesion: 0.33
Nodes (6): additionalProperties, required, type, dataset, bands, size

### Community 109 - "PostGIS Component 109"
Cohesion: 0.33
Nodes (6): $comment, maxItems, minItems, title, type, proj:shape

### Community 110 - "PostGIS Component 110"
Cohesion: 0.33
Nodes (6): group, additionalProperties, required, type, groups, layerNames

### Community 111 - "PostGIS Component 111"
Cohesion: 0.33
Nodes (6): additionalProperties, description, required, type, name, authority

### Community 112 - "PostGIS Component 112"
Cohesion: 0.33
Nodes (6): time_function_constant, additionalProperties, description, properties, required, type

### Community 113 - "PostGIS Component 113"
Cohesion: 0.53
Nodes (6): enum, horizontal, none, vertical, enum, 3d

### Community 114 - "PostGIS Component 114"
Cohesion: 0.33
Nodes (6): description, enum, type, horizontal_offset_method, addition, geocentric

### Community 115 - "PostGIS Component 115"
Cohesion: 0.33
Nodes (5): $comment, description, $id, oneOf, $schema

### Community 116 - "PostGIS Component 116"
Cohesion: 0.33
Nodes (6): additionalProperties, allOf, required, axis, abbreviation, direction

### Community 117 - "PostGIS Component 117"
Cohesion: 0.33
Nodes (6): engineering_crs, additionalProperties, allOf, required, type, datum

### Community 118 - "PostGIS Component 118"
Cohesion: 0.33
Nodes (6): geodetic_crs, additionalProperties, allOf, description, required, type

### Community 119 - "Frontend Module 119"
Cohesion: 0.33
Nodes (6): scripts, build, dev, lint, test, test:watch

### Community 120 - "Backend Module 120"
Cohesion: 0.40
Nodes (5): IVR Recommendation Endpoint, Recommendations Endpoint, Database Seed Data, Golden Demo Safety Score Derivation, IVR Engine Parity

### Community 121 - "PostGIS Component 121"
Cohesion: 0.50
Nodes (3): pgtopo_export script, PGDATABASE, usage()

### Community 122 - "PostGIS Component 122"
Cohesion: 0.40
Nodes (5): $ref, additionalProperties, properties, type, arrays

### Community 123 - "PostGIS Component 123"
Cohesion: 0.40
Nodes (5): type, structural_info, additionalProperties, properties, type

### Community 124 - "PostGIS Component 124"
Cohesion: 0.40
Nodes (5): type, enum, type, array, group

### Community 125 - "PostGIS Component 125"
Cohesion: 0.40
Nodes (4): additionalProperties, description, $schema, type

### Community 126 - "PostGIS Component 126"
Cohesion: 0.40
Nodes (5): items, maxItems, minItems, type, bbox

### Community 127 - "PostGIS Component 127"
Cohesion: 0.40
Nodes (5): time_function_exponential, additionalProperties, description, properties, type

### Community 128 - "PostGIS Component 128"
Cohesion: 0.40
Nodes (5): time_function_reverse_step, additionalProperties, description, properties, type

### Community 129 - "PostGIS Component 129"
Cohesion: 0.40
Nodes (5): time_function_step, additionalProperties, description, properties, type

### Community 130 - "PostGIS Component 130"
Cohesion: 0.40
Nodes (5): time_function_velocity, additionalProperties, description, properties, type

### Community 131 - "PostGIS Component 131"
Cohesion: 0.40
Nodes (5): description, enum, type, file_type, deformation_model_master_file

### Community 132 - "PostGIS Component 132"
Cohesion: 0.40
Nodes (5): description, items, minItems, type, model

### Community 133 - "PostGIS Component 133"
Cohesion: 0.40
Nodes (5): engineering_datum, additionalProperties, allOf, required, type

### Community 134 - "PostGIS Component 134"
Cohesion: 0.40
Nodes (5): description, enum, type, file_type, triangulation_file

### Community 135 - "PostGIS Component 135"
Cohesion: 0.40
Nodes (5): enum, type, 1.0, format_version, 1.1

### Community 136 - "Backend Module 136"
Cohesion: 0.40
Nodes (4): Test API v1 health endpoint returns ok., Test root health endpoint returns ok., test_health_check(), test_v1_health_check()

### Community 137 - "Frontend Module 137"
Cohesion: 0.40
Nodes (4): name, private, type, version

### Community 139 - "Backend Module 139"
Cohesion: 0.50
Nodes (3): Settings, BaseSettings, field_validator

### Community 140 - "Backend Module 140"
Cohesion: 0.50
Nodes (3): Base, WaterSource, WaterSourceType

### Community 141 - "Frontend Module 141"
Cohesion: 0.50
Nodes (4): CropShift API Specification, Frontend API Service Methods, Mock Data Toggle, Frontend Routing System

### Community 142 - "Backend Module 142"
Cohesion: 0.50
Nodes (4): Decision Thresholds, Weighted Safety Score Components, Deterministic Decision Engine Design, Modular Monolith Architecture

### Community 144 - "PostGIS Component 144"
Cohesion: 0.50
Nodes (4): items, type, $ref, bands

### Community 145 - "PostGIS Component 145"
Cohesion: 0.50
Nodes (4): dimensions, items, type, anyOf

### Community 146 - "PostGIS Component 146"
Cohesion: 0.50
Nodes (4): metadata, $comment, patternProperties, type

### Community 147 - "PostGIS Component 147"
Cohesion: 0.50
Nodes (4): relationships, additionalProperties, patternProperties, type

### Community 148 - "PostGIS Component 148"
Cohesion: 0.50
Nodes (4): oneOf, supportedSRSList, items, type

### Community 149 - "PostGIS Component 149"
Cohesion: 0.50
Nodes (4): enum, type, 1.0, format_version

### Community 150 - "PostGIS Component 150"
Cohesion: 0.50
Nodes (4): enum, type, horizontal_uncertainty_type, circular 95% confidence limit

### Community 151 - "PostGIS Component 151"
Cohesion: 0.50
Nodes (4): vertical_uncertainty_type, enum, type, 95% confidence limit

### Community 152 - "PostGIS Component 152"
Cohesion: 0.50
Nodes (4): dynamic_geodetic_reference_frame, additionalProperties, allOf, type

### Community 155 - "PostGIS Component 155"
Cohesion: 0.67
Nodes (3): $comment, $ref, codedValues

### Community 156 - "PostGIS Component 156"
Cohesion: 0.67
Nodes (3): $comment, type, maxValueIncluded

### Community 157 - "PostGIS Component 157"
Cohesion: 0.67
Nodes (3): description, type, before_first

### Community 158 - "PostGIS Component 158"
Cohesion: 0.67
Nodes (3): description, type, before_scale_factor

### Community 159 - "PostGIS Component 159"
Cohesion: 0.67
Nodes (3): description, type, displacement_type

### Community 160 - "PostGIS Component 160"
Cohesion: 0.67
Nodes (3): description, $ref, end_epoch

### Community 161 - "PostGIS Component 161"
Cohesion: 0.67
Nodes (3): description, type, final_scale_factor

### Community 162 - "PostGIS Component 162"
Cohesion: 0.67
Nodes (3): description, type, horizontal_uncertainty

### Community 163 - "PostGIS Component 163"
Cohesion: 0.67
Nodes (3): description, type, license

### Community 164 - "PostGIS Component 164"
Cohesion: 0.67
Nodes (3): publication_date, description, $ref

### Community 165 - "PostGIS Component 165"
Cohesion: 0.67
Nodes (3): relaxation_constant, description, type

### Community 166 - "PostGIS Component 166"
Cohesion: 0.67
Nodes (3): uncertainty_type, description, type

### Community 167 - "PostGIS Component 167"
Cohesion: 0.67
Nodes (3): version, description, type

## Knowledge Gaps
- **918 isolated node(s):** `Config`, `WaterSourceType`, `$schema`, `description`, `oneOf` (+913 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **24 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `properties` connect `PostGIS Component 35` to `PostGIS Component 65`, `PostGIS Component 66`, `PostGIS Component 131`, `PostGIS Component 163`, `PostGIS Component 164`, `PostGIS Component 167`, `PostGIS Component 111`, `PostGIS Component 114`, `PostGIS Component 50`, `PostGIS Component 149`, `PostGIS Component 54`, `PostGIS Component 150`, `PostGIS Component 87`, `PostGIS Component 151`, `PostGIS Component 125`, `PostGIS Component 95`?**
  _High betweenness centrality (0.017) - this node is a cross-community bridge._
- **Why does `properties` connect `PostGIS Component 87` to `PostGIS Component 160`, `PostGIS Component 161`, `PostGIS Component 132`, `PostGIS Component 165`, `PostGIS Component 93`, `PostGIS Component 126`, `PostGIS Component 92`, `PostGIS Component 157`, `PostGIS Component 158`?**
  _High betweenness centrality (0.008) - this node is a cross-community bridge._
- **Why does `definitions` connect `Proj CRS Definitions` to `PostGIS Component 67`, `PostGIS Component 36`, `PostGIS Component 133`, `PostGIS Component 105`, `Proj Coordinate Systems`, `PostGIS Component 115`, `PostGIS Component 116`, `PostGIS Component 51`, `PostGIS Component 117`, `PostGIS Component 55`, `Proj Derived CRS Schema`, `PostGIS Component 118`, `PostGIS Component 152`?**
  _High betweenness centrality (0.008) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `generate_recommendation()` (e.g. with `CropEconomics` and `CropSuitability`) actually correct?**
  _`generate_recommendation()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `Crop` (e.g. with `get_market_info()` and `get_profitability()`) actually correct?**
  _`Crop` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `Farm` (e.g. with `create_recommendation()` and `simulate_risk()`) actually correct?**
  _`Farm` has 13 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Config`, `WaterSourceType`, `$schema` to the rest of the system?**
  _918 weakly-connected nodes found - possible documentation gaps or missing edges._