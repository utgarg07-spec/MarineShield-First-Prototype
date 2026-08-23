from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass(frozen=True)
class EvidenceWeights:
    """Canonical weights configuration for the deterministic evidence scoring formula.

    
    Formula:
    E(H) = max(0, min(100, w_s*S_spatial + w_t*S_temporal + w_r*S_trajectory +
                           w_d*S_drift + w_v*S_vessel + w_b*S_behavior - w_c*C_contradiction))
    """
    version_id: str = "m4-weights-v1.0-canonical"
    calibration_source: str = "HEURISTIC_BASELINE"
    w_spatial: float = 0.20
    w_temporal: float = 0.15
    w_trajectory: float = 0.15
    w_drift: float = 0.20
    w_vessel: float = 0.15
    w_behavior: float = 0.15
    w_contradiction: float = 0.20

    def to_dict(self) -> Dict[str, Any]:
        return {
            "weights_version_id": self.version_id,
            "calibration_source": self.calibration_source,
            "weights": {
                "w_spatial": self.w_spatial,
                "w_temporal": self.w_temporal,
                "w_trajectory": self.w_trajectory,
                "w_drift": self.w_drift,
                "w_vessel": self.w_vessel,
                "w_behavior": self.w_behavior,
                "w_contradiction": self.w_contradiction
            }
        }


@dataclass(frozen=True)
class InvestigationThresholds:
    """Canonical decision thresholds for hypothesis ranking, strength classification, and abstention."""
    # Evidence Strength Thresholds (§6)
    strong_min_score: float = 75.0
    moderate_min_score: float = 50.0
    weak_min_score: float = 30.0
    max_contradiction_for_strong: float = 0.0
    min_dqi_for_strong: float = 0.70
    min_dqi_for_moderate: float = 0.50

    # Counterfactual Stability Margins (§9)
    dominant_margin_threshold: float = 15.0
    ambiguous_margin_threshold: float = 5.0

    # Unknown & Abstention Triggers (§7)
    unknown_score_threshold: float = 30.0
    ais_blackout_trigger_pct: float = 80.0
    min_dqi_for_execution: float = 0.35
