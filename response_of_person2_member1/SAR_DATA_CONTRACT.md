# MarineShield Canonical SAR Data Contract Specification

**Document Version:** `1.0.0`  
**Status:** `AUTHORITATIVE / FROZEN`  
**Producer Workstream:** **Person 2** (Member 1: Sentinel-1 Satellite Ingestion & SAR Preprocessing)  
**Consumer Workstreams:**
- **Person 1** (Member 2: Oil Segmentation, Look-Alike Classification, SAR Vessel Detection; Member 4: Release Estimation)
- **Person 3** (Member 5: PyGNOME Drift Modeling; Member 6: Backend REST API & Incident Reports)
- **Person 4** (Member 6: WebGIS Command Center UI)

---

## 1. Executive Summary & Purpose

This document defines the **canonical data contract** governing all Synthetic Aperture Radar (SAR) products across the MarineShield platform.

To eliminate ambiguity across workstream boundaries, every SAR granule ingested and preprocessed by **Person 2** MUST adhere strictly to the schema, coordinate reference systems, pixel encodings, metadata fields, and provenance structures defined herein. **Person 1 (ML / Detection Engine)** and downstream consumers will reject any raster or payload that violates this specification.

> **CRITICAL ARCHITECTURAL DIRECTIVE**:
> In accordance with project rules, this document defines the contract specification only. Preprocessing execution pipelines are implemented in subsequent tasks.

---

## 2. Fundamental Radiometric, Spatial & Engineering Rules

1. **Radiometric Calibrated Units**:
   - All SAR intensity arrays MUST be calibrated to **$\sigma^0$ (Sigma Naught) in decibels ($\text{dB}$)**:
     $$\sigma^0_{\text{dB}} = 10 \cdot \log_{10}(\sigma^0_{\text{linear}})$$
   - Pixel data type in master GeoTIFFs: `Float32` (`float32`).
   - NoData / Mask values MUST be represented as `-9999.0` (or IEEE `NaN`).

2. **Coordinate Reference System (CRS)**:
   - Primary Standard CRS: **`EPSG:4326` (WGS84 2D Geographic Coordinates)** with longitude in $[-180.0, +180.0]$ and latitude in $[-90.0, +90.0]$.
   - All spatial boundaries, bounding boxes, and scene footprint geometries MUST be encoded in `EPSG:4326`.

3. **Polarization Channels**:
   - **`VV` (Vertical-Vertical)**: Mandatory primary channel for surface roughness damping and oil-slick detection.
   - **`VH` (Vertical-Horizontal)**: Mandatory cross-polarization channel for ship detection, metallic volume scattering, and look-alike texture analysis.
   - Optional auxiliary bands: `INCIDENCE_ANGLE` (local incidence angle raster in degrees $[20.0^\circ, 46.0^\circ]$).

4. **Spatial Resolution & Grid Alignment**:
   - Nominal pixel spacing for Sentinel-1 IW GRD: **$10.0\text{ m} \times 10.0\text{ m}$**.
   - Pixel registration: Pixel-is-Area / Area convention.

5. **ML Tiling & Normalization Standard (Person 1 Interface)**:
   - Inference tile dimension: $512 \times 512$ pixels (or $1024 \times 1024$ pixels) with configurable overlap (e.g. 64px border).
   - Normalization standard for neural network inputs:
     $$I_{\text{norm}} = \text{clip}\left(\frac{\sigma^0_{\text{dB}} - \mu_{\text{dB}}}{s_{\text{dB}}}, -1.0, 1.0\right) \quad \text{or} \quad \text{clip}\left(\frac{\sigma^0_{\text{dB}} - (-30.0)}{0.0 - (-30.0)}, 0.0, 1.0\right)$$

---

## 3. Canonical SAR Data Contract Schema

