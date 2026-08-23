import unittest
import json
from pathlib import Path

class TestInvestigationFixtures(unittest.TestCase):
    """Test suite verifying deterministic behavior and contract compliance across all 8 synthetic investigation fixtures."""

    FIXTURES_DIR = Path("tests/fixtures/investigation")

    @classmethod
    def load_fixture(cls, filename: str) -> dict:
        fixture_path = cls.FIXTURES_DIR / filename
        assert fixture_path.exists(), f"Fixture file not found: {fixture_path}"
        with open(fixture_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def test_all_fixtures_exist_and_parse(self):
        """Verifies that all 8 required fixture files exist and parse as valid JSON."""
        expected_files = [
            "01_single_dominant_candidate.json",
            "02_two_equally_plausible_candidates.json",
            "03_no_plausible_candidate.json",
            "04_ais_gap_anomaly.json",
            "05_sar_unmatched_dark_vessel.json",
            "06_contradictory_evidence.json",
            "07_invalid_missing_data.json",
            "08_unknown_source_outcome.json"
        ]
        for fname in expected_files:
            data = self.load_fixture(fname)
            self.assertIn("scenario_id", data)
            self.assertIn("expected_outcome", data)

    def test_fixture_01_single_dominant_candidate(self):
        """Verifies Fixture 1: One obvious candidate with robust dominant ranking."""
        data = self.load_fixture("01_single_dominant_candidate.json")
        outcome = data["expected_outcome"]
        
        self.assertEqual(outcome["top_hypothesis_id"], "src-hyp-01-vessel-a")
        self.assertEqual(outcome["top_hypothesis_category"], "VESSEL_IDENTIFIED")
        self.assertEqual(outcome["top_evidence_strength"], "STRONG_COMPATIBILITY")
        self.assertEqual(outcome["ranking_stability"], "ROBUST_DOMINANT_HYPOTHESIS")
        self.assertGreater(outcome["score_margin_over_second"], 40.0)
        self.assertFalse(outcome["is_unknown_triggered"])

        # Check deterministic formula calculation for top candidate
        cand = data["candidate_hypotheses"][0]
        scores = cand["component_scores"]
        weights = {"s": 0.20, "t": 0.15, "r": 0.15, "d": 0.20, "v": 0.15, "b": 0.15, "c": 0.20}
        calc_score = (
            weights["s"] * scores["spatial"] +
            weights["t"] * scores["temporal"] +
            weights["r"] * scores["trajectory"] +
            weights["d"] * scores["drift"] +
            weights["v"] * scores["vessel"] +
            weights["b"] * scores["behavior"] -
            weights["c"] * scores["contradiction"]
        )
        self.assertAlmostEqual(calc_score, cand["evidence_score"], places=2)

    def test_fixture_02_two_equally_plausible_candidates(self):
        """Verifies Fixture 2: Two competitive candidates with ambiguous close alternatives."""
        data = self.load_fixture("02_two_equally_plausible_candidates.json")
        outcome = data["expected_outcome"]

        self.assertEqual(outcome["ranking_stability"], "AMBIGUOUS_CLOSE_ALTERNATIVES")
        self.assertLess(outcome["score_margin_over_second"], 2.0)
        self.assertFalse(outcome["is_unknown_triggered"])

        # Verify rank 1 and rank 2 both have strong scores
        h1 = data["candidate_hypotheses"][0]
        h2 = data["candidate_hypotheses"][1]
        self.assertGreaterEqual(h1["evidence_score"], 75.0)
        self.assertGreaterEqual(h2["evidence_score"], 75.0)
        self.assertAlmostEqual(h1["evidence_score"] - h2["evidence_score"], outcome["score_margin_over_second"], places=2)

    def test_fixture_03_no_plausible_candidate(self):
        """Verifies Fixture 3: No candidates cross threshold, triggering UNKNOWN source."""
        data = self.load_fixture("03_no_plausible_candidate.json")
        outcome = data["expected_outcome"]

        self.assertTrue(outcome["is_unknown_triggered"])
        self.assertEqual(outcome["top_hypothesis_category"], "UNKNOWN_SOURCE")
        self.assertEqual(outcome["top_evidence_strength"], "INSUFFICIENT_EVIDENCE")
        self.assertLess(outcome["top_evidence_score"], 30.0)

    def test_fixture_04_ais_gap_anomaly(self):
        """Verifies Fixture 4: AIS gap behavioral anomaly correctly flagged."""
        data = self.load_fixture("04_ais_gap_anomaly.json")
        outcome = data["expected_outcome"]

        self.assertTrue(outcome["behavioral_anomaly_detected"])
        self.assertEqual(outcome["top_evidence_strength"], "STRONG_COMPATIBILITY")
        self.assertFalse(outcome["is_unknown_triggered"])

        # Check that behavior score is elevated due to gap detection
        cand = data["candidate_hypotheses"][0]
        self.assertGreaterEqual(cand["component_scores"]["behavior"], 90.0)

    def test_fixture_05_sar_unmatched_dark_vessel(self):
        """Verifies Fixture 5: SAR dark vessel without AIS match forms top hypothesis."""
        data = self.load_fixture("05_sar_unmatched_dark_vessel.json")
        outcome = data["expected_outcome"]

        self.assertTrue(outcome["unmatched_sar_target"])
        self.assertEqual(outcome["top_hypothesis_category"], "VESSEL_UNTRACKED_DARK")
        self.assertEqual(outcome["top_evidence_strength"], "STRONG_COMPATIBILITY")

        # Verify candidate entity has null MMSI and valid SAR detection ID
        dark_cand = data["candidate_hypotheses"][0]
        self.assertIsNone(dark_cand["candidate_entity"]["vessel_mmsi"])
        self.assertIsNotNone(dark_cand["candidate_entity"]["sar_vessel_detection_id"])

    def test_fixture_06_contradictory_evidence(self):
        """Verifies Fixture 6: Active contradiction heavily penalizes candidate score."""
        data = self.load_fixture("06_contradictory_evidence.json")
        outcome = data["expected_outcome"]

        self.assertEqual(outcome["active_contradictions_count"], 1)
        self.assertTrue(outcome["is_unknown_triggered"])
        self.assertGreaterEqual(outcome["contradiction_penalty_applied"], 15.0)

        # Check penalty calculation: 0.20 * 80.0 = 16.0
        contra_cand = data["candidate_hypotheses"][0]
        penalty_deduction = 0.20 * contra_cand["component_scores"]["contradiction"]
        self.assertAlmostEqual(penalty_deduction, outcome["contradiction_penalty_applied"], places=2)

    def test_fixture_07_invalid_missing_data(self):
        """Verifies Fixture 7: Severe data quality deficit safely triggers pipeline abstention."""
        data = self.load_fixture("07_invalid_missing_data.json")
        outcome = data["expected_outcome"]

        self.assertTrue(outcome["is_abstention_triggered"])
        self.assertEqual(outcome["abstention_state"], "ABSTAINED")
        self.assertEqual(outcome["abstention_reason"], "LOW_DATA_QUALITY")
        self.assertFalse(outcome["can_proceed_to_attribution"])
        self.assertEqual(outcome["recommendation"], "ANALYST_REVIEW_REQUIRED")

    def test_fixture_08_unknown_source_outcome(self):
        """Verifies Fixture 8: Unknown source state with concrete diagnostic actions."""
        data = self.load_fixture("08_unknown_source_outcome.json")
        outcome = data["expected_outcome"]

        self.assertTrue(outcome["is_unknown_triggered"])
        self.assertEqual(outcome["unknown_trigger_reason"], "AIS_DATA_BLACKOUT")
        self.assertGreaterEqual(outcome["recommended_actions_count"], 3)
        self.assertIn("unknown_state", data)
        self.assertEqual(data["unknown_state"]["status"], "SOURCE_UNKNOWN")

if __name__ == "__main__":
    unittest.main()
