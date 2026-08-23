import uuid
import datetime
from typing import Dict, Any, List, Optional
from marineshield.investigation.scoring_config import EvidenceWeights, InvestigationThresholds

class EvidenceContradictionEngine:
    """Deterministic Evidence + Contradiction Engine for MarineShield Incident Attribution.

    
    Core Principles:
    1. Deterministic Calculation: Same inputs + same weights = exact same output score.
    2. Non-Suppression: Contradictions are explicitly recorded and deduct from evidence score.
    3. Responsible AI: No LLMs in scoring loop, non-legal terminology, UNKNOWN is a 1st-class output.
    """
    def __init__(self, weights: Optional[EvidenceWeights] = None, thresholds: Optional[InvestigationThresholds] = None):
        self.weights = weights or EvidenceWeights()
        self.thresholds = thresholds or InvestigationThresholds()
        self.algorithm_version = "deterministic-evidence-v1.0.0"

    def calculate_evidence_score(self, component_scores: Dict[str, float]) -> Dict[str, Any]:
        """Calculates deterministic score E(H) and component breakdown.

        
        E(H) = max(0, min(100, w_s*S_spatial + w_t*S_temporal + w_r*S_trajectory +
                               w_d*S_drift + w_v*S_vessel + w_b*S_behavior - w_c*C_contradiction))
        """
        s_spatial = float(component_scores.get("spatial", 0.0))
        s_temporal = float(component_scores.get("temporal", 0.0))
        s_trajectory = float(component_scores.get("trajectory", 0.0))
        s_drift = float(component_scores.get("drift", 0.0))
        s_vessel = float(component_scores.get("vessel", 0.0))
        s_behavior = float(component_scores.get("behavior", 0.0))
        c_contradiction = float(component_scores.get("contradiction", 0.0))

        contrib_spatial = self.weights.w_spatial * s_spatial
        contrib_temporal = self.weights.w_temporal * s_temporal
        contrib_trajectory = self.weights.w_trajectory * s_trajectory
        contrib_drift = self.weights.w_drift * s_drift
        contrib_vessel = self.weights.w_vessel * s_vessel
        contrib_behavior = self.weights.w_behavior * s_behavior
        deduction_contradiction = self.weights.w_contradiction * c_contradiction

        raw_score = (contrib_spatial + contrib_temporal + contrib_trajectory +
                     contrib_drift + contrib_vessel + contrib_behavior -
                     deduction_contradiction)
        
        final_score = max(0.0, min(100.0, raw_score))

        return {
            "evidence_score": round(final_score, 2),
            "raw_unclamped_score": round(raw_score, 4),
            "component_breakdown": {
                "spatial_score": {"raw_score": s_spatial, "weight": self.weights.w_spatial, "weighted_contribution": round(contrib_spatial, 3)},
                "temporal_score": {"raw_score": s_temporal, "weight": self.weights.w_temporal, "weighted_contribution": round(contrib_temporal, 3)},
                "trajectory_score": {"raw_score": s_trajectory, "weight": self.weights.w_trajectory, "weighted_contribution": round(contrib_trajectory, 3)},
                "drift_score": {"raw_score": s_drift, "weight": self.weights.w_drift, "weighted_contribution": round(contrib_drift, 3)},
                "vessel_score": {"raw_score": s_vessel, "weight": self.weights.w_vessel, "weighted_contribution": round(contrib_vessel, 3)},
                "behavior_score": {"raw_score": s_behavior, "weight": self.weights.w_behavior, "weighted_contribution": round(contrib_behavior, 3)},
                "contradiction_penalty": {"raw_penalty": c_contradiction, "weight": self.weights.w_contradiction, "weighted_deduction": round(deduction_contradiction, 3)}
            }
        }

    def classify_evidence_strength(self, evidence_score: float, contradiction_score: float = 0.0, dqi: float = 1.0) -> str:
        """Classifies evidence strength level according to §6 thresholds."""
        if dqi < self.thresholds.min_dqi_for_moderate or evidence_score < self.thresholds.weak_min_score:
            return "INSUFFICIENT_EVIDENCE"
        if evidence_score >= self.thresholds.strong_min_score and contradiction_score <= 10.0 and dqi >= self.thresholds.min_dqi_for_strong:
            return "STRONG_COMPATIBILITY"
        if evidence_score >= self.thresholds.moderate_min_score and contradiction_score < 20.0:
            return "MODERATE_COMPATIBILITY"
        return "WEAK_COMPATIBILITY"

    def evaluate_counterfactual(self, ranked_candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Performs counterfactual attribution analysis (§9) evaluating ranking stability upon top candidate removal."""
        if not ranked_candidates:
            return {
                "delta_score_margin": 0.0,
                "ranking_stability": "FRAGILE_RANKING",
                "explanation": "No candidate hypotheses evaluated."
            }

        top_cand = ranked_candidates[0]
        top_score = top_cand.get("evidence_score", 0.0)

        # Filter out explicit UNKNOWN hypotheses when calculating candidate-to-candidate margin
        valid_candidates = [c for c in ranked_candidates if c.get("source_category") != "UNKNOWN_SOURCE"]
        
        if len(valid_candidates) > 1:
            second_cand = valid_candidates[1]
            second_score = second_cand.get("evidence_score", 0.0)
            margin = round(top_score - second_score, 2)
        else:
            second_cand = None
            second_score = 0.0
            margin = top_score

        if top_score < self.thresholds.unknown_score_threshold:
            stability = "FRAGILE_RANKING"
            expl = f"Top candidate score ({top_score:.1f}) is below threshold {self.thresholds.unknown_score_threshold}; UNKNOWN triggered."
        elif margin >= self.thresholds.dominant_margin_threshold:
            stability = "ROBUST_DOMINANT_HYPOTHESIS"
            expl = f"Top candidate has decisive margin ({margin:.1f} pts) over second alternative ({second_score:.1f} pts)."
        elif margin <= self.thresholds.ambiguous_margin_threshold and second_score >= self.thresholds.moderate_min_score:
            stability = "AMBIGUOUS_CLOSE_ALTERNATIVES"
            expl = f"Top candidate and second alternative are in close statistical contention (delta: {margin:.1f} pts)."
        else:
            stability = "MARGINAL"
            expl = f"Top candidate leads by moderate margin ({margin:.1f} pts)."

        return {
            "baseline_top_hypothesis_id": top_cand.get("source_hypothesis_id"),
            "baseline_top_score": top_score,
            "second_ranked_baseline_score": second_score,
            "delta_score_margin": margin,
            "ranking_stability": stability,
            "explanation": expl
        }

    def process_incident(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Main investigation pipeline processing canonical incident payload or synthetic fixture."""
        incident_id = payload.get("incident_id", str(uuid.uuid4()))
        scenario_id = payload.get("scenario_id", "SCENARIO-CUSTOM")
        
        # 1. Data Quality & Abstention Extraction (§10 of ML / §7 of Investigation)
        dqi = 1.0
        if "data_quality_index" in payload:
            dqi_raw = payload["data_quality_index"]
            dqi = float(dqi_raw.get("overall_dqi", 1.0) if isinstance(dqi_raw, dict) else dqi_raw)
        elif "release_hypothesis" in payload and "data_quality" in payload["release_hypothesis"]:
            dqi = float(payload["release_hypothesis"]["data_quality"].get("index", 1.0))
        elif "abstention" in payload and "triggering_values" in payload["abstention"]:
            dqi = float(payload["abstention"]["triggering_values"].get("data_quality_index", 1.0))

        is_abstained = (
            payload.get("abstention_state") == "ABSTAINED" or
            payload.get("abstention", {}).get("abstention_state") == "ABSTAINED" or
            payload.get("release_hypothesis", {}).get("hypothesis_state") == "ABSTAINED" or
            dqi < self.thresholds.min_dqi_for_execution
        )

        if is_abstained:
            reason = payload.get("abstention_reason") or payload.get("abstention", {}).get("abstention_reason_primary", "LOW_DATA_QUALITY")
            return {
                "incident_id": incident_id,
                "scenario_id": scenario_id,
                "status": "ABSTAINED",
                "abstention_state": "ABSTAINED",
                "abstention_reason": reason,
                "can_proceed_to_attribution": False,
                "data_quality_index": dqi,
                "explanation": f"Investigation pipeline abstained due to severe data quality deficit (DQI={dqi:.2f} < {self.thresholds.min_dqi_for_execution:.2f}).",
                "recommendation": "ANALYST_REVIEW_REQUIRED"
            }

        # 2. Score and Rank Candidate Hypotheses
        raw_candidates = payload.get("candidate_hypotheses", [])
        scored_candidates = []

        for cand in raw_candidates:
            c_scores = cand.get("component_scores", {})
            score_eval = self.calculate_evidence_score(c_scores)
            ev_score = score_eval["evidence_score"]
            c_contradiction = c_scores.get("contradiction", 0.0)
            strength = self.classify_evidence_strength(ev_score, c_contradiction, dqi)

            cand_ent = cand.get("candidate_entity", {})
            source_cat = cand.get("source_category", "VESSEL_IDENTIFIED")
            is_unmatched_sar = (
                source_cat == "VESSEL_UNTRACKED_DARK" or
                cand_ent.get("sar_vessel_detection_id") is not None or
                cand.get("unmatched_sar_target", False)
            )

            # Check behavioral anomaly flags
            is_anomaly = cand.get("behavioral_anomaly_detected", False) or (c_scores.get("behavior", 0.0) >= 90.0)

            scored_item = {
                "source_hypothesis_id": cand.get("source_hypothesis_id", str(uuid.uuid4())),
                "hypothesis_label": cand.get("hypothesis_label", "H"),
                "source_category": source_cat,
                "candidate_entity": cand_ent,
                "component_scores": c_scores,
                "component_breakdown": score_eval["component_breakdown"],
                "evidence_score": ev_score,
                "evidence_strength": strength,
                "supporting_evidence": cand.get("supporting_evidence", []),
                "contradictory_evidence": cand.get("contradictory_evidence", []),
                "behavioral_anomaly_detected": is_anomaly,
                "unmatched_sar_target": is_unmatched_sar
            }
            scored_candidates.append(scored_item)

        # Sort descending by evidence score
        scored_candidates.sort(key=lambda x: x["evidence_score"], reverse=True)
        for rank, cand in enumerate(scored_candidates, start=1):
            cand["ranking_position"] = rank

        # 3. Counterfactual Stability Analysis
        cf_eval = self.evaluate_counterfactual(scored_candidates)

        # Update counterfactual per candidate
        for cand in scored_candidates:
            if cand["ranking_position"] == 1:
                cand["counterfactual_analysis"] = {
                    "delta_score_without_this_candidate": cf_eval["delta_score_margin"],
                    "ranking_stability": cf_eval["ranking_stability"]
                }
            else:
                cand["counterfactual_analysis"] = {
                    "delta_score_without_this_candidate": 0.0,
                    "ranking_stability": "MARGINAL"
                }

        # 4. Unknown Trigger Analysis (§7)
        top_cand = scored_candidates[0] if scored_candidates else None
        top_score = top_cand["evidence_score"] if top_cand else 0.0
        
        # Check AIS coverage from payload or unknown_state block
        ais_cov = 100.0
        if "ais_coverage_percentage" in payload:
            ais_cov = float(payload["ais_coverage_percentage"])
        elif "unknown_state" in payload and "diagnostic_summary" in payload["unknown_state"]:
            ais_cov = float(payload["unknown_state"]["diagnostic_summary"].get("ais_coverage_percentage", 100.0))

        unknown_triggered = False
        unknown_reason = None

        if ais_cov <= (100.0 - self.thresholds.ais_blackout_trigger_pct) or payload.get("unknown_state", {}).get("trigger_condition") == "AIS_DATA_BLACKOUT":
            unknown_triggered = True
            unknown_reason = "AIS_DATA_BLACKOUT"
        elif not top_cand or top_score < self.thresholds.unknown_score_threshold:
            unknown_triggered = True
            unknown_reason = "ALL_CANDIDATES_BELOW_THRESHOLD"
        elif payload.get("status") == "SOURCE_UNKNOWN":
            unknown_triggered = True
            unknown_reason = payload.get("unknown_trigger_reason", "INSUFFICIENT_EVIDENCE")

        # 5. Build Result Envelope
        top_hyp_id = None
        if unknown_triggered:
            # Look for an explicit unknown hypothesis in candidates if available
            unk_cand = next((c for c in scored_candidates if c["source_category"] == "UNKNOWN_SOURCE"), None)
            top_hyp_id = unk_cand["source_hypothesis_id"] if unk_cand else "src-unknown"
        else:
            top_hyp_id = top_cand["source_hypothesis_id"] if top_cand else None

        result = {
            "incident_id": incident_id,
            "scenario_id": scenario_id,
            "status": "SOURCE_UNKNOWN" if unknown_triggered else "ATTRIBUTED_CANDIDATES_EVALUATED",
            "is_unknown_triggered": unknown_triggered,
            "unknown_trigger_reason": unknown_reason,
            "top_hypothesis_id": top_hyp_id,
            "top_hypothesis_category": "UNKNOWN_SOURCE" if unknown_triggered else top_cand["source_category"],
            "top_evidence_score": top_score,
            "top_evidence_strength": "INSUFFICIENT_EVIDENCE" if unknown_triggered else top_cand["evidence_strength"],
            "ranking_stability": cf_eval["ranking_stability"],
            "score_margin_over_second": cf_eval["delta_score_margin"],
            "candidate_hypotheses": scored_candidates,
            "counterfactual_analysis": cf_eval,
            "provenance": {
                "algorithm_version": self.algorithm_version,
                "weights_version": self.weights.version_id,
                "execution_timestamp_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "reproducibility_seed": 42
            },
            "non_guilt_clause": "This hypothesis evaluation reflects spatio-temporal compatibility with observed data and does not constitute legal proof of responsibility or regulatory violation."
        }
        return result
