import json
import unittest
from pathlib import Path
from marineshield.investigation import EvidenceContradictionEngine, EvidenceWeights, InvestigationThresholds

class TestEvidenceContradictionEngine(unittest.TestCase):
    """Test suite verifying deterministic operation, adversarial robustness, and contract conformance

    of the EvidenceContradictionEngine against canonical synthetic fixtures.
    """
    FIXTURES_DIR = Path("tests/fixtures/investigation")

    def setUp(self):
        self.engine = EvidenceContradictionEngine()

    def _load_fixture(self, filename: str) -> dict:
        path = self.FIXTURES_DIR / filename
        self.assertTrue(path.exists(), f"Fixture missing: {path}")
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def test_strict_mathematical_determinism(self):
        """Verifies that 100 consecutive executions on identical input yield identical results."""
        fixture = self._load_fixture("01_single_dominant_candidate.json")
        reference_result = self.engine.process_incident(fixture)
        
        for _ in range(100):
            res = self.engine.process_incident(fixture)
            self.assertEqual(res["top_evidence_score"], reference_result["top_evidence_score"])
            self.assertEqual(res["ranking_stability"], reference_result["ranking_stability"])
            self.assertEqual(res["score_margin_over_second"], reference_result["score_margin_over_second"])
            self.assertEqual(len(res["candidate_hypotheses"]), len(reference_result["candidate_hypotheses"]))

    def test_fixture_01_single_dominant_candidate(self):
        """Adversarial Case 1: Obvious dominant candidate with decisive margin."""
        fixture = self._load_fixture("01_single_dominant_candidate.json")
        result = self.engine.process_incident(fixture)

        self.assertEqual(result["top_hypothesis_id"], "src-hyp-01-vessel-a")
        self.assertEqual(result["top_hypothesis_category"], "VESSEL_IDENTIFIED")
        self.assertAlmostEqual(result["top_evidence_score"], 88.50, places=2)
        self.assertEqual(result["top_evidence_strength"], "STRONG_COMPATIBILITY")
        self.assertEqual(result["ranking_stability"], "ROBUST_DOMINANT_HYPOTHESIS")
        self.assertAlmostEqual(result["score_margin_over_second"], 47.85, places=2)
        self.assertFalse(result["is_unknown_triggered"])

    def test_fixture_02_two_equally_plausible_candidates(self):
        """Adversarial Case 2: Tied/close competitive candidates."""
        fixture = self._load_fixture("02_two_equally_plausible_candidates.json")
        result = self.engine.process_incident(fixture)

        self.assertEqual(result["top_hypothesis_id"], "src-hyp-02-vessel-alpha")
        self.assertAlmostEqual(result["top_evidence_score"], 81.15, places=2)
        self.assertEqual(result["ranking_stability"], "AMBIGUOUS_CLOSE_ALTERNATIVES")
        self.assertAlmostEqual(result["score_margin_over_second"], 1.05, places=2)
        self.assertFalse(result["is_unknown_triggered"])

    def test_fixture_03_no_plausible_candidate(self):
        """Adversarial Case 3: No candidates cross threshold, triggering UNKNOWN."""
        fixture = self._load_fixture("03_no_plausible_candidate.json")
        result = self.engine.process_incident(fixture)

        self.assertTrue(result["is_unknown_triggered"])
        self.assertEqual(result["status"], "SOURCE_UNKNOWN")
        self.assertEqual(result["top_hypothesis_category"], "UNKNOWN_SOURCE")
        self.assertEqual(result["top_evidence_strength"], "INSUFFICIENT_EVIDENCE")

    def test_fixture_04_ais_gap_anomaly(self):
        """Adversarial Case 4: AIS gap behavioral anomaly."""
        fixture = self._load_fixture("04_ais_gap_anomaly.json")
        result = self.engine.process_incident(fixture)

        self.assertEqual(result["top_hypothesis_id"], "src-hyp-04-vessel-gap")
        self.assertAlmostEqual(result["top_evidence_score"], 84.15, places=2)
        self.assertEqual(result["top_evidence_strength"], "STRONG_COMPATIBILITY")
        self.assertTrue(result["candidate_hypotheses"][0]["behavioral_anomaly_detected"])
        self.assertFalse(result["is_unknown_triggered"])

    def test_fixture_05_sar_unmatched_dark_vessel(self):
        """Adversarial Case 5: SAR dark vessel without AIS match forms top hypothesis."""
        fixture = self._load_fixture("05_sar_unmatched_dark_vessel.json")
        result = self.engine.process_incident(fixture)

        self.assertEqual(result["top_hypothesis_id"], "src-hyp-05-dark-vessel")
        self.assertEqual(result["top_hypothesis_category"], "VESSEL_UNTRACKED_DARK")
        self.assertAlmostEqual(result["top_evidence_score"], 86.25, places=2)
        self.assertTrue(result["candidate_hypotheses"][0]["unmatched_sar_target"])
        self.assertFalse(result["is_unknown_triggered"])

    def test_fixture_06_contradictory_evidence(self):
        """Adversarial Case 6: Active contradiction heavily penalizes candidate score."""
        fixture = self._load_fixture("06_contradictory_evidence.json")
        result = self.engine.process_incident(fixture)

        cand = result["candidate_hypotheses"][0]
        self.assertEqual(cand["source_hypothesis_id"], "src-hyp-06-vessel-contradicted")
        # Raw weighted = 45.5, deduction = 0.20 * 80.0 = 16.0 -> final = 29.50
        self.assertAlmostEqual(cand["evidence_score"], 29.50, places=2)
        self.assertTrue(result["is_unknown_triggered"])

    def test_fixture_07_invalid_missing_data_abstention(self):
        """Adversarial Case 7: Severe data quality deficit safely triggers pipeline abstention."""
        fixture = self._load_fixture("07_invalid_missing_data.json")
        result = self.engine.process_incident(fixture)

        self.assertEqual(result["status"], "ABSTAINED")
        self.assertEqual(result["abstention_state"], "ABSTAINED")
        self.assertEqual(result["abstention_reason"], "LOW_DATA_QUALITY")
        self.assertFalse(result["can_proceed_to_attribution"])
        self.assertEqual(result["recommendation"], "ANALYST_REVIEW_REQUIRED")

    def test_fixture_08_unknown_source_outcome(self):
        """Adversarial Case 8: AIS data blackout triggers mandatory UNKNOWN state."""
        fixture = self._load_fixture("08_unknown_source_outcome.json")
        result = self.engine.process_incident(fixture)

        self.assertTrue(result["is_unknown_triggered"])
        self.assertEqual(result["status"], "SOURCE_UNKNOWN")
        self.assertEqual(result["unknown_trigger_reason"], "AIS_DATA_BLACKOUT")
        self.assertEqual(result["top_hypothesis_category"], "UNKNOWN_SOURCE")

    def test_clamping_extremes(self):
        """Adversarial Test 9: Mathematical clamping bounds E(H) in [0.0, 100.0]."""
        # Test max clamping: All 100 scores
        max_scores = {"spatial": 100, "temporal": 100, "trajectory": 100, "drift": 100, "vessel": 100, "behavior": 100, "contradiction": 0}
        eval_max = self.engine.calculate_evidence_score(max_scores)
        self.assertEqual(eval_max["evidence_score"], 100.0)

        # Test min clamping: High contradiction penalty with 0 scores
        min_scores = {"spatial": 10, "temporal": 0, "trajectory": 0, "drift": 0, "vessel": 0, "behavior": 0, "contradiction": 100}
        eval_min = self.engine.calculate_evidence_score(min_scores)
        self.assertEqual(eval_min["evidence_score"], 0.0)
        self.assertLess(eval_min["raw_unclamped_score"], 0.0)

    def test_responsible_ai_non_guilt_clause(self):
        """Adversarial Test 10: Non-guilt disclaimer clause is present in every result."""
        fixture = self._load_fixture("01_single_dominant_candidate.json")
        result = self.engine.process_incident(fixture)
        self.assertIn("non_guilt_clause", result)
        self.assertIn("does not constitute legal proof", result["non_guilt_clause"])

if __name__ == "__main__":
    unittest.main()
