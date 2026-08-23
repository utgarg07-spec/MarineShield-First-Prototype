import uuid
import datetime
from typing import Dict, Any, List, Optional, Tuple, Union

from marineshield.investigation.schemas import (
    ReleaseHypothesisContract,
    SourceHypothesisContract,
    EnvironmentalHistory,
    VesselObservation,
    InvestigationResult
)
from marineshield.investigation.scoring_config import EvidenceWeights, InvestigationThresholds
from marineshield.investigation.release_reconstructor import BackwardReleaseReconstructor
from marineshield.investigation.candidate_filter import CandidateFilterAndEvaluator
from marineshield.investigation.evidence_engine import EvidenceContradictionEngine

class SourceInvestigationEngine:
    """Production Release Reconstruction and Source-Investigation Engine for MarineShield.

    
    Pipeline:
    Detected Spill -> Historical Environmental Conditions -> Backward Reconstruction
    -> Release Region / Time Window -> Candidate Vessel Filtering -> Source Hypotheses
    -> Evidence + Contradiction Analysis -> Ranking -> Unknown if evidence is insufficient.
    """
    def __init__(
        self,
        weights: Optional[EvidenceWeights] = None,
        thresholds: Optional[InvestigationThresholds] = None
    ):
        self.weights = weights or EvidenceWeights()
        self.thresholds = thresholds or InvestigationThresholds()
        self.reconstructor = BackwardReleaseReconstructor()
        self.candidate_evaluator = CandidateFilterAndEvaluator()
        self.evidence_engine = EvidenceContradictionEngine(self.weights, self.thresholds)
        self.engine_version = "source-investigation-engine-v1.0.0"

    def run_investigation(
        self,
        spill_centroid: Tuple[float, float],
        t_observation_utc: str,
        environmental_history: Union[EnvironmentalHistory, Dict[str, Any]],
        vessel_observations: Optional[List[Union[VesselObservation, Dict[str, Any]]]] = None,
        ais_coverage_percentage: float = 100.0,
        data_quality_index: float = 0.90,
        incident_id: Optional[str] = None,
        spill_geometry_id: Optional[str] = None,
        scenario_id: str = "SCENARIO-LIVE"
    ) -> InvestigationResult:
        """Executes full release reconstruction and deterministic source attribution pipeline."""
        inc_id = incident_id or str(uuid.uuid4())
        geom_id = spill_geometry_id or str(uuid.uuid4())
        vessels = vessel_observations or []

        # 1. Standardize Environmental History
        if isinstance(environmental_history, dict):
            env_hist = EnvironmentalHistory(**environmental_history)
        else:
            env_hist = environmental_history

        # Effective DQI combines environmental and sensor quality
        effective_dqi = min(data_quality_index, env_hist.data_quality_index)

        # 2. Data Quality / Abstention Gating (§10 / §7)
        if effective_dqi < self.thresholds.min_dqi_for_execution:
            dummy_release = ReleaseHypothesisContract(
                incident_id=inc_id,
                spill_geometry_id=geom_id,
                hypothesis_state="ABSTAINED",
                t_observation_utc=t_observation_utc
            )
            return InvestigationResult(
                incident_id=inc_id,
                scenario_id=scenario_id,
                status="ABSTAINED",
                is_unknown_triggered=True,
                unknown_trigger_reason="LOW_DATA_QUALITY",
                release_hypothesis=dummy_release,
                candidate_hypotheses=[],
                top_hypothesis_id=None,
                top_hypothesis_category="UNKNOWN_SOURCE",
                top_evidence_score=0.0,
                top_evidence_strength="INSUFFICIENT_EVIDENCE",
                ranking_stability="FRAGILE_RANKING",
                score_margin_over_second=0.0,
                data_quality_index=round(effective_dqi, 2),
                provenance={
                    "engine_version": self.engine_version,
                    "weights_version": self.weights.version_id,
                    "execution_timestamp_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                }
            )

        # 3. Backward Lagrangian Release Reconstruction
        release_hypothesis = self.reconstructor.reconstruct_release(
            spill_centroid=spill_centroid,
            t_observation_utc=t_observation_utc,
            environmental_history=env_hist,
            spill_geometry_id=geom_id,
            incident_id=inc_id
        )

        # 4. Candidate Vessel Filtering & Evaluation
        candidate_payloads = []
        for idx, v_item in enumerate(vessels, start=1):
            if isinstance(v_item, dict):
                v_obj = VesselObservation(**v_item)
            else:
                v_obj = v_item

            eval_res = self.candidate_evaluator.evaluate_candidate(v_obj, release_hypothesis)
            
            cand_payload = {
                "source_hypothesis_id": f"src-hyp-{inc_id[:8]}-{idx:02d}",
                "hypothesis_label": f"H_{idx}",
                "source_category": eval_res["source_category"],
                "candidate_entity": eval_res["candidate_entity"],
                "component_scores": eval_res["component_scores"],
                "supporting_evidence": eval_res["supporting_evidence"],
                "contradictory_evidence": eval_res["contradictory_evidence"],
                "behavioral_anomaly_detected": eval_res["behavioral_anomaly_detected"],
                "unmatched_sar_target": eval_res["unmatched_sar_target"]
            }
            candidate_payloads.append(cand_payload)

        # 5. Deterministic Evidence Scoring & Ranking via EvidenceContradictionEngine
        incident_engine_payload = {
            "incident_id": inc_id,
            "scenario_id": scenario_id,
            "data_quality_index": effective_dqi,
            "ais_coverage_percentage": ais_coverage_percentage,
            "candidate_hypotheses": candidate_payloads
        }

        engine_result = self.evidence_engine.process_incident(incident_engine_payload)

        # Convert scored candidates to SourceHypothesisContract instances
        candidate_contracts = []
        for c_dict in engine_result["candidate_hypotheses"]:
            contract = SourceHypothesisContract(
                source_hypothesis_id=c_dict["source_hypothesis_id"],
                incident_id=inc_id,
                release_hypothesis_id=release_hypothesis.release_hypothesis_id,
                hypothesis_label=c_dict["hypothesis_label"],
                source_category=c_dict["source_category"],
                candidate_entity=c_dict["candidate_entity"],
                component_scores=c_dict["component_scores"],
                component_breakdown=c_dict["component_breakdown"],
                evidence_score=c_dict["evidence_score"],
                evidence_strength=c_dict["evidence_strength"],
                ranking_position=c_dict["ranking_position"],
                counterfactual_analysis=c_dict.get("counterfactual_analysis", {}),
                supporting_evidence=c_dict["supporting_evidence"],
                contradictory_evidence=c_dict["contradictory_evidence"],
                behavioral_anomaly_detected=c_dict["behavioral_anomaly_detected"],
                unmatched_sar_target=c_dict["unmatched_sar_target"]
            )
            candidate_contracts.append(contract)

        return InvestigationResult(
            incident_id=inc_id,
            scenario_id=scenario_id,
            status=engine_result["status"],
            is_unknown_triggered=engine_result["is_unknown_triggered"],
            unknown_trigger_reason=engine_result["unknown_trigger_reason"],
            release_hypothesis=release_hypothesis,
            candidate_hypotheses=candidate_contracts,
            top_hypothesis_id=engine_result["top_hypothesis_id"],
            top_hypothesis_category=engine_result["top_hypothesis_category"],
            top_evidence_score=engine_result["top_evidence_score"],
            top_evidence_strength=engine_result["top_evidence_strength"],
            ranking_stability=engine_result["ranking_stability"],
            score_margin_over_second=engine_result["score_margin_over_second"],
            data_quality_index=round(effective_dqi, 2),
            provenance={
                "engine_version": self.engine_version,
                "weights_version": self.weights.version_id,
                "reconstruction_engine": release_hypothesis.reconstruction_method["engine"],
                "execution_timestamp_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            }
        )
