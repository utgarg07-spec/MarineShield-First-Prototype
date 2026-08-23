# Environmental History Contract (Development Only)

**IMPORTANT: This is a synthetic development-only document. It does NOT authorize production forecast implementation.**

This contract defines the schema and rules for the local, deterministic integration testing of Person 1’s Member 4 release-reconstruction and source-investigation engine.

## Status and Limitations
- **Status:** Deterministic fixture for local integration testing.
- **Limitations:** This data is synthetic and not scientifically valid. It must not be used for actual marine forecasting. Never contact a live provider or read credentials.
- **Data Mode:** SYNTHETIC_DEVELOPMENT_FIXTURE

## Data Schema & Types

### Coordinate Reference System (CRS)
- **CRS:** WGS84 / EPSG:4326
- **Coordinate Order:** `[longitude, latitude]`
- **Longitude Convention:** -180 to 180 degrees

### Temporal Specification
- **Timestamp Format:** ISO 8601 UTC strings ending in Z (e.g., `2024-01-20T00:55:41Z`).
- **Temporal Resolution:** 1 hour.
- **No-Interpolation Rule:** The investigation engine may use only exact records whose timestamps are at or before the investigation timestamp. If an exact timestamp is unavailable, it returns a clearly reported missing-value condition rather than interpolating.
- **Future-Data Rejection Rule:** Every record must have a timestamp less than or equal to the investigation timestamp. The loader must strictly reject any future records.

### Environmental Variables & Units
- **Wind:**
  - `u10_mps`: Eastward wind component at 10 m above the surface (m/s).
  - `v10_mps`: Northward wind component at 10 m above the surface (m/s).
- **Current:**
  - `u_current_mps`: Eastward ocean-current component (m/s).
  - `v_current_mps`: Northward ocean-current component (m/s).
- **Vector Convention:** Positive u means eastward; Positive v means northward.

### Missing Values & Quality Flags
- **Missing-Value Behavior:** Use JSON `null`. Do not replace missing values with zero.
- **Quality Flags:** Each time/grid record must contain a `quality_flag` with one of the following exact strings:
  - `VALID`
  - `MISSING`
  - `SYNTHETIC`

### Provenance Requirements
Every environmental record must include the following provenance fields:
- `provider`
- `dataset_name`
- `dataset_version`
- `data_mode`
- `acquisition_time`
- `processing_time`
- `lineage_id`
- `source_identifier`
- `historical_availability` (Must be true only for timestamps at or before the investigation timestamp. No future records allowed.)
