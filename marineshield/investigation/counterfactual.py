import copy
import datetime
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple, Union

from marineshield.investigation.schemas import (
    SourceHypothesisContract,
    EvidenceItemContract,
    InvestigationResult,
    VesselObservation,
    EnvironmentalHistory
)
from marineshield.investigation.engine import SourceInvestigationEngine
from marineshield.replay.loader import HistoricalSceneLoader
from marineshield.replay.schemas import FrozenReplayView

@dataclass
class CounterfactualResult:
    """Canonical Counterfactual Sensitivity Analysis Result Payload."""
    incident_id: str
    status: str  # SUCCESS | NOT_APPLICABLE | BLOCKED_TIE_POLICY_REQUIRED
    reason: str
    replay_timestamp_utc: Optional[str]
    original_candidate_count: int
    counterfactual_candidate_count: int
    removed_candidate_id: Optional[str]
    removed_candidate_label: Optional[str]
    original_top_hypothesis_label: Optional[str]
    original_top_hypothesis_score: Optional[float]
    original_attribution_status: str
    counterfactual_attribution_status: str
    is_top_hypothesis_dominant: bool
    is_result_weak_or_tied: bool
    original_result: Dict[str, Any]
    counterfactual_result: Dict[str, Any]
    rank_changes: List[Dict[str, Any]] = field(default_factory=list)
    evidence_provenance: Dict[str, Any] = field(default_factory=dict)
    data_mode: str = "MOCK_HYBRID"
    non_guilt_clause: str = (
        "Counterfactual attribution is a deterministic sensitivity analysis of the source-ranking engine. "
        "It does not establish legal causality, responsibility, or illegal behavior."
    )
    created_at_utc: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "incident_id": self.incident_id,
            "status": self.status,
            "reason": self.reason,
            "replay_timestamp_utc": self.replay_timestamp_utc,
            "original_candidate_count": self.original_candidate_count,
            "counterfactual_candidate_count": self.counterfactual_candidate_count,
            "removed_candidate_id": self.removed_candidate_id,
            "removed_candidate_label": self.removed_candidate_label,
            "original_top_hypothesis_label": self.original_top_hypothesis_label,
            "original_top_hypothesis_score": self.original_top_hypothesis_score,
            "original_attribution_status": self.original_attribution_status,
            "counterfactual_attribution_status": self.counterfactual_attribution_status,
            "is_top_hypothesis_dominant": self.is_top_hypothesis_dominant,
            "is_result_weak_or_tied": self.is_result_weak_or_tied,
            "rank_changes": self.rank_changes,
            "evidence_provenance": self.evidence_provenance,
            "data_mode": self.data_mode,
            "non_guilt_clause": self.non_guilt_clause,
            "original_result": self.original_result,
            "counterfactual_result": self.counterfactual_result,
            "created_at_utc": self.created_at_utc
        }