The canonical contract comprises two inseparable deliverables for every processed SAR scene:
1. **Georeferenced Raster Product** (Multi-band or single-band Cloud-Optimized GeoTIFFs).
2. **Standardized JSON Metadata Document** (`{scene_id}_metadata.json`).

### 3.1 JSON Schema Specification (`marineshield.sar.v1`)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "MarineShieldSARSceneMetadata",
  "type": "object",
  "required": [
    "contract_version",
    "scene_identifier",
    "product_metadata",
    "acquisition_time",
    "sensor_specification",
    "polarization",
    "spatial_reference",
    "processing_status",
    "preprocessing_pipeline",
    "provenance",
    "raster_files"
  ],
  "properties": {
    "contract_version": {
      "type": "string",
      "enum": ["1.0.0"]
    },
    "scene_identifier": {
      "type": "object",
      "required": [
        "granule_id",
        "mission",
        "acquisition_mode",
        "product_type",
        "orbit_direction",
        "relative_orbit_number",
        "absolute_orbit_number"
      ],
      "properties": {
        "granule_id": { "type": "string", "example": "S1A_IW_GRDH_1SDV_20240115T053000_20240115T053025_052110_064D3F_A89B" },
        "mission": { "type": "string", "enum": ["SENTINEL_1A", "SENTINEL_1B", "SENTINEL_1C"] },
        "acquisition_mode": { "type": "string", "enum": ["IW", "EW", "SM"] },
        "product_type": { "type": "string", "enum": ["GRD", "SLC"] },
        "orbit_direction": { "type": "string", "enum": ["ASCENDING", "DESCENDING"] },
        "relative_orbit_number": { "type": "integer", "minimum": 1, "maximum": 175 },
        "absolute_orbit_number": { "type": "integer", "minimum": 1 }
      }
    },
    "product_metadata": {
      "type": "object",
      "required": [
        "product_level",
        "instrument_configuration_id",
        "look_direction",
        "incidence_angle_min_deg",
        "incidence_angle_max_deg",
        "slice_number",
        "total_slices"
      ],
      "properties": {
        "product_level": { "type": "string", "enum": ["L1", "L2"] },
        "instrument_configuration_id": { "type": "string" },
        "look_direction": { "type": "string", "enum": ["RIGHT", "LEFT"] },
        "incidence_angle_min_deg": { "type": "number", "minimum": 15.0, "maximum": 55.0 },
        "incidence_angle_max_deg": { "type": "number", "minimum": 15.0, "maximum": 55.0 },
        "slice_number": { "type": "integer", "minimum": 0 },
        "total_slices": { "type": "integer", "minimum": 0 }
      }
    },
    "acquisition_time": {
      "type": "object",
      "required": ["start_time", "stop_time", "center_time", "duration_seconds"],
      "properties": {
        "start_time": { "type": "string", "format": "date-time", "example": "2024-01-15T05:30:00.000Z" },
        "stop_time": { "type": "string", "format": "date-time", "example": "2024-01-15T05:30:25.000Z" },
        "center_time": { "type": "string", "format": "date-time", "example": "2024-01-15T05:30:12.500Z" },
        "duration_seconds": { "type": "number", "minimum": 0.0 }
      }
    },
    "sensor_specification": {
      "type": "object",
      "required": ["sensor_name", "radar_band", "center_frequency_ghz", "antenna_pointing"],
      "properties": {
        "sensor_name": { "type": "string", "enum": ["C-SAR"] },
        "radar_band": { "type": "string", "enum": ["C_BAND"] },
        "center_frequency_ghz": { "type": "number", "enum": [5.405] },
        "antenna_pointing": { "type": "string", "enum": ["RIGHT"] }
      }
    },
    "polarization": {
      "type": "object",
      "required": ["channels", "primary_detection_channel", "vessel_detection_channel"],
      "properties": {
        "channels": {
          "type": "array",
          "items": { "type": "string", "enum": ["VV", "VH", "HH", "HV"] },
          "minItems": 1
        },
        "primary_detection_channel": { "type": "string", "enum": ["VV", "HH"] },
        "vessel_detection_channel": { "type": "string", "enum": ["VH", "HV"] }
      }
    },
    "spatial_reference": {
      "type": "object",
      "required": [
        "crs",
        "bbox_wgs84",
        "footprint_geojson",
        "pixel_spacing_range_m",
        "pixel_spacing_azimuth_m",
        "raster_width_px",
        "raster_height_px",
        "nodata_value"
      ],
      "properties": {
        "crs": { "type": "string", "enum": ["EPSG:4326"] },
        "bbox_wgs84": {
          "type": "array",
          "items": { "type": "number" },
          "minItems": 4,
          "maxItems": 4,
          "description": "[min_lon, min_lat, max_lon, max_lat]"
        },
        "footprint_geojson": {
          "type": "object",
          "description": "GeoJSON Polygon or MultiPolygon in EPSG:4326"
        },
        "pixel_spacing_range_m": { "type": "number", "example": 10.0 },
        "pixel_spacing_azimuth_m": { "type": "number", "example": 10.0 },
        "raster_width_px": { "type": "integer", "minimum": 1 },
        "raster_height_px": { "type": "integer", "minimum": 1 },
        "nodata_value": { "type": "number", "example": -9999.0 }
      }
    },
    "processing_status": {
      "type": "object",
      "required": ["state", "error_code", "error_message", "stage_timestamps"],
      "properties": {
        "state": {
          "type": "string",
          "enum": [
            "PENDING",
            "ACQUIRED",
            "ORBIT_APPLIED",
            "CALIBRATED",
            "SPECKLE_FILTERED",
            "TERRAIN_CORRECTED",
            "TILED",
            "READY_FOR_INFERENCE",
            "FAILED",
            "CORRUPTED"
          ]
        },
        "error_code": { "type": ["string", "null"] },
        "error_message": { "type": ["string", "null"] },
        "stage_timestamps": {
          "type": "object",
          "additionalProperties": { "type": "string", "format": "date-time" }
        }
      }
    },
    "preprocessing_pipeline": {
      "type": "object",
      "required": [
        "pipeline_version",
        "calibration_model",
        "orbit_file_type",
        "speckle_filter",
        "dem_source",
        "toolchain_manifest"
      ],
      "properties": {
        "pipeline_version": { "type": "string", "example": "1.0.0" },
        "calibration_model": { "type": "string", "enum": ["RADIOMETRIC_SIGMA0_DB", "RADIOMETRIC_GAMMA0_DB", "RADIOMETRIC_BETA0_DB"] },
        "orbit_file_type": { "type": "string", "enum": ["PRECISE_ORBIT_EPHEMERIDES_POEORB", "RESTITUTED_ORBIT_RESORB", "HEADER_ORBIT"] },
        "speckle_filter": {
          "type": "object",
          "required": ["algorithm", "window_size_px"],
          "properties": {
            "algorithm": { "type": "string", "enum": ["REFINED_LEE", "LEE", "FROST", "GAMMA_MAP", "NONE"] },
            "window_size_px": { "type": "string", "example": "7x7" }
          }
        },
        "dem_source": { "type": "string", "enum": ["COPERNICUS_30M_GLO30", "SRTM_1SEC_HGT", "AUTO_DEM"] },
        "toolchain_manifest": {
          "type": "object",
          "additionalProperties": { "type": "string" }
        }
      }
    },
    "provenance": {
      "type": "object",
      "required": [
        "data_provider",
        "source_archive_url",
        "source_granule_sha256",
        "ingestion_timestamp",
        "execution_duration_seconds",
        "worker_node_id",
        "checksum_verified"
      ],
      "properties": {
        "data_provider": { "type": "string", "enum": ["COPERNICUS_DATA_SPACE_ECOSYSTEM", "ALASKA_SATELLITE_FACILITY", "LOCAL_ARCHIVE", "MOCK_SIMULATOR"] },
        "source_archive_url": { "type": "string" },
        "source_granule_sha256": { "type": "string", "pattern": "^[a-fA-F0-9]{64}$" },
        "ingestion_timestamp": { "type": "string", "format": "date-time" },
        "execution_duration_seconds": { "type": "number", "minimum": 0.0 },
        "worker_node_id": { "type": "string" },
        "checksum_verified": { "type": "boolean" }
      }
    },
    "raster_files": {
      "type": "object",
      "required": ["vv_geotiff_path", "vh_geotiff_path"],
      "properties": {
        "vv_geotiff_path": { "type": "string" },
        "vh_geotiff_path": { "type": "string" },
        "incidence_angle_path": { "type": ["string", "null"] },
        "tiled_dir_path": { "type": ["string", "null"] }
      }
    }
  }
}
```

---

## 4. Field-by-Field Technical Specification

### 4.1 `scene_identifier`
- **`granule_id`** *(string, Required)*: The complete, unique Sentinel-1 SAFE granule name adhering to ESA naming convention:
  `MMM_BB_TTTF_LFPP_YYYYMMDDTHHMMSS_YYYYMMDDTHHMMSS_OOOOOO_DDDDDD_CCCC`
- **`mission`** *(enum, Required)*: Satellite platform (`SENTINEL_1A`, `SENTINEL_1B`, or `SENTINEL_1C`).
- **`acquisition_mode`** *(enum, Required)*: SAR sensor beam mode. MarineShield primarily utilizes `IW` (Interferometric Wide Swath, 250km swath).
- **`product_type`** *(enum, Required)*: Ground Range Detected (`GRD`) or Single Look Complex (`SLC`).
- **`orbit_direction`** *(enum, Required)*: Satellite track direction (`ASCENDING` for South-to-North, `DESCENDING` for North-to-South). Vital for determining look direction and wind-vector relative geometry.
- **`relative_orbit_number`** *(integer, Required)*: Repeat track cycle index ($1 - 175$).
- **`absolute_orbit_number`** *(integer, Required)*: Total orbit revolutions since launch.

### 4.2 `product_metadata`
- **`product_level`** *(enum, Required)*: Processing level (`L1` for standard calibrated products).
- **`instrument_configuration_id`** *(string, Required)*: Sentinel-1 instrument mode configuration counter.
- **`look_direction`** *(enum, Required)*: Radar antenna look direction relative to orbit track (`RIGHT` for standard operations).
- **`incidence_angle_min_deg` & `incidence_angle_max_deg`** *(float, Required)*: Range of incidence angles across near-range to far-range (typically $29.1^\circ$ to $46.0^\circ$ for IW).
- **`slice_number` & `total_slices`** *(integer, Required)*: Slice index within the complete datatake pass.

### 4.3 `acquisition_time`
- **`start_time`** *(ISO 8601 UTC, Required)*: Timestamp of the first zero-Doppler azimuth line.
- **`stop_time`** *(ISO 8601 UTC, Required)*: Timestamp of the final azimuth line.
- **`center_time`** *(ISO 8601 UTC, Required)*: Scene midpoint timestamp ($t_{obs}$), used as the primary reference epoch for AIS trajectory matching and backward/forward PyGNOME drift modeling.
- **`duration_seconds`** *(float, Required)*: Total scene acquisition duration ($\approx 25.0\text{ s}$ for standard IW slices).

### 4.4 `sensor_specification`
- **`sensor_name`** *(string, Required)*: `C-SAR`.
- **`radar_band`** *(string, Required)*: `C_BAND`.
- **`center_frequency_ghz`** *(float, Required)*: $5.405\text{ GHz}$ ($\lambda \approx 5.546\text{ cm}$).
- **`antenna_pointing`** *(string, Required)*: `RIGHT`.

### 4.5 `polarization`
- **`channels`** *(list of string, Required)*: List of polarimetric channels included (e.g. `["VV", "VH"]`).
- **`primary_detection_channel`** *(string, Required)*: `VV`. Preferred for dark-spot segmentation because co-polarized backscatter has higher sea-clutter return, maximizing contrast between oil-damped water and clean sea surface.
- **`vessel_detection_channel`** *(string, Required)*: `VH`. Cross-polarized channel exhibits low sea clutter, maximizing Signal-to-Clutter Ratio (SCR) for metallic vessel structures.

### 4.6 `spatial_reference`
- **`crs`** *(string, Required)*: `EPSG:4326`.
- **`bbox_wgs84`** *(list of 4 floats, Required)*: Geographic bounding box `[min_lon, min_lat, max_lon, max_lat]`.
- **`footprint_geojson`** *(GeoJSON Polygon, Required)*: Closed 4-point or multi-point polygon tracing the exact geographic boundary of the calibrated valid image data.
- **`pixel_spacing_range_m` & `pixel_spacing_azimuth_m`** *(float, Required)*: Orthorectified ground resolution ($10.0\text{ m} \times 10.0\text{ m}$).
- **`raster_width_px` & `raster_height_px`** *(integer, Required)*: Array dimensions of the output GeoTIFFs.
- **`nodata_value`** *(float, Required)*: Constant value indicating non-ocean or masked pixels (`-9999.0`).

### 4.7 `processing_status`
- **`state`** *(enum, Required)*: Explicit state machine tracking the granule through the Person 2 preprocessing lifecycle:
  ```
  PENDING
    │
    ▼
  ACQUIRED (Raw SAFE granule downloaded & checksum verified)
    │
    ▼
  ORBIT_APPLIED (Precise Orbit Ephemerides applied)
    │
    ▼
  CALIBRATED (Radiometric calibration to sigma0 dB)
    │
    ▼
  SPECKLE_FILTERED (Refined Lee / Lee filter applied)
    │
    ▼
  TERRAIN_CORRECTED (Range-Doppler orthorectification to EPSG:4326)
    │
    ▼
  TILED (Optional ML tile pyramid generated)
    │
    ▼
  READY_FOR_INFERENCE (Delivered to Person 1 ML pipeline)
  ```
  - `FAILED`: Preprocessing error encountered (details in `error_message`).
  - `CORRUPTED`: Granule integrity check or checksum failed.
- **`error_code`** *(string or null)*: Standardized error identifier (`ERR_ORBIT_UNAVAILABLE`, `ERR_CORRUPT_TIFF`, `ERR_CALIBRATION_OVERFLOW`, `ERR_INVALID_CRS`).
- **`stage_timestamps`** *(dict)*: ISO 8601 timestamps recording the completion of each lifecycle transition.

### 4.8 `preprocessing_pipeline`
- **`pipeline_version`** *(string, Required)*: Semantic version of the MarineShield preprocessing module (`1.0.0`).
- **`calibration_model`** *(enum, Required)*: `RADIOMETRIC_SIGMA0_DB` ($\sigma^0\text{ dB}$).
- **`orbit_file_type`** *(enum, Required)*: `PRECISE_ORBIT_EPHEMERIDES_POEORB` (most accurate, 20-day latency) or `RESTITUTED_ORBIT_RESORB` (fast operational, <3 hour latency).
- **`speckle_filter`** *(object, Required)*: Algorithm (`REFINED_LEE`, `LEE`, `FROST`, `NONE`) and spatial window size (e.g. `7x7` pixels).
- **`dem_source`** *(enum, Required)*: Digital Elevation Model used for Range-Doppler terrain correction (`COPERNICUS_30M_GLO30`).
- **`toolchain_manifest`** *(dict, Required)*: Exact versions of underlying software (e.g. `{"esa_snap": "9.0.0", "gdal": "3.8.4", "rasterio": "1.3.9"}`).

### 4.9 `provenance`
- **`data_provider`** *(enum, Required)*: Origin service (`COPERNICUS_DATA_SPACE_ECOSYSTEM`, `ALASKA_SATELLITE_FACILITY`, `LOCAL_ARCHIVE`, `MOCK_SIMULATOR`).
- **`source_archive_url`** *(string, Required)*: Full URI from which the raw data package was acquired.
- **`source_granule_sha256`** *(string, Required)*: SHA-256 cryptographic hash of the original input SAFE `.zip` / archive.
- **`ingestion_timestamp`** *(ISO 8601 UTC, Required)*: Exact time when the scene entered the MarineShield system.
- **`execution_duration_seconds`** *(float, Required)*: Preprocessing runtime in seconds.
- **`worker_node_id`** *(string, Required)*: Identifier of the background Celery/Ray worker that performed the preprocessing.
- **`checksum_verified`** *(boolean, Required)*: Must be `true` before inference handoff.

### 4.10 `raster_files`
- **`vv_geotiff_path`** *(string, Required)*: Relative or absolute file path to the calibrated `VV` GeoTIFF raster.
- **`vh_geotiff_path`** *(string, Required)*: Relative or absolute file path to the calibrated `VH` GeoTIFF raster.
- **`incidence_angle_path`** *(string or null)*: Path to optional incidence angle raster.
- **`tiled_dir_path`** *(string or null)*: Path to pre-generated $512 \times 512$ ML tile cache.

---

## 5. Standard Filesystem Layout & Naming Conventions

All preprocessed SAR assets generated by **Person 2** MUST be organized under the standard directory hierarchy:

```
data/sar_preprocessed/
└── {granule_id}/
    ├── {granule_id}_metadata.json       <-- Canonical JSON Contract Document
    ├── {granule_id}_VV_sigma0_db.tif     <-- Calibrated VV GeoTIFF (Float32, EPSG:4326)
    ├── {granule_id}_VH_sigma0_db.tif     <-- Calibrated VH GeoTIFF (Float32, EPSG:4326)
    ├── {granule_id}_inc_angle.tif       <-- (Optional) Incidence Angle GeoTIFF
    └── tiles_512/                       <-- (Optional) ML Inference Tiles
        ├── tile_000_000.npy
        ├── tile_000_001.npy
        └── tiles_index.geojson
