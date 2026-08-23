# MarineShield — Person 2 Handoff Audit Report

**Audit Execution Date:** 2026-08-21  
**Auditor Role:** MarineShield Integration Auditor  
**Scope of Audit:** Read-only inspection of Person 2 handoff packages:
1. `response_of_person2_member1/` (Member 1: Sentinel-1 SAR Acquisition, Preprocessing & ML-Tiling)
2. `response_of_person2_member3/` (Member 3: Vessel / AIS / Global Fishing Watch Intelligence & AIS-SAR Reconciliation)

---

## 1. Executive Summary & Audit Mandate

This document provides a factual, evidence-based audit of the deliverables submitted by **Person 2** for **Member 1** and **Member 3**. All findings are derived strictly from actual code files, JSON schemas, metadata sidecars, configuration files, test suites, and demonstration payloads in the repository.

### Key Summary Findings
- **Member 1 (SAR Acquisition & Preprocessing):** Delivered a functional Sentinel-1 Copernicus client, preprocessing pipeline, and tiling engine generating $(2, 512, 512)$ Float32 tiles in $\text{dB}$ scale with JSON sidecars and SHA-256 integrity hashes. **Crucial Finding:** The handoff provides SAR preprocessing and tile generation tools; it does **not** contain or claim a trained oil-spill segmentation model.
- **Member 3 (Vessel / AIS Intelligence):** Delivered a GFW API client adapter, parser, deterministic AIS-SAR reconciliation matcher, and anomaly detector. Demonstration results reflect a **`MOCK_HYBRID`** execution mode.
- **Security & Hygiene Finding:** The file `response_of_person2_member3/.env.example` contains active Copernicus CDSE and Global Fishing Watch credentials embedded directly in the example template. These must be purged before merging into production.

---

## 2. Member 1 (SAR Ingestion & Preprocessing) Detailed Audit

### 2.1 File & Path Inventory

| Component | Repository Path | Exists | Description / Verification |
| :--- | :--- | :---: | :--- |
| **SAR Data Contract** | `response_of_person2_member1/SAR_DATA_CONTRACT.md` | **YES** | 520 lines. Canonical schema (`marineshield.sar.v1`) for Sentinel-1 scenes and tiles. |
| **Copernicus Auth** | `response_of_person2_member1/copernicus_auth.py` | **YES** | OAuth2 client credentials token manager with caching. |
| **Copernicus Client** | `response_of_person2_member1/copernicus_client.py` | **YES** | OData search and download client for CDSE. |
| **SAR Preprocessor** | `response_of_person2_member1/sar_preprocessor.py` | **YES** | Calibration, orbit application, Refined Lee speckle filtering, and $\text{dB}$ conversion. |
| **Metadata Parser** | `response_of_person2_member1/metadata_parser.py` | **YES** | Extracts orbit, footprint polygon, sensor parameters, and timestamps. |
| **Tiler Engine** | `response_of_person2_member1/tiler.py` | **YES** | Deterministic $(2, 512, 512)$ tile generator with sidecars and hash verification. |
| **Tile Generator Script**| `response_of_person2_member1/generate_sar_tiles.py` | **YES** | CLI script generating tiles from calibrated rasters. |
| **Pipeline Runner** | `response_of_person2_member1/pipeline.py` | **YES** | End-to-end orchestration from granule query to preprocessed tiles. |
| **Tile Manifest** | `response_of_person2_member1/tile_manifest.json` | **YES** | 4-tile grid manifest (`3 train, 1 val`) for scene `S1A_IW_GRDH_1SDV_20240120...`. |
| **Sample Tiles (.npy)** | `response_of_person2_member1/S1A_..._tile_*.npy` | **YES** | 4 binary tile arrays (2,097,280 bytes each = $2 \times 512 \times 512 \times 4$ bytes Float32). |
| **Tile Sidecars (.json)**| `response_of_person2_member1/S1A_..._metadata.json` | **YES** | 4 JSON metadata sidecars with exact pixel/geographic bounding boxes. |
| **Unit & Accept Tests** | `response_of_person2_member1/test_sar_tiling.py`<br>`response_of_person2_member1/test_sentinel1_acquisition.py`<br>`response_of_person2_member1/verify_phase3_member1.py` | **YES** | Test suites covering authentication, tiling, hashing, and split leakage. |

---

### 2.2 Technical Verification of SAR Products

```
Raw Sentinel-1 SAFE Granule (IW GRD)
  │
  ▼
Radiometric Calibration & Specke Filter (Refined Lee 7x7)
  │
  ▼
Calibrated Multi-band Scene [VV, VH] (Float32, dB scale [-30.0 to 0.0])
  │
  ▼
Deterministic Tiling Engine (SARTiler, 512x512, Stride 512)
  ├── Normalized Tile Array (.npy) -> Shape: (2, 512, 512), dtype: float32, range: [0.0, 1.0]
  └── Metadata Sidecar (.json)     -> GeoBBOX [WGS84], SHA-256, Split (Train/Val)
```

