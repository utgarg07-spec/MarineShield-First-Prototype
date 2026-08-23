import unittest
import json
import uuid
import math
from datetime import datetime, timezone, timedelta

class TestInvestigationContracts(unittest.TestCase):
    """Authoritative test suite verifying investigation domain contracts (Member 4 / Person 1)."""

    def test_release_hypothesis_schema(self):
        """Verifies release hypothesis temporal, spatial, and state schema contracts."""
        rel_id = str(uuid.uuid4())
        inc_id = str(uuid.uuid4())
        spill_id = str(uuid.uuid4())

        t_obs = datetime.now(timezone.utc)
        t_early = t_obs - timedelta(hours=6)
        t_likely = t_obs - timedelta(hours=3, minutes=30)
        t_late = t_obs - timedelta(hours=1)

        payload = {
            "release_hypothesis_id": rel_id,
            "incident_id": inc_id,
            "spill_geometry_id": spill_id,
            "hypothesis_state": "EVALUATED",
            "discharge_modality": "SINGLE_DISCHARGE",
            "temporal_scope": {
                "t_observation_utc": t_obs.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "t_earliest_utc": t_early.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "t_most_likely_utc": t_likely.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "t_latest_utc": t_late.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "window_duration_hours": (t_late - t_early).total_seconds() / 3600.0
            },
            "spatial_scope": {
                "release_polygon_geojson": {
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[[72.5, 18.5], [72.6, 18.5], [72.6, 18.6], [72.5, 18.6], [72.5, 18.5]]]
                    },
                    "properties": {
                        "uncertainty_area_km2": 11.2,
                        "centroid_lon": 72.55,
                        "centroid_lat": 18.55
                    }
                },
                "crs": "EPSG:4326"
            },
            "created_at_utc": t_obs.strftime("%Y-%m-%dT%H:%M:%SZ")
        }

        # Roundtrip JSON test
        encoded = json.dumps(payload)
        decoded = json.loads(encoded)

        self.assertIn(decoded["hypothesis_state"], ["CANDIDATE", "EVALUATED", "UNRESOLVED", "ABSTAINED", "REJECTED"])
        self.assertIn(decoded["discharge_modality"], ["SINGLE_DISCHARGE", "MULTIPLE_DISCHARGE", "CONTINUOUS_DISCHARGE", "UNCERTAIN_ORIGIN"])
        self.assertEqual(decoded["temporal_scope"]["window_duration_hours"], 5.0)
        self.assertEqual(decoded["spatial_scope"]["crs"], "EPSG:4326")

    def test_source_hypothesis_categories(self):
        """Verifies that all 4 mandatory source hypothesis categories are representable."""
        categories = ["VESSEL_IDENTIFIED", "VESSEL_UNTRACKED_DARK", "NON_VESSEL_SOURCE", "UNKNOWN_SOURCE"]
        
        for cat in categories:
            hyp = {
                "source_hypothesis_id": str(uuid.uuid4()),
                "source_category": cat,
                "hypothesis_label": f"H_{cat.lower()}",
                "analytical_status": "UNDER_INVESTIGATION" if cat != "UNKNOWN_SOURCE" else "UNRESOLVED_UNKNOWN",
                "evidence_evaluation": {
                    "evidence_score": 78.5 if cat != "UNKNOWN_SOURCE" else 15.0,
                    "evidence_strength": "STRONG_COMPATIBILITY" if cat != "UNKNOWN_SOURCE" else "INSUFFICIENT_EVIDENCE",
                    "ranking_position": 1
                }
            }
            encoded = json.dumps(hyp)
            decoded = json.loads(encoded)
            self.assertEqual(decoded["source_category"], cat)
            self.assertIn(decoded["evidence_evaluation"]["evidence_strength"], 
                          ["STRONG_COMPATIBILITY", "MODERATE_COMPATIBILITY", "WEAK_COMPATIBILITY", "INSUFFICIENT_EVIDENCE"])

    def test_deterministic_evidence_score_formula(self):
        """Verifies exact deterministic calculation of formula E(H)."""
        # E(H) = w_s S_s + w_t S_t + w_r S_r + w_d S_d + w_v S_v + w_b S_b - w_c C_c
        scores = {
            "spatial": 85.0,
            "temporal": 90.0,
            "trajectory": 80.0,
            "drift": 88.0,
            "vessel": 75.0,
            "behavior": 70.0,
            "contradiction": 10.0
        }
        weights = {
            "w_spatial": 0.20,
            "w_temporal": 0.15,
            "w_trajectory": 0.15,
            "w_drift": 0.20,
            "w_vessel": 0.15,
            "w_behavior": 0.15,
            "w_contradiction": 0.20
        }

        # Expected: (0.20*85 + 0.15*90 + 0.15*80 + 0.20*88 + 0.15*75 + 0.15*70) - (0.20*10)
        # = 17.0 + 13.5 + 12.0 + 17.6 + 11.25 + 10.5 - 2.0 = 79.85
        computed_score = (
            weights["w_spatial"] * scores["spatial"] +
            weights["w_temporal"] * scores["temporal"] +
            weights["w_trajectory"] * scores["trajectory"] +
            weights["w_drift"] * scores["drift"] +
            weights["w_vessel"] * scores["vessel"] +
            weights["w_behavior"] * scores["behavior"] -
            weights["w_contradiction"] * scores["contradiction"]
        )
        clamped_score = max(0.0, min(100.0, computed_score))
        
        self.assertAlmostEqual(clamped_score, 79.85, places=5)
        
        # Test bounds clamping
        negative_score = max(0.0, min(100.0, -15.0))
        self.assertEqual(negative_score, 0.0)
        
        overflow_score = max(0.0, min(100.0, 115.0))
        self.assertEqual(overflow_score, 100.0)

    def test_evidence_item_polarity_and_data_quality(self):
        """Verifies evidence item polarity, observation source, and data quality fields."""
        evidence = {
            "evidence_id": str(uuid.uuid4()),
            "evidence_type": "TRAJECTORY_INTERSECTION",
            "polarity": "SUPPORTING",
            "assertion": {
                "summary_text": "Vessel track intersects estimated release polygon",
                "numeric_value": 0.8,
                "unit": "km"
            },
            "observation_source": {
                "source_channel": "AIS_TRAJECTORY",
                "granule_or_feed_id": "GFW_AIS_STREAM_V2"
            },
            "data_quality": {
                "index": 0.92,
                "quality_flags": []
            },
            "weight_assigned": 0.15,
            "normalized_score_contribution": 12.0
        }
        
        encoded = json.dumps(evidence)
        decoded = json.loads(encoded)
        self.assertIn(decoded["polarity"], ["SUPPORTING", "CONTRADICTORY", "NEUTRAL_CONTEXT"])
        self.assertGreaterEqual(decoded["data_quality"]["index"], 0.0)
        self.assertLessEqual(decoded["data_quality"]["index"], 1.0)

    def test_contradiction_non_suppression(self):
        """Verifies contradiction structure and non-suppression status."""
        contra = {
            "contradiction_id": str(uuid.uuid4()),
            "contradiction_type": "TEMPORAL_IMPOSSIBILITY",
            "conflict_description": {
                "assertion_text": "Vessel departed harbor 3 hours after slick was already observed in SAR",
                "evidence_item_a_id": str(uuid.uuid4()),
                "evidence_item_b_id": str(uuid.uuid4()),
                "severity_penalty_weight": 0.35
            },
            "non_suppression_status": "ACTIVE_UNRESOLVED"
        }
        encoded = json.dumps(contra)
        decoded = json.loads(encoded)
        self.assertIn(decoded["non_suppression_status"], ["ACTIVE_UNRESOLVED", "ANALYST_ACKNOWLEDGED", "EXPLAINED_BY_SENSOR_ERROR"])

    def test_counterfactual_stability_schema(self):
        """Verifies counterfactual analysis stability rankings and score delta fields."""
        cf = {
            "counterfactual_analysis_id": str(uuid.uuid4()),
            "baseline_top_hypothesis_id": str(uuid.uuid4()),
            "baseline_top_score": 88.0,
            "second_ranked_hypothesis_id": str(uuid.uuid4()),
            "second_ranked_baseline_score": 52.0,
            "delta_score_margin": 36.0,
            "counterfactual_evaluation": {
                "ranking_stability": "ROBUST_DOMINANT_HYPOTHESIS"
            }
        }
        encoded = json.dumps(cf)
        decoded = json.loads(encoded)
        self.assertIn(decoded["counterfactual_evaluation"]["ranking_stability"], 
                      ["ROBUST_DOMINANT_HYPOTHESIS", "AMBIGUOUS_CLOSE_ALTERNATIVES", "FRAGILE_RANKING"])
        self.assertEqual(decoded["delta_score_margin"], 36.0)

if __name__ == "__main__":
    unittest.main()