```

---

## 6. Sample Canonical Metadata Document

```json
{
  "contract_version": "1.0.0",
  "scene_identifier": {
    "granule_id": "S1A_IW_GRDH_1SDV_20240115T053000_20240115T053025_052110_064D3F_A89B",
    "mission": "SENTINEL_1A",
    "acquisition_mode": "IW",
    "product_type": "GRD",
    "orbit_direction": "DESCENDING",
    "relative_orbit_number": 45,
    "absolute_orbit_number": 52110
  },
  "product_metadata": {
    "product_level": "L1",
    "instrument_configuration_id": "1",
    "look_direction": "RIGHT",
    "incidence_angle_min_deg": 30.5,
    "incidence_angle_max_deg": 46.2,
    "slice_number": 4,
    "total_slices": 8
  },
  "acquisition_time": {
    "start_time": "2024-01-15T05:30:00.000Z",
    "stop_time": "2024-01-15T05:30:25.000Z",
    "center_time": "2024-01-15T05:30:12.500Z",
    "duration_seconds": 25.0
  },
  "sensor_specification": {
    "sensor_name": "C-SAR",
    "radar_band": "C_BAND",
    "center_frequency_ghz": 5.405,
    "antenna_pointing": "RIGHT"
  },
  "polarization": {
    "channels": ["VV", "VH"],
    "primary_detection_channel": "VV",
    "vessel_detection_channel": "VH"
  },
  "spatial_reference": {
    "crs": "EPSG:4326",
    "bbox_wgs84": [72.50, 18.20, 75.10, 20.10],
    "footprint_geojson": {
      "type": "Polygon",
      "coordinates": [
        [
          [72.50, 18.20],
          [75.10, 18.20],
          [75.10, 20.10],
          [72.50, 20.10],
          [72.50, 18.20]
        ]
      ]
    },
    "pixel_spacing_range_m": 10.0,
    "pixel_spacing_azimuth_m": 10.0,
    "raster_width_px": 25000,
    "raster_height_px": 16500,
    "nodata_value": -9999.0
  },
  "processing_status": {
    "state": "READY_FOR_INFERENCE",
    "error_code": null,
    "error_message": null,
    "stage_timestamps": {
      "ACQUIRED": "2024-01-15T06:05:00.000Z",
      "ORBIT_APPLIED": "2024-01-15T06:08:12.000Z",
      "CALIBRATED": "2024-01-15T06:12:45.000Z",
      "SPECKLE_FILTERED": "2024-01-15T06:18:30.000Z",
      "TERRAIN_CORRECTED": "2024-01-15T06:24:10.000Z",
      "READY_FOR_INFERENCE": "2024-01-15T06:25:00.000Z"
    }
  },
  "preprocessing_pipeline": {
    "pipeline_version": "1.0.0",
    "calibration_model": "RADIOMETRIC_SIGMA0_DB",
    "orbit_file_type": "PRECISE_ORBIT_EPHEMERIDES_POEORB",
    "speckle_filter": {
      "algorithm": "REFINED_LEE",
      "window_size_px": "7x7"
    },
    "dem_source": "COPERNICUS_30M_GLO30",
    "toolchain_manifest": {
      "esa_snap": "9.0.0",
      "gdal": "3.8.4",
      "rasterio": "1.3.9"
    }
  },
  "provenance": {
    "data_provider": "COPERNICUS_DATA_SPACE_ECOSYSTEM",
    "source_archive_url": "https://catalogue.dataspace.copernicus.eu/odata/v1/Products(12345678-abcd-ef01-2345-6789abcdef01)/$value",
    "source_granule_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "ingestion_timestamp": "2024-01-15T06:02:15.000Z",
    "execution_duration_seconds": 1365.0,
    "worker_node_id": "worker-sar-node-04",
    "checksum_verified": true
  },
  "raster_files": {
    "vv_geotiff_path": "data/sar_preprocessed/S1A_IW_GRDH_1SDV_20240115T053000_20240115T053025_052110_064D3F_A89B/S1A_IW_GRDH_1SDV_20240115T053000_20240115T053025_052110_064D3F_A89B_VV_sigma0_db.tif",
    "vh_geotiff_path": "data/sar_preprocessed/S1A_IW_GRDH_1SDV_20240115T053000_20240115T053025_052110_064D3F_A89B/S1A_IW_GRDH_1SDV_20240115T053000_20240115T053025_052110_064D3F_A89B_VH_sigma0_db.tif",
    "incidence_angle_path": null,
    "tiled_dir_path": null
  }
}
```

---

## 7. Contract Verification & Quality Gate Checklist

Before delivering preprocessed SAR rasters to Person 1 for segmentation or detection, the automated pipeline MUST verify:

1. **Schema Conformance**: JSON metadata passes 100% against the schema defined in Section 3.1.
2. **File Existence & Integrity**: `vv_geotiff_path` and `vh_geotiff_path` exist on disk, are valid GeoTIFF format, and match `raster_width_px` $\times$ `raster_height_px`.
3. **GeoTIFF Spatial Tags**: Coordinate System is explicitly tagged as `EPSG:4326` with valid affine geotransform matching `bbox_wgs84`.
4. **Data Range Audit**: Calibrated $\sigma^0\text{ dB}$ pixel values fall predominantly within valid maritime range $[-40.0\text{ dB}, +10.0\text{ dB}]$, with no unexpected infs or invalid zeros.
5. **State Gate**: `processing_status.state` is strictly `READY_FOR_INFERENCE`.
