# MarineShield — Person 4 Frontend/WebGIS Handoff

**Document Generation Date:** 2026-08-21  
**Author / Workstream Origin:** Prepared by Member 2 / Member 4 (Person 1)  
**Target Recipient:** Person 4 (Member 6 Frontend / WebGIS Lead)  
**Inspection Basis:** Generated entirely by direct structural inspection of the current MarineShield repository.  

---

## 1. Current Project Status

- **Person 1 Responsibility:** Person 1 owns **Member 2** (Oil-Intelligence & ML dual-stage verification) and **Member 4** (Release Reconstruction & Source Attribution Engine).
- **Person 1 Completion Status:** Person 1 has completed their assigned work through **Phase 5** (dataset registry, vanilla SAM baseline experiment, parameter-efficient SAR SAM adaptation, deterministic Evidence + Contradiction Engine, Oil Intelligence Service, and Source Investigation Engine).
- **Shared Project Status:** The shared repository is currently preparing for **Phase 6 integration**. Other member workstreams (Member 1 SAR Ingestion, Member 3 Vessel Intelligence / AIS, Member 5 Drift & Threat Forecasting, Member 6 FastAPI Backend) have not yet merged their full implementation pipelines into the codebase. Therefore, the shared project as a whole cannot be claimed as Phase 5 complete.
- **Phase 6 Objective:** The objective of Phase 6 is to deliver the first end-to-end incident investigation flow connecting Sentinel-1 SAR acquisition, oil-spill detection, vessel intelligence, deterministic source attribution, PyGNOME forward drift forecasting, sensitive asset threat analysis, FastAPI REST routes, and the interactive WebGIS Command Center UI.
- **Figma Status:** A Figma account exists for the team, but the MarineShield Figma project, design file, component library, and design system **have not yet been created or approved**.
- **Frontend Status:** **No frontend implementation found.** There are currently no frontend source files, React/Vite/Next.js frameworks, WebGIS map components, or `package.json` configuration files in the repository.

---

## 2. What Person 4 Owns

Person 4 owns the frontend and WebGIS command center portion of **Member 6 (Decision Support & Replay)**, comprising:

1. **Application Shell & Layout:** Modern, high-performance WebGIS command center shell, sidebar navigation, dark/light theme tokens, and role-based views.
2. **Incident Management Views:** Incident list dashboard, search/filter controls, and deep-dive incident detail workspaces.
3. **Interactive Map Canvas (WebGIS):** Primary MapLibre GL / Leaflet spatial workspace rendering:
   - SAR satellite footprint bounding boxes and raster overlay tiles;
   - Vectorized spill geometry polygons (`EPSG:4326` GeoJSON);
   - Maritime vessel positions (AIS tracks, correlated markers, and SAR-detected dark vessel targets);
   - Backward-reconstructed release uncertainty polygons and release corridors;
   - Forward PyGNOME drift trajectory cones ($+6\text{h}, +12\text{h}, +24\text{h}, +48\text{h}$);
   - Sensitive environmental and coastal asset GIS layers (mangroves, MPAs, fisheries, ports).
4. **Source Attribution & Evidence Panels:** Transparent, explainable attribution cards presenting candidate hypothesis rankings ($H_1 \dots H_n$, $H_{dark}$, $H_{non-vessel}$, $H_{unknown}$), component score breakdowns, supporting evidence, and non-suppressed contradiction penalties.
5. **Threat & Response Priority Views:** Automated MarineShield Response Priority display ($0-100$ and `LOW`/`MEDIUM`/`HIGH`/`CRITICAL` tiers), asset time-to-impact (ETA) counters, and escalation action workflows.
6. **Incident Dossier & Report Views:** Printable and exportable incident summary dossiers with complete data provenance and mandatory non-guilt legal disclaimers.
7. **System States:** Comprehensive handling of loading spinners, skeleton screens, empty states, error banners, offline caching, and low-bandwidth coastal field mode.
8. **API Integration:** Clean REST client integration connecting frontend components to versioned FastAPI endpoints (`/api/v1/*`).

> [!IMPORTANT]
> **Strict Architectural Boundary:** Person 4 **must not duplicate** ML inference, drift physics, evidence calculation, attribution ranking, or database queries inside React/frontend components. The WebGIS frontend is strictly a visualization and decision-support command interface consuming processed JSON/GeoJSON payloads from FastAPI backend endpoints.

---

## 3. Repository Structure Relevant to Person 4

