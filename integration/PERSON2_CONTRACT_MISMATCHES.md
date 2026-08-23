# MarineShield — Person 2 Contract Mismatch & Gap Analysis

**Document Generation Date:** 2026-08-21  
**Author:** MarineShield Integration Auditor  
**Scope:** Cross-comparison of Person 2 Member 1 / Member 3 handoffs against canonical MarineShield Phase 2 contracts.  

---

## 1. Phase 2 Contracts Status Matrix

| Contract Domain | Canonical Contract File Path | Exists in Repo? | Completeness | Producer | Primary Consumer | Compliance Status |
| :--- | :--- | :---: | :---: | :--- | :--- | :---: |
| **SAR Data Contract** | `response_of_person2_member1/SAR_DATA_CONTRACT.md` | **YES** | **Complete** | Member 1 (Person 2) | Member 2 (Person 1) | **COMPLIANT** with minor geodetic note |
| **ML Output Contract** | `docs/ml/OIL_INTELLIGENCE_CONTRACTS.md` | **YES** | **Complete** | Member 2 (Person 1) | FastAPI / Person 4 WebGIS | **COMPLIANT** |
| **Vessel Domain Contract** | `response_of_person2_member3/VESSEL_DATA_CONTRACT.md` | **YES** | **Complete** | Member 3 (Person 2) | Member 4 (Person 1) | **COMPLIANT** with bridge adapter needed |
| **Investigation Contract**| `docs/api/INVESTIGATION_CONTRACTS.md` | **YES** | **Complete** | Member 4 (Person 1) | FastAPI / Person 4 WebGIS | **COMPLIANT** |
| **Forecast Contract** | `docs/architecture/ARCHITECTURE.md` (Layer 6) | **NO** (No formal contract doc) | **PARTIAL** | Member 5 (Person 3) | Member 6 / WebGIS | **MISSING FORMAL SPEC** |
| **API Contract** | `docs/api/README.md`, `.agents/rules/api_contracts.md` | **YES** | **Partial** | Member 6 Backend | Person 4 WebGIS | **PARTIAL — Routes Pending** |
| **Database Schema** | `docs/database/README.md`, `.agents/rules/database_rules.md` | **YES** | **Partial** | Member 6 Backend | Domain Services | **PARTIAL — Migrations Pending** |
| **Testing Standards** | `docs/testing/DEFINITION_OF_DONE.md` | **YES** | **Complete** | All Workstreams | QA / CI / CD | **COMPLIANT** |

---

## 2. Comprehensive Issue & Mismatch Classification

Each issue is assigned a strict risk severity:
- **`BLOCKER`**: Prevents runtime execution or violates fundamental architectural constraints.
- **`HIGH RISK`**: Potential for silent runtime data corruption, data leakage, or security exposure.
- **`MEDIUM RISK`**: Schema mismatch requiring an explicit transformation adapter.
- **`LOW RISK`**: Minor naming convention or documentation alignment.
- **`INFORMATIONAL`**: Architectural observation or recommendation.

---

### Issue 1: Hardcoded Secrets in Example Configuration (CRITICAL SECURITY)
- **Classification:** **`HIGH RISK`** (Security & Hygiene)
- **Locations:** `response_of_person2_member3/.env.example` (lines 57-59).
- **Description:** The `.env.example` template file in Member 3 contains real Copernicus CDSE credentials and an active Global Fishing Watch JWT bearer token.
- **Impact:** While `.env` is gitignored, `.env.example` is committed to version control. If pushed to a public or shared remote repository, these external API credentials would be compromised.
- **Required Resolution:** Cleanse `response_of_person2_member3/.env.example` immediately. Replace active values with empty dummy strings (`CDSE_USERNAME=""`, `GFW_API_ACCESS_TOKEN=""`).

---

### Issue 2: Direct Dataclass Interface Mismatch between Member 3 Output and Member 4 Input
- **Classification:** **`MEDIUM RISK`** (Integration Adapter Gap)
- **Locations:** 
  - Producer: `response_of_person2_member3/intelligence_service.py` (emits dictionary payloads with `matches`, `unmatched_detections`, `behavior_features`).
  - Consumer: `marineshield/investigation/engine.py` (consumes `VesselObservation` dataclass instances).
