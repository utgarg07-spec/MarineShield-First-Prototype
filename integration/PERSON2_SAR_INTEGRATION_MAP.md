# MarineShield — Person 2 Member 1 SAR Integration Map

**Document Generation Date:** 2026-08-21  
**Author:** MarineShield Integration Auditor  
**Domain:** Sentinel-1 Satellite SAR Ingestion & Preprocessing $\to$ Person 1 Oil Intelligence Pipeline  

---

## 1. End-to-End Pipeline Overview

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                     MEMBER 1 (PERSON 2)                                          │
│                                                                                                  │
│   Sentinel-1 SAFE Granule ──► SAR Preprocessing ──► Calibrated Array ──► ML-Ready Tile & Sidecar │
└────────────────────────────────────────────────┬─────────────────────────────────────────────────┘
                                                 │
                                                 ▼ (Handoff Boundary)
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                     MEMBER 2 (PERSON 1)                                          │
│                                                                                                  │
│   Tile Input ──► Adapted SAM Inference ──► Binary Spill Mask ──► Topological Geometry Extractor │
│                                                                                 │                │
│   Canonical SpillDetectionResponse ◄── Severity & Abstention Gating ◄───────────┘                │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Step-by-Step Integration Mapping

---

### Step 1: Sentinel-1 SAFE Archive $\to$ SAR Preprocessing

```
[Sentinel-1 SAFE Archive] ────► [SAR Preprocessor (sar_preprocessor.py)]
```

- **Producer:** Copernicus Data Space Ecosystem (CDSE) / Member 1 Acquisition (`response_of_person2_member1/copernicus_client.py`).
- **Consumer:** Member 1 Preprocessor (`response_of_person2_member1/sar_preprocessor.py`).
- **Input Format:** Standard ESA Sentinel-1 Level-1 GRD SAFE directory (`manifest.safe`, measurement TIFFs).
- **Output Format:** Radiometrically calibrated, speckle-filtered, terrain-corrected NumPy multi-band array $\sigma^0$ in decibels ($\text{dB}$).
- **Exact Fields Produced:**
  - Array shape: $(2, H, W)$ where Band 0 = `VV`, Band 1 = `VH`.
  - Values: `float32`, dynamic range typically $[-35.0\text{ dB}, +5.0\text{ dB}]$.
  - NoData value: `-9999.0`.
- **Transformations Required:**
  1. Radiometric calibration: $\sigma^0_{\text{linear}} = \frac{DN^2}{A_i^2}$, $\sigma^0_{\text{dB}} = 10 \log_{10}(\sigma^0_{\text{linear}})$.
  2. Speckle suppression: Refined Lee Filter ($7 \times 7$ window).
  3. Geocoding / Orthorectification to `EPSG:4326` using Copernicus 30m GLO-30 DEM.
- **Validation Required:**
  - Verify backscatter range does not contain infinite or non-numeric float values.
  - Verify footprint boundary coordinates match SAFE manifest corner coordinates.
- **Test Proving Compatibility:** `response_of_person2_member1/verify_phase3_member1.py::test_metadata_extraction`.
- **Unresolved Issue:** Raw SNAP / GDAL engine dependency: In production, GDAL/Rasterio C-bindings must be installed in the server environment.

---

### Step 2: Calibrated Array $\to$ ML-Ready Tiles & Sidecars

```
[Calibrated Array (sar_preprocessor.py)] ────► [Deterministic Tiler (tiler.py)]
```

- **Producer:** Member 1 Preprocessor (`sar_preprocessor.py`).
- **Consumer:** Member 1 Tiler Engine (`response_of_person2_member1/tiler.py`).
- **Input Format:** In-memory $(2, H, W)$ NumPy array with scene bounding box `[min_lon, min_lat, max_lon, max_lat]`.
- **Output Format:**
  1. Serialized NumPy binary tile: `{tile_id}.npy` (Shape: `(2, 512, 512)`, dtype: `float32`, range: `[0.0, 1.0]`).
  2. JSON metadata sidecar: `{tile_id}_metadata.json` (conforming to `marineshield.sar.v1`).
  3. Scene manifest: `tile_manifest.json`.