| Repository-Relative Path | What Was Found There | Exists? | How Person 4 Should Use It |
| :--- | :--- | :---: | :--- |
| `docs/architecture/` | `ARCHITECTURE.md`, `WORKSTREAMS.md` | **YES** | Read first to understand subsystem boundaries, workstream ownership, and data flow. |
| `docs/api/` | `INVESTIGATION_CONTRACTS.md`, `README.md` | **YES** | Read canonical payload schemas for release hypotheses, candidate entities, evidence items, and attribution. |
| `docs/ml/` | `OIL_INTELLIGENCE_CONTRACTS.md`, `README.md` | **YES** | Read canonical ML schemas for spill masks, spill polygons, look-alike verification, severity, and DQI. |
| `docs/database/` | `README.md` | **YES** | Conceptual PostGIS table catalog. Note: No SQL migrations exist yet. |
| `docs/testing/` | `DEFINITION_OF_DONE.md` | **YES** | Quality, evaluation, and test coverage standards for all subsystems. |
| `docs/decisions/` | `DECISION_LOG.md` | **YES** | Authoritative record of architectural and ML methodology decisions. |
| `docs/source/` | Master plan, marine shield theory, feature inventories | **YES** | Product background, maritime operational context, and core feature roadmap. |
| `.agents/rules/` | `agent_core.md`, `api_contracts.md`, `ui_rules.md`, etc. | **YES** | Mandatory engineering and WebGIS UI guidelines (e.g. UTC timestamps, WGS84, non-guilt clauses). |
| `marineshield/oil_intelligence/` | `schemas.py`, `service.py`, `preprocessing.py`, `geometry_extractor.py`, `lookalike_classifier.py`, `severity_classifier.py` | **YES** | Member 2 Python implementation producing `SpillDetectionResponse` payloads. |
| `marineshield/investigation/` | `schemas.py`, `engine.py`, `evidence_engine.py`, `release_reconstructor.py`, `candidate_filter.py`, `scoring_config.py` | **YES** | Member 4 Python implementation producing `InvestigationResult` payloads. |
| `tests/fixtures/investigation/` | 8 canonical synthetic investigation JSON fixtures | **YES** | Reference JSON payloads showing exact real-world output structures across 8 edge-case scenarios. |
| `backend/` or `server/` | None found | **NO** | MISSING — FastApi routes, backend controllers, and server entry points have not yet been created. |
| `frontend/`, `src/`, `web/` | None found | **NO** | MISSING — Frontend codebase has not yet been initialized. |
| `supabase/` or `migrations/` | None found | **NO** | MISSING — Versioned database migration scripts have not yet been added to the repository. |
| `package.json` | None found | **NO** | MISSING — No Node.js / frontend dependencies or scripts currently exist in the repository root. |

---

## 4. Current Architecture Documents