- **Description:** Member 3's demonstration pipeline outputs nested dictionary lists (`matches`, `unmatched_detections`, `anomalies_detected`), whereas Member 4's `SourceInvestigationEngine` consumes `VesselObservation` objects containing combined `track_points`, `has_ais_gap`, and `speed_drop_knots` properties.
- **Impact:** Passing Member 3's raw output dictionary into Member 4's engine directly without a transformation bridge will cause an `AttributeError` or missing field validation failure.
- **Required Resolution:** Implement a thin adapter function (`marineshield.adapters.vessel_to_investigation_adapter`) that maps:
  1. `VesselMatch` $\to$ `VesselObservation(source_type="AIS_TRACK", vessel_name=..., track_points=...)`
  2. `UnmatchedVessel` $\to$ `VesselObservation(source_type="SAR_DETECTION", sar_vessel_detection_id=..., estimated_length_m=...)`
  3. `AnomalyEvent` (`AIS_TRANSMISSION_GAP`) $\to$ sets `has_ais_gap = True`
  4. `AnomalyEvent` (`ABNORMAL_SPEED_DROP`) $\to$ sets `speed_drop_knots = drop_value`.

---

### Issue 3: Geodetic Inconsistency between EPSG:4326 and Metric Spatial Resolution
- **Classification:** **`MEDIUM RISK`** (Geodetic / Metric Precision)
- **Locations:** `response_of_person2_member1/tiler.py` and `tile_manifest.json`.
- **Description:** Member 1 metadata sidecars declare `crs: "EPSG:4326"` alongside `spatial_resolution_m: [10.0, 10.0]`. In geographic coordinate systems (`EPSG:4326`), pixel dimensions represent angular degrees ($\Delta \lambda, \Delta \phi$). Physical distance per degree longitude varies with latitude ($\approx 111.32 \cdot \cos(\phi)\text{ km}$).
- **Impact:** If Member 2's geometry extractor assumes isotropic metric spacing ($10\text{ m} \times 10\text{ m}$) directly from pixel count without applying latitude cosine correction, calculated spill area ($\text{km}^2$) and perimeter ($\text{km}$) will be distorted by $5-15\%$ in the Arabian Sea ($15^\circ-20^\circ\text{N}$).
- **Required Resolution:** Confirm that `marineshield.oil_intelligence.geometry_extractor` computes metric area using the exact geodetic bounding box `geo_bbox_wgs84` and WGS84 ellipsoidal scaling rather than a naive $100\text{ m}^2/\text{pixel}$ multiplication.

---

### Issue 4: Input Tile Spatial Dimension Assumption in Member 2 Service
- **Classification:** **`LOW RISK`** (Spatial Rescaling)
- **Locations:** 
  - Member 1 Tiler: Outputs tiles of shape $(2, 512, 512)$.
  - Member 2 SAM Model: Native ViT image encoder operates on $(3, 1024, 1024)$.
- **Description:** Member 1 outputs $512 \times 512$ pixel arrays, whereas SAM ViT-B expects $1024 \times 1024$ tensors.
- **Resolution:** Member 2's preprocessor (`marineshield/oil_intelligence/preprocessing.py`) already contains bilinear upsampling and $\times 2.0$ bounding box scaling. This must be formally verified in the Phase 6 integration test.

---

### Issue 5: Missing Formal Contract for Member 5 PyGNOME Drift Modeling
- **Classification:** **`HIGH RISK`** (Missing Phase 2 Contract)
- **Locations:** `docs/api/` (No `FORECAST_CONTRACTS.md` or `THREAT_CONTRACTS.md` currently exists).
- **Description:** While Member 1, Member 2, Member 3, and Member 4 have formal contract documents (`SAR_DATA_CONTRACT.md`, `OIL_INTELLIGENCE_CONTRACTS.md`, `VESSEL_DATA_CONTRACT.md`, `INVESTIGATION_CONTRACTS.md`), Member 5's drift trajectory output format and Member 6's sensitive asset threat intersection format are only documented conceptually in `ARCHITECTURE.md`.
- **Impact:** Downstream frontend components (Person 4) cannot finalize forecast slider UI or threat alert cards until Member 5's exact JSON schema is frozen.
- **Required Resolution:** Person 3 (Member 5 Lead) must author and freeze `docs/api/FORECAST_CONTRACTS.md` and `docs/api/THREAT_CONTRACTS.md` prior to Phase 6 integration.

---

### Issue 6: FastApi Backend REST Routes and Database Migrations Missing
- **Classification:** **`HIGH RISK`** (Missing Infrastructure Layer)
- **Locations:** `backend/`, `server/`, `supabase/`, `migrations/` (none exist in repository).
- **Description:** All domain logic for Member 1, Member 2, Member 3, and Member 4 currently exists as standalone Python modules without an overarching FastAPI REST wrapper or Alembic database migrations.
- **Impact:** Person 4 (WebGIS Frontend) cannot execute live HTTP REST queries until the FastAPI server layer is implemented.
- **Required Resolution:** Member 6 Backend lead must initialize FastAPI app (`/api/v1/*`) and author PostGIS migration scripts.
