"""
MarineShield Demonstration Vessel Observations Verification Test
Verifies:
1. Existence and valid JSON parsing of data/vessel_demonstration_results.json artifact.
2. Presence of all 5 required result categories:
   - ais_candidates
   - sar_vessel_detections
   - matches
   - unmatched_detections
   - behavior_features
3. Conformance of entities with VESSEL_DATA_CONTRACT.md definitions.
4. Absence of plain-text API tokens or sensitive credentials.
5. Presence of metadata and provenance hash.
"""

import sys
import json
import unittest
from pathlib import Path

# Setup paths
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(root_dir / "src"))


class TestVesselDemonstrationArtifact(unittest.TestCase):

    def setUp(self):
        self.artifact_path = root_dir / "data" / "vessel_demonstration_results.json"
        self.assertTrue(self.artifact_path.exists(), f"Artifact not found at {self.artifact_path}")
        
        with open(self.artifact_path, "r", encoding="utf-8") as f:
            self.data = json.load(f)

    def test_top_level_categories(self):
        required_categories = [
            "ais_candidates",
            "sar_vessel_detections",
            "matches",
            "unmatched_detections",
            "behavior_features",
            "demonstration_metadata",
        ]
        for cat in required_categories:
            self.assertIn(cat, self.data, f"Missing category: {cat}")

    def test_demonstration_metadata(self):
        meta = self.data["demonstration_metadata"]
        self.assertEqual(meta["period_start"], "2024-01-15")
        self.assertEqual(meta["period_end"], "2024-01-25")
        self.assertEqual(meta["bbox_wgs84"], [72.0, 18.0, 74.0, 20.0])
        self.assertIn("provenance_hash", meta)

    def test_ais_candidates(self):
        candidates = self.data["ais_candidates"]
        self.assertGreater(len(candidates), 0, "ais_candidates must not be empty")
        for cand in candidates:
            self.assertIn("observation_id", cand)
            self.assertIn("mmsi", cand)
            self.assertEqual(len(cand["mmsi"]), 9)
            self.assertIn("latitude", cand)
            self.assertIn("longitude", cand)
            self.assertTrue(-90.0 <= cand["latitude"] <= 90.0)
            self.assertTrue(-180.0 <= cand["longitude"] <= 180.0)

    def test_sar_vessel_detections(self):
        detections = self.data["sar_vessel_detections"]
        self.assertGreater(len(detections), 0, "sar_vessel_detections must not be empty")
        for det in detections:
            self.assertIn("detection_id", det)
            self.assertIn("source_granule_id", det)
            self.assertIn("centroid_lat", det)
            self.assertIn("centroid_lon", det)
            self.assertIn("detection_confidence", det)

    def test_matches(self):
        matches = self.data["matches"]
        self.assertGreater(len(matches), 0, "matches must not be empty")
        for m in matches:
            self.assertIn("match_id", m)
            self.assertIn("sar_detection_id", m)
            self.assertIn("matched_mmsi", m)
            self.assertIn("match_status", m)
            self.assertIn("match_confidence", m)

    def test_unmatched_detections(self):
        unmatched = self.data["unmatched_detections"]
        self.assertGreater(len(unmatched), 0, "unmatched_detections must not be empty")
        for u in unmatched:
            self.assertIn("unmatched_id", u)
            self.assertIn("sar_detection_id", u)
            self.assertIn("description", u)
            self.assertIn("INVESTIGATION FLAG ONLY", u["description"])

    def test_behavior_features(self):
        bf = self.data["behavior_features"]
        self.assertIn("anomalies_detected", bf)
        self.assertIn("vessel_trajectories_summary", bf)
        self.assertGreater(len(bf["anomalies_detected"]), 0)
        self.assertGreater(len(bf["vessel_trajectories_summary"]), 0)

    def test_no_secret_leaks(self):
        content = json.dumps(self.data)
        self.assertNotIn("eyJhbGciOiJSUzI1NiIs", content, "JWT / API token leaked in JSON output!")


def main():
    print("================================================================================")
    print("      MarineShield Demonstration Vessel Observations Verification Suite")
    print("================================================================================")
    suite = unittest.TestLoader().loadTestsFromTestCase(TestVesselDemonstrationArtifact)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
