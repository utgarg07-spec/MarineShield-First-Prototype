import uuid
import datetime
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional

@dataclass
class DataQualityIndex:
    """Canonical Data Quality Index (§11) measuring SAR input suitability."""
    index: float  # [0.0, 1.0]
    component_scores: Dict[str, Optional[float]] = field(default_factory=lambda: {
        "noise_floor_score": 1.0,
        "incidence_angle_score": 1.0,
        "wind_context_score": 1.0,
        "scene_completeness_score": 1.0,
        "temporal_freshness_score": 1.0
    })
    quality_flags: List[str] = field(default_factory=list)
    dqi_computation_version: str = "dqi-sar-v1.0.0"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "index": round(self.index, 3),
            "component_scores": self.component_scores,
            "quality_flags": self.quality_flags,
            "dqi_computation_version": self.dqi_computation_version
        }


@dataclass
class ProvenanceBlock:
    """Canonical Provenance Contract (§9) ensuring end-to-end reproducibility."""
    sar_granule_id: str
    model_version_id: str
    dataset_version_id: str
    inference_device: str
    inference_framework: str = "torch 2.11.0+cu128"
    preprocessing_version: str = "sar-prep-v1.0.0"
    execution_timestamp_utc: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    pipeline_parameters: Dict[str, Any] = field(default_factory=lambda: {
        "tile_size_px": 512,
        "binarization_threshold": 0.50,
        "minimum_slick_area_px": 50,
        "adapter_bottleneck_channels": 64
    })
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sar_scene": {
                "granule_id": self.sar_granule_id,
                "polarization": "VV_VH",
                "source_api": "Copernicus Sentinel-1 SAR"
            },
            "preprocessing": {
                "pipeline_version": self.preprocessing_version,
                "processing_steps_applied": [
                    "RADIOMETRIC_CALIBRATION_SIGMA0",
                    "DB_CONVERSION",
                    "SPECKLE_FILTERING_REFINED_LEE",
                    "DETERMINISTIC_TILING_AND_NORMALIZATION"
                ]
            },
            "model": {
                "model_version_id": self.model_version_id,
                "module": "OIL_INTELLIGENCE_DUAL_STAGE",
                "inference_timestamp_utc": self.execution_timestamp_utc,
                "inference_device": self.inference_device,
                "inference_framework_version": self.inference_framework
            },
            "training_dataset": {
                "dataset_version_id": self.dataset_version_id,
                "dataset_name": "DARTIS-2019"
            },
            "pipeline_parameters": self.pipeline_parameters,
            "request_id": self.request_id
        }


@dataclass
class AbstentionDetails:
    """Canonical Abstention Contract (§10) for insufficient evidence or low quality."""
    abstention_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    artifact_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    artifact_type: str = "SPILL_DETECTION"
    abstention_state: str = "ABSTAINED"
    abstention_reason_primary: str = "LOW_DATA_QUALITY"  # LOW_DATA_QUALITY | LOW_MODEL_CONFIDENCE | AMBIGUOUS_CLASS
    abstention_reasons_all: List[str] = field(default_factory=list)
    triggering_values: Dict[str, Any] = field(default_factory=dict)
    recommendation: str = "ANALYST_REVIEW_REQUIRED"
    escalation_path: Dict[str, Any] = field(default_factory=lambda: {
        "analyst_review_required": True,
        "incident_status_update": "SET_TO_UNDER_VERIFICATION"
    })
    created_at_utc: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SpillMaskContract:
    """Canonical Spill Mask Contract (§1)."""
    mask_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    incident_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    tile_id: str = "T_001"
    sar_granule_id: str = "S1A_IW_GRDH_..."
    mask_type: str = "PROBABILITY"
    tile_size_px: int = 512
    tile_crs: str = "EPSG:4326"
    binarization_threshold: float = 0.50
    model_confidence: Dict[str, float] = field(default_factory=lambda: {
        "mean_oil_probability": 0.0,
        "pixel_coverage_fraction": 0.0
    })
    data_quality: DataQualityIndex = field(default_factory=lambda: DataQualityIndex(index=1.0))
    created_at_utc: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mask_id": self.mask_id,
            "incident_id": self.incident_id,
            "tile_id": self.tile_id,
            "sar_granule_id": self.sar_granule_id,
            "mask_type": self.mask_type,
            "tile_size_px": self.tile_size_px,
            "tile_crs": self.tile_crs,
            "binarization_threshold": self.binarization_threshold,
            "model_confidence": self.model_confidence,
            "data_quality": self.data_quality.to_dict(),
            "created_at_utc": self.created_at_utc
        }