- **Exact Fields in Metadata Sidecar:**
  - `tile_id`: Unique identifier string.
  - `source_granule_id`: Parent Sentinel-1 granule UUID.
  - `tile_row`, `tile_col`: Grid indices.
  - `pixel_bounds_yx`: `[y_start, y_end, x_start, x_end]`.
  - `geo_bbox_wgs84`: `[min_lon, min_lat, max_lon, max_lat]` in `EPSG:4326`.
  - `spatial_resolution_m`: `[10.0, 10.0]`.
  - `tile_dimensions_px`: `[512, 512]`.
  - `crs`: `"EPSG:4326"`.
  - `channels`: `["VV", "VH"]`.
  - `normalization`: Formula and clipping bounds (`min_db: -30.0, max_db: 0.0, clip_min: 0.0, clip_max: 1.0`).
  - `split`: `"train"` or `"val"` (quadrant partitioned).
  - `sha256_hash`: 64-character SHA-256 cryptographic hash of array bytes.
- **Transformations Required:**
  1. Window slicing with stride (default: 512px).
  2. Normalization: $I_{\text{norm}} = \text{clip}\left(\frac{\sigma^0 - (-30.0)}{0.0 - (-30.0)}, 0.0, 1.0\right)$.
  3. Padding border tiles to exact $512 \times 512$.
- **Validation Required:**
  - Ensure zero data leakage between train/val splits.
  - Ensure SHA-256 hash matches array bytes exactly.
- **Test Proving Compatibility:** `response_of_person2_member1/test_sar_tiling.py`.
- **Unresolved Issue:** None. Tiling engine is fully deterministic.

---

### Step 3: ML Tile & Sidecar $\to$ Person 1 Oil Intelligence Service

```
[ML Tile .npy + Sidecar (Member 1)] ────► [OilIntelligenceService (marineshield.oil_intelligence)]
```

- **Producer:** Member 1 Tiler (`tiler.py`).
- **Consumer:** Person 1 Oil Intelligence Service (`marineshield/oil_intelligence/service.py`).
- **Input Format:** Path to `.npy` array (or in-memory tensor) and metadata sidecar dictionary.
- **Output Format:** Internal standardized PyTorch tensor `(1, 3, 1024, 1024)` prepared for SAM ViT image encoder.
- **Exact Fields Consumed:**
  - `tile_id`, `source_granule_id`, `geo_bbox_wgs84`, `channels`, `spatial_resolution_m`.
- **Transformations Required:**
  1. Channel replication / adaptation: Expand 2-channel SAR `[VV, VH]` into adapted 3-channel input tensor via `marineshield.oil_intelligence.preprocessing.SARTilePreprocessor`.
  2. Interpolation / Resize: Bilinear upsampling from $512 \times 512$ to SAM native $1024 \times 1024$ resolution.
  3. Standardization: Apply ImageNet / SAM normalization parameters.
- **Validation Required:**
  - Verify tensor dimensions $(1, 3, 1024, 1024)$ on target compute device (`cuda` or `cpu`).
  - Validate that bounding box georeferencing is preserved across scaling.
- **Test Proving Compatibility:** `tests/unit/test_oil_intelligence_service.py::test_valid_oil_candidate`.
- **Unresolved Issue:** Bounding box coordinate transformation between $512 \times 512$ tile space and $1024 \times 1024$ model input tensor must use exact scale factor ($\times 2.0$).

---

### Step 4: Adapted SAM Inference $\to$ Binary Spill Mask

```
[Adapted SAM (marineshield.models.sam_adapter)] ────► [Binary Spill Mask Tensor]
```

- **Producer:** Person 1 Adapted SAM Model (`marineshield/models/sam_adapter.py`).
- **Consumer:** Person 1 Geometry Extractor (`marineshield/oil_intelligence/geometry_extractor.py`).
- **Input Format:** Encoded image embeddings + prompt bounding box.
- **Output Format:** Binary classification mask $(1024, 1024)$ where $1 = \text{Oil Candidate}, 0 = \text{Clean Sea/Look-alike}$.
- **Exact Fields Produced:**
  - `mask_array`: Binary 2D array.
  - `mean_oil_probability`: Float ($0.0-1.0$).
  - `pixel_coverage_fraction`: Float ($0.0-1.0$).
