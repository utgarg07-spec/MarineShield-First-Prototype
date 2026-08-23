import uuid
import datetime
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, Tuple

@dataclass
class EnvironmentalHistory:
    """Historical meteorological and oceanographic conditions over the lookback window."""
    wind_speed_ms: float
    wind_direction_deg: float  # Direction wind is blowing FROM (0-360)
    current_u_ms: float       # Eastward surface current (m/s)
    current_v_ms: float       # Northward surface current (m/s)
    lookback_hours: float = 6.0
    wind_dataset_id: str = "ERA5-Reanalysis-2026-08"
    current_dataset_id: str = "HYCOM-Global-Analysis-2026-08"
    data_quality_index: float = 0.90

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class VesselObservation:
    """Observed vessel trajectory (AIS track) or SAR dark vessel detection."""
    vessel_id: str
    source_type: str  # AIS_TRACK | SAR_DETECTION | NON_VESSEL_FACILITY
    vessel_name: Optional[str] = None
    vessel_mmsi: Optional[str] = None
    vessel_type: Optional[str] = "CARGO"  # TANKER | CARGO | BULK_CARRIER | FISHING | UNKNOWN
    vessel_flag: Optional[str] = None
    track_points: List[Dict[str, Any]] = field(default_factory=list)  # [{"lon": x, "lat": y, "timestamp_utc": "...", "speed_knots": s}]
    sar_vessel_detection_id: Optional[str] = None
    estimated_length_m: Optional[float] = None
    is_moored_at_berth: bool = False
    has_ais_gap: bool = False
    speed_drop_knots: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class EvidenceItemContract:
    """Canonical Evidence Item (§3) representing an atomic verifiable analytical observation."""
    evidence_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    target_hypothesis_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    evidence_type: str = "SPATIAL_PROXIMITY"  # SPATIAL_PROXIMITY | TEMPORAL_INTERSECTION | TRAJECTORY_INTERSECTION | DRIFT_COMPATIBILITY | VESSEL_CHARACTERISTICS | BEHAVIOR_ANOMALY | CONTRADICTORY_PHYSICS
    polarity: str = "SUPPORTING"  # SUPPORTING | CONTRADICTORY | NEUTRAL_CONTEXT
    assertion_summary: str = ""
    numeric_value: Optional[float] = None
    unit: Optional[str] = None
    observation_channel: str = "AIS_TRAJECTORY"
    data_quality_score: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "target_hypothesis_id": self.target_hypothesis_id,
            "evidence_type": self.evidence_type,
            "polarity": self.polarity,
            "assertion": {
                "summary_text": self.assertion_summary,
                "numeric_value": self.numeric_value,
                "unit": self.unit
            },
            "observation_source": {
                "source_channel": self.observation_channel,
                "data_quality_score": self.data_quality_score
            }
        }


@dataclass
class ReleaseHypothesisContract:
    """Canonical Release Hypothesis (§1) modeling backward-reconstructed release envelope."""
    release_hypothesis_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    incident_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    spill_geometry_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    hypothesis_state: str = "EVALUATED"  # CANDIDATE | EVALUATED | UNRESOLVED | ABSTAINED
    discharge_modality: str = "SINGLE_DISCHARGE"
    t_observation_utc: str = ""
    t_earliest_utc: str = ""
    t_most_likely_utc: str = ""
    t_latest_utc: str = ""
    window_duration_hours: float = 6.0
    release_polygon_geojson: Dict[str, Any] = field(default_factory=dict)
    centroid_lon: float = 0.0
    centroid_lat: float = 0.0
    uncertainty_area_km2: float = 0.0
    reconstruction_method: Dict[str, Any] = field(default_factory=lambda: {
        "engine": "PYGNOME_BACKWARD_DRIFT_INTEGRATION",
        "engine_version": "pygnome-1.1.8-m4-adapter-v1.0"
    })
    created_at_utc: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "release_hypothesis_id": self.release_hypothesis_id,
            "incident_id": self.incident_id,
            "spill_geometry_id": self.spill_geometry_id,
            "hypothesis_state": self.hypothesis_state,
            "discharge_modality": self.discharge_modality,
            "temporal_scope": {
                "t_observation_utc": self.t_observation_utc,
                "t_earliest_utc": self.t_earliest_utc,
                "t_most_likely_utc": self.t_most_likely_utc,
                "t_latest_utc": self.t_latest_utc,
                "window_duration_hours": self.window_duration_hours
            },
            "spatial_scope": {
                "release_polygon_geojson": self.release_polygon_geojson,
                "crs": "EPSG:4326"
            },
            "reconstruction_method": self.reconstruction_method,
            "created_at_utc": self.created_at_utc
        }


