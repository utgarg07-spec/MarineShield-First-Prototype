import unittest
import copy
from typing import Dict, Any, List
from marineshield.investigation.counterfactual import CounterfactualAttributionEngine, CounterfactualResult
from marineshield.investigation.schemas import VesselObservation, EnvironmentalHistory
from marineshield.replay.loader import HistoricalSceneLoader

class TestCounterfactualAttribution(unittest.TestCase):

    def setUp(self):
        self.engine = CounterfactualAttributionEngine()
        self.mock_spill_geometry = {
            "type": "Polygon",
            "coordinates": [[[73.20, 18.50], [73.22, 18.50], [73.22, 18.52], [73.20, 18.52], [73.20, 18.50]]]
        }
        self.mock_env_history = EnvironmentalHistory(
            wind_speed_ms=8.5,
            wind_direction_deg=220.0,
            current_u_ms=0.15,
            current_v_ms=-0.05,
            lookback_hours=6.0,
            wind_dataset_id="ERA5-WIND-20240120",
            current_dataset_id="HYCOM-CURR-20240120"
        )
        self.ts = "2024-01-20T00:55:41Z"

    def test_01_dominant_candidate(self):
        v1 = VesselObservation(
            vessel_id="vsl-dominant-001", source_type="AIS_TRACK", vessel_name="MV Dominant Tanker", vessel_mmsi="413111111", vessel_type="TANKER",
            track_points=[{"lon": 73.205, "lat": 18.505, "timestamp_utc": "2024-01-20T00:50:00Z", "speed_knots": 12.0}],
            has_ais_gap=True, speed_drop_knots=4.5
        )
        v2 = VesselObservation(
            vessel_id="vsl-distant-002", source_type="AIS_TRACK", vessel_name="MV Distant Cargo", vessel_mmsi="413222222", vessel_type="CARGO",
            track_points=[{"lon": 73.800, "lat": 18.900, "timestamp_utc": "2024-01-20T00:30:00Z", "speed_knots": 14.0}],
            has_ais_gap=False, speed_drop_knots=0.0
        )

        cf_res = self.engine.evaluate_counterfactual(
            incident_id="inc-cf-001",
            spill_geometry_geojson=self.mock_spill_geometry,
            spill_timestamp_utc=self.ts,
            vessel_observations=[v1, v2],
            env_history=self.mock_env_history
        )

        self.assertEqual(cf_res.status, "SUCCESS")
        self.assertEqual(cf_res.original_candidate_count, 2)
        self.assertEqual(cf_res.counterfactual_candidate_count, 1)
        self.assertIn(cf_res.removed_candidate_id, ["vsl-dominant-001", "413111111"])
        self.assertTrue(cf_res.is_top_hypothesis_dominant)
        self.assertEqual(len(cf_res.rank_changes), 1)

    def test_02_weak_candidate(self):
        v1 = VesselObservation(
            vessel_id="vsl-weak-A", source_type="AIS_TRACK", vessel_name="Vessel A", vessel_mmsi="413333333",
            track_points=[{"lon": 73.40, "lat": 18.60, "timestamp_utc": "2024-01-20T00:40:00Z", "speed_knots": 10.0}]
        )
        v2 = VesselObservation(
            vessel_id="vsl-weak-B", source_type="AIS_TRACK", vessel_name="Vessel B", vessel_mmsi="413444444",
            track_points=[{"lon": 73.45, "lat": 18.65, "timestamp_utc": "2024-01-20T00:42:00Z", "speed_knots": 11.0}]
        )

        cf_res = self.engine.evaluate_counterfactual(
            incident_id="inc-cf-002",
            spill_geometry_geojson=self.mock_spill_geometry,
            spill_timestamp_utc=self.ts,
            vessel_observations=[v1, v2],
            env_history=self.mock_env_history
        )

        self.assertEqual(cf_res.status, "SUCCESS")
        self.assertTrue(cf_res.is_result_weak_or_tied)

    def test_03_tied_candidates(self):
        v1 = VesselObservation(
            vessel_id="vsl-tie-1", source_type="AIS_TRACK", vessel_name="Twin 1", vessel_mmsi="413555555",
            track_points=[{"lon": 73.21, "lat": 18.51, "timestamp_utc": "2024-01-20T00:50:00Z", "speed_knots": 12.0}]
        )
        v2 = VesselObservation(
            vessel_id="vsl-tie-2", source_type="AIS_TRACK", vessel_name="Twin 2", vessel_mmsi="413666666",
            track_points=[{"lon": 73.21, "lat": 18.51, "timestamp_utc": "2024-01-20T00:50:00Z", "speed_knots": 12.0}]
        )

        cf_res = self.engine.evaluate_counterfactual(
            incident_id="inc-cf-003",
            spill_geometry_geojson=self.mock_spill_geometry,
            spill_timestamp_utc=self.ts,
            vessel_observations=[v1, v2],
            env_history=self.mock_env_history
        )

        self.assertEqual(cf_res.status, "BLOCKED_TIE_POLICY_REQUIRED")
        self.assertEqual(cf_res.reason, "TOP_RANK_TIE_DETECTED_NO_SINGLE_CANDIDATE_REMOVED")
        self.assertIsNone(cf_res.removed_candidate_id)

    def test_04_unknown_source(self):
        cf_res = self.engine.evaluate_counterfactual(
            incident_id="inc-cf-004",
            spill_geometry_geojson=self.mock_spill_geometry,
            spill_timestamp_utc=self.ts,
            vessel_observations=[],
            env_history=self.mock_env_history
        )

        self.assertEqual(cf_res.status, "NOT_APPLICABLE")
        self.assertEqual(cf_res.reason, "NO_RANKED_CANDIDATE_AVAILABLE")
        self.assertEqual(cf_res.original_candidate_count, 0)

    def test_05_input_immutability(self):
        v1 = VesselObservation(
            vessel_id="vsl-dominant-001", source_type="AIS_TRACK", vessel_name="MV Dominant Tanker", vessel_mmsi="413111111",
            track_points=[{"lon": 73.205, "lat": 18.505, "timestamp_utc": "2024-01-20T00:50:00Z", "speed_knots": 12.0}]
        )
        obs_list = [v1]
        orig_len = len(obs_list)
        orig_mmsi = v1.vessel_mmsi

        _ = self.engine.evaluate_counterfactual(
            incident_id="inc-cf-005",
            spill_geometry_geojson=self.mock_spill_geometry,
            spill_timestamp_utc=self.ts,
            vessel_observations=obs_list,
            env_history=self.mock_env_history
        )

        self.assertEqual(len(obs_list), orig_len)
        self.assertEqual(v1.vessel_mmsi, orig_mmsi)

    def test_06_determinism(self):
        v1 = VesselObservation(
            vessel_id="vsl-dominant-001", source_type="AIS_TRACK", vessel_name="MV Dominant Tanker", vessel_mmsi="413111111",
            track_points=[{"lon": 73.205, "lat": 18.505, "timestamp_utc": "2024-01-20T00:50:00Z", "speed_knots": 12.0}]
        )

        cf1 = self.engine.evaluate_counterfactual("inc-cf-006", self.mock_spill_geometry, self.ts, [v1], self.mock_env_history)
        cf2 = self.engine.evaluate_counterfactual("inc-cf-006", self.mock_spill_geometry, self.ts, [v1], self.mock_env_history)

        def strip_dyn(d):
            if isinstance(d, dict):
                return {k: strip_dyn(v) for k, v in d.items() if not k.endswith("_id") and not k.endswith("_utc")}
            elif isinstance(d, list):
                return [strip_dyn(v) for v in d]
            return d

        self.assertEqual(strip_dyn(cf1.to_dict()), strip_dyn(cf2.to_dict()))

    def test_07_historical_replay_compatibility(self):
        v1 = VesselObservation(
            vessel_id="vsl-replay-1", source_type="AIS_TRACK", vessel_name="Vessel Replay", vessel_mmsi="413777777",
            track_points=[
                {"lon": 73.20, "lat": 18.50, "timestamp_utc": "2024-01-20T00:30:00Z", "speed_knots": 12.0},
                {"lon": 72.50, "lat": 17.50, "timestamp_utc": "2024-01-20T03:00:00Z", "speed_knots": 15.0}
            ]
        )

        cf_res = self.engine.evaluate_counterfactual(
            incident_id="inc-cf-007",
            spill_geometry_geojson=self.mock_spill_geometry,
            spill_timestamp_utc=self.ts,
            vessel_observations=[v1],
            env_history=self.mock_env_history,
            replay_timestamp_utc=self.ts
        )

        self.assertEqual(cf_res.replay_timestamp_utc, self.ts)

if __name__ == "__main__":
    unittest.main()