- **Transformations Required:**
  1. Sigmoid activation on raw logits: $P(\text{oil}) = \sigma(\text{logits})$.
  2. Thresholding at $0.50$.
  3. Downsampling / Rescaling binary mask back to original tile grid ($512 \times 512$).
- **Validation Required:**
  - False positive rejection: Ensure look-alike signatures (calm water, ship wakes) produce $0$ positive pixels after adapter inference.
- **Test Proving Compatibility:** `tests/unit/test_sam_adaptation_experiment.py::test_lookalike_false_positive_elimination`.
- **Unresolved Issue:** None.

---

### Step 5: Binary Mask $\to$ Topological Geometry Extractor

```
[Binary Mask (512x512)] ────► [GeometryExtractor (geometry_extractor.py)]
```

- **Producer:** Binary classification mask.
- **Consumer:** Pure-NumPy Geometry Extractor (`marineshield/oil_intelligence/geometry_extractor.py`).
- **Input Format:** Binary 2D mask array $(512, 512)$ and tile geographic bounding box `[min_lon, min_lat, max_lon, max_lat]`.
- **Output Format:** Standardized GeoJSON `Feature` (`Polygon`, `EPSG:4326`) and geometric morphometry metrics.
- **Exact Fields Produced:**
  - `area_km2`: Polygon surface area in square kilometers.
  - `perimeter_km`: Boundary perimeter in kilometers.
  - `centroid_lon`, `centroid_lat`: Geographic center of mass (`EPSG:4326`).
  - `orientation_deg`: Primary orientation angle $[0^\circ, 180^\circ]$.
  - `elongation_ratio`: Major axis / minor axis ratio.
  - `fragmentation_index`: Connected component count and dispersion index.
  - `bounding_box`: `[min_lon, min_lat, max_lon, max_lat]`.
- **Transformations Required:**
  1. 8-connected topological component labeling.
  2. Boundary contour extraction in pixel coordinates.
  3. Geodetic coordinate transformation from pixel $(x, y)$ to $(lon, lat)$ using affine transform from tile sidecar.
  4. Metric area calculation using Haversine / WGS84 geodesic polygon integration.
- **Validation Required:**
  - Ensure GeoJSON polygon is strictly closed (first coordinate equals last coordinate).
  - Verify coordinate order is strictly `[longitude, latitude]`.
- **Test Proving Compatibility:** `tests/unit/test_oil_intelligence_service.py::test_valid_oil_candidate`.
- **Unresolved Issue:** Multi-part s協力: If multiple fragmented slicks exist in one tile, geometry extractor must output a GeoJSON `MultiPolygon` or list of discrete polygon features.

---

### Step 6: Geometry & Metrics $\to$ Canonical SpillDetectionResponse

```
[Geometry + Look-Alike Verification + Severity] ────► [Canonical SpillDetectionResponse]
```

- **Producer:** Person 1 `OilIntelligenceService` (`marineshield/oil_intelligence/service.py`).
- **Consumer:** Downstream FastAPI Endpoints (`/api/v1/detection`), Source Attribution Engine (Member 4), and WebGIS Frontend (Person 4).
- **Input Format:** Component outputs from segmentation, look-alike verification, and severity classifiers.
- **Output Format:** Canonical `SpillDetectionResponse` envelope conforming to `docs/ml/OIL_INTELLIGENCE_CONTRACTS.md`.
- **Exact Fields in Payload:**
  - `detection_id`, `incident_id`, `status` (`SUCCESS` / `ABSTAINED`).
  - `mask`: `SpillMaskContract` (§1).
  - `geometry`: `SpillGeometryContract` (§7).
  - `lookalike_verification`: `LookAlikeVerificationContract` (§6).
  - `severity`: `SpillSeverityContract` (§5).
  - `data_quality`: `DataQualityIndex` (§11).
  - `provenance`: `ProvenanceBlock` (§9).
  - `abstention`: `AbstentionDetails` (§10).
- **Transformations Required:** Serialization to standard ISO 8601 UTC JSON.
- **Validation Required:** All fields must validate against canonical Pydantic/dataclass schema definitions.
- **Test Proving Compatibility:** `tests/integration/test_oil_intelligence_integration.py`.
- **Unresolved Issue:** None.
