import json
import unittest
from pathlib import Path
from marineshield.investigation import (
    SourceInvestigationEngine,
    EnvironmentalHistory,
    VesselObservation
)

class TestInvestigationIntegration(unittest.TestCase):
    """End-to-End Synthetic Investigation Integration Test.

    
    Validates complete pipeline integration:
    Spill Detection Input -> Environmental History Ingest -> Backward Release Reconstruction
    -> AIS Candidate Filtering -> Evidence Scoring & Contradiction -> JSON Output Envelope.
    """
    def test_end_to_end_synthetic_investigation(self):
        engine = SourceInvestigationEngine()

        # 1. Spill input from Member 2
        spill_centroid = (73.325, 15.525)
        t_obs_utc = "2026-08-20T05:30:00Z"

        # 2. Environmental forcing from Member 5
        env_history = EnvironmentalHistory(
            wind_speed_ms=8.2,
            wind_direction_deg=225.0,  # SW Monsoon
            current_u_ms=0.30,
            current_v_ms=-0.15,
            lookback_hours=5.0,
            wind_dataset_id="ERA5-Reanalysis-2026-08",
            current_dataset_id="HYCOM-Global-Analysis-2026-08",
            data_quality_index=0.95
        )

        # 3. Vessel intelligence observations from Member 3
        vessels = [
            VesselObservation(
                vessel_id="vsl-mmsi-538009123",
                source_type="AIS_TRACK",
                vessel_name="PACIFIC VOYAGER",
                vessel_mmsi="538009123",
                vessel_type="OIL_TANKER",
                vessel_flag="PA",
                track_points=[
                    {"lon": 73.310, "lat": 15.540, "timestamp_utc": "2026-08-20T02:45:00Z", "speed_knots": 14.2}
                ],
                has_ais_gap=True,
                speed_drop_knots=5.2
            ),
            VesselObservation(
                vessel_id="vsl-mmsi-419008888",
                source_type="AIS_TRACK",
                vessel_name="INDIAN SEA",
                vessel_mmsi="419008888",
                vessel_type="CARGO",
                vessel_flag="IN",
                track_points=[
                    {"lon": 73.318, "lat": 15.535, "timestamp_utc": "2026-08-20T03:00:00Z", "speed_knots": 11.0}
                ]
            ),
            VesselObservation(
                vessel_id="sar-dark-target-007",
                source_type="SAR_DETECTION",
                sar_vessel_detection_id="sar-det-s1a-20260820-0042",
                estimated_length_m=165.0
            )
        ]

        # 4. Run Investigation
        result = engine.run_investigation(
            spill_centroid=spill_centroid,
            t_observation_utc=t_obs_utc,
            environmental_history=env_history,
            vessel_observations=vessels,
            ais_coverage_percentage=92.0,
            data_quality_index=0.95,
            incident_id="8f3b21c4-91a5-4e89-b762-d21f8a49c101",
            scenario_id="SCENARIO-E2E-INTEGRATION"
        )

        result_dict = result.to_dict()

        # 5. Assertions & Contract Validations
        self.assertEqual(result_dict["incident_id"], "8f3b21c4-91a5-4e89-b762-d21f8a49c101")
        self.assertEqual(result_dict["status"], "ATTRIBUTED_CANDIDATES_EVALUATED")
        self.assertFalse(result_dict["is_unknown_triggered"])

        # Release Hypothesis Checks
        rel = result_dict["release_hypothesis"]
        self.assertIn("temporal_scope", rel)
        self.assertIn("spatial_scope", rel)
        self.assertEqual(rel["spatial_scope"]["release_polygon_geojson"]["type"], "Feature")
        self.assertGreater(rel["spatial_scope"]["release_polygon_geojson"]["properties"]["uncertainty_area_km2"], 0.0)

        # Candidate Hypotheses Checks
        cands = result_dict["candidate_hypotheses"]
        self.assertEqual(len(cands), 3)
        self.assertEqual(cands[0]["evidence_evaluation"]["ranking_position"], 1)
        self.assertGreaterEqual(cands[0]["evidence_evaluation"]["evidence_score"], 75.0)
        self.assertEqual(cands[0]["evidence_evaluation"]["evidence_strength"], "STRONG_COMPATIBILITY")

        # JSON Serializability Check
        json_output = json.dumps(result_dict, indent=2)
        self.assertIsInstance(json_output, str)
        self.assertGreater(len(json_output), 1000)

        # Print formatted summary for reporting
        print("\n=== End-to-End Synthetic Investigation Output Summary ===")
        print(f"Incident ID: {result_dict['incident_id']}")
        print(f"Status: {result_dict['status']}")
        print(f"Release Reconstructed Centroid: [{rel['spatial_scope']['release_polygon_geojson']['properties']['centroid_lon']}, {rel['spatial_scope']['release_polygon_geojson']['properties']['centroid_lat']}]")
        print(f"Release Window: [{rel['temporal_scope']['t_earliest_utc']} to {rel['temporal_scope']['t_latest_utc']}]")
        print(f"Top Candidate: {cands[0]['candidate_entity'].get('vessel_name') or cands[0]['candidate_entity'].get('description')}")
        print(f"Top Evidence Score: {cands[0]['evidence_evaluation']['evidence_score']} ({cands[0]['evidence_evaluation']['evidence_strength']})")
        print(f"Ranking Stability: {result_dict['ranking_stability']} (margin: {result_dict['score_margin_over_second']:.1f} pts)")
        print(f"Non-Guilt Clause: {result_dict['non_guilt_clause']}")
        print("==========================================================\n")

if __name__ == "__main__":
    unittest.main()
