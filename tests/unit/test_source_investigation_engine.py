import json
import unittest
from pathlib import Path
from marineshield.investigation import (
    SourceInvestigationEngine,
    EnvironmentalHistory,
    VesselObservation,
    InvestigationResult
)

class TestSourceInvestigationEngine(unittest.TestCase):
    """Automated test suite verifying the end-to-end Release Reconstruction

    and Source-Investigation Engine.
    """
    def setUp(self):
        self.engine = SourceInvestigationEngine()
        self.spill_centroid = (73.250, 15.450)
        self.t_observation_utc = "2026-08-20T06:00:00Z"
        self.env_history = EnvironmentalHistory(
            wind_speed_ms=7.5,
            wind_direction_deg=240.0,
            current_u_ms=0.25,
            current_v_ms=-0.10,
            lookback_hours=6.0,
            data_quality_index=0.92
        )

    def test_strong_candidate(self):
        """Test Case 1: Strong dominant candidate vessel transiting release zone."""
        vessels = [
            VesselObservation(
                vessel_id="vessel-01",
                source_type="AIS_TRACK",
                vessel_name="OCEAN TITAN",
                vessel_mmsi="538001234",
                vessel_type="OIL_TANKER",
                vessel_flag="LR",
                track_points=[
                    {"lon": 73.235, "lat": 15.460, "timestamp_utc": "2026-08-20T02:30:00Z", "speed_knots": 13.5}
                ],
                has_ais_gap=True,
                speed_drop_knots=4.5
            ),
            VesselObservation(
                vessel_id="vessel-02",
                source_type="AIS_TRACK",
                vessel_name="COASTAL RUNNER",
                vessel_mmsi="538009999",
                vessel_type="FISHING",
                vessel_flag="IN",
                track_points=[
                    {"lon": 73.800, "lat": 15.900, "timestamp_utc": "2026-08-20T03:00:00Z", "speed_knots": 8.0}
                ]
            )
        ]

        result = self.engine.run_investigation(
            spill_centroid=self.spill_centroid,
            t_observation_utc=self.t_observation_utc,
            environmental_history=self.env_history,
            vessel_observations=vessels
        )

        self.assertIsInstance(result, InvestigationResult)
        self.assertEqual(result.status, "ATTRIBUTED_CANDIDATES_EVALUATED")
        self.assertFalse(result.is_unknown_triggered)
        self.assertEqual(result.top_hypothesis_category, "VESSEL_IDENTIFIED")
        self.assertGreaterEqual(result.top_evidence_score, 75.0)
        self.assertEqual(result.top_evidence_strength, "STRONG_COMPATIBILITY")
        self.assertEqual(result.ranking_stability, "ROBUST_DOMINANT_HYPOTHESIS")
        self.assertGreaterEqual(result.score_margin_over_second, 15.0)
        self.assertEqual(result.candidate_hypotheses[0].candidate_entity["vessel_name"], "OCEAN TITAN")

    def test_competing_candidates(self):
        """Test Case 2: Two candidate vessels in close spatio-temporal contention."""
        vessels = [
            VesselObservation(
                vessel_id="vessel-alpha",
                source_type="AIS_TRACK",
                vessel_name="PACIFIC TRADER",
                vessel_mmsi="419001111",
                vessel_type="BULK_CARRIER",
                track_points=[
                    {"lon": 73.240, "lat": 15.455, "timestamp_utc": "2026-08-20T02:15:00Z", "speed_knots": 12.0}
                ]
            ),
            VesselObservation(
                vessel_id="vessel-beta",
                source_type="AIS_TRACK",
                vessel_name="ATLANTIC LEADER",
                vessel_mmsi="419002222",
                vessel_type="CARGO",
                track_points=[
                    {"lon": 73.245, "lat": 15.450, "timestamp_utc": "2026-08-20T02:40:00Z", "speed_knots": 12.5}
                ]
            )
        ]

        result = self.engine.run_investigation(
            spill_centroid=self.spill_centroid,
            t_observation_utc=self.t_observation_utc,
            environmental_history=self.env_history,
            vessel_observations=vessels
        )

        self.assertEqual(result.ranking_stability, "AMBIGUOUS_CLOSE_ALTERNATIVES")
        self.assertLessEqual(result.score_margin_over_second, 5.0)

    def test_no_candidates(self):
        """Test Case 3: Zero candidate vessels present in maritime area."""
        result = self.engine.run_investigation(
            spill_centroid=self.spill_centroid,
            t_observation_utc=self.t_observation_utc,
            environmental_history=self.env_history,
            vessel_observations=[]
        )

        self.assertTrue(result.is_unknown_triggered)
        self.assertEqual(result.status, "SOURCE_UNKNOWN")
        self.assertEqual(result.top_hypothesis_category, "UNKNOWN_SOURCE")
        self.assertEqual(result.top_evidence_strength, "INSUFFICIENT_EVIDENCE")

    def test_contradictory_evidence(self):
        """Test Case 4: Candidate vessel moored at berth gets heavily penalized."""
        vessels = [
            VesselObservation(
                vessel_id="vessel-berth",
                source_type="AIS_TRACK",
                vessel_name="HARBOR QUEEN",
                vessel_mmsi="352009876",
                vessel_type="TANKER",
                track_points=[
                    {"lon": 73.235, "lat": 15.460, "timestamp_utc": "2026-08-20T02:30:00Z", "speed_knots": 0.0}
                ],
                is_moored_at_berth=True
            )
        ]

        result = self.engine.run_investigation(
            spill_centroid=self.spill_centroid,
            t_observation_utc=self.t_observation_utc,
            environmental_history=self.env_history,
            vessel_observations=vessels
        )

        cand = result.candidate_hypotheses[0]
        self.assertGreater(cand.component_scores["contradiction"], 50.0)
        self.assertLess(cand.evidence_score, 50.0)
        self.assertTrue(any(e["polarity"] == "CONTRADICTORY" for e in cand.contradictory_evidence))

    def test_missing_ais_blackout(self):
        """Test Case 5: 85% regional AIS blackout cleanly triggers mandatory UNKNOWN state."""
        vessels = [
            VesselObservation(
                vessel_id="vessel-marginal",
                source_type="AIS_TRACK",
                track_points=[{"lon": 73.24, "lat": 15.45, "timestamp_utc": "2026-08-20T02:00:00Z"}]
            )
        ]

        result = self.engine.run_investigation(
            spill_centroid=self.spill_centroid,
            t_observation_utc=self.t_observation_utc,
            environmental_history=self.env_history,
            vessel_observations=vessels,
            ais_coverage_percentage=15.0  # 85% blackout
        )

        self.assertTrue(result.is_unknown_triggered)
        self.assertEqual(result.status, "SOURCE_UNKNOWN")
        self.assertEqual(result.unknown_trigger_reason, "AIS_DATA_BLACKOUT")
        self.assertEqual(result.top_hypothesis_category, "UNKNOWN_SOURCE")

    def test_unmatched_sar_dark_vessel(self):
        """Test Case 6: SAR-detected dark vessel forms top hypothesis."""
        vessels = [
            VesselObservation(
                vessel_id="sar-dark-001",
                source_type="SAR_DETECTION",
                sar_vessel_detection_id="sar-det-s1a-20260820-0099",
                estimated_length_m=180.0
            )
        ]

        result = self.engine.run_investigation(
            spill_centroid=self.spill_centroid,
            t_observation_utc=self.t_observation_utc,
            environmental_history=self.env_history,
            vessel_observations=vessels
        )

        self.assertEqual(result.top_hypothesis_category, "VESSEL_UNTRACKED_DARK")
        self.assertTrue(result.candidate_hypotheses[0].unmatched_sar_target)
        self.assertGreater(result.top_evidence_score, 70.0)

    def test_uncertain_release_window(self):
        """Test Case 7: Extended 12-hour lookback expands release uncertainty polygon."""
        long_env = EnvironmentalHistory(
            wind_speed_ms=12.0,
            wind_direction_deg=270.0,
            current_u_ms=0.5,
            current_v_ms=0.2,
            lookback_hours=12.0
        )

        result = self.engine.run_investigation(
            spill_centroid=self.spill_centroid,
            t_observation_utc=self.t_observation_utc,
            environmental_history=long_env,
            vessel_observations=[]
        )

        self.assertEqual(result.release_hypothesis.window_duration_hours, 12.0)
        self.assertGreater(result.release_hypothesis.uncertainty_area_km2, 50.0)

    def test_non_vessel_source(self):
        """Test Case 8: Offshore facility non-vessel candidate."""
        facilities = [
            VesselObservation(
                vessel_id="platform-bombay-high-01",
                source_type="NON_VESSEL_FACILITY",
                vessel_name="BOMBAY HIGH SOUTH PLATFORM",
                track_points=[{"lon": 73.245, "lat": 15.452, "timestamp_utc": "2026-08-20T02:00:00Z"}]
            )
        ]

        result = self.engine.run_investigation(
            spill_centroid=self.spill_centroid,
            t_observation_utc=self.t_observation_utc,
            environmental_history=self.env_history,
            vessel_observations=facilities
        )

        self.assertEqual(result.top_hypothesis_category, "NON_VESSEL_SOURCE")

    def test_mathematical_reproducibility(self):
        """Test Case 9: 50 consecutive runs on identical inputs yield exact same output."""
        vessels = [
            VesselObservation(
                vessel_id="vessel-test",
                source_type="AIS_TRACK",
                track_points=[{"lon": 73.235, "lat": 15.460, "timestamp_utc": "2026-08-20T02:30:00Z"}]
            )
        ]

        ref = self.engine.run_investigation(
            spill_centroid=self.spill_centroid,
            t_observation_utc=self.t_observation_utc,
            environmental_history=self.env_history,
            vessel_observations=vessels
        )

        for _ in range(50):
            res = self.engine.run_investigation(
                spill_centroid=self.spill_centroid,
                t_observation_utc=self.t_observation_utc,
                environmental_history=self.env_history,
                vessel_observations=vessels
            )
            self.assertEqual(res.top_evidence_score, ref.top_evidence_score)
            self.assertEqual(res.ranking_stability, ref.ranking_stability)
            self.assertEqual(res.release_hypothesis.centroid_lon, ref.release_hypothesis.centroid_lon)

if __name__ == "__main__":
    unittest.main()
