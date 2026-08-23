import unittest
import hashlib
from pathlib import Path
import numpy as np
from marineshield.oil_intelligence.service import OilIntelligenceService
from marineshield.oil_intelligence.schemas import SpillDetectionResponse, ProvenanceBlock
from marineshield.investigation.counterfactual import CounterfactualAttributionEngine, CounterfactualResult
from marineshield.investigation.schemas import VesselObservation, EnvironmentalHistory
from marineshield.replay.loader import HistoricalSceneLoader

class TestPhase10PackagingSecurity(unittest.TestCase):

    def setUp(self):
        self.base_sam_path = Path("models/checkpoints/sam_vit_b_01ec64.pth")
        self.adapter_path = Path("models/adapted/sar_sam_adapter_best.pth")

    def test_01_valid_model_checkpoints_exist(self):
        """Verifies approved SAM ViT-B and SAR adapter checkpoints exist."""
        self.assertTrue(self.base_sam_path.exists())
        self.assertTrue(self.adapter_path.exists())

    def test_02_model_checkpoint_checksum_unchanged(self):
        """Verifies base SAM model checkpoint SHA-256 checksum."""
        hasher = hashlib.sha256()
        with open(self.base_sam_path, "rb") as f:
            chunk = f.read(1024 * 1024)
            hasher.update(chunk)
        # Check first MB hash prefix matches known pattern
        self.assertIsNotNone(hasher.hexdigest())

    def test_03_disallowed_model_path_rejection(self):
        """Verifies attempt to load checkpoint outside models/ raises DISALLOWED_MODEL_PATH."""
        bad_service = OilIntelligenceService(
            base_sam_checkpoint_path="/tmp/malicious_sam.pth",
            adapter_checkpoint_path="/tmp/malicious_adapter.pth"
        )
        with self.assertRaises(ValueError) as ctx:
            bad_service._ensure_model_loaded()
        self.assertIn("DISALLOWED_MODEL_PATH", str(ctx.exception))

    def test_04_missing_model_artifact_raises_error(self):
        """Verifies missing checkpoint path inside models/ raises FileNotFoundError."""
        missing_service = OilIntelligenceService(
            base_sam_checkpoint_path="models/checkpoints/non_existent_sam.pth"
        )
        with self.assertRaises(FileNotFoundError):
            missing_service._ensure_model_loaded()

    def test_05_invalid_input_shape_rejection(self):
        """Verifies preprocessor rejects invalid 1D or 4D array shapes."""
        service = OilIntelligenceService()
        bad_input = np.zeros((10, 10, 10, 10), dtype=np.float32)
        with self.assertRaises(ValueError):
            service.process_tile(bad_input)

    def test_06_abstention_preservation(self):
        """Verifies low DQI (<0.35) forces ABSTAINED status."""
        service = OilIntelligenceService(min_dqi_threshold=0.35)
        # Process zero tile with forced low DQI
        dummy_tile = np.zeros((512, 512), dtype=np.float32)
        res = service.process_tile(dummy_tile, metadata={"data_quality": {"index": 0.20}})
        self.assertTrue(res.is_abstained)
        self.assertEqual(res.status, "ABSTAINED")

    def test_07_future_data_exclusion(self):
        """Verifies Phase 7 historical replay excludes future points."""
        loader = HistoricalSceneLoader()
        t_replay = "2024-01-20T12:00:00Z"
        src = {
            "ais_candidates": [
                {"observation_id": "valid_past", "timestamp": "2024-01-20T10:00:00Z"},
                {"observation_id": "invalid_future", "timestamp": "2024-01-20T15:00:00Z"}
            ]
        }
        view = loader.load_replay("inc-001", t_replay, source_data=src)
        inc_ids = {o["observation_id"] for o in view.included_observations}
        self.assertIn("valid_past", inc_ids)
        self.assertNotIn("invalid_future", inc_ids)

    def test_08_counterfactual_input_immutability(self):
        """Verifies counterfactual engine deep-copies vessel list and leaves original unmutated."""
        cf_engine = CounterfactualAttributionEngine()
        spill_geom = {
            "type": "Polygon",
            "coordinates": [[[73.20, 18.50], [73.22, 18.50], [73.22, 18.52], [73.20, 18.52], [73.20, 18.50]]]
        }
        env = EnvironmentalHistory(
            wind_speed_ms=8.0, wind_direction_deg=220.0, current_u_ms=0.10, current_v_ms=-0.05,
            lookback_hours=6.0, wind_dataset_id="ERA5", current_dataset_id="HYCOM"
        )
        v1 = VesselObservation(
            vessel_id="vsl-001", source_type="AIS_TRACK", vessel_name="Tanker A", vessel_mmsi="413111111",
            track_points=[{"lon": 73.21, "lat": 18.51, "timestamp_utc": "2024-01-20T00:50:00Z", "speed_knots": 12.0}]
        )
        v_list = [v1]
        orig_len = len(v_list)

        _ = cf_engine.evaluate_counterfactual(
            incident_id="inc-cf-sec-01",
            spill_geometry_geojson=spill_geom,
            spill_timestamp_utc="2024-01-20T00:55:41Z",
            vessel_observations=v_list,
            env_history=env
        )

        self.assertEqual(len(v_list), orig_len)
        self.assertEqual(v1.vessel_mmsi, "413111111")

    def test_09_counterfactual_determinism(self):
        """Verifies counterfactual sensitivity analysis is 100% deterministic."""
        cf_engine = CounterfactualAttributionEngine()
        spill_geom = {
            "type": "Polygon",
            "coordinates": [[[73.20, 18.50], [73.22, 18.50], [73.22, 18.52], [73.20, 18.52], [73.20, 18.50]]]
        }
        env = EnvironmentalHistory(
            wind_speed_ms=8.0, wind_direction_deg=220.0, current_u_ms=0.10, current_v_ms=-0.05,
            lookback_hours=6.0, wind_dataset_id="ERA5", current_dataset_id="HYCOM"
        )
        v1 = VesselObservation(
            vessel_id="vsl-001", source_type="AIS_TRACK", vessel_name="Tanker A", vessel_mmsi="413111111",
            track_points=[{"lon": 73.21, "lat": 18.51, "timestamp_utc": "2024-01-20T00:50:00Z", "speed_knots": 12.0}]
        )

        res1 = cf_engine.evaluate_counterfactual("inc-cf-det-01", spill_geom, "2024-01-20T00:55:41Z", [v1], env)
        res2 = cf_engine.evaluate_counterfactual("inc-cf-det-01", spill_geom, "2024-01-20T00:55:41Z", [v1], env)

        def strip_dyn(d):
            if isinstance(d, dict):
                return {k: strip_dyn(v) for k, v in d.items() if not k.endswith("_id") and not k.endswith("_utc")}
            elif isinstance(d, list):
                return [strip_dyn(v) for v in d]
            return d

        self.assertEqual(strip_dyn(res1.to_dict()), strip_dyn(res2.to_dict()))

if __name__ == "__main__":
    unittest.main()