1. **Input Scene Format:** Sentinel-1 Level-1 Ground Range Detected High-Resolution (GRDH), Interferometric Wide (IW) swath mode.
2. **Channel Order:** 2 channels: Band 0 = `VV` (primary oil detection channel), Band 1 = `VH` (cross-pol vessel detection / texture channel).
3. **Tile Dimensions & Data Type:** Array shape `(2, 512, 512)` of type `np.float32`.
4. **Radiometric Units & Normalization:**
   - Calibrated backscatter: $\sigma^0$ in decibels ($\text{dB}$), where $\text{min\_db} = -30.0\text{ dB}$, $\text{max\_db} = 0.0\text{ dB}$.
   - Linear clipping normalization:
     $$I_{\text{norm}} = \text{clip}\left(\frac{\sigma^0_{\text{dB}} - (-30.0)}{0.0 - (-30.0)}, 0.0, 1.0\right)$$
   - No-Data representation: `-9999.0` in master GeoTIFFs, mapped to `0.0` after normalization with valid data mask.
5. **Geographic & Coordinate System Verification:**
   - Coordinate Reference System: `EPSG:4326` (WGS84 2D Geographic).
   - Pixel Spacing Claim: Nominal $10.0\text{ m} \times 10.0\text{ m}$ range/azimuth spacing.
6. **Train/Validation Split Policy:**
   - Spatial quadrant partitioning (`spatial_quadrant_no_leakage`): South-East quadrant is assigned to `val` ($25\%$), remainder to `train` ($75\%$). Avoids spatial leakage between adjacent overlapping tiles.
7. **Execution Commands:**
   - Generate Tiles: `python response_of_person2_member1/generate_sar_tiles.py`
   - Run Test Suite: `python response_of_person2_member1/verify_phase3_member1.py`

---

### 2.3 Critical Geodetic Finding: EPSG:4326 vs. 10m Spacing

> [!WARNING]
> **Geodetic Consistency Issue in SAR Metadata:**
> The metadata sidecar claims CRS `EPSG:4326` (degrees) while simultaneously reporting `spatial_resolution_m: [10.0, 10.0]`. In `EPSG:4326`, $1^\circ \text{ latitude} \approx 111.32\text{ km}$, but $1^\circ \text{ longitude} = 111.32 \cdot \cos(\text{lat})\text{ km}$ (e.g. $\approx 105.7\text{ km}$ at $18^\circ\text{N}$).
> 
> **Impact:** While neural networks (SAM/U-Net) process dimensionless $512 \times 512$ pixel tensors directly, metric geometry computations (e.g., polygon area in $\text{km}^2$, perimeter in $\text{km}$, elongation ratios in `marineshield.oil_intelligence.geometry_extractor`) **must** project coordinates to local UTM (e.g. `EPSG:32643` for Arabian Sea) or apply ellipsoidal geodesics (Haversine/Vincenty) to prevent latitude-dependent spatial distortion.

---

## 3. Member 3 (Vessel / AIS Intelligence) Detailed Audit

### 3.1 File & Path Inventory

| Component | Repository Path | Exists | Description / Verification |
| :--- | :--- | :---: | :--- |
| **Vessel Data Contract** | `response_of_person2_member3/VESSEL_DATA_CONTRACT.md` | **YES** | 548 lines. Full schema for 7 canonical vessel entities. |
| **GFW Client Adapter** | `response_of_person2_member3/gfw_client.py` | **YES** | Global Fishing Watch API v3 adapter with fallback mock data generator. |
| **Vessel Cache Manager** | `response_of_person2_member3/vessel_cache_manager.py` | **YES** | File-based cache for AIS vessel records and spatial queries. |
| **Vessel Parser** | `response_of_person2_member3/vessel_parser.py` | **YES** | Transforms raw GFW/AIS dictionaries into canonical contracts. |
| **Intelligence Service** | `response_of_person2_member3/intelligence_service.py` | **YES** | Spatio-temporal filter, AIS-SAR reconciliation, and anomaly detection. |
| **Demonstration Script** | `response_of_person2_member3/run_vessel_demonstration.py`| **YES** | Executes pipeline on 2024 Arabian Sea demonstration scenario. |
| **Demonstration Results**| `response_of_person2_member3/vessel_demonstration_results.json` | **YES** | Output JSON containing 5 AIS candidates, 2 SAR detections, 1 match, 1 unmatched dark vessel, and 3 anomalies. |
| **Unit & Accept Tests** | `response_of_person2_member3/test_vessel_data_contract.py`<br>`response_of_person2_member3/test_vessel_intelligence.py`<br>`response_of_person2_member3/verify_phase3_member3.py` | **YES** | Tests validating the 7 entity contracts, matching heuristics, and anomaly scores. |

---

