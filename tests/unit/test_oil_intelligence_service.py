import json
import unittest
import numpy as np
import torch
from pathlib import Path

from marineshield.oil_intelligence import (
    OilIntelligenceService,
    SpillDetectionResponse,
    DataQualityIndex
)

class TestOilIntelligenceService(unittest.TestCase):
    """Comprehensive test suite for the MarineShield Oil Intelligence Service.

    
    Tests:
    - Valid oil candidate detection & geometry extraction
    - Look-alike candidate rejection
    - Uncertain candidate handling
    - Malformed input rejection (empty, NaN/Inf, unsupported shape)
    - Missing model checkpoint handling
    - Missing metadata robustness
    - Abstention gating under low DQI (< 0.35)
    - Separation of detection confidence, verification confidence, and data quality
    - Presence of canonical non-claims in severity
    """
    SAMPLES_MANIFEST = Path("data/samples/samples_manifest.json")
    OIL_SAMPLE_PATH = Path("data/samples/oil/sample_oil_01_linear_slick.png")
    LOOKALIKE_SAMPLE_PATH = Path("data/samples/lookalike/sample_lookalike_01_low_wind_c0.png")

    @classmethod
    def setUpClass(cls):
        # Initialize service instance with existing adapted checkpoint
        cls.service = OilIntelligenceService(
            adapter_checkpoint_path="models/adapted/sar_sam_adapter_best.pth",
            base_sam_checkpoint_path="models/checkpoints/sam_vit_b_01ec64.pth",
            device="cuda" if torch.cuda.is_available() else "cpu"
        )
        with open(cls.SAMPLES_MANIFEST, "r", encoding="utf-8") as f:
            cls.manifest = json.load(f)

    def test_valid_oil_candidate(self):
        """Tests end-to-end processing of a known confirmed oil slick tile."""
        self.assertTrue(self.OIL_SAMPLE_PATH.exists(), f"Oil sample missing: {self.OIL_SAMPLE_PATH}")
        sample_meta = self.manifest["samples"][0]
        
        metadata = {
            "sar_granule_id": sample_meta["parent_scene_id"],
            "tile_id": sample_meta["sample_id"],
            "tile_bounds": (73.10, 15.20, 73.60, 15.70),
            "prompts": sample_meta["prompts"],
            "data_quality": {"index": 0.92, "quality_flags": []}
        }

        response = self.service.process_tile(self.OIL_SAMPLE_PATH, metadata=metadata)
        
        self.assertIsInstance(response, SpillDetectionResponse)
        self.assertEqual(response.status, "OIL_DETECTED")
        self.assertFalse(response.is_abstained)
        self.assertIsNone(response.abstention_details)
        
        # Check Look-Alike Verification (§6)
        self.assertEqual(response.lookalike_verification.predicted_class, "PETROLEUM_OIL")
        self.assertEqual(response.lookalike_verification.pipeline_decision, "ACCEPT_AS_OIL")
        self.assertGreaterEqual(response.lookalike_verification.class_probabilities["PETROLEUM_OIL"], 0.60)
        self.assertAlmostEqual(sum(response.lookalike_verification.class_probabilities.values()), 1.0, places=2)

        # Check Spill Geometry (§7)
        self.assertIsNotNone(response.spill_geometry)
        geojson = response.spill_geometry.geometry_geojson
        self.assertEqual(geojson["type"], "Feature")
        self.assertEqual(geojson["geometry"]["type"], "Polygon")
        self.assertGreater(geojson["properties"]["area_km2"], 0.0)
        self.assertGreater(geojson["properties"]["pixel_count"], 100)

        # Check Severity (§5)
        self.assertIn(response.severity.severity_class, ["SHEEN", "MODERATE", "THICK_HIGH_SEVERITY"])
        self.assertGreater(len(response.severity.explicit_non_claims), 0)

        # Check Provenance (§9)
        self.assertIsNotNone(response.provenance)
        self.assertEqual(response.provenance.sar_granule_id, sample_meta["parent_scene_id"])
        self.assertEqual(response.provenance.model_version_id, self.service.model_version_id)

    def test_lookalike_candidate(self):
        """Tests processing of a known look-alike (calm water / low-wind) tile."""
        self.assertTrue(self.LOOKALIKE_SAMPLE_PATH.exists(), f"Lookalike sample missing: {self.LOOKALIKE_SAMPLE_PATH}")
        sample_meta = self.manifest["samples"][5]  # first lookalike sample
        
        metadata = {
            "sar_granule_id": sample_meta["parent_scene_id"],
            "tile_id": sample_meta["sample_id"],
            "prompts": sample_meta["prompts"],
            "data_quality": {"index": 0.88, "quality_flags": []}
        }

        response = self.service.process_tile(self.LOOKALIKE_SAMPLE_PATH, metadata=metadata)
        
        self.assertIsInstance(response, SpillDetectionResponse)
        # Verify look-alike rejection behavior
        self.assertIn(response.status, ["LOOKALIKE_REJECTED", "NO_CANDIDATE_FOUND"])
        self.assertIn(response.lookalike_verification.predicted_class, ["LOW_WIND_AREA", "BIOGENIC_SLICK", "NATURAL_FILM", "SHIP_WAKE"])
        self.assertEqual(response.lookalike_verification.pipeline_decision, "REJECT_AS_LOOKALIKE")

    def test_uncertain_candidate(self):
        """Tests handling of an ambiguous/uncertain SAR patch."""
        # Create a synthetic low-contrast tile
        np.random.seed(42)
        ambiguous_tile = np.random.normal(loc=128.0, scale=5.0, size=(512, 512)).astype(np.float32)
        
        metadata = {
            "sar_granule_id": "S1A_IW_GRDH_AMBIGUOUS_TEST",
            "tile_id": "T_AMBIGUOUS_01",
            "data_quality": {"index": 0.65, "quality_flags": []}
        }

        response = self.service.process_tile(ambiguous_tile, metadata=metadata)
        self.assertIsInstance(response, SpillDetectionResponse)
        self.assertIn(response.status, ["LOOKALIKE_REJECTED", "NO_CANDIDATE_FOUND", "UNCERTAIN_ANALYSIS"])

    def test_malformed_input_rejection(self):
        """Tests strict validation against malformed, empty, or NaN inputs."""
        # 1. None input
        with self.assertRaises(ValueError):
            self.service.process_tile(None)

        # 2. Empty array
        with self.assertRaises(ValueError):
            self.service.process_tile(np.array([]))

        # 3. Array containing NaNs
        nan_arr = np.zeros((512, 512), dtype=np.float32)
        nan_arr[10, 10] = np.nan
        with self.assertRaises(ValueError):
            self.service.process_tile(nan_arr)

        # 4. Array with unsupported 4D shape
        invalid_shape = np.zeros((2, 3, 512, 512), dtype=np.float32)
        with self.assertRaises(ValueError):
            self.service.process_tile(invalid_shape)

    def test_missing_model_checkpoint(self):
        """Tests that initializing service with non-existent checkpoint raises FileNotFoundError."""
        bad_service = OilIntelligenceService(
            adapter_checkpoint_path="models/adapted/non_existent_adapter.pth",
            base_sam_checkpoint_path="models/checkpoints/sam_vit_b_01ec64.pth"
        )
        with self.assertRaises(FileNotFoundError):
            bad_service.process_tile(np.zeros((512, 512), dtype=np.float32))

    def test_missing_metadata_defaults(self):
        """Tests that service provides robust canonical defaults when optional metadata is omitted."""
        arr = np.ones((512, 512), dtype=np.float32) * 100.0
        response = self.service.process_tile(arr)
        
        self.assertIsInstance(response, SpillDetectionResponse)
        self.assertTrue(response.sar_granule_id.startswith("S1A_IW_GRDH"))
        self.assertIsNotNone(response.provenance)
        self.assertEqual(response.data_quality.index, 1.0)

    def test_abstention_gating(self):
        """Tests that low DQI (< 0.35) or fatal error flags trigger hard abstention (§10)."""
        arr = np.ones((512, 512), dtype=np.float32) * 100.0
        metadata = {
            "sar_granule_id": "S1A_IW_GRDH_LOW_QUALITY",
            "data_quality": {"index": 0.20, "quality_flags": ["SEVERE_THERMAL_NOISE", "NEAR_SCENE_EDGE"]}
        }
        response = self.service.process_tile(arr, metadata=metadata)
        
        self.assertTrue(response.is_abstained)
        self.assertEqual(response.status, "ABSTAINED")
        self.assertIsNotNone(response.abstention_details)
        self.assertEqual(response.abstention_details.abstention_reason_primary, "LOW_DATA_QUALITY")
        self.assertEqual(response.abstention_details.recommendation, "ANALYST_REVIEW_REQUIRED")
        self.assertIsNone(response.spill_mask)
        self.assertIsNone(response.spill_geometry)

    def test_separation_of_uncertainties(self):
        """Verifies strict separation between detection confidence, verification confidence, and data quality."""
        metadata = {
            "sar_granule_id": "S1A_IW_GRDH_SEPARATION_TEST",
            "data_quality": {"index": 0.77, "quality_flags": []}
        }
        response = self.service.process_tile(self.OIL_SAMPLE_PATH, metadata=metadata)
        
        # 1. Detection confidence (from mask/geometry)
        det_conf = response.spill_mask.model_confidence
        self.assertIn("mean_oil_probability", det_conf)
        self.assertIn("pixel_coverage_fraction", det_conf)

        # 2. Verification confidence (from lookalike classifier)
        ver_conf = response.lookalike_verification.model_confidence
        self.assertIn("max_class_probability", ver_conf)
        self.assertIn("entropy", ver_conf)
        self.assertIn("margin", ver_conf)

        # 3. Data quality (from pre-inference DQI)
        dqi = response.data_quality
        self.assertEqual(dqi.index, 0.77)

        # Assert no conflation
        self.assertNotEqual(det_conf["mean_oil_probability"], dqi.index)

if __name__ == "__main__":
    unittest.main()