class CounterfactualAttributionEngine:
    """Deterministic Counterfactual Attribution Engine for MarineShield (Member 4).

    
    Evaluates sensitivity by systematically removing the top-ranked hypothesis
    and re-evaluating the remaining candidate set under identical scoring rules,
    weights, time windows, environmental inputs, and replay constraints.
    """

    def __init__(self, investigation_engine: Optional[SourceInvestigationEngine] = None):
        self.engine = investigation_engine or SourceInvestigationEngine()

    def evaluate_counterfactual(
        self,
        incident_id: str,
        spill_geometry_geojson: Dict[str, Any],
        spill_timestamp_utc: str,
        vessel_observations: List[VesselObservation],
        env_history: Optional[Union[EnvironmentalHistory, Dict[str, Any]]] = None,
        replay_timestamp_utc: Optional[str] = None,
        frozen_view: Optional[FrozenReplayView] = None
    ) -> CounterfactualResult:
        """Executes counterfactual sensitivity analysis without mutating inputs."""
        # 1. Input Immutability: Deep copy vessel observations
        vessels_orig = copy.deepcopy(vessel_observations)

        # Handle default / missing env_history
        if env_history is None:
            env_history = EnvironmentalHistory(
                wind_speed_ms=8.0, wind_direction_deg=220.0, current_u_ms=0.10, current_v_ms=-0.05,
                lookback_hours=6.0, wind_dataset_id="UNAVAILABLE", current_dataset_id="UNAVAILABLE",
                data_quality_index=0.90
            )

        # Extract centroid
        coords = spill_geometry_geojson.get("coordinates", [[[73.20, 18.50], [73.22, 18.50], [73.22, 18.52], [73.20, 18.52], [73.20, 18.50]]])[0]
        lons = [c[0] for c in coords]
        lats = [c[1] for c in coords]
        spill_centroid = (sum(lons)/len(lons), sum(lats)/len(lats))

        # 2. Replay Cutoff Gating (if replay timestamp provided)
        if replay_timestamp_utc:
            replay_loader = HistoricalSceneLoader()
            if frozen_view is None:
                dummy_src = {
                    "ais_candidates": [
                        {
                            "observation_id": f"obs-{idx}",
                            "mmsi": getattr(v, "vessel_mmsi", str(idx)),
                            "timestamp": p["timestamp_utc"],
                            "latitude": p["lat"],
                            "longitude": p["lon"]
                        }
                        for idx, v in enumerate(vessels_orig) for p in getattr(v, "track_points", []) if "timestamp_utc" in p
                    ]
                }
                frozen_view = replay_loader.load_replay(incident_id, replay_timestamp_utc, source_data=dummy_src)

            cutoff_dt = datetime.datetime.fromisoformat(replay_timestamp_utc.replace("Z", "+00:00"))
            filtered_vessels = []
            for v in vessels_orig:
                v_copy = copy.deepcopy(v)
                v_copy.track_points = [
                    p for p in v_copy.track_points
                    if "timestamp_utc" in p and datetime.datetime.fromisoformat(p["timestamp_utc"].replace("Z", "+00:00")) <= cutoff_dt
                ]
                if v_copy.track_points or getattr(v_copy, "source_type", "") == "SAR_DETECTION":
                    filtered_vessels.append(v_copy)
            vessels_eval = filtered_vessels
        else:
            vessels_eval = vessels_orig

        # 3. Original Evaluation
        res_orig: InvestigationResult = self.engine.run_investigation(
            spill_centroid=spill_centroid,
            t_observation_utc=spill_timestamp_utc,
            environmental_history=env_history,
            vessel_observations=vessels_eval,
            incident_id=incident_id
        )
        orig_dict = res_orig.to_dict()

        orig_hypotheses = res_orig.candidate_hypotheses
        if not orig_hypotheses or (res_orig.status == "SOURCE_UNKNOWN" and len(orig_hypotheses) == 0):
            return CounterfactualResult(
                incident_id=incident_id,
                status="NOT_APPLICABLE",
                reason="NO_RANKED_CANDIDATE_AVAILABLE",
                replay_timestamp_utc=replay_timestamp_utc,
                original_candidate_count=len(vessels_eval),
                counterfactual_candidate_count=len(vessels_eval),
                removed_candidate_id=None,
                removed_candidate_label=None,
                original_top_hypothesis_label=None,
                original_top_hypothesis_score=None,
                original_attribution_status=res_orig.status,
                counterfactual_attribution_status=res_orig.status,
                is_top_hypothesis_dominant=False,
                is_result_weak_or_tied=False,
                original_result=orig_dict,
                counterfactual_result=orig_dict,
                rank_changes=[],
                evidence_provenance=orig_dict.get("provenance", {})
            )

        # 4. Tie Policy Evaluation
        if len(orig_hypotheses) >= 2:
            s1 = orig_hypotheses[0].evidence_score
            s2 = orig_hypotheses[1].evidence_score
            if abs(s1 - s2) < 0.001:
                return CounterfactualResult(
                    incident_id=incident_id,
                    status="BLOCKED_TIE_POLICY_REQUIRED",
                    reason="TOP_RANK_TIE_DETECTED_NO_SINGLE_CANDIDATE_REMOVED",
                    replay_timestamp_utc=replay_timestamp_utc,
                    original_candidate_count=len(orig_hypotheses),
                    counterfactual_candidate_count=len(orig_hypotheses),
                    removed_candidate_id=None,
                    removed_candidate_label=None,
                    original_top_hypothesis_label=orig_hypotheses[0].hypothesis_label,
                    original_top_hypothesis_score=s1,
                    original_attribution_status=res_orig.status,
                    counterfactual_attribution_status="BLOCKED_TIE_POLICY_REQUIRED",
                    is_top_hypothesis_dominant=False,
                    is_result_weak_or_tied=True,
                    original_result=orig_dict,
                    counterfactual_result=orig_dict,
                    rank_changes=[],
                    evidence_provenance=orig_dict.get("provenance", {})
                )

        # 5. Remove Top Candidate & Form Counterfactual Vessel List
        top_hyp = orig_hypotheses[0]
        top_cand_id = (
            top_hyp.candidate_entity.get("vessel_id") or
            top_hyp.candidate_entity.get("vessel_mmsi") or
            top_hyp.candidate_entity.get("sar_detection_id") or
            top_hyp.source_hypothesis_id
        )
        top_label = top_hyp.hypothesis_label

        cf_vessels = [
            v for v in vessels_eval
            if v.vessel_id != top_cand_id and getattr(v, "vessel_mmsi", None) != top_cand_id and f"vsl-mmsi-{getattr(v, 'vessel_mmsi', '')}" != top_cand_id and f"dark-vessel-{getattr(v, 'sar_vessel_detection_id', '')}" != top_cand_id
        ]

        # 6. Counterfactual Evaluation
        res_cf: InvestigationResult = self.engine.run_investigation(
            spill_centroid=spill_centroid,
            t_observation_utc=spill_timestamp_utc,
            environmental_history=env_history,
            vessel_observations=cf_vessels,
            incident_id=incident_id
        )
        cf_dict = res_cf.to_dict()
        cf_hypotheses = res_cf.candidate_hypotheses

        # 7. Compute Rank & Score Movements
        rank_changes = []
        orig_map = {h.hypothesis_label: (idx + 1, h.evidence_score) for idx, h in enumerate(orig_hypotheses)}

        for idx_cf, h_cf in enumerate(cf_hypotheses, start=1):
            lbl = h_cf.hypothesis_label
            score_cf = h_cf.evidence_score
            cid = (
                h_cf.candidate_entity.get("vessel_id") or
                h_cf.candidate_entity.get("vessel_mmsi") or
                h_cf.candidate_entity.get("sar_detection_id") or
                h_cf.source_hypothesis_id
            )
            if lbl in orig_map:
                rank_orig, score_orig = orig_map[lbl]
                rank_delta = rank_orig - idx_cf  # Positive means moved up in rank
                score_delta = round(score_cf - score_orig, 4)
            else:
                rank_orig, score_orig, rank_delta, score_delta = None, None, None, None

            rank_changes.append({
                "hypothesis_label": lbl,
                "candidate_id": cid,
                "original_rank": rank_orig,
                "original_score": score_orig,
                "counterfactual_rank": idx_cf,
                "counterfactual_score": score_cf,
                "rank_change": rank_delta,
                "score_change": score_delta
            })

        # 8. Dominance & Stability Assessment
        top_score = top_hyp.evidence_score
        second_score = orig_hypotheses[1].evidence_score if len(orig_hypotheses) > 1 else 0.0
        score_margin = top_score - second_score

        is_weak_or_tied = (score_margin < 0.15 or top_score < 60.0 or top_hyp.evidence_strength in ["WEAK_COMPATIBILITY", "INSUFFICIENT_EVIDENCE"])
        is_dominant = (score_margin >= 0.15 and not is_weak_or_tied and (res_cf.status == "SOURCE_UNKNOWN" or len(cf_hypotheses) == 0 or res_orig.status != "SOURCE_UNKNOWN"))

        return CounterfactualResult(
            incident_id=incident_id,
            status="SUCCESS",
            reason="COUNTERFACTUAL_EVALUATION_COMPLETED",
            replay_timestamp_utc=replay_timestamp_utc,
            original_candidate_count=len(orig_hypotheses),
            counterfactual_candidate_count=len(cf_hypotheses),
            removed_candidate_id=top_cand_id,
            removed_candidate_label=top_label,
            original_top_hypothesis_label=top_label,
            original_top_hypothesis_score=top_score,
            original_attribution_status=res_orig.status,
            counterfactual_attribution_status=res_cf.status,
            is_top_hypothesis_dominant=is_dominant,
            is_result_weak_or_tied=is_weak_or_tied,
            original_result=orig_dict,
            counterfactual_result=cf_dict,
            rank_changes=rank_changes,
            evidence_provenance=orig_dict.get("provenance", {})
        )
