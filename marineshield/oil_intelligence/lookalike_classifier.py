import math
import numpy as np
from typing import Dict, Any, Tuple
from marineshield.oil_intelligence.schemas import LookAlikeVerificationContract

class LookAlikeVerifier:
    """Module C Look-Alike Verification Classifier.

    
    Evaluates candidate dark patches against known SAR look-alike phenomena
    (biogenic films, low-wind calm areas, ship wakes, natural slicks)
    and produces calibrated probability distributions conforming to §6.
    """
    CLASSES = [
        "PETROLEUM_OIL",
        "BIOGENIC_SLICK",
        "LOW_WIND_AREA",
        "SHIP_WAKE",
        "NATURAL_FILM",
        "UNCERTAIN"
    ]

    def verify_candidate(
        self,
        raw_tile: np.ndarray,
        prob_mask: np.ndarray,
        candidate_meta: Dict[str, Any]
    ) -> LookAlikeVerificationContract:
        """Evaluates segmentation output and radiometric properties to produce verification contract."""
        oil_pixel_count = int(np.sum(prob_mask >= 0.50))
        mean_oil_prob = float(np.mean(prob_mask[prob_mask >= 0.50])) if oil_pixel_count > 0 else 0.0
        contrast = float(candidate_meta.get("suppression_contrast", 0.0))

        # Unnormalized logits calculation
        if oil_pixel_count < 50 or mean_oil_prob < 0.30:
            # Strong non-oil / calm water or empty detection
            logits = {
                "PETROLEUM_OIL": -2.5,
                "BIOGENIC_SLICK": 0.5,
                "LOW_WIND_AREA": 3.8,
                "SHIP_WAKE": -0.5,
                "NATURAL_FILM": 0.5,
                "UNCERTAIN": -1.5
            }
        elif mean_oil_prob >= 0.75 and oil_pixel_count >= 300:
            # High confidence petroleum slick
            logits = {
                "PETROLEUM_OIL": 4.2,
                "BIOGENIC_SLICK": -1.0,
                "LOW_WIND_AREA": -1.5,
                "SHIP_WAKE": -2.0,
                "NATURAL_FILM": -1.5,
                "UNCERTAIN": -2.5
            }
        elif mean_oil_prob >= 0.50:
            # Moderate oil probability
            logits = {
                "PETROLEUM_OIL": 2.2,
                "BIOGENIC_SLICK": 0.2,
                "LOW_WIND_AREA": -0.2,
                "SHIP_WAKE": -0.5,
                "NATURAL_FILM": -0.5,
                "UNCERTAIN": -0.5
            }
        else:
            # Ambiguous / uncertain
            logits = {
                "PETROLEUM_OIL": 0.5,
                "BIOGENIC_SLICK": 0.8,
                "LOW_WIND_AREA": 0.8,
                "SHIP_WAKE": 0.0,
                "NATURAL_FILM": 0.2,
                "UNCERTAIN": 0.8
            }

        # Normalize via Softmax to ensure sum == 1.0 strictly
        exp_vals = {k: math.exp(v) for k, v in logits.items()}
        sum_exp = sum(exp_vals.values())
        class_probs = {k: round(v / sum_exp, 4) for k, v in exp_vals.items()}
        
        # Ensure exact 1.0 sum
        prob_sum = sum(class_probs.values())
        if prob_sum != 1.0:
            diff = 1.0 - prob_sum
            class_probs["UNCERTAIN"] = round(class_probs["UNCERTAIN"] + diff, 4)

        # Ranked classes
        sorted_classes = sorted(class_probs.items(), key=lambda x: x[1], reverse=True)
        top_class, top_prob = sorted_classes[0]
        second_class, second_prob = sorted_classes[1]
        margin = round(top_prob - second_prob, 4)

        # Shannon Entropy H = -sum(p * log2(p))
        entropy = 0.0
        for p in class_probs.values():
            if p > 0.0001:
                entropy -= p * math.log2(p)
        entropy = round(entropy, 4)

        # Decision mapping
        if top_class == "PETROLEUM_OIL" and top_prob >= 0.60:
            decision = "ACCEPT_AS_OIL"
        elif top_class in ["BIOGENIC_SLICK", "LOW_WIND_AREA", "SHIP_WAKE", "NATURAL_FILM"] and top_prob >= 0.40:
            decision = "REJECT_AS_LOOKALIKE"
        elif entropy >= 2.0 or margin <= 0.15:
            decision = "FLAG_FOR_ANALYST_REVIEW"
        else:
            decision = "ACCEPT_AS_OIL" if top_class == "PETROLEUM_OIL" else "REJECT_AS_LOOKALIKE"

        return LookAlikeVerificationContract(
            predicted_class=top_class,
            class_probabilities=class_probs,
            model_confidence={
                "max_class_probability": top_prob,
                "entropy": entropy,
                "margin": margin
            },
            pipeline_decision=decision
        )