@dataclass
class LookAlikeVerificationContract:
    """Canonical Look-Alike Verification Contract (§6)."""
    verification_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    candidate_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sar_granule_id: str = "S1A_IW_GRDH_..."
    predicted_class: str = "PETROLEUM_OIL"  # PETROLEUM_OIL | BIOGENIC_SLICK | LOW_WIND_AREA | SHIP_WAKE | NATURAL_FILM | UNCERTAIN | ABSTAINED
    class_probabilities: Dict[str, float] = field(default_factory=lambda: {
        "PETROLEUM_OIL": 0.0,
        "BIOGENIC_SLICK": 0.0,
        "LOW_WIND_AREA": 0.0,
        "SHIP_WAKE": 0.0,
        "NATURAL_FILM": 0.0,
        "UNCERTAIN": 0.0
    })
    model_confidence: Dict[str, float] = field(default_factory=lambda: {
        "max_class_probability": 0.0,
        "entropy": 0.0,
        "margin": 0.0
    })
    pipeline_decision: str = "ACCEPT_AS_OIL"  # ACCEPT_AS_OIL | REJECT_AS_LOOKALIKE | FLAG_FOR_ANALYST_REVIEW | ABSTAIN
    created_at_utc: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "verification_id": self.verification_id,
            "candidate_id": self.candidate_id,
            "sar_granule_id": self.sar_granule_id,
            "predicted_class": self.predicted_class,
            "class_probabilities": {k: round(v, 4) for k, v in self.class_probabilities.items()},
            "model_confidence": {k: round(v, 4) for k, v in self.model_confidence.items()},
            "pipeline_decision": self.pipeline_decision,
            "created_at_utc": self.created_at_utc
        }


@dataclass
class SpillSeverityContract:
    """Canonical Severity Contract (§5)."""
    severity_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    severity_class: str = "MODERATE"  # SHEEN | MODERATE | THICK_HIGH_SEVERITY | UNKNOWN
    severity_basis: Dict[str, Optional[float]] = field(default_factory=lambda: {
        "mean_backscatter_db": -22.5,
        "backscatter_suppression_db": 6.8,
        "estimated_area_km2": 1.45,
        "texture_features_used": True
    })
    model_confidence: Dict[str, Any] = field(default_factory=lambda: {
        "severity_class_probability": 0.85,
        "class_probabilities": {
            "SHEEN": 0.05,
            "MODERATE": 0.85,
            "THICK_HIGH_SEVERITY": 0.10,
            "UNKNOWN": 0.00
        }
    })
    explicit_non_claims: List[str] = field(default_factory=lambda: [
        "This classification does not represent estimated oil volume in tonnes or litres.",
        "This classification does not constitute ecological damage assessment.",
        "This classification does not imply legal severity of a MARPOL violation."
    ])
    created_at_utc: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "severity_id": self.severity_id,
            "severity_class": self.severity_class,
            "severity_basis": self.severity_basis,
            "model_confidence": self.model_confidence,
            "explicit_non_claims": self.explicit_non_claims,
            "created_at_utc": self.created_at_utc
        }


@dataclass
class SpillGeometryContract:
    """Canonical Spill Geometry Contract (§7)."""
    spill_geometry_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    incident_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    geometry_geojson: Dict[str, Any] = field(default_factory=dict)
    properties: Dict[str, Any] = field(default_factory=dict)
    model_confidence: Dict[str, float] = field(default_factory=lambda: {
        "mean_oil_probability_within_polygon": 0.0,
        "polygon_pixel_count": 0
    })
    created_at_utc: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "spill_geometry_id": self.spill_geometry_id,
            "incident_id": self.incident_id,
            "geometry_geojson": self.geometry_geojson,
            "properties": self.properties,
            "model_confidence": self.model_confidence,
            "created_at_utc": self.created_at_utc
        }


@dataclass
class SpillDetectionResponse:
    """Top-Level Canonical Spill Detection Service Output."""
    incident_id: str
    tile_id: str
    sar_granule_id: str
    status: str  # OIL_DETECTED | LOOKALIKE_REJECTED | UNCERTAIN_ANALYSIS | ABSTAINED | NO_CANDIDATE_FOUND
    is_abstained: bool
    abstention_details: Optional[AbstentionDetails]
    spill_mask: Optional[SpillMaskContract]
    spill_geometry: Optional[SpillGeometryContract]
    lookalike_verification: LookAlikeVerificationContract
    severity: SpillSeverityContract
    data_quality: DataQualityIndex
    metrics_metadata_ref: str = "METRICS-SAR-SAM-ADAPT-v1.0"
    provenance: Optional[ProvenanceBlock] = None
    created_at_utc: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "incident_id": self.incident_id,
            "tile_id": self.tile_id,
            "sar_granule_id": self.sar_granule_id,
            "status": self.status,
            "is_abstained": self.is_abstained,
            "abstention_details": self.abstention_details.to_dict() if self.abstention_details else None,
            "spill_mask": self.spill_mask.to_dict() if self.spill_mask else None,
            "spill_geometry": self.spill_geometry.to_dict() if self.spill_geometry else None,
            "lookalike_verification": self.lookalike_verification.to_dict(),
            "severity": self.severity.to_dict(),
            "data_quality": self.data_quality.to_dict(),
            "metrics_metadata_ref": self.metrics_metadata_ref,
            "provenance": self.provenance.to_dict() if self.provenance else None,
            "created_at_utc": self.created_at_utc
        }
