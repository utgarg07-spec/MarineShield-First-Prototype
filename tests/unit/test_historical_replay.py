import unittest
import copy
import datetime
from marineshield.replay.loader import HistoricalSceneLoader, parse_iso_utc
from marineshield.replay.schemas import FrozenReplayView

class TestHistoricalReplay(unittest.TestCase):

    def setUp(self):
        self.loader = HistoricalSceneLoader()
        self.t_replay = "2024-01-20T12:00:00Z"
        self.timeline_dataset = {
            "demonstration_metadata": {
                "data_mode": "MOCK_HYBRID",
                "provenance_hash": "test_hash_123"
            },
            "ais_candidates": [
                {"observation_id": "obs-t-minus-6h", "mmsi": "111111111", "timestamp": "2024-01-20T06:00:00Z", "latitude": 18.0, "longitude": 73.0},
                {"observation_id": "obs-t-minus-1h", "mmsi": "222222222", "timestamp": "2024-01-20T11:00:00Z", "latitude": 18.1, "longitude": 73.1},
                {"observation_id": "obs-t-exact", "mmsi": "333333333", "timestamp": "2024-01-20T12:00:00Z", "latitude": 18.2, "longitude": 73.2},
                {"observation_id": "obs-t-plus-1h", "mmsi": "444444444", "timestamp": "2024-01-20T13:00:00Z", "latitude": 18.3, "longitude": 73.3},
                {"observation_id": "obs-t-plus-6h", "mmsi": "555555555", "timestamp": "2024-01-20T18:00:00Z", "latitude": 18.4, "longitude": 73.4},
            ],
            "sar_vessel_detections": [
                {"detection_id": "sar-t-minus-1h", "detection_timestamp": "2024-01-20T11:00:00Z", "centroid_lat": 18.5, "centroid_lon": 73.5},
                {"detection_id": "sar-t-plus-1h", "detection_timestamp": "2024-01-20T13:00:00Z", "centroid_lat": 18.6, "centroid_lon": 73.6}
            ]
        }

    def test_replay_timeline_cutoff(self):
        view = self.loader.load_replay("inc-001", self.t_replay, source_data=self.timeline_dataset)
        included_ids = {obs["observation_id"] for obs in view.included_observations}
        excluded_ids = {obs["observation_id"] for obs in view.excluded_observations_summary}

        self.assertIn("obs-t-minus-6h", included_ids)
        self.assertIn("obs-t-minus-1h", included_ids)
        self.assertIn("obs-t-exact", included_ids)
        self.assertIn("sar-t-minus-1h", included_ids)

        self.assertIn("obs-t-plus-1h", excluded_ids)
        self.assertIn("obs-t-plus-6h", excluded_ids)
        self.assertIn("sar-t-plus-1h", excluded_ids)

    def test_direct_access_future_record_prevention(self):
        view = self.loader.load_replay("inc-001", self.t_replay, source_data=self.timeline_dataset)
        future_obs = [obs for obs in view.included_observations if obs["observation_id"] == "obs-t-plus-1h"]
        self.assertEqual(len(future_obs), 0)

    def test_source_mutation_isolation(self):
        view = self.loader.load_replay("inc-001", self.t_replay, source_data=self.timeline_dataset)
        initial_included_count = len(view.included_observations)

        self.timeline_dataset["ais_candidates"].append({
            "observation_id": "malicious-injected-record",
            "mmsi": "999999999",
            "timestamp": "2024-01-20T05:00:00Z"
        })

        self.assertEqual(len(view.included_observations), initial_included_count)

    def test_timezone_normalization(self):
        dataset = {
            "ais_candidates": [
                {"observation_id": "est-future", "timestamp": "2024-01-20T13:00:00-05:00"},
                {"observation_id": "est-past", "timestamp": "2024-01-20T05:00:00-05:00"}
            ]
        }
        view = self.loader.load_replay("inc-001", self.t_replay, source_data=dataset)
        included_ids = {obs["observation_id"] for obs in view.included_observations}
        excluded_ids = {obs["observation_id"] for obs in view.excluded_observations_summary}

        self.assertIn("est-past", included_ids)
        self.assertIn("est-future", excluded_ids)

    def test_ambiguous_or_missing_timestamp_quarantine(self):
        dataset = {
            "ais_candidates": [
                {"observation_id": "valid-ts", "timestamp": "2024-01-20T10:00:00Z"},
                {"observation_id": "missing-ts", "timestamp": None},
                {"observation_id": "malformed-ts", "timestamp": "NOT-A-TIMESTAMP"}
            ]
        }
        view = self.loader.load_replay("inc-001", self.t_replay, source_data=dataset)
        included_ids = {obs["observation_id"] for obs in view.included_observations}
        quarantined_ids = {obs["record_id"] for obs in view.quarantined_records_summary}

        self.assertIn("valid-ts", included_ids)
        self.assertIn("missing-ts", quarantined_ids)
        self.assertIn("malformed-ts", quarantined_ids)

    def test_source_dataset_remains_unmutated(self):
        original_len = len(self.timeline_dataset["ais_candidates"])
        _ = self.loader.load_replay("inc-001", self.t_replay, source_data=self.timeline_dataset)
        self.assertEqual(len(self.timeline_dataset["ais_candidates"]), original_len)

    def test_replay_determinism(self):
        view1 = self.loader.load_replay("inc-001", self.t_replay, source_data=self.timeline_dataset)
        view2 = self.loader.load_replay("inc-001", self.t_replay, source_data=self.timeline_dataset)
        self.assertEqual(view1.to_dict(), view2.to_dict())

if __name__ == "__main__":
    unittest.main()
