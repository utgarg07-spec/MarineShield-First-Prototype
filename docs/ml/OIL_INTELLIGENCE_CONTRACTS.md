# MarineShield — Canonical ML Output Contracts
## Oil-Intelligence Subsystem (Member 2 / Person 1)

**Owner**: Person 1 / Member 2  
**Modules Covered**: Module B (Oil Segmentation), Module C (Look-Alike Rejection), Module D (Spill Severity), Module E (SAR Vessel Detection)  
**Status**: `CANONICAL — DO NOT MODIFY WITHOUT RECORDED ARCHITECTURAL DECISION`  
**Document Version**: `1.0.0`  
**Created**: `2026-08-20T10:09:00Z`  
**Governed By**: [`docs/architecture/ARCHITECTURE.md`](file:///d:/MarineShield/MarineShield/docs/architecture/ARCHITECTURE.md), [`.agents/rules/agent_core.md`](file:///d:/MarineShield/MarineShield/.agents/rules/agent_core.md), [`.agents/rules/api_contracts.md`](file:///d:/MarineShield/MarineShield/.agents/rules/api_contracts.md)

---

## CRITICAL CONTRACT PREAMBLE

This document defines the **canonical output schemas** for all ML pipeline outputs produced by Member 2 (Person 1). These schemas govern what is consumed by:

- **Member 4 (Person 1)** — Release Estimation & Evidence Engine
- **Member 3 (Person 2)** — AIS–SAR Reconciliation (SAR Vessel Detection outputs)
- **Member 5 / Member 6 Backend (Person 3)** — Forecasting & Response Priority Engine (via FastAPI)

### Mandatory Separation of Four Distinct Uncertainty Types

> **NO schema field, API payload, or downstream consumer may conflate these four distinct concepts.**

| Concept | Definition | Owner | Field Prefix |
|:---|:---|:---|:---|
| **Model Confidence** | Empirical probability from ML model output (softmax or sigmoid). Represents the model's internal statistical certainty about a prediction given the input. **Does NOT imply real-world correctness.** | Member 2 (ML Inference) | `model_confidence.*` |
| **Data Quality Index** | Measured quality metrics of the input SAR scene or environmental data (noise floor, incidence angle, cloud-equivalent flags, AIS coverage completeness). Independent of model output. | Member 2 (Preprocessing) | `data_quality.*` |
| **Evidence Strength** | Member 4's weighted multi-modal evidence score `E(H)` combining spatial, temporal, trajectory, drift, vessel, and behavioral evidence against a candidate hypothesis. Entirely computed **downstream** of Member 2 outputs. | Member 4 (Evidence Engine) | `evidence.*` |
| **Forecast Uncertainty** | PyGNOME ensemble spatial spread (km²) representing oceanographic and meteorological variability in trajectory predictions. | Member 5 (Drift) | `forecast_uncertainty.*` |

**Violation of this separation is an architectural error. Any PR conflating them must be rejected.**

---

## §1 — Spill Mask Contract

### 1.1 Definition

A **spill mask** is a per-tile floating-point array representing the model's pixel-wise oil probability output for a single 512×512 input tile. It is the direct sigmoid/softmax output of the segmentation model **before any thresholding**.

### 1.2 Schema

```json
{
  "mask_id": "string (UUID v4) — unique identifier for this mask artifact",
  "incident_id": "string (UUID v4) — parent incident this mask belongs to",
  "tile_id": "string — tile identifier within the parent SAR scene (e.g. 'T_R003_C007')",
  "sar_granule_id": "string — Copernicus/GFW granule ID (e.g. 'S1A_IW_GRDH_...')",
  "mask_type": "PROBABILITY | BINARY",
  "mask_storage_uri": "string — cloud storage URI (S3/MinIO) of the GeoTIFF raster file",
  "tile_size_px": 512,
  "tile_crs": "EPSG:4326",
  "tile_bounds_geojson": {
    "type": "Polygon",
    "coordinates": [[[lon_min, lat_min], [lon_max, lat_min], [lon_max, lat_max], [lon_min, lat_max], [lon_min, lat_min]]]
  },
  "binarization_threshold": "float [0.0, 1.0] | null — threshold used to produce binary mask. Null for PROBABILITY type",
  "dtype": "float32",
  "value_range": {"min": 0.0, "max": 1.0},
  "nodata_value": -9999.0,
  "model_confidence": {
    "mean_oil_probability": "float [0.0, 1.0] — mean probability over oil-classified pixels",
    "pixel_coverage_fraction": "float [0.0, 1.0] — fraction of tile pixels classified as oil at threshold"
  },
  "data_quality": {
    "index": "float [0.0, 1.0] — composite SAR tile quality score (see §11)",
    "quality_flags": ["string"]
  },
  "provenance": {"$ref": "#section-9-provenance"},
  "created_at_utc": "string (ISO 8601 UTC) — e.g. '2026-08-20T11:41:00Z'"
}
```

### 1.3 Storage Rule

- **Raw raster binary data MUST NOT be stored as a PostgreSQL column.** Store `mask_storage_uri` + bounding GeoJSON only.
- GeoTIFF files are stored in object storage (S3/MinIO).
- PostGIS stores only the spatial footprint for indexing.

### 1.4 Multi-Tile Mask Aggregation

When a SAR scene is processed as multiple tiles, each tile produces an independent `SpillMask`. A scene-level mask is assembled by the pipeline orchestrator after all tiles complete. Scene-level assembly is not Member 2's responsibility.

---

## §2 — Spill Probability & Model Confidence Contract

### 2.1 Definition

**Model confidence** is the model's empirical probability estimate. It is derived directly from ML model output (sigmoid for binary segmentation, softmax for multi-class). It is **not** a quality guarantee. High model confidence on a low-quality input scene does not mean the prediction is reliable.

### 2.2 What Model Confidence Is NOT

| Incorrect Interpretation | Correct Interpretation |
|:---|:---|
| "The spill exists with 94% probability" | "The segmentation model assigned 94% oil probability to these pixels" |
| Evidence of vessel guilt | Input to the Evidence Engine; not itself evidence |
| Legal certainty | Statistical model output only |
| Corrected for data quality | Raw model output; quality correction is separate |

### 2.3 Schema

```json
{
  "segmentation_confidence": {
    "mask_mean_probability": "float [0.0, 1.0] — average oil probability across oil-labelled pixels",
    "mask_max_probability": "float [0.0, 1.0] — maximum pixel oil probability in this mask",
    "high_confidence_pixel_count": "int — pixels with probability >= 0.75",
    "medium_confidence_pixel_count": "int — pixels with probability in [0.5, 0.75)",
    "low_confidence_pixel_count": "int — pixels with probability in [binarization_threshold, 0.5)"
  },
  "lookalike_confidence": {
    "predicted_class": "string — see §6 for valid values",
    "class_probabilities": {
      "PETROLEUM_OIL": "float [0.0, 1.0]",
      "BIOGENIC_SLICK": "float [0.0, 1.0]",
      "LOW_WIND_AREA": "float [0.0, 1.0]",
      "SHIP_WAKE": "float [0.0, 1.0]",
      "NATURAL_FILM": "float [0.0, 1.0]",
      "UNCERTAIN": "float [0.0, 1.0]"
    },
    "max_class_probability": "float [0.0, 1.0] — softmax argmax value",
    "entropy": "float >= 0.0 — Shannon entropy of class probability distribution (higher = less certain)"
  }
}
```

### 2.4 Confidence Calibration Requirement

Model confidence values MUST originate from empirical model outputs. They must not be synthetically scaled, artificially boosted, or replaced by rule-based scores. Any calibration (e.g., temperature scaling) applied post-training must be documented in the model version record (§3).

---

## §3 — Model Version Contract

### 3.1 Definition

Every inference output must be traceable to an exact, reproducible model version. A "model version" is an immutable, versioned artifact record that uniquely identifies the trained weights, architecture, and training configuration used.

### 3.2 Schema

```json
{
  "model_version_id": "string — globally unique ID (e.g. 'unet-resnet50-v1.2.3')",
  "semantic_version": "string — MAJOR.MINOR.PATCH (e.g. '1.2.3')",
  "architecture": {
    "name": "UNET | SEGFORMER | RESNET50 | EFFICIENTNET_B0",
    "backbone": "string (e.g. 'resnet50', 'efficientnet-b0', 'mit-b2') | null",
    "variant_note": "string | null — e.g. 'SegFormer-B2 benchmark candidate'"
  },
  "module": "SEGMENTATION | LOOKALIKE_REJECTION | SEVERITY_CLASSIFICATION | SAR_VESSEL_DETECTION",
  "training_dataset_version_id": "string — references §4 DatasetVersion record",
  "validation_dataset_version_id": "string — references §4 DatasetVersion record (must be disjoint from training)",
  "training_completed_at_utc": "string (ISO 8601 UTC)",
  "inference_framework": "string (e.g. 'torch 2.11.0+cu128')",
  "device": "string (e.g. 'cuda:0 — NVIDIA GeForce RTX 3050 6GB')",
  "calibration_applied": "boolean — true if post-hoc confidence calibration (e.g. temperature scaling) was applied",
  "calibration_method": "string | null — e.g. 'temperature_scaling' | null if not calibrated",
  "hyperparameters": {
    "tile_size_px": 512,
    "input_channels": "int (e.g. 2 for VV+VH dual-pol)",
    "binarization_threshold": "float [0.0, 1.0]",
    "batch_size_inference": "int",
    "normalization_mean": ["float"],
    "normalization_std": ["float"]
  },
  "validation_metrics_summary": {
    "note": "Aggregate validation set performance — references §8 MetricsMetadata record. NOT per-inference metrics."
  },
  "checksum_sha256": "string — SHA-256 hash of model weights file for integrity verification",
  "weights_storage_uri": "string — URI to frozen model weights in object storage",
  "status": "ACTIVE | DEPRECATED | EXPERIMENTAL | BENCHMARK_CANDIDATE",
  "deprecation_reason": "string | null",
  "registered_by": "string (workstream member identifier)",
  "registered_at_utc": "string (ISO 8601 UTC)"
}
```

### 3.3 Versioning Rules

| Version Component | Increment Trigger |
|:---|:---|
| `MAJOR` | Architecture change (e.g. U-Net → SegFormer), input schema change, incompatible output format change |
| `MINOR` | New training dataset version, significant hyperparameter change, re-calibration |
| `PATCH` | Bug fix to inference pipeline, minor postprocessing change, updated normalization stats |

### 3.4 Exactly One ACTIVE Model Per Module

At any time, exactly one model version per module may have `status: ACTIVE`. All other versions must be `DEPRECATED` or `BENCHMARK_CANDIDATE`. Benchmark candidates must not be used for production inference without explicit architectural decision record in `DECISION_LOG.md`.

---

## §4 — Dataset Version Contract

### 4.1 Definition

A dataset version is an immutable, versioned record of a specific training or evaluation split. Dataset versions are referenced by model versions and provenance records to ensure reproducibility.

### 4.2 Schema

```json
{
  "dataset_version_id": "string — unique identifier (e.g. 'DARTIS-v1-train-2024-08')",
  "dataset_name": "string (e.g. 'DARTIS', 'HRSID', 'MarineShield-Custom-v1')",
  "split": "TRAIN | VALIDATION | TEST | EVALUATION_BENCHMARK",
  "source_references": [
    {
      "source_name": "string (e.g. 'ESA Copernicus DARTIS', 'HRSID Public Dataset')",
      "source_url": "string | null",
      "license": "string (e.g. 'CC BY 4.0', 'Research Only')",
      "citation": "string | null"
    }
  ],
  "acquisition_date_range": {
    "start_utc": "string (ISO 8601 UTC)",
    "end_utc": "string (ISO 8601 UTC)"
  },
  "scene_count": "int — number of SAR scenes included",
  "tile_count": "int — number of 512x512 tiles included",
  "oil_tile_count": "int — tiles with confirmed oil presence",
  "lookalike_tile_count": "int — tiles with confirmed look-alike labels",
  "negative_tile_count": "int — tiles with confirmed no-oil labels",
  "class_distribution": {
    "PETROLEUM_OIL": "int",
    "BIOGENIC_SLICK": "int",
    "LOW_WIND_AREA": "int",
    "SHIP_WAKE": "int",
    "NATURAL_FILM": "int",
    "CLEAN_WATER": "int"
  },
  "geographic_coverage": {
    "regions": ["string (e.g. 'Indian Ocean', 'Arabian Sea', 'Bay of Bengal')"],
    "bbox_geojson": {
      "type": "Polygon",
      "coordinates": [[[lon_min, lat_min], [lon_max, lat_min], [lon_max, lat_max], [lon_min, lat_max], [lon_min, lat_min]]]
    }
  },
  "sensor_modes": ["string (e.g. 'Sentinel-1 IW GRD VV+VH')"],
  "preprocessing_pipeline_version": "string — version of preprocessing used to prepare this dataset",
  "checksum_manifest_sha256": "string — SHA-256 of the dataset manifest file",
  "storage_uri": "string — path to dataset manifest in object storage",
  "created_at_utc": "string (ISO 8601 UTC)",
  "created_by": "string (workstream member identifier)"
}
```

### 4.3 Dataset Governance Rules

- Training and validation splits must be **disjoint** (no scene overlap).
- Test and evaluation benchmark splits must be **held out** and not used during any training or hyperparameter tuning.
- Dataset provenance (license, source, citation) must be recorded before any model is trained on it.
- Hard-negative examples (look-alikes mis-labeled as oil) must be tracked with a distinct flag.

---

## §5 — Severity Contract

### 5.1 Definition

Operational severity is a **coarse classification** of spill characteristics derived from SAR backscatter intensity and contextual indicators. It does **NOT** represent oil volume, exact thickness, or environmental damage assessment. These claims are not scientifically defensible from SAR backscatter alone without extensive field validation.

### 5.2 Valid Severity Classes

| Class | Operational Interpretation | NOT a Claim |
|:---|:---|:---|
| `SHEEN` | Thin surface film, low backscatter damping, small area or sparse coverage | Not "minor spill" or "low risk" |
| `MODERATE` | Intermediate backscatter suppression, moderate spatial coverage | Not precise volume measurement |
| `THICK_HIGH_SEVERITY` | Strong backscatter damping over large area, potential thick oil layer | Not confirmed ecological damage |
| `UNKNOWN` | Insufficient data quality or model confidence to classify | Valid output — not an error |

### 5.3 Schema

```json
{
  "severity_id": "string (UUID v4)",
  "spill_polygon_id": "string — references the SpillGeometry record this severity applies to",
  "severity_class": "SHEEN | MODERATE | THICK_HIGH_SEVERITY | UNKNOWN",
  "severity_basis": {
    "mean_backscatter_db": "float | null — mean sigma-zero dB value over the spill polygon",
    "backscatter_suppression_db": "float | null — difference from surrounding clean water baseline",
    "estimated_area_km2": "float | null — estimated spill area from geometry",
    "texture_features_used": "boolean — true if SAR texture statistics contributed to classification"
  },
  "model_confidence": {
    "severity_class_probability": "float [0.0, 1.0] — model probability for the predicted class",
    "class_probabilities": {
      "SHEEN": "float",
      "MODERATE": "float",
      "THICK_HIGH_SEVERITY": "float",
      "UNKNOWN": "float"
    }
  },
  "data_quality": {
    "index": "float [0.0, 1.0]",
    "incidence_angle_deg": "float | null — radar incidence angle affects backscatter interpretation",
    "wind_speed_ms_at_acquisition": "float | null — wind speed affects backscatter damping baseline"
  },
  "explicit_non_claims": [
    "This classification does not represent estimated oil volume in tonnes or litres.",
    "This classification does not constitute ecological damage assessment.",
    "This classification does not imply legal severity of a MARPOL violation."
  ],
  "provenance": {"$ref": "#section-9-provenance"},
  "created_at_utc": "string (ISO 8601 UTC)"
}
```

---

## §6 — Look-Alike Verification Class Contract

### 6.1 Definition

The look-alike verification classifier (Module C) acts on dark SAR candidate patches and assigns a class label indicating what the dark region most likely represents. This is a **separate** inference step from segmentation. Its output determines whether the candidate enters the spill investigation pipeline.

### 6.2 Valid Look-Alike Classes

| Class | Meaning | Pipeline Consequence |
|:---|:---|:---|
| `PETROLEUM_OIL` | High confidence of petroleum oil presence | Enters full investigation pipeline |
| `BIOGENIC_SLICK` | Natural biological film (algae, zooplankton) | Rejected from incident pipeline; logged |
| `LOW_WIND_AREA` | Calm water patch due to low surface wind | Rejected from incident pipeline; logged |
| `SHIP_WAKE` | Turbulence/foam wake from vessel propulsion | Rejected from incident pipeline; logged |
| `NATURAL_FILM` | Other natural oceanographic phenomena | Rejected from incident pipeline; logged |
| `UNCERTAIN` | Model cannot confidently distinguish class | Flagged for analyst review (§10 Abstention) |
| `ABSTAINED` | Insufficient data quality for any classification | Hard abstention; triggers §10 workflow |

### 6.3 Schema

```json
{
  "verification_id": "string (UUID v4)",
  "candidate_id": "string — ID of the dark-candidate region being verified",
  "sar_granule_id": "string",
  "predicted_class": "PETROLEUM_OIL | BIOGENIC_SLICK | LOW_WIND_AREA | SHIP_WAKE | NATURAL_FILM | UNCERTAIN | ABSTAINED",
  "class_probabilities": {
    "PETROLEUM_OIL": "float [0.0, 1.0]",
    "BIOGENIC_SLICK": "float [0.0, 1.0]",
    "LOW_WIND_AREA": "float [0.0, 1.0]",
    "SHIP_WAKE": "float [0.0, 1.0]",
    "NATURAL_FILM": "float [0.0, 1.0]",
    "UNCERTAIN": "float [0.0, 1.0]"
  },
  "model_confidence": {
    "max_class_probability": "float [0.0, 1.0]",
    "entropy": "float — Shannon entropy; high entropy = uncertain prediction",
    "margin": "float — difference between top-1 and top-2 class probabilities"
  },
  "environmental_context": {
    "wind_speed_ms_at_acquisition": "float | null",
    "sea_surface_temperature_c": "float | null",
    "bathymetry_m": "float | null",
    "note": "Environmental context used as auxiliary input features to classifier, if available"
  },
  "hard_negative_flag": "boolean — true if this sample was sourced from the hard-negative learning dataset",
  "pipeline_decision": "ACCEPT_AS_OIL | REJECT_AS_LOOKALIKE | FLAG_FOR_ANALYST_REVIEW | ABSTAIN",
  "abstention_details": {"$ref": "#section-10-abstention"},
  "provenance": {"$ref": "#section-9-provenance"},
  "created_at_utc": "string (ISO 8601 UTC)"
}
```

### 6.4 Output Probabilities Must Sum to 1.0

The `class_probabilities` values must be the raw softmax outputs from the model. They must sum to exactly 1.0 (within floating-point precision). Renormalization that discards classes is not permitted.

---

## §7 — Spill Geometry Contract

### 7.1 Definition

A spill geometry record represents the **vectorized geospatial footprint** of a detected and verified oil slick, derived from the binary spill mask via contour extraction and coordinate reprojection. It is the primary geospatial artifact consumed downstream by Member 4 (attribution) and Member 5 (drift modeling).

### 7.2 Coordinate Standard

All coordinates: **WGS84 (EPSG:4326)**, `[longitude, latitude]` ordering. No exceptions.

### 7.3 Schema

```json
{
  "spill_geometry_id": "string (UUID v4)",
  "incident_id": "string (UUID v4)",
  "mask_id": "string — references the SpillMask this geometry was derived from",
  "slick_index": "int — 0-indexed within scene (0 = largest slick by area)",
  "geometry_geojson": {
    "type": "Feature",
    "geometry": {
      "type": "Polygon",
      "coordinates": [[[lon, lat], "..."]]
    },
    "properties": {
      "spill_geometry_id": "string",
      "area_km2": "float — estimated area in km² from projected geometry",
      "perimeter_km": "float — perimeter in km",
      "centroid_lon": "float — longitude of geometric centroid",
      "centroid_lat": "float — latitude of geometric centroid",
      "orientation_deg": "float — major axis orientation (0-180 degrees, clockwise from North)",
      "elongation_ratio": "float >= 1.0 — major axis / minor axis ratio (1.0 = circular)",
      "fragmentation_index": "float [0.0, 1.0] — 0 = single cohesive polygon, 1 = highly fragmented",
      "bounding_box": {
        "lon_min": "float",
        "lat_min": "float",
        "lon_max": "float",
        "lat_max": "float"
      }
    }
  },
  "multi_slick_collection": {
    "type": "FeatureCollection | null",
    "features": ["SpillGeometry GeoJSON Feature"],
    "note": "Populated only when multiple discrete slick fragments are identified in one scene"
  },
  "source_tile_ids": ["string — tile IDs contributing to this geometry"],
  "contour_extraction_parameters": {
    "binarization_threshold": "float — threshold applied to probability mask",
    "minimum_area_px": "int — minimum connected-component area in pixels to retain",
    "smoothing_tolerance_m": "float — polygon simplification tolerance in metres"
  },
  "model_confidence": {
    "mean_oil_probability_within_polygon": "float [0.0, 1.0]",
    "polygon_pixel_count": "int"
  },
  "data_quality": {
    "index": "float [0.0, 1.0]",
    "geometry_quality_flags": ["string (e.g. 'NEAR_SCENE_EDGE', 'TILING_ARTIFACT_RISK', 'LOW_RESOLUTION_TILE')"]
  },
  "provenance": {"$ref": "#section-9-provenance"},
  "acquisition_timestamp_utc": "string (ISO 8601 UTC) — SAR scene acquisition time",
  "created_at_utc": "string (ISO 8601 UTC)"
}
```

### 7.4 Geometry Validity Requirements

- All polygons must be topologically valid (no self-intersections, no unclosed rings).
- Polygons must have area > 0.
- Degenerate geometries (lines, points) must never be emitted as spill geometries.
- Geometry validation must be applied before any record is persisted to PostGIS.

---

## §8 — Metrics Metadata Contract

### 8.1 Definition

Metrics metadata records aggregate performance measurements from a **model validation run** against a held-out evaluation dataset. These are **model-level statistics**, not per-inference outputs. They must never be reported as per-scene accuracy guarantees.

### 8.2 What Metrics Metadata Is NOT

- It is NOT a per-inference confidence score.
- It is NOT a scene-specific accuracy guarantee.
- It is NOT legal or operational proof of detection reliability.

### 8.3 Schema

```json
{
  "metrics_record_id": "string (UUID v4)",
  "model_version_id": "string — references §3 ModelVersion",
  "evaluation_dataset_version_id": "string — references §4 DatasetVersion (must be held-out evaluation set)",
  "evaluation_timestamp_utc": "string (ISO 8601 UTC)",
  "module": "SEGMENTATION | LOOKALIKE_REJECTION | SEVERITY_CLASSIFICATION | SAR_VESSEL_DETECTION",

  "segmentation_metrics": {
    "iou_intersection_over_union": "float [0.0, 1.0] | null",
    "dice_f1_score": "float [0.0, 1.0] | null",
    "precision": "float [0.0, 1.0] | null",
    "recall": "float [0.0, 1.0] | null",
    "false_positive_rate": "float [0.0, 1.0] | null — FPR on hard-negative look-alike scenes",
    "inference_latency_p50_ms": "float | null — median inference latency per 512x512 tile",
    "inference_latency_p95_ms": "float | null — 95th percentile inference latency",
    "scene_count_evaluated": "int | null"
  },

  "lookalike_rejection_metrics": {
    "per_class_precision": {
      "PETROLEUM_OIL": "float",
      "BIOGENIC_SLICK": "float",
      "LOW_WIND_AREA": "float",
      "SHIP_WAKE": "float",
      "NATURAL_FILM": "float"
    },
    "per_class_recall": {
      "PETROLEUM_OIL": "float",
      "BIOGENIC_SLICK": "float",
      "LOW_WIND_AREA": "float",
      "SHIP_WAKE": "float",
      "NATURAL_FILM": "float"
    },
    "overall_accuracy": "float [0.0, 1.0] | null",
    "oil_vs_non_oil_f1": "float [0.0, 1.0] | null — binary oil detection F1",
    "hard_negative_fpr": "float [0.0, 1.0] | null — false positive rate specifically on hard-negative samples",
    "abstention_rate": "float [0.0, 1.0] | null — fraction of samples assigned ABSTAINED/UNCERTAIN class"
  },

  "vessel_detection_metrics": {
    "precision": "float [0.0, 1.0] | null",
    "recall": "float [0.0, 1.0] | null",
    "mean_average_precision_map": "float [0.0, 1.0] | null — mAP at IoU threshold(s)",
    "iou_threshold": "float (e.g. 0.5) | null",
    "inference_latency_p50_ms": "float | null",
    "scene_count_evaluated": "int | null"
  },

  "threshold_sensitivity": {
    "evaluated_thresholds": ["float — binarization thresholds evaluated"],
    "iou_at_threshold": [{"threshold": "float", "iou": "float"}],
    "f1_at_threshold": [{"threshold": "float", "f1": "float"}],
    "selected_operating_threshold": "float — threshold selected for production deployment"
  },

  "evaluation_notes": "string | null — any caveats, data quality issues, or evaluation conditions",
  "evaluated_by": "string (workstream member identifier)"
}
```

### 8.4 Threshold Selection Rule

The `selected_operating_threshold` must be chosen based on empirical validation against the held-out evaluation dataset. It must not be a default constant (e.g., 0.5) without validation evidence. The selection rationale must be documented in the evaluation notes.

---

## §9 — Provenance Contract

### 9.1 Definition

Every ML output artifact (spill mask, spill geometry, look-alike verification record, severity record, SAR vessel detection) must carry a `provenance` block. This block ensures reproducibility: given the same provenance, the same output should be reproducible.

### 9.2 Schema

```json
{
  "provenance": {
    "sar_scene": {
      "granule_id": "string — Copernicus/GFW granule identifier",
      "product_type": "string (e.g. 'IW_GRDH')",
      "orbit_direction": "ASCENDING | DESCENDING",
      "orbit_number": "int | null",
      "polarization": "VV_VH | VV | HH_HV | HH",
      "acquisition_start_utc": "string (ISO 8601 UTC)",
      "acquisition_end_utc": "string (ISO 8601 UTC)",
      "scene_footprint_geojson": {
        "type": "Polygon",
        "coordinates": [[[lon, lat], "..."]]
      },
      "incidence_angle_deg": {"min": "float | null", "max": "float | null"},
      "source_api": "string (e.g. 'Copernicus CDS', 'Global Fishing Watch')"
    },
    "preprocessing": {
      "pipeline_version": "string — preprocessing pipeline version (e.g. 'sar-prep-v1.3.2')",
      "processing_steps_applied": [
        "ORBIT_CORRECTION",
        "THERMAL_NOISE_REMOVAL",
        "RADIOMETRIC_CALIBRATION_SIGMA0",
        "SPECKLE_FILTERING",
        "TERRAIN_CORRECTION",
        "DB_CONVERSION",
        "TILING_AND_NORMALIZATION"
      ],
      "speckle_filter": "string (e.g. 'Refined Lee') | null",
      "dem_source": "string (e.g. 'Copernicus DEM 30m') | null"
    },
    "model": {
      "model_version_id": "string — references §3 ModelVersion",
      "module": "SEGMENTATION | LOOKALIKE_REJECTION | SEVERITY_CLASSIFICATION | SAR_VESSEL_DETECTION",
      "inference_timestamp_utc": "string (ISO 8601 UTC)",
      "inference_device": "string (e.g. 'cuda:0 NVIDIA GeForce RTX 3050 6GB')",
      "inference_framework_version": "string (e.g. 'torch==2.11.0+cu128')"
    },
    "pipeline_parameters": {
      "tile_size_px": 512,
      "tile_stride_px": "int — stride used during tiling (may overlap tiles)",
      "binarization_threshold": "float [0.0, 1.0]",
      "minimum_slick_area_px": "int",
      "polygon_smoothing_tolerance_m": "float"
    },
    "training_dataset": {
      "dataset_version_id": "string — references §4 DatasetVersion (training split)",
      "dataset_name": "string"
    },
    "request_id": "string (UUID v4) — pipeline execution request identifier",
    "pipeline_run_id": "string (UUID v4) — Celery task or job queue execution ID"
  }
}
```

### 9.3 Provenance Immutability Rule

Once a provenance record is written for an output artifact, it must not be modified. If reprocessing occurs (e.g., with a new model version), a new artifact record with new provenance is created. The original record is preserved with `status: SUPERSEDED`.

### 9.4 Downstream Propagation Rule

When Member 4 (Evidence Engine) or Member 5 (Drift) consume a Member 2 output, they must carry forward the `provenance.model.model_version_id` and `provenance.sar_scene.granule_id` in their own output records. Evidence scores without traceable source provenance are invalid.

---

## §10 — Abstention & Insufficient-Confidence Contract

### 10.1 Definition

**Abstention is a mandatory first-class output**, not an error state or fallback. The system must be capable of explicitly declining to classify when evidence quality or model confidence falls below defined thresholds. Forcing a classification when evidence is insufficient produces scientifically unreliable outputs.

### 10.2 Abstention Is NOT

- A pipeline failure
- A missing feature  
- An error to be suppressed
- Equivalent to "no oil detected"

### 10.3 Abstention Trigger Conditions

| Condition | Code | Trigger |
|:---|:---|:---|
| SAR scene quality too low | `LOW_DATA_QUALITY` | `data_quality.index < configured_min_dqi` |
| Model confidence below operating threshold | `LOW_MODEL_CONFIDENCE` | `max_class_probability < configured_abstention_threshold` |
| High class ambiguity | `AMBIGUOUS_CLASS` | Softmax entropy above configured entropy ceiling |
| Required environmental context missing | `MISSING_ENVIRONMENTAL_CONTEXT` | Wind speed / SST not available and required by model |
| Scene partially outside area of interest | `PARTIAL_SCENE_COVERAGE` | > configured_edge_fraction of tile is nodata |

### 10.4 Schema

```json
{
  "abstention_id": "string (UUID v4)",
  "artifact_id": "string — references the artifact that triggered abstention (mask_id, verification_id, etc.)",
  "artifact_type": "SPILL_MASK | LOOKALIKE_VERIFICATION | SEVERITY | SAR_VESSEL_DETECTION | SPILL_GEOMETRY",
  "abstention_state": "ABSTAINED",
  "abstention_reason_primary": "LOW_DATA_QUALITY | LOW_MODEL_CONFIDENCE | AMBIGUOUS_CLASS | MISSING_ENVIRONMENTAL_CONTEXT | PARTIAL_SCENE_COVERAGE",
  "abstention_reasons_all": ["string — all trigger codes that contributed"],
  "triggering_values": {
    "data_quality_index": "float | null",
    "max_class_probability": "float | null",
    "softmax_entropy": "float | null",
    "configured_abstention_threshold": "float — the threshold value at time of abstention",
    "configured_min_dqi": "float — the minimum DQI threshold at time of abstention"
  },
  "recommendation": "ANALYST_REVIEW_REQUIRED | REQUEST_ADDITIONAL_SAR_PASS | EXPAND_ENVIRONMENTAL_CONTEXT | ESCALATE_TO_UNKNOWN",
  "escalation_path": {
    "analyst_review_required": "boolean",
    "incident_status_update": "string | null (e.g. 'Set to UNDER_VERIFICATION')"
  },
  "provenance": {"$ref": "#section-9-provenance"},
  "created_at_utc": "string (ISO 8601 UTC)"
}
```

### 10.5 Abstention Threshold Configuration

Abstention thresholds (`configured_abstention_threshold`, `configured_min_dqi`, entropy ceiling) are pipeline configuration parameters, not model hyperparameters. They must be:

- Defined in a versioned pipeline configuration file (not hardcoded)
- Included in the provenance record of every inference output
- Subject to review and calibration using historical incident evaluation results

### 10.6 Propagation to Downstream Consumers

When a Member 2 output has `abstention_state: ABSTAINED`:

1. **Member 4 (Evidence Engine)** must not attempt to generate evidence scores from the abstained artifact. The `data_quality.index` and `abstention_reason_primary` must be included in Member 4's data quality panel.
2. **Member 6 Frontend** must display an explicit abstention banner (not a hidden null or silent empty result).
3. **Member 5 (Drift)** must not accept an abstained spill geometry as input. Drift cannot be computed from a geometry that has not passed verification.

---

## §11 — Data Quality Index (DQI) Sub-Contract

### 11.1 Definition

The Data Quality Index is a composite `float [0.0, 1.0]` score that quantifies the suitability of the input SAR scene and environmental context for reliable ML inference. It is **derived from pre-inference scene analysis**, independent of model output.

DQI is **not** model confidence. A scene may have high DQI but produce low model confidence (ambiguous scene content), or low DQI but coincidentally high model confidence (unreliable inference on a poor scene).

### 11.2 DQI Component Factors

| Factor | Description |
|:---|:---|
| `noise_floor_score` | Thermal noise floor relative to expected signal — low noise = high score |
| `incidence_angle_score` | Radar incidence angle within optimal range for oil detection (typically 20°–45°) |
| `wind_context_score` | Wind speed availability and whether it falls in a detectable range |
| `scene_completeness_score` | Fraction of scene without nodata, flagged scan lines, or artifact regions |
| `temporal_freshness_score` | Age of scene relative to incident detection time (optional lower-weight factor) |

### 11.3 DQI Schema

```json
{
  "data_quality": {
    "index": "float [0.0, 1.0] — composite DQI",
    "component_scores": {
      "noise_floor_score": "float [0.0, 1.0] | null",
      "incidence_angle_score": "float [0.0, 1.0] | null",
      "wind_context_score": "float [0.0, 1.0] | null",
      "scene_completeness_score": "float [0.0, 1.0] | null",
      "temporal_freshness_score": "float [0.0, 1.0] | null"
    },
    "quality_flags": [
      "NEAR_SCENE_EDGE",
      "HIGH_WIND_BACKSCATTER_MASK",
      "THERMAL_NOISE_ANOMALY",
      "ORBIT_CORRECTION_FAILED",
      "INCOMPLETE_DUAL_POL",
      "LOW_INCIDENCE_ANGLE",
      "HIGH_INCIDENCE_ANGLE",
      "MISSING_WIND_DATA",
      "MISSING_SST_DATA"
    ],
    "dqi_computation_version": "string — version of DQI algorithm used"
  }
}
```

### 11.4 DQI Weighting Calibration Rule

The specific weights applied to compute the composite DQI must not be arbitrary constants. They must be calibrated and documented against historical incident scenes where scene quality was independently assessed. The weighting scheme version is recorded in `dqi_computation_version`.

---

## §12 — Inter-Contract References & Downstream Dependency Map

```
Member 2 Output                     Consumed By
─────────────────────────────────────────────────────────────────────
SpillMask (§1)                  →   SpillGeometry extraction (§7)
SpillMask (§1)                  →   Severity Classifier (§5)
LookAlikeVerification (§6)      →   Pipeline gate (ACCEPT / REJECT)
SpillGeometry (§7)              →   Member 4: Release Estimation
SpillGeometry (§7)              →   Member 5: PyGNOME Forward Drift
SpillGeometry (§7)              →   Member 6 Backend: Threat Intersection
SARVesselDetection              →   Member 3: AIS-SAR Reconciliation
Severity (§5)                   →   Member 6 Backend: Response Priority
ModelVersion (§3)               →   Member 4: Evidence Provenance
DatasetVersion (§4)             →   Model training audit trail
MetricsMetadata (§8)            →   Historical Time Machine evaluation
Abstention (§10)                →   Member 4: Data Quality Panel
Abstention (§10)                →   Member 6 Frontend: Abstention Banner
Provenance (§9)                 →   ALL downstream records (mandatory carry-forward)
DataQualityIndex (§11)          →   Member 6 Frontend: Data Quality Dashboard
```

---

## §13 — Unresolved Questions & Open Decisions

The following items require explicit human review and architectural decision before pipeline implementation:

| # | Question | Impact | Status |
|:-:|:---|:---|:---|
| **Q-1** | What is the calibrated abstention threshold for segmentation model confidence? | Determines abstention rate; must be set via validation, not heuristically | **PENDING** |
| **Q-2** | What is the minimum DQI value below which inference must not proceed? | Determines pipeline gating behaviour | **PENDING** |
| **Q-3** | Will temperature scaling be applied to segmentation model softmax outputs? | Affects model_confidence calibration claim in §2 | **PENDING** |
| **Q-4** | Which look-alike labeled datasets are available for Indian Ocean / Bay of Bengal? | Affects dataset version records and class distribution in §4 | **PENDING** |
| **Q-5** | What tile stride (overlap) is used during inference? | Affects tiling artifacts, geometry stitching, and provenance records | **PENDING** |
| **Q-6** | Is incidence angle correction applied before or after DQI computation? | Affects DQI component score interpretation in §11 | **PENDING** |
| **Q-7** | What minimum connected-component area (px) is used to filter noise in binary masks? | Affects geometry sensitivity vs. noise rejection in §7 | **PENDING** |

---

## §14 — Assumptions

1. Segmentation model produces pixel-wise float32 output in `[0.0, 1.0]` via sigmoid activation (binary segmentation). If multi-class softmax is used, the contract must be updated with a schema change record in `DECISION_LOG.md`.
2. Input tiles are always 512×512 pixels, dual-polarization VV+VH, normalized to [0, 1] range.
3. SAR granule IDs conform to Copernicus naming convention (`S1A_IW_GRDH_...` or equivalent GFW identifiers).
4. All object storage URIs are accessible to authorized pipeline services. This contract does not define storage access control policies.
5. The `data_quality.index` is computed by the SAR preprocessing pipeline (Member 1 / Person 2) and passed to Member 2 inference services with the preprocessed tile. Member 2 does not independently recompute DQI from raw SAR data.
6. `evidence_strength` is **never** a Member 2 output. Any field labelled `evidence_strength` in a Member 2 output record is a contract violation and must be rejected in code review.
7. `forecast_uncertainty` is **never** a Member 2 output. It belongs exclusively to Member 5 (Person 3 / PyGNOME drift outputs).

---

## §15 — Schema Validation

### Structural Validation (Runnable Now)

```bash
# Run from repository root with active .venv
.venv\Scripts\python.exe -c "
import json, uuid, datetime

# Minimal valid SpillMask record
mask = {
    'mask_id': str(uuid.uuid4()),
    'incident_id': str(uuid.uuid4()),
    'tile_id': 'T_R003_C007',
    'sar_granule_id': 'S1A_IW_GRDH_1SDV_20240815T052301_20240815T052326_055123_06B8A7',
    'mask_type': 'PROBABILITY',
    'mask_storage_uri': 's3://marineshield-dev/masks/test.tif',
    'tile_size_px': 512,
    'tile_crs': 'EPSG:4326',
    'binarization_threshold': None,
    'dtype': 'float32',
    'value_range': {'min': 0.0, 'max': 1.0},
    'nodata_value': -9999.0,
    'model_confidence': {'mean_oil_probability': 0.87, 'pixel_coverage_fraction': 0.12},
    'data_quality': {'index': 0.81, 'quality_flags': []},
    'created_at_utc': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
}
serialized = json.dumps(mask, indent=2)
roundtrip = json.loads(serialized)
assert roundtrip == mask, 'Round-trip serialization failed'
assert roundtrip['mask_type'] in ('PROBABILITY', 'BINARY'), 'Invalid mask_type'
assert 0.0 <= roundtrip['model_confidence']['mean_oil_probability'] <= 1.0, 'Confidence out of range'
assert 0.0 <= roundtrip['data_quality']['index'] <= 1.0, 'DQI out of range'
print('SpillMask contract structural validation: PASS')
print(serialized)
"
```

### Formal JSON Schema

A machine-readable JSON Schema (Draft 7) for each contract section will be created in `docs/ml/schemas/` when the pipeline implementation phase begins. This document is the authoritative human-readable specification that all JSON Schema files must match exactly.

---

## Document Change Log

| Version | Date (UTC) | Author | Change |
|:---|:---|:---|:---|
| `1.0.0` | `2026-08-20T10:09:00Z` | Member 2 / Person 1 | Initial canonical contract definition covering §1–§15 |

> **Any modification to this document after Version 1.0.0 requires:**
> 1. A recorded entry in [`docs/decisions/DECISION_LOG.md`](file:///d:/MarineShield/MarineShield/docs/decisions/DECISION_LOG.md) with change description, author, and architectural justification.
> 2. A semantic version bump in the Document Version field above.
> 3. Review and acknowledgement by the downstream consuming workstreams (Member 4, Member 3, Member 5).