@dataclass
class SourceHypothesisContract:
    """Canonical Source Hypothesis (§2) representing a ranked candidate source."""
    source_hypothesis_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    incident_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    release_hypothesis_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    hypothesis_label: str = "H_1"
    source_category: str = "VESSEL_IDENTIFIED"  # VESSEL_IDENTIFIED | VESSEL_UNTRACKED_DARK | NON_VESSEL_SOURCE | UNKNOWN_SOURCE
    candidate_entity: Dict[str, Any] = field(default_factory=dict)
    component_scores: Dict[str, float] = field(default_factory=dict)
    component_breakdown: Dict[str, Any] = field(default_factory=dict)
    evidence_score: float = 0.0
    evidence_strength: str = "INSUFFICIENT_EVIDENCE"  # STRONG_COMPATIBILITY | MODERATE_COMPATIBILITY | WEAK_COMPATIBILITY | INSUFFICIENT_EVIDENCE
    ranking_position: int = 1
    counterfactual_analysis: Dict[str, Any] = field(default_factory=dict)
    supporting_evidence: List[Dict[str, Any]] = field(default_factory=list)
    contradictory_evidence: List[Dict[str, Any]] = field(default_factory=list)
    behavioral_anomaly_detected: bool = False
    unmatched_sar_target: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_hypothesis_id": self.source_hypothesis_id,
            "incident_id": self.incident_id,
            "release_hypothesis_id": self.release_hypothesis_id,
            "hypothesis_label": self.hypothesis_label,
            "source_category": self.source_category,
            "candidate_entity": self.candidate_entity,
            "evidence_evaluation": {
                "evidence_score": self.evidence_score,
                "evidence_strength": self.evidence_strength,
                "ranking_position": self.ranking_position,
                "counterfactual_analysis": self.counterfactual_analysis
            },
            "component_scores": self.component_scores,
            "component_breakdown": self.component_breakdown,
            "supporting_evidence": self.supporting_evidence,
            "contradictory_evidence": self.contradictory_evidence,
            "behavioral_anomaly_detected": self.behavioral_anomaly_detected,
            "unmatched_sar_target": self.unmatched_sar_target
        }


@dataclass
class InvestigationResult:
    """Canonical Top-Level Investigation Result Envelope (§1-§10)."""
    incident_id: str
    scenario_id: str
    status: str  # ATTRIBUTED_CANDIDATES_EVALUATED | SOURCE_UNKNOWN | ABSTAINED
    is_unknown_triggered: bool
    unknown_trigger_reason: Optional[str]
    release_hypothesis: ReleaseHypothesisContract
    candidate_hypotheses: List[SourceHypothesisContract]
    top_hypothesis_id: Optional[str]
    top_hypothesis_category: str
    top_evidence_score: float
    top_evidence_strength: str
    ranking_stability: str
    score_margin_over_second: float
    data_quality_index: float
    provenance: Dict[str, Any]
    non_guilt_clause: str = "This hypothesis evaluation reflects spatio-temporal compatibility with observed data and does not constitute legal proof of responsibility or regulatory violation."
    created_at_utc: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "incident_id": self.incident_id,
            "scenario_id": self.scenario_id,
            "status": self.status,
            "is_unknown_triggered": self.is_unknown_triggered,
            "unknown_trigger_reason": self.unknown_trigger_reason,
            "release_hypothesis": self.release_hypothesis.to_dict(),
            "top_hypothesis_id": self.top_hypothesis_id,
            "top_hypothesis_category": self.top_hypothesis_category,
            "top_evidence_score": self.top_evidence_score,
            "top_evidence_strength": self.top_evidence_strength,
            "ranking_stability": self.ranking_stability,
            "score_margin_over_second": self.score_margin_over_second,
            "candidate_hypotheses": [c.to_dict() for c in self.candidate_hypotheses],
            "data_quality_index": self.data_quality_index,
            "provenance": self.provenance,
            "non_guilt_clause": self.non_guilt_clause,
            "created_at_utc": self.created_at_utc
        }