### 3.2 Verification of the 7 Canonical Vessel Entities

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│     Vessel      │       │ AISObservation  │       │    AISTrack     │
│ (Static Profile)│◄──────┤ (Instantaneous) ├──────►│  (Trajectory)   │
└─────────────────┘       └────────┬────────┘       └─────────────────┘
                                   │
                                   ▼
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│SARVesselDetection│◄─────►│   VesselMatch   │       │ UnmatchedVessel │
│ (Remote Radar)  │       │ (Reconciliation)│       │  (Dark Target)  │
└─────────────────┘       └─────────────────┘       └─────────────────┘
                                   │
                                   ▼
                          ┌─────────────────┐
                          │  AnomalyEvent   │
                          │(Gaps/Speed/Turn)│
                          └─────────────────┘
```

1. **`Vessel`**: Validated fields: `vessel_id` (UUID), `mmsi` (9-digit string), `imo` (7-digit string or null), `vessel_name`, `ship_type` (12-class enum), `length_meters`, `beam_meters`.
2. **`AISObservation`**: Validated fields: `observation_id`, `mmsi`, `timestamp` (ISO 8601 UTC), `latitude` $[-90.0, 90.0]$, `longitude` $[-180.0, 180.0]$, `speed_over_ground_knots`, `course_over_ground_deg`, `heading_deg`, `navigational_status`, `source_provider`.
3. **`AISTrack`**: Segmented LineString GeoJSON with trajectory kinematics.
4. **`SARVesselDetection`**: Validated fields: `detection_id`, `source_granule_id`, `detection_timestamp`, `centroid_lat`, `centroid_lon`, `estimated_length_meters`, `estimated_width_meters`, `estimated_heading_deg`, `radar_cross_section_db`, `signal_to_clutter_ratio_db`, `detection_confidence`, `polarization_used` (`VH`), `geometry_geojson` (Point `[lon, lat]`).
5. **`VesselMatch`**: Validated fields: `match_id`, `sar_detection_id`, `matched_mmsi`, `match_status` (`MATCHED`), `match_confidence` ($0.0-1.0$), `distance_offset_meters`, `timestamp_offset_seconds`, `heading_delta_deg`, `speed_delta_knots`, `dimension_match_score`, `reconciliation_algorithm`.
6. **`UnmatchedVessel`**: Validated fields: `unmatched_id`, `sar_detection_id`, `source_granule_id`, `detection_timestamp`, `centroid_lat`, `centroid_lon`, `estimated_length_meters`, `detection_confidence`, `ais_search_radius_km`, `ais_time_window_minutes`, `candidate_vessels_searched_count`, `dark_vessel_confidence`, `description`.
   - *Mandatory Non-Accusation Rule:* Description explicitly states: `"INVESTIGATION FLAG ONLY - Indicates a physically detected SAR signature lacking active transponder correlation. Do not interpret as illegal behavior."*
7. **`AnomalyEvent`**: Validated fields: `anomaly_id`, `mmsi`, `anomaly_type` (`AIS_TRANSMISSION_GAP`, `ABNORMAL_SPEED_DROP`, `LOITERING_IN_ZONE`, `ERRATIC_COURSE_CHANGE`), `severity_level` (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`), `time_start`, `time_end`, `duration_seconds`, `geometry_geojson`, `anomaly_score` ($0.0-1.0$), `context_indicators`.

---

### 3.3 Provenance & Data Mode Audit in Demonstration Results

Inspection of `vessel_demonstration_results.json` reveals:
- **Execution Timestamp:** `2026-08-21T13:01:30.786Z`
- **Reported `gfw_api_status`:** `"LIVE_API"`
- **Actual `data_mode`:** `"MOCK_HYBRID"`
- **Provenance Hash:** `"demo_run_dff3e36e4f111353"`

> [!IMPORTANT]
> **Audit Finding on Demonstration Data:**
> Although the demonstration runner queried the GFW API, fallback mock observations were utilized to simulate a complete multi-vessel scenario with known ground-truth matches and anomalies. In Phase 6 integration, records must retain explicit `data_mode: "MOCK_HYBRID"` or `source_provider: "MOCK_SYNTHETIC"` provenance tags to avoid mislabeling test fixtures as live maritime intelligence.

---

## 4. Discrepancies Between Written Summaries and Actual Code

1. **Coordinate Format Consistency:** Written summaries refer to `(lat, lon)` in prose, but actual JSON schemas and code consistently enforce GeoJSON WGS84 `[longitude, latitude]` coordinate order.
2. **Channel Dimensions:** Written text occasionally mentions single-channel SAR, but the actual tiler implementation and saved `.npy` artifacts strictly output **2-channel arrays** `(2, 512, 512)` with `VV` (Band 0) and `VH` (Band 1).
3. **Reconciliation Heuristics:** The summary references a multi-stage machine learning matching classifier, but the actual code (`intelligence_service.py`) implements a deterministic distance/heading/timestamp weighted heuristic (`DETERMINISTIC_SPATIO_TEMPORAL_HEURISTIC_V1`). This is compliant with project architectural rules (ADR-002: no black-box matchers).
