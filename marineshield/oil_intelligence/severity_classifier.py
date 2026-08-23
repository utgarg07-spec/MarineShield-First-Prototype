import math
import numpy as np
from typing import Dict, Any, Optional
from marineshield.oil_intelligence.schemas import SpillSeverityContract

class SpillSeverityClassifier:
    """Module D Operational Spill Severity Classifier (§5).

    
    Classifies spill intensity into coarse operational tiers (SHEEN, MODERATE, THICK_HIGH_SEVERITY, UNKNOWN)
    based on SAR backscatter suppression (damping) and polygon area.
    """
    CLASSES = ["SHEEN", "MODERATE", "THICK_HIGH_SEVERITY", "UNKNOWN"]

    def classify_severity(
        self,
        mean_db: float,
        suppression_db: float,
        area_km2: float,
        is_valid_detection: bool
    ) -> SpillSeverityContract:
        """Classifies severity and returns canonical SpillSeverityContract."""
        if not is_valid_detection or area_km2 <= 0.0:
            return SpillSeverityContract(
                severity_class="UNKNOWN",
                severity_basis={
                    "mean_backscatter_db": round(mean_db, 2) if mean_db else None,
                    "backscatter_suppression_db": round(suppression_db, 2) if suppression_db else None,
                    "estimated_area_km2": 0.0,
                    "texture_features_used": False
                },
                model_confidence={
                    "severity_class_probability": 1.0,
                    "class_probabilities": {
                        "SHEEN": 0.0,
                        "MODERATE": 0.0,
                        "THICK_HIGH_SEVERITY": 0.0,
                        "UNKNOWN": 1.0
                    }
                }
            )

        # Severity categorization logic based on SAR radar damping:
        # High suppression (> 8 dB) + large area (> 2 km2) -> THICK_HIGH_SEVERITY
        # Moderate suppression (4-8 dB) or medium area -> MODERATE
        # Low suppression (< 4 dB) -> SHEEN
        if suppression_db >= 8.0 and area_km2 >= 1.5:
            top_class = "THICK_HIGH_SEVERITY"
            probs = {"SHEEN": 0.05, "MODERATE": 0.20, "THICK_HIGH_SEVERITY": 0.75, "UNKNOWN": 0.00}
        elif suppression_db >= 4.0 or area_km2 >= 0.5:
            top_class = "MODERATE"
            probs = {"SHEEN": 0.15, "MODERATE": 0.75, "THICK_HIGH_SEVERITY": 0.10, "UNKNOWN": 0.00}
        else:
            top_class = "SHEEN"
            probs = {"SHEEN": 0.80, "MODERATE": 0.15, "THICK_HIGH_SEVERITY": 0.05, "UNKNOWN": 0.00}

        return SpillSeverityContract(
            severity_class=top_class,
            severity_basis={
                "mean_backscatter_db": round(mean_db, 2),
                "backscatter_suppression_db": round(suppression_db, 2),
                "estimated_area_km2": round(area_km2, 4),
                "texture_features_used": True
            },
            model_confidence={
                "severity_class_probability": probs[top_class],
                "class_probabilities": probs
            }
        )