| Document Path | Summary & Status | Frontend Relevance |
| :--- | :--- | :--- |
| [`docs/architecture/ARCHITECTURE.md`](file:///d:/MarineShield/MarineShield/docs/architecture/ARCHITECTURE.md) | **Exists (Canonical)**. Defines 7-layer pipeline architecture, modular Python subsystems, data flow, and separation of concerns. | Primary system architecture reference. Outlines overall subsystem boundaries. |
| [`docs/architecture/WORKSTREAMS.md`](file:///d:/MarineShield/MarineShield/docs/architecture/WORKSTREAMS.md) | **Exists (Canonical)**. Defines 4-person / 6-member team ownership boundaries. | Explains Person 4's ownership of Member 6 (WebGIS Command Center UI). |
| [`docs/testing/DEFINITION_OF_DONE.md`](file:///d:/MarineShield/MarineShield/docs/testing/DEFINITION_OF_DONE.md) | **Exists (Canonical)**. Outlines quantitative evaluation metrics, unit testing standards, and zero-defect criteria. | Governs DoD requirements for UI accessibility, responsiveness, and zero-error test runs. |
| [`docs/source/master-plan.md`](file:///d:/MarineShield/MarineShield/docs/source/master-plan.md) | **Exists (Reference)**. Product vision, Phase 1–8 roadmap, and end-to-end system goals. | Operational context and product feature roadmap. |
| [`docs/source/feature-inventory.md`](file:///d:/MarineShield/MarineShield/docs/source/feature-inventory.md) | **Exists (Reference)**. Comprehensive functional breakdown of all 6 modules. | UI screen and widget feature checklist. |
| [`.agents/rules/ui_rules.md`](file:///d:/MarineShield/MarineShield/.agents/rules/ui_rules.md) | **Exists (Canonical)**. UI/UX design principles: Map-first WebGIS, explainability panels, accessibility indicators, low-bandwidth mode. | Mandatory rules governing WebGIS design and implementation. |
| [`.agents/rules/agent_core.md`](file:///d:/MarineShield/MarineShield/.agents/rules/agent_core.md) | **Exists (Canonical)**. Responsible-AI constraints: Evidence $\ne$ legal guilt, no fabricated confidence, UNKNOWN is valid, UTC timestamps. | Mandatory non-guilt disclaimers, neutral taxonomy, and UTC standards in UI. |
| `docs/architecture/SECURITY_RLS.md` | **MISSING — REQUIRES CONFIRMATION** | Multi-agency tenant isolation rules and authentication contracts require definition. |

---

## 5. Current API Documentation and Contracts

### 5.1 Existing API Contract Documents & Schemas
- **[`docs/api/INVESTIGATION_CONTRACTS.md`](file:///d:/MarineShield/MarineShield/docs/api/INVESTIGATION_CONTRACTS.md)**: **Canonical Specification (Complete)** for release hypotheses (§1), source hypotheses (§2), evidence items (§3), contradictions (§4), deterministic score formula $E(H)$ (§5), evidence strength tiers (§6), unknown-source states (§7), counterfactual analysis (§9), and provenance (§10).
- **[`docs/ml/OIL_INTELLIGENCE_CONTRACTS.md`](file:///d:/MarineShield/MarineShield/docs/ml/OIL_INTELLIGENCE_CONTRACTS.md)**: **Canonical Specification (Complete)** for spill masks (§1), model confidence (§2), model version (§3), dataset version (§4), operational severity (§5), look-alike verification (§6), spill geometry (§7), metrics metadata (§8), provenance (§9), abstention (§10), and Data Quality Index (§11).
- **[`marineshield/oil_intelligence/schemas.py`](file:///d:/MarineShield/MarineShield/marineshield/oil_intelligence/schemas.py)**: Implementation Python dataclasses for all Member 2 schemas.
- **[`marineshield/investigation/schemas.py`](file:///d:/MarineShield/MarineShield/marineshield/investigation/schemas.py)**: Implementation Python dataclasses for all Member 4 schemas.

### 5.2 Required API Domain Assessment Table

| Domain | Required Response Information | Status | Producer | Frontend Consumer | Confirmed Schema / Endpoint |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Incidents** | Incident ID, status, timestamps (UTC), location, severity, response priority, provenance | **PARTIAL** | Backend Orchestrator | Incident List & Detail Views | Documented in `docs/api/README.md` (`/api/v1/incidents`), but FastAPI route code is **MISSING — REQUIRES CONFIRMATION**. |
| **Spill detections** | Mask URI, GeoJSON polygon, CRS (`EPSG:4326`), confidence, severity, look-alike class, model/dataset version, DQI, abstention | **COMPLETE** (in ML contract & code) | Member 2 (`marineshield.oil_intelligence`) | Map Canvas (Spill Layer) & Detection Card | Documented in `docs/ml/OIL_INTELLIGENCE_CONTRACTS.md` and implemented in `marineshield/oil_intelligence/schemas.py` (`SpillDetectionResponse`). Endpoint route code is **MISSING — REQUIRES CONFIRMATION**. |
| **Vessels** | Vessel ID / MMSI, coordinates, timestamp, track geometry, vessel type, SAR-AIS match score, dark vessel flag | **PARTIAL** | Member 3 (Person 2) | Map Canvas (Vessel Layer) & Vessel Table | Candidate entity schema defined in `INVESTIGATION_CONTRACTS.md` §2. Dedicated Member 3 AIS-SAR endpoint contract is **MISSING — REQUIRES CONFIRMATION**. |
| **Evidence** | Evidence item ID, polarity (`SUPPORTING`/`CONTRADICTORY`), assertion summary, numeric value, observation source, DQI | **COMPLETE** (in Investigation contract & code) | Member 4 (`marineshield.investigation`) | Evidence Inspection Panel | Documented in `docs/api/INVESTIGATION_CONTRACTS.md` §3 and implemented in `marineshield/investigation/schemas.py` (`EvidenceItemContract`). |
| **Source hypotheses** | Candidate ID, label ($H_1 \dots H_n$), category (`VESSEL_IDENTIFIED`, `VESSEL_UNTRACKED_DARK`, `NON_VESSEL_SOURCE`, `UNKNOWN_SOURCE`), score $E(H)$, strength, ranking, counterfactual stability, release polygon, release window, non-guilt clause | **COMPLETE** (in Investigation contract & code) | Member 4 (`marineshield.investigation`) | Source Attribution Ranking Panel | Documented in `docs/api/INVESTIGATION_CONTRACTS.md` §2 & §5 and implemented in `marineshield/investigation/schemas.py` (`SourceHypothesisContract`, `InvestigationResult`). |
| **Forecasts** | Forward trajectory GeoJSON, forecast timesteps ($+6\text{h}, +12\text{h}, +24\text{h}, +48\text{h}$), particle spread (km²), ETA to asset, uncertainty cone | **MISSING — REQUIRES CONFIRMATION** | Member 5 (Person 3) | Map Canvas (Drift Forecast Cone) & Slider | Documented conceptually in `ARCHITECTURE.md` Layer 6, but formal contract and FastAPI route are **MISSING — REQUIRES CONFIRMATION**. |
| **Threats** | Sensitive zone GeoJSON (mangroves, MPAs, ports), asset type, arrival ETA, Response Priority ($0-100$), alert level | **MISSING — REQUIRES CONFIRMATION** | Member 5 / Member 6 Backend | Threat Intersection Panel & Alert Banner | Documented conceptually in `ARCHITECTURE.md` Layer 7, but formal contract and FastAPI route are **MISSING — REQUIRES CONFIRMATION**. |
| **Reports** | Dossier summary, detection parameters, release window, vessel ranking, forecast summary, threat analysis, audit provenance, legal disclaimers | **PARTIAL** | Member 6 Backend | Incident Report & Export Modal | Data contracts exist for detection (§1) and attribution (§2); complete consolidated report contract is **MISSING — REQUIRES CONFIRMATION**. |

---

## 6. Current Database and Schema Documentation

### 6.1 Database Specifications Status
- **Documentation Found:** [`docs/database/README.md`](file:///d:/MarineShield/MarineShield/docs/database/README.md) and [`.agents/rules/database_rules.md`](file:///d:/MarineShield/MarineShield/.agents/rules/database_rules.md).
- **ORM / Migrations Status:** No SQLAlchemy models, SQL migration files, Alembic configurations, or Supabase project files exist in the repository yet.
- **Architectural Access Rule:** The WebGIS frontend **MUST NOT connect directly to PostgreSQL/Supabase** or embed database connection strings. All access must be routed through authenticated FastAPI backend endpoints (`/api/v1/*`).

### 6.2 Entity Confirmation Matrix

| Entity | Target Table | Primary Key | Key Relationships | Spatial Column & CRS | Status | Confirmed via |
| :--- | :--- | :--- | :--- | :--- | :---: | :--- |
| `users` | `users` | `user_id` (UUID) | Roles, agencies | None | **MISSING — REQUIRES CONFIRMATION** | Auth schema not yet implemented. |
| `incidents` | `incidents` | `incident_id` (UUID) | Has many spill detections, hypotheses | `centroid_geom` (`EPSG:4326`) | **PARTIAL** | Documented in `docs/database/README.md` and investigation schemas. |
| `spill_detections` | `spill_polygons` | `spill_geometry_id` (UUID) | Belongs to incident, references mask | `geom` (`GEOMETRY(Polygon, 4326)`) | **COMPLETE (Contract)** | Documented in `docs/ml/OIL_INTELLIGENCE_CONTRACTS.md` §7. |
| `vessels` | `sar_vessels` | `sar_vessel_detection_id` | Linked to AIS track via match | `geom` (`GEOMETRY(Point, 4326)`) | **PARTIAL** | Documented in `INVESTIGATION_CONTRACTS.md` §2. |
| `ais_tracks` | `vessel_tracks` | `track_id` (UUID) | MMSI, belongs to vessel | `geom` (`GEOMETRY(LineString, 4326)`) | **PARTIAL** | Documented in `docs/database/README.md` & `INVESTIGATION_CONTRACTS.md`. |
| `evidence` | `evidence_items` | `evidence_id` (UUID) | Target hypothesis | `observation_coordinates` (`EPSG:4326`) | **COMPLETE (Contract)** | Documented in `docs/api/INVESTIGATION_CONTRACTS.md` §3. |
| `source_hypotheses` | `source_hypotheses` | `source_hypothesis_id` (UUID) | Belongs to incident & release hypothesis | None | **COMPLETE (Contract)** | Documented in `docs/api/INVESTIGATION_CONTRACTS.md` §2. |
| `forecasts` | `drift_forecasts` | `forecast_id` (UUID) | Belongs to incident | `geom` (`GEOMETRY(Polygon, 4326)`) | **MISSING — REQUIRES CONFIRMATION** | Member 5 table not yet formalized. |
| `threats` | `sensitive_zones` | `zone_id` (UUID) | Intersects forecast | `geom` (`GEOMETRY(Polygon, 4326)`) | **MISSING — REQUIRES CONFIRMATION** | GIS reference layers not yet committed. |
| `alerts` | `alert_notifications` | `alert_id` (UUID) | Belongs to incident | None | **MISSING — REQUIRES CONFIRMATION** | Alert dispatch schema not yet formalized. |

---

## 7. Member 2 and Member 4 Outputs Available to the Frontend

### 7.1 Member 2 (Oil Intelligence) Outputs
*Implemented in [`marineshield/oil_intelligence/service.py`](file:///d:/MarineShield/MarineShield/marineshield/oil_intelligence/service.py) and [`schemas.py`](file:///d:/MarineShield/MarineShield/marineshield/oil_intelligence/schemas.py); contract defined in [`docs/ml/OIL_INTELLIGENCE_CONTRACTS.md`](file:///d:/MarineShield/MarineShield/docs/ml/OIL_INTELLIGENCE_CONTRACTS.md).*

| Output Artifact | Schema Object | Key Fields for Frontend Display | Availability Status |
| :--- | :--- | :--- | :--- |
| **Spill Mask** | `SpillMaskContract` | `mask_id`, `binarization_threshold` (0.50), `model_confidence.mean_oil_probability`, `pixel_coverage_fraction`, `data_quality.index` | Available in service/code, but not yet confirmed as a frontend API response. |
| **Spill Geometry** | `SpillGeometryContract` | GeoJSON `Feature` (`Polygon`, `EPSG:4326`), `area_km2`, `perimeter_km`, `centroid_lon`, `centroid_lat`, `orientation_deg`, `elongation_ratio`, `fragmentation_index`, `bounding_box` | Available in service/code, but not yet confirmed as a frontend API response. |
| **Detection Confidence** | `model_confidence` | `mean_oil_probability`, `pixel_coverage_fraction` | Available in service/code, but not yet confirmed as a frontend API response. |
| **Look-Alike Verification** | `LookAlikeVerificationContract` | `predicted_class` (`PETROLEUM_OIL`, `BIOGENIC_SLICK`, `LOW_WIND_AREA`, `SHIP_WAKE`, `NATURAL_FILM`, `UNCERTAIN`), `class_probabilities`, `entropy`, `margin`, `pipeline_decision` (`ACCEPT_AS_OIL`, `REJECT_AS_LOOKALIKE`, `FLAG_FOR_ANALYST_REVIEW`, `ABSTAIN`) | Available in service/code, but not yet confirmed as a frontend API response. |
| **Operational Severity** | `SpillSeverityContract` | `severity_class` (`SHEEN`, `MODERATE`, `THICK_HIGH_SEVERITY`, `UNKNOWN`), `severity_basis` (`mean_backscatter_db`, `suppression_db`, `estimated_area_km2`), `explicit_non_claims` | Available in service/code, but not yet confirmed as a frontend API response. |
| **Data Quality Index** | `DataQualityIndex` | `index` ($0.0-1.0$), `component_scores`, `quality_flags` (`NEAR_SCENE_EDGE`, `THERMAL_NOISE_ANOMALY`, etc.) | Available in service/code, but not yet confirmed as a frontend API response. |
| **Abstention State** | `AbstentionDetails` | `abstention_state` (`ABSTAINED`), `abstention_reason_primary` (`LOW_DATA_QUALITY`), `triggering_values`, `recommendation` (`ANALYST_REVIEW_REQUIRED`) | Available in service/code, but not yet confirmed as a frontend API response. |
| **Provenance Block** | `ProvenanceBlock` | `sar_granule_id`, `model_version_id`, `dataset_version_id`, `inference_device`, `pipeline_parameters` | Available in service/code, but not yet confirmed as a frontend API response. |

---

### 7.2 Member 4 (Release Reconstruction & Attribution) Outputs
*Implemented in [`marineshield/investigation/engine.py`](file:///d:/MarineShield/MarineShield/marineshield/investigation/engine.py) and [`schemas.py`](file:///d:/MarineShield/MarineShield/marineshield/investigation/schemas.py); contract defined in [`docs/api/INVESTIGATION_CONTRACTS.md`](file:///d:/MarineShield/MarineShield/docs/api/INVESTIGATION_CONTRACTS.md).*

| Output Artifact | Schema Object | Key Fields for Frontend Display | Availability Status |
| :--- | :--- | :--- | :--- |
| **Release Hypothesis** | `ReleaseHypothesisContract` | `temporal_scope` (`t_observation_utc`, `t_earliest_utc`, `t_most_likely_utc`, `t_latest_utc`, `window_duration_hours`), `spatial_scope.release_polygon_geojson` (GeoJSON `Polygon`, `EPSG:4326`, `uncertainty_area_km2`, `centroid_lon`, `centroid_lat`) | Available in service/code, but not yet confirmed as a frontend API response. |
| **Candidate Hypotheses** | `SourceHypothesisContract` | `source_hypothesis_id`, `hypothesis_label` ($H_1 \dots H_n$), `source_category` (`VESSEL_IDENTIFIED`, `VESSEL_UNTRACKED_DARK`, `NON_VESSEL_SOURCE`, `UNKNOWN_SOURCE`), `candidate_entity` (name, MMSI, type, flag, description) | Available in service/code, but not yet confirmed as a frontend API response. |
| **Evidence Score & Strength** | `evidence_evaluation` | `evidence_score` ($0.0-100.0$), `evidence_strength` (`STRONG_COMPATIBILITY`, `MODERATE_COMPATIBILITY`, `WEAK_COMPATIBILITY`, `INSUFFICIENT_EVIDENCE`), `ranking_position` | Available in service/code, but not yet confirmed as a frontend API response. |
| **Counterfactual Stability** | `counterfactual_analysis` | `delta_score_margin` ($\Delta$), `ranking_stability` (`ROBUST_DOMINANT_HYPOTHESIS`, `AMBIGUOUS_CLOSE_ALTERNATIVES`, `FRAGILE_RANKING`, `MARGINAL`), explanation string | Available in service/code, but not yet confirmed as a frontend API response. |
| **Component Score Breakdown** | `component_breakdown` | Weighted contributions for $S_{spatial}$ ($0.20$), $S_{temporal}$ ($0.15$), $S_{trajectory}$ ($0.15$), $S_{drift}$ ($0.20$), $S_{vessel}$ ($0.15$), $S_{behavior}$ ($0.15$), and $C_{contradiction}$ deduction ($-0.20$) | Available in service/code, but not yet confirmed as a frontend API response. |
| **Supporting Evidence** | `supporting_evidence` | List of atomic evidence items (`SPATIAL_PROXIMITY`, `TEMPORAL_INTERSECTION`, `TRAJECTORY_INTERSECTION`, `DRIFT_COMPATIBILITY`, `BEHAVIOR_ANOMALY`) with human-readable summary text | Available in service/code, but not yet confirmed as a frontend API response. |
| **Contradictory Evidence** | `contradictory_evidence` | List of non-suppressed active contradictions (`CONTRADICTORY_PHYSICS`, moored at berth, speed limit violations) with penalty values | Available in service/code, but not yet confirmed as a frontend API response. |
| **Unknown Source State** | `InvestigationResult` | `status` (`SOURCE_UNKNOWN`), `is_unknown_triggered` (`true`), `unknown_trigger_reason` (`AIS_DATA_BLACKOUT`, `ALL_CANDIDATES_BELOW_THRESHOLD`), diagnostic recommendations | Available in service/code, but not yet confirmed as a frontend API response. |
| **Legal Non-Guilt Clause** | `non_guilt_clause` | Mandatory analytical disclaimer string required on all attribution views | Available in service/code, but not yet confirmed as a frontend API response. |

---

## 8. Figma and UI Status

### 8.1 Verified Figma & Design System Facts
- A Figma account exists for the project team.
- **No MarineShield Figma project, file, component library, or design tokens currently exist.**
- No final design system has been formally approved.
- No canonical Figma screen link currently exists.
- Stitch exploration has not yet been confirmed or linked.
- **Person 4 must not assume that a final Figma design or component library already exists.**

### 8.2 Governing Design & Layout Rules
1. **Canonical Source:** Once created, Figma will be the single canonical design source for UI typography, colors, component tokens, and layout geometry.
2. **Exploration Tool:** Stitch may be utilized for exploratory layout prototyping, but final production implementations must align with Figma specs.
3. **No Conflicting Dashboard Layouts:** Person 4 must not introduce an ad-hoc dashboard layout that diverges from the team's visual direction.
4. **Pre-Agreed UI Direction:** Person 1 has already communicated the intended visual command center direction to Person 4 separately.
5. **Mandatory Checkpoints:** Person 4 must consult and align with Person 1 at three specific milestones:
   - **Checkpoint A:** Initial WebGIS application shell and navigation framework.
   - **Checkpoint B:** Full incident detail workspace layout (map canvas, evidence panels, forecast slider).
   - **Checkpoint C:** Final UI polish, responsiveness, and accessibility refinement.

---

## 9. What Person 4 May Do Now

Before final UI implementation and backend integration, Person 4 is encouraged to:

1. **Inspect Repository Architecture:** Review [`docs/architecture/ARCHITECTURE.md`](file:///d:/MarineShield/MarineShield/docs/architecture/ARCHITECTURE.md), [`docs/architecture/WORKSTREAMS.md`](file:///d:/MarineShield/MarineShield/docs/architecture/WORKSTREAMS.md), and [`.agents/rules/ui_rules.md`](file:///d:/MarineShield/MarineShield/.agents/rules/ui_rules.md).
2. **Study Real-World Synthetic Fixtures:** Examine all 8 JSON scenario files in [`tests/fixtures/investigation/`](file:///d:/MarineShield/MarineShield/tests/fixtures/investigation/) to understand exact data payloads for single dominant candidates, tied candidates, AIS blackouts, dark vessels, contradictions, and unknown outcomes.
3. **Inspect Output Contracts:** Review [`marineshield/oil_intelligence/schemas.py`](file:///d:/MarineShield/MarineShield/marineshield/oil_intelligence/schemas.py) and [`marineshield/investigation/schemas.py`](file:///d:/MarineShield/MarineShield/marineshield/investigation/schemas.py).
4. **Draft Frontend Screen & Component Inventory:** Plan the hierarchy of reusable React components (e.g. MapContainer, LayerManager, EvidenceCard, ContradictionList, ConfidenceGauge, DqiBanner, ForecastTimeline, IncidentSummaryModal).
5. **Design System Preparation:** Prepare CSS design tokens, HSL color palettes, MapLibre GL layer styling rules, and Lucide icon sets adhering to `.agents/rules/ui_rules.md`.
6. **State Management & Edge Case Planning:** Define frontend state handling for loading skeletons, network timeouts, empty candidate lists, low-bandwidth coastal mode, and abstention banners.
7. **Document Integration Blockers:** Maintain an active list of questions regarding missing FastAPI routes and backend contracts.
8. **Wait for Approved Figma Wireframes:** Align on wireframes with Person 1 before locking the final visual design.

---

## 10. What Person 4 Must Not Do Yet

To preserve architectural integrity and avoid wasted effort, Person 4 **MUST NOT**:

1. **Invent Ad-Hoc API Endpoints or Payloads:** Do not create frontend interfaces based on imagined API response schemas that differ from `OIL_INTELLIGENCE_CONTRACTS.md` or `INVESTIGATION_CONTRACTS.md`.
2. **Invent Database Tables or Direct DB Queries:** Do not write direct SQL/Supabase client calls in the frontend; all persistence is mediated by FastAPI.
3. **Assume Figma Screens Already Exist:** Do not block progress waiting for links that have not yet been generated.
4. **Introduce Conflicting Layout Directions:** Do not implement a generic admin-template dashboard; MarineShield is an interactive spatial WebGIS Command Center.
5. **Duplicate Subsystem Logic on Client:** Do not implement drift physics, polygon clipping, look-alike classification, or evidence score arithmetic inside JavaScript/TypeScript.
6. **Display False Certainty:** Do not hide confidence scores, data quality deficits, active contradictions, or `UNKNOWN_SOURCE` states.
7. **Use Legal Guilt Terminology:** Never label candidates as "culprits", "perpetrators", or "guilty vessels" in the UI. Always use neutral analytical terminology (`candidate_hypothesis`, `compatibility_score`).
8. **Treat Unmatched SAR Targets as Proven Dischargers:** Always display dark vessels with analytical caveats (`VESSEL_UNTRACKED_DARK`).
9. **Hardcode Backend Secrets:** Do not include API keys, database passwords, or private tokens in frontend environment variables.
10. **Silently Modify Shared Contracts:** Never alter API schema structures without recording an architectural decision in [`docs/decisions/DECISION_LOG.md`](file:///d:/MarineShield/MarineShield/docs/decisions/DECISION_LOG.md).

---

## 11. Required Questions and Missing Items

| Item | Current Status | Repository Path / Evidence | Owner | Action Required Before Phase 6 Frontend Integration |
| :--- | :---: | :--- | :--- | :--- |
| **FastAPI Backend Server & Routes** | **MISSING — REQUIRES CONFIRMATION** | No `server/`, `backend/`, or `api/` directory found. | Member 6 Backend (Person 3 / Person 4) | Create FastAPI app entry point (`main.py`) and implement REST routers for `/api/v1/incidents`, `/api/v1/detection`, `/api/v1/attribution`. |
| **Spill Detection REST Endpoint** | **PARTIAL** | Python service exists in `marineshield/oil_intelligence/service.py`; REST route missing. | Member 6 Backend | Wrap `OilIntelligenceService.process_tile` in FastAPI route `POST /api/v1/detection/process-tile`. |
| **Attribution REST Endpoint** | **PARTIAL** | Python engine exists in `marineshield/investigation/engine.py`; REST route missing. | Member 6 Backend | Wrap `SourceInvestigationEngine.run_investigation` in FastAPI route `POST /api/v1/attribution/investigate`. |
| **Vessel Intelligence & AIS Stream Contract** | **PARTIAL** | Candidate schema in `INVESTIGATION_CONTRACTS.md` §2; AIS ingestion API missing. | Member 3 (Person 2) | Provide OpenAPI spec for historical AIS trajectory queries (`GET /api/v1/vessels/tracks`) and SAR-AIS reconciliation matches. |
| **PyGNOME Drift Forecast Contract & Endpoint** | **MISSING — REQUIRES CONFIRMATION** | Mentioned conceptually in `ARCHITECTURE.md` Layer 6; schema missing. | Member 5 (Person 3) | Define canonical schema and REST endpoint (`POST /api/v1/forecast/drift`) for $+6\text{h}/+12\text{h}/+24\text{h}/+48\text{h}$ drift cones. |
| **Threat Intelligence & Sensitive Asset Contract** | **MISSING — REQUIRES CONFIRMATION** | Mentioned conceptually in `ARCHITECTURE.md` Layer 7; schema missing. | Member 5 (Person 3) / Member 6 Backend | Define canonical schema for sensitive coastal assets and MarineShield Response Priority calculation (`/api/v1/threats`). |
| **Database Migrations & Models** | **MISSING — REQUIRES CONFIRMATION** | Overview in `docs/database/README.md`; SQL/Alembic scripts missing. | Member 6 Backend | Create Alembic migration scripts establishing PostGIS spatial tables for incidents, polygons, tracks, and hypotheses. |
| **Figma Project & UI Design File** | **MISSING — REQUIRES CONFIRMATION** | Figma account exists; project file not created. | Person 4 & Person 1 | Create Figma project file, establish design tokens, and approve WebGIS layout wireframes. |
| **Frontend Project Initialization** | **MISSING — REQUIRES CONFIRMATION** | No `package.json` or `frontend/` directory found. | Person 4 | Initialize modern WebGIS project (e.g. Vite + React + TypeScript + MapLibre GL + Tailwind CSS v4) in `frontend/`. |
| **Sample API Mock Responses** | **COMPLETE (in Fixtures)** | [`tests/fixtures/investigation/*.json`](file:///d:/MarineShield/MarineShield/tests/fixtures/investigation/) | Member 4 (Person 1) | Person 4 can directly use the 8 JSON fixture files as mock API responses for client development. |

---

## 12. Instructions for Person 4

Please follow these sequential steps to begin frontend development smoothly:

1. **Read This Handoff Document First:** Review all sections above, paying special attention to Section 2 (Ownership), Section 7 (Available Outputs), Section 8 (Figma Status), and Section 10 (Prohibitions).
2. **Open Workspace via Git Access:** Clone and open the MarineShield repository using the repository access provided separately by Person 1.
3. **Verify Repository Structure:** Inspect the actual paths listed in Section 3 (`docs/api/`, `docs/ml/`, `marineshield/`, `tests/fixtures/`). Do not assume unlisted folders exist.
4. **Utilize Verified Fixtures for Mock Data:** Use the 8 validated JSON files in [`tests/fixtures/investigation/`](file:///d:/MarineShield/MarineShield/tests/fixtures/investigation/) as realistic mock data for rendering incident attribution cards, evidence lists, contradictions, and unknown state views.
5. **Align on Milestone Checkpoints with Person 1:**
   - Review proposed WebGIS layout wireframes at **Checkpoint A** before building complex component logic.
   - Review incident detail workspace assembly at **Checkpoint B**.
   - Review responsiveness, theme tokens, and accessibility at **Checkpoint C**.
6. **Consult on Missing Contracts:** For any item marked `MISSING — REQUIRES CONFIRMATION` in Section 11 (e.g. Member 3 AIS endpoints, Member 5 Forecast schemas, FastAPI routers), coordinate with Person 1 and respective workstream leads before writing client adapters.
7. **Strictly Enforce Separation of Concerns:** Keep all ML inference, drift calculations, and database business logic on the backend.
8. **Respect Responsible-AI Guidelines:** Always display confidence indicators, non-guilt disclaimers, and clear status badges for `UNKNOWN_SOURCE` and `ABSTAINED` states.
9. **Update Documentation Formally:** If changes to shared API contracts or WebGIS requirements are agreed upon, record them formally in [`docs/decisions/DECISION_LOG.md`](file:///d:/MarineShield/MarineShield/docs/decisions/DECISION_LOG.md).
