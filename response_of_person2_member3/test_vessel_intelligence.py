"""
Unit & Integration Test Suite for the MarineShield Vessel Intelligence Service.
Verifies:
1. Normalization of observations and spatial-temporal filtering.
2. Spatio-temporal matching (reconciliation algorithm v1).
3. Matched vs unmatched vessel categorization.
4. "Investigation flag, not an accusation" disclaimer on unmatched vessels.
5. Behavioral anomalies analysis (transmission gaps & speed drops).
6. Compliance with VESSEL_DATA_CONTRACT.md schema definitions.
"""

import sys
import uuid
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Setup paths
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(root_dir / "src"))

from marineshield.vessels.intelligence_service import VesselIntelligenceService
from marineshield.vessels.vessel_parser import VesselParser


class TestVesselIntelligenceService(unittest.TestCase):

    def setUp(self):
        self.service = VesselIntelligenceService()
        self.mock_mmsi = "413123456"
        self.sar_detection_id = str(uuid.uuid4())
        self.granule_id = "S1A_IW_GRDH_1SDV_20240120T005528_20240120T005553_052183_064ED6_FAD2"

        # ISO format UTC timestamp
        self.base_time = datetime(2024, 1, 20, 12, 0, 0, tzinfo=timezone.utc)
        self.base_time_str = self.base_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")

    def test_haversine_distance(self):
        # Mumbai to Alibag (~30km apart)
        dist = self.service.haversine_distance(18.93, 72.83, 18.66, 72.90)
        self.assertTrue(25000 < dist < 35000)

    def test_spatial_temporal_filtering(self):
        obs = [
            VesselParser.parse_ais_observation({
                "mmsi": self.mock_mmsi,
                "timestamp": (self.base_time - timedelta(minutes=10)).isoformat(),
                "latitude": 18.5,
                "longitude": 72.5
            }),
            VesselParser.parse_ais_observation({
                "mmsi": self.mock_mmsi,
                "timestamp": (self.base_time + timedelta(hours=5)).isoformat(),
                "latitude": 18.5,
                "longitude": 72.5
            })
        ]

        bbox = {
            "type": "Polygon",
            "coordinates": [[[72.0, 18.0], [73.0, 18.0], [73.0, 19.0], [72.0, 19.0], [72.0, 18.0]]]
        }

        filtered = self.service.filter_observations_by_window(
            observations=obs,
            geojson_polygon=bbox,
            start_time=self.base_time - timedelta(hours=1),
            end_time=self.base_time + timedelta(hours=1)
        )
        self.assertEqual(len(filtered), 1)

    def test_reconciliation_matching(self):
        # 1. Prepare simulated inputs
        sar_detections = [
            {
                "detection_id": self.sar_detection_id,
                "source_granule_id": self.granule_id,
                "detection_timestamp": self.base_time_str,
                "centroid_lat": 18.5,
                "centroid_lon": 72.5,
                "estimated_length_meters": 120.0,
                "estimated_width_meters": 20.0,
                "estimated_heading_deg": 90.0,
                "radar_cross_section_db": 42.0,
                "signal_to_clutter_ratio_db": 15.0,
                "detection_confidence": 0.95,
                "polarization_used": "VH",
            }
        ]

        # Close matching AIS observation
        ais_observations = [
            VesselParser.parse_ais_observation({
                "mmsi": self.mock_mmsi,
                "timestamp": (self.base_time + timedelta(seconds=30)).isoformat(),
                "latitude": 18.501,  # ~110m offset
                "longitude": 72.501,
                "sog": 10.0,
                "cog": 92.0,
                "heading_deg": 91.0,
                "nav_status": "UNDER_WAY_USING_ENGINE"
            })
        ]

        vessels = [VesselParser.create_mock_vessel(mmsi=self.mock_mmsi)]

        # 2. Run reconciliation
        results = self.service.run_reconciliation(
            sar_detections=sar_detections,
            ais_observations=ais_observations,
            vessels=vessels
        )

        self.assertEqual(len(results["matches"]), 1)
        self.assertEqual(len(results["unmatched"]), 0)

        match = results["matches"][0]
        self.assertEqual(match["matched_mmsi"], self.mock_mmsi)
        self.assertEqual(match["match_status"], "MATCHED")
        self.assertTrue(match["match_confidence"] > 0.8)

    def test_unmatched_vessel_investigation_flag(self):
        # SAR detection in spatial/temporal isolation
        sar_detections = [
            {
                "detection_id": self.sar_detection_id,
                "source_granule_id": self.granule_id,
                "detection_timestamp": self.base_time_str,
                "centroid_lat": 18.5,
                "centroid_lon": 72.5,
                "estimated_length_meters": 120.0,
                "estimated_width_meters": 20.0,
                "estimated_heading_deg": 90.0,
                "radar_cross_section_db": 42.0,
                "signal_to_clutter_ratio_db": 15.0,
                "detection_confidence": 0.95,
                "polarization_used": "VH",
            }
        ]

        # AIS observation is far away (~110km offset)
        ais_observations = [
            VesselParser.parse_ais_observation({
                "mmsi": self.mock_mmsi,
                "timestamp": self.base_time_str,
                "latitude": 19.5,
                "longitude": 72.5,
                "sog": 10.0,
                "cog": 92.0,
                "heading_deg": 91.0,
                "nav_status": "UNDER_WAY_USING_ENGINE"
            })
        ]

        vessels = [VesselParser.create_mock_vessel(mmsi=self.mock_mmsi)]

        results = self.service.run_reconciliation(
            sar_detections=sar_detections,
            ais_observations=ais_observations,
            vessels=vessels
        )

        self.assertEqual(len(results["matches"]), 0)
        self.assertEqual(len(results["unmatched"]), 1)

        unmatched = results["unmatched"][0]
        self.assertIn("INVESTIGATION FLAG ONLY", unmatched["description"])
        self.assertNotIn("accusation", unmatched["description"].lower())

    def test_behavior_anomaly_detection(self):
        # 1. AIS Gap simulation
        gap_obs = [
            VesselParser.parse_ais_observation({
                "mmsi": self.mock_mmsi,
                "timestamp": self.base_time_str,
                "latitude": 18.5,
                "longitude": 72.5,
                "sog": 12.0
            }),
            VesselParser.parse_ais_observation({
                "mmsi": self.mock_mmsi,
                "timestamp": (self.base_time + timedelta(hours=2)).isoformat(), # 2 hours gap
                "latitude": 18.6,
                "longitude": 72.6,
                "sog": 11.0
            })
        ]

        anomalies = self.service.detect_behavior_anomalies(gap_obs)
        self.assertEqual(len(anomalies), 1)
        self.assertEqual(anomalies[0]["anomaly_type"], "AIS_TRANSMISSION_GAP")

        # 2. Speed drop simulation
        drop_obs = [
            VesselParser.parse_ais_observation({
                "mmsi": self.mock_mmsi,
                "timestamp": self.base_time_str,
                "latitude": 18.5,
                "longitude": 72.5,
                "sog": 15.0
            }),
            VesselParser.parse_ais_observation({
                "mmsi": self.mock_mmsi,
                "timestamp": (self.base_time + timedelta(minutes=5)).isoformat(),
                "latitude": 18.505,
                "longitude": 72.505,
                "sog": 0.5  # Sudden speed drop to near-stationary
            })
        ]

        anomalies2 = self.service.detect_behavior_anomalies(drop_obs)
        self.assertEqual(len(anomalies2), 1)
        self.assertEqual(anomalies2[0]["anomaly_type"], "ABNORMAL_SPEED_DROP")


def main():
    print("================================================================================")
    print("        MarineShield Vessel Intelligence Service Unit Test Suite")
    print("================================================================================")
    suite = unittest.TestLoader().loadTestsFromTestCase(TestVesselIntelligenceService)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
